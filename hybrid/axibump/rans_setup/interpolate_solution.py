#!/usr/bin/env python3
""" Interpolate a slice onto an SU2 ASCII restart file.
"""

import argparse
import numpy as np
from scipy.interpolate import griddata
import sys

def WriteToSU2(restart_file, outfile, array, num_footer_lines=9):
    """ Write an array to an SU2 restart file, using another file as a template

    This function assumes that the array has all the data necessary for SU2.

    Args:
        restart_file: An ASCII restart file for SU2, whose points should
            match the array's points
        outfile: The name of the file to be written, including the extension
        array: The array to be saved
        num_footer_lines: The number of lines in the footer of the SU2 restart
    """
    # Get the header and footer from interpolated file
    print("Saving results to " + outfile)
    with open(restart_file, 'r') as infile:
        header = infile.readline().strip()
        footer = ""
        # Skip over the data
        for i in range(array['x'].size):
            infile.readline()
        for i in range(num_footer_lines):
            footer += infile.readline()
        footer = footer.strip()

    # Write the results to a file
    fmt_str = "%d"
    for i in range(len(array.dtype.names) - 1):
        fmt_str += "\t%.17e"
    np.savetxt(outfile, array, fmt=fmt_str, header=header, footer=footer,
               comments="")

def main(args):
    # The number of lines in the footer of the SU2 restart file
    num_lines_in_footer = 8

    print("Reading in original data...")
    restart_data = np.genfromtxt(args.restart, names=True,
                                 skip_footer=num_lines_in_footer)
    print(restart_data.dtype.names)

    # Convert restart coordinates to polar
    restart = {}
    restart['phi'] = np.arctan2(restart_data['z'], restart_data['y'])
    restart['r'] = restart_data['y']*np.cos(restart['phi']) + \
                     restart_data['z']*np.sin(restart['phi'])

    print("Reading in data to be interpolated...")
    coarse_data = np.load(args.input)

    # Check for anything slightly out of bounds
    fine_x_bounds = [np.min(restart_data["x"]), np.max(restart_data["x"])]
    fine_r_bounds = [np.min(restart["r"]), np.max(restart["r"])]
    coarse_x_bounds = [np.min(coarse_data["x"]), np.max(coarse_data["x"])]
    coarse_r_bounds = [np.min(coarse_data["r"]), np.max(coarse_data["r"])]
    coarse_r_bounds[0] = 0.375
    if (fine_x_bounds[0] < coarse_x_bounds[0]):
        mask = (restart_data["x"] < coarse_x_bounds[0])
        print("Changing {} points to lie inside bounds".format(np.sum(mask)))
        restart_data["x"][mask] = coarse_x_bounds[0]
    if (fine_x_bounds[1] > coarse_x_bounds[1]):
        mask = (restart_data["x"] > coarse_x_bounds[1])
        print("Changing {} points to lie inside bounds".format(np.sum(mask)))
        restart_data["x"][mask] = coarse_x_bounds[1]
    if (fine_r_bounds[0] < coarse_r_bounds[0]):
        mask = (restart["r"] < coarse_r_bounds[0])
        print("Changing {} points to lie inside bounds".format(np.sum(mask)))
        restart["r"][mask] = coarse_r_bounds[0]
    if (fine_r_bounds[1] > coarse_r_bounds[1]):
        mask = (restart["r"] > coarse_r_bounds[1])
        print("Changing {} points to lie inside bounds".format(np.sum(mask)))
        restart["r"][mask] = coarse_r_bounds[1]

    print("Remapping the data to the new grid...")
    coarse_coords = (coarse_data['x'], coarse_data['r'])
    fine_coords = (restart_data['x'], restart['r'])
    polar_output = {}
    polar_vars = ['Density', 'Momentum_x', 'Momentum_phi', 'Momentum_r',
                  'Energy', 'TKE', 'Dissipation', 'v2', 'f']
    for key in polar_vars:
        polar_output[key] = griddata(coarse_coords, coarse_data[key], fine_coords,
                                     method='linear', fill_value=np.nan)

    # Make sure the wall BC is respected
    vel_mag = np.sqrt(restart_data["Momentum_x"]**2 + restart_data["Momentum_y"]**2 + restart_data["Momentum_z"]**2)
    mask = (np.abs(vel_mag) < 1E-8)
    for key in ["Momentum_x", "Momentum_r", "Momentum_phi", "TKE", "v2", "f"]:
        polar_output[key][mask] = 0.0

    mask = np.isnan(polar_output["Momentum_x"])
    if np.sum(mask) > 0:
        print("Found {} NaN points for Momentum_x. Using nearest neighbor for these points.".format(np.sum(mask)))
        fine_coords = (restart_data['x'][mask], restart['r'][mask])
        for key in polar_vars:
            polar_output[key][mask] = griddata(coarse_coords, coarse_data[key], fine_coords,
                                         method='nearest')

    mask = np.isnan(polar_output["Density"])
    if np.sum(mask) > 0:
        print("Found {} NaN points for density. Using nearest neighbor for these points.".format(np.sum(mask)))
        fine_coords = (restart_data['x'][mask], restart['r'][mask])
        for key in polar_vars:
            polar_output[key][mask] = griddata(coarse_coords, coarse_data[key], fine_coords,
                                         method='nearest')

    mask = np.isnan(polar_output["Momentum_x"])
    if np.sum(mask) > 0:
        sys.exit("ERROR: Found {} NaN points.".format(np.sum(mask)))

    # Convert data back to Cartesian
    output = np.zeros(restart_data.shape, restart_data.dtype)
    for key in ['PointID', 'x', 'y', 'z']:
        output[key] = restart_data[key]
    for key in ['Density', 'Momentum_x', 'Energy', 'TKE', 'Dissipation', 'v2', 'f']:
        output[key] = polar_output[key]
    output["Momentum_y"] =  polar_output['Momentum_r']*np.cos(restart['phi']) + \
                           -polar_output['Momentum_phi']*np.sin(restart['phi'])
    output["Momentum_z"] =  polar_output['Momentum_r']*np.sin(restart['phi']) + \
                            polar_output['Momentum_phi']*np.cos(restart['phi'])

    # Double check the wall BC is respected
    vel_mag = np.sqrt(restart_data["Momentum_x"]**2 + restart_data["Momentum_y"]**2 + restart_data["Momentum_z"]**2)
    mask = (np.abs(vel_mag) < 1E-8)
    for key in ["Momentum_x", "Momentum_y", "Momentum_z", "TKE", "v2", "f"]:
        output[key][mask] = 0.0

    mask = np.isnan(output["Momentum_y"]) | np.isnan(output["Dissipation"])
    if np.sum(mask) > 0:
        sys.exit("ERROR: Found {} NaN points.".format(np.sum(mask)))

    WriteToSU2(args.restart, args.output, output, num_lines_in_footer)

if __name__ == "__main__":
    short_description = "Interpolate a set of profiles onto an SU2 restart file"
    parser = argparse.ArgumentParser(description=short_description)
    parser.add_argument("input", help="npy file containing data to be used")
    parser.add_argument("restart",
                        help="Existing SU2 restart file to be used as a template")
    parser.add_argument("-o", "--output",
                        help="The output restart file (default: 'outfile.dat')",
                        default="outfile.dat")
    args = parser.parse_args()

    main(args)
