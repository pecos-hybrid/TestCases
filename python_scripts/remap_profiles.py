#!/usr/bin/env python
"""Interpolate a set of profiles onto an SU2 restart file

This script is designed to allow an SU2 restart file to be filled in
with the data from a set of profiles, defined in an external file.
It requires an ASCII SU2 restart file as an input, in order to define
the coordinates of each data point. The output is also an ASCII SU2
restart file, with the flow and turbulence variables set to match the
profile.

Because this script uses a linear interpolation, the grid points in the
profile do not have to match the grid points in the SU2 restart file.

The script currently assumes that the profiles are 1D, and they are
constant in the x and y directions.
"""

import numpy as np
from scipy.interpolate import interp1d
import argparse


def RemapData(old_data, profiles):
    """ Take an old array of data and interpolate new data on the same grid.

    The remapping uses a 1-D linear interpolation.
    Poor results were observed using a cubic interpolation where sharp
    gradients exist (e.g. in the dissipation near the wall).

    Args:
        old_data: The data to be overwritten
        profiles: The interpolation data

    Returns:
        A new array with the same coordinates as old_data, but with
        the field variables interpolated from the profiles file.
    """
    interp = {}
    for key in profiles.dtype.names:
        interp[key] = interp1d(profiles['y'], profiles[key],
                               kind="linear")
    out = np.array(old_data)
    y = old_data['y']
    if 'TKE' in old_data.dtype.names:
        flow_vars = ['Density', 'XMomentum', 'YMomentum', 'Energy',
                     'TKE', 'Dissipation', 'v2', 'f']
    elif 'Nu_Tilde' in old_data.dtype.names:
        flow_vars = ['Density', 'XMomentum', 'YMomentum', 'Energy', 'Nu_Tilde']
    else:
        raise KeyError("Could not find turbulence variables in restart file!")
    for key in flow_vars:
        out[key] = interp[key](y)
    if "ZMomentum" in out.dtype.names:
        out['ZMomentum'] = 0.0
    if "Alpha" in out.dtype.names:
        out["Alpha"] = 1.0
    return out


def AddTGNoise(data, num_freqs=20, magnitude=0.2):
    """ Add random Taylor-Green vortex fields to a set of data.

    This function adds incompressible noise to a velocity field.
    Taylor-Green vortex fields are added to the x-z plane, and a
    simple wall-damping function is added to the y direction to ensure
    that u=0 at the walls.

    Args:
        data: The field containing x,y,z coordinates and momentums
        num_freqs: The number of different vortex fields to add
        magnitude: The amplitude of the TG field for X-Momentum.
           This value is rescaled by the maximum value of the
           X-Momentum field, such that setting magnitude = 1 gives
           the noise an actual amplitude equal to the maximum value
           of the X-Momentum.

    Returns:
        A field identical in structure and coordinates to the input
        data, but with additional noise.
    """
    x = data['x']
    y = data['y']
    z = data['z']
    u_TG = np.zeros(x.shape)
    v_TG = np.zeros(x.shape)
    w_TG = np.zeros(x.shape)
    umax = np.max(data["XMomentum"])
    A = 1.0
    C = -1.0
    x_frequencies = np.random.uniform(1.0, 30.0, num_freqs)
    y_frequencies = np.random.randint(1, 20, num_freqs)
    z_frequencies = np.random.uniform(1.0, 30.0, num_freqs)
    u_magnitudes = np.random.uniform(0.0, magnitude*umax, num_freqs)
    params = zip(x_frequencies, y_frequencies, z_frequencies, u_magnitudes)
    for x_freq, y_freq, z_freq, u_mag in params:
        # Wall damping to enforce no-slip
        B = np.sin(y_freq*np.pi*y/2)
        # Rescale to give high frequencies low magnitudes
        rescale = 1.0/max(x_freq, z_freq)
        a = x_freq
        c = z_freq
        A = u_mag
        # Ensure that incompressibility is satisfied
        C = -(A*a)/c
        # Create the fields
        u_TG += A*np.cos(a*x)*np.sin(c*z)*B*rescale
        w_TG += C*np.sin(a*x)*np.cos(c*z)*B*rescale
    data["XMomentum"] += u_TG
    data["ZMomentum"] += w_TG
    return data


def AddRandomNoise(data, magnitude=0.005):
    """ Add random normally-distributed noise to a set of data.

    Adds random noise to a velocity field. The noise is normally
    distributed, with a mean of zero and a standard deviation defined by
    both the X-Momentum field and the magnitude.

    Args:
        data: The field containing x,y,z coordinates and momentums
        magnitude: The standard deviation of the noise.  This standard
           deviation is rescaled by the X-Momentum field, such that
           setting magnitude = 1 gives the noise an actual standard
           deviation equal to the local value of the X-Momentum.
           Setting magnitude=0.01 gives the noise an actual standard
           deviation equal to 1% of the local X-Momentum.

    Returns:
        A field identical in structure and coordinates to the input
        data, but with additional noise.
    """
    N = data["XMomentum"].size
    u_noise = np.multiply(np.random.normal(0, 0.005, N), data["XMomentum"])
    v_noise = np.multiply(np.random.normal(0, 0.005, N), data["XMomentum"])
    w_noise = np.multiply(np.random.normal(0, 0.005, N), data["XMomentum"])
    data["XMomentum"] += u_noise
    data["YMomentum"] += v_noise
    data["ZMomentum"] += w_noise
    return data


short_description = "Interpolate a set of profiles onto an SU2 restart file"
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("input", help="ASCII file containing profiles to be used")
parser.add_argument("restart",
                    help="Existing SU2 restart file to be used as a template")
parser.add_argument("-o", "--output",
                    help="The output restart file (default: 'outfile.dat')",
                    default="outfile.dat")
parser.add_argument("-n", "--noise", help="Add random velocity fluctuations",
                    action="store_true")
parser.add_argument("-t", "--taylor",
                    help="Add random Taylor-Green fluctuations",
                    action="store_true")
args = parser.parse_args()

# The number of lines in the footer of the SU2 restart file
num_lines_in_footer = 9

print("Reading in original data...")
original = np.genfromtxt(args.restart, names=True,
                         skip_footer=num_lines_in_footer)
print("Reading in data to be interpolated...")
data = np.genfromtxt(args.input, names=True, delimiter=', ')

print("Remapping the data to the new grid...")
out_arr = RemapData(original, data)
if args.taylor:
    out_arr = AddTGNoise(out_arr)
if args.noise:
    out_arr = AddRandomNoise(out_arr)

# Get the header and footer from interpolated file
print("Saving results to " + args.output)
with open(args.restart, 'r') as infile:
    header = infile.readline().strip()
    footer = ""
    # Skip over the data
    for i in range(out_arr['x'].size):
        infile.readline()
    for i in range(num_lines_in_footer):
        footer += infile.readline()
    footer = footer.strip()

# Write the results to a file
fmt_str = "%d"
for i in range(len(out_arr.dtype.names) - 1):
    fmt_str += "\t%.15e"
np.savetxt(args.output, out_arr, fmt=fmt_str, header=header, footer=footer,
           comments="")
