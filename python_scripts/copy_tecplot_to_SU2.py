import numpy as np
from numpy.lib.recfunctions import rename_fields
import argparse
from remapSU2 import WriteToSU2
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption
import scipy
from scipy.interpolate import LinearNDInterpolator
import time


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
    array = np.zeros(data.shape, dtype=dt)
    for key in keys:
        array[key] = dataset.zone(zone_name).values(key).as_numpy_array()
    return array


def Remap(gridded_data, input_data, interpolator):
    """
    Args:
        gridded_data: A dict-type object containing arrays of the x,y,z
            coordinates to be used.
        input_data: The data to be mapped to the new coordinates.
    Returns:
        A numpy ndarray with a dtype matching the input data, but coordinates
        matching the gridded data.
    """
    assert(gridded_data.shape == input_data.shape)

    old_coords = np.array([input_data[key] for key in ['x', 'y', 'z']]).T
    new_coords = np.array([gridded_data[key] for key in ['x', 'y', 'z']]).T

    names = input_data.dtype.names
    if "PointID" not in input_data.dtype.names:
        names = ("PointID",) + names
    dt = [(key, np.float32) for key in names]
    remapped = np.zeros(input_data.shape, dtype=dt)
    # Don't interpolate the grid data
    for key in ['x', 'y', 'z', 'PointID']:
        remapped[key] = gridded_data[key]
    # Find the delaunay triangulation to avoid recomputing for each variable
    if (interpolator == "linear"):
        delaunay = scipy.spatial.Delaunay(old_coords)
    # Interpolate all other variables
    for key in input_data.dtype.names:
        if key in ['x', 'y', 'z', 'PointID']:
            continue
        if (interpolator == "linear"):
            interp = LinearNDInterpolator(delaunay, input_data[key])
        elif (interpolator == "nearest-neighbor"):
            interp = NearestNDInterpolator(old_coords, input_data[key])
        remapped[key] = interp(new_coords)
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

print("Reading in Tecplot data...")
tecplot_data = ReadTecData(args.input)
conversions = {'x': 'x',
               'y': 'y',
               'z': 'z'}
SU2_data = rename_fields(tecplot_data, conversions)

print("Remapping the Tecplot data to the SU2 coordinates...")
SU2_new = Remap(original, SU2_data, "linear")

WriteToSU2(args.restart, args.output, SU2_new, num_lines_in_footer)
