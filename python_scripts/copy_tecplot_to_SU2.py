"""
This script serves to set up an SU2 ASCII restart file using data from
a Tecplot file.  This is mainly useful for inter-code comparisons, where
the output of one code is used as an initial condition for another code.

Depending on the solver used (e.g. CDP), you will need to change the
dict specifying the variable name conversions.  For example, if CDP
specifies the turbulent dissipation rate as "TDR" but SU2 defines it as
"Dissipation", then you would add an entry to the dict as:
    "TDR": "Dissipation"
"""

import numpy as np
from numpy.lib.recfunctions import rename_fields
import argparse
from remapSU2 import WriteToSU2
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption
import scipy
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from progress.bar import IncrementalBar


def ReadTecData(infile, verbose=True):
    """ Read in tecplot data and output it as a numpy dtype object

    Args:
        infile: Name(s) of the input files with the solution
        verbose: Print information about the tecplot file.
            Useful for debugging.
    """
    dataset = tp.data.load_tecplot(infile,
                                   read_data_option=ReadDataOption.Replace)
    if (verbose):
        print(dataset)
    # Supposedly, there's an easier way to do the following line.
    keys = [variable.name for variable in dataset.variables("*")]
    zones = [zone.name for zone in dataset.zones("*")]
    zone_name = zones[0]
    dt = [(key, np.float32) for key in keys]
    data = dataset.zone(zone_name).values(keys[0])
    if (verbose):
        print("Shape: {0}".format(data.shape))
    array = np.zeros(data.shape, dtype=dt)
    for key in keys:
        array[key] = dataset.zone(zone_name).values(key).as_numpy_array()
    return array


def ConvertCDPToSU2(CDP_data, SU2_dtype):
    """ Convert an array holding CDP data to an array holding SU2 data.

    This performs two functions: renaming variables and transforming
    incompressible (non-conservative) variables to compressible
    (conservative) variables.

    Args:
        CDP_data: A numpy dtype holding CDP data.
        SU2_data: A numpy dtype describing the SU2 data
    Returns:
        A numpy dtype array holding SU2-compatible data
    """
    SU2_data = np.zeros(CDP_data.shape, dtype=SU2_dtype)
    # All the variables whose names match between SU2 and CDP
    for key in ['TKE']:
        SU2_data[key] = CDP_data[key]
    # conversions is a list of all the variable names to be swapped.
    # The first string in each pair is the name in the Tecplot file
    # The second string is the SU2 name
    conversions = {'X': 'x', 'Y': 'y', 'Z': 'z',
                   'TDR': 'Dissipation', 'V2F_V2': 'v2', 'V2F_F22': 'f',
                   'K_RESOLVED': 'ksubressub'}
    for key, value in conversions.items():
        SU2_data[value] = CDP_data[key]
    # Derive all the other quantities for compressible flow
    density = 1.0
    gamma = 1.4
    Mach = 0.05
    u_ave = np.mean(CDP_data['U-X'])
    p_ave = np.mean(CDP_data['P_AVE'])
    a = u_ave / Mach
    p = (density / gamma)*(a)**2
    CDP_data['P'] += (p - p_ave)
    CDP_data['P_AVE'] += (p - p_ave)
    SU2_data['Density'] = np.ones(CDP_data.shape)*density
    SU2_data['Average_Density'] = np.ones(CDP_data.shape)*density
    prims = {'U-X': 'XMomentum', 'U-Y': 'YMomentum', 'U-Z': 'ZMomentum',
             'U_AVERAGE-X': 'Average_XMomentum',
             'U_AVERAGE-Y': 'Average_YMomentum',
             'U_AVERAGE-Z': 'Average_ZMomentum',
             'PROD': 'Production'}
    for key, value in prims.items():
        SU2_data[value] = np.multiply(CDP_data[key], density)
    sgs_energy = np.multiply(CDP_data["TKE"], 0.5*density)
    # Resolved total energy
    static_energy = np.divide(CDP_data['P'], gamma-1.0)
    kinetic_energy = np.zeros(CDP_data.shape)
    for direction in ['X', 'Y', 'Z']:
        CDP_label = 'U-'+direction
        kinetic_energy += np.power(CDP_data[CDP_label], 2.0)
    kinetic_energy = np.multiply(kinetic_energy, 0.5*density)
    SU2_data['Energy'] = static_energy + kinetic_energy + sgs_energy
    # Average total energy
    static_energy = np.divide(CDP_data['P_AVE'], gamma-1.0)
    kinetic_energy = np.zeros(CDP_data.shape)
    for direction in ['X', 'Y', 'Z']:
        CDP_label = 'U_AVERAGE-'+direction
        kinetic_energy += np.power(CDP_data[CDP_label], 2.0)
    kinetic_energy = np.multiply(kinetic_energy, 0.5*density)
    SU2_data['Average_Energy'] = static_energy + kinetic_energy + sgs_energy
    return SU2_data


def Remap(gridded_data, input_data, interpolator):
    """ A wrapper method for variable interpolation.

    Args:
        gridded_data: A dict-type object containing arrays of the x,y,z
            coordinates to be used.
        input_data: The data to be mapped to the new coordinates.
    Returns:
        A numpy ndarray with a dtype matching the input data, but coordinates
        matching the gridded data.
    """
    old_coords = np.array([input_data[key] for key in ['x', 'y', 'z']]).T
    new_coords = np.array([gridded_data[key] for key in ['x', 'y', 'z']]).T

    names = input_data.dtype.names
    if "PointID" not in input_data.dtype.names:
        names = ("PointID",) + names
    dt = [(key, np.float32) for key in names]
    remapped = np.zeros(gridded_data.shape, dtype=dt)
    for key in ['x', 'y', 'z', 'PointID']:
        remapped[key] = gridded_data[key]
    # Find the delaunay triangulation to avoid recomputing for each variable
    if (interpolator == "linear"):
        delaunay = scipy.spatial.Delaunay(old_coords)
    # Interpolate all other variables
    bar = IncrementalBar('Interpolating', max=len(input_data.dtype.names))
    for key in input_data.dtype.names:
        if key in ['x', 'y', 'z', 'PointID']:
            bar.next()
            continue
        if (interpolator == "linear"):
            interp = LinearNDInterpolator(delaunay, input_data[key])
        elif (interpolator == "nearest-neighbor"):
            interp = NearestNDInterpolator(old_coords, input_data[key])
        remapped[key] = interp(new_coords)
        bar.next()
    bar.finish()
    return remapped


short_description = "Copy tecplot data onto an SU2 restart file"
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("input", help="Tecplot file to be copied over.")
parser.add_argument("restart",
                    help="Existing SU2 restart file to be used as a template")
parser.add_argument("-o", "--output",
                    help="The output restart file (default: 'outfile.dat')",
                    default="outfile.dat")
args = parser.parse_args()

print("Reading in original data...")
num_lines_in_footer = 9
original = np.genfromtxt(args.restart, names=True,
                         skip_footer=num_lines_in_footer)
print(original.shape)
print(original.dtype.names)

print("Reading in Tecplot data...")
tecplot_data = ReadTecData(args.input, verbose=True)

SU2_data = ConvertCDPToSU2(tecplot_data, original.dtype)

print("Remapping the Tecplot data to the SU2 coordinates...")
SU2_new = Remap(original, SU2_data, "nearest-neighbor")

WriteToSU2(args.restart, args.output, SU2_new, num_lines_in_footer)
