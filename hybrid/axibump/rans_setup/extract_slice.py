#!/usr/bin/env python3
""" Extract a slice perpendicular to the azimuthal direction.

This script can be used as part of a larger interpolation process, where
a coarse simulation is run, then extracted and interpolated to
a finer grid.

Inputs:
    A tecplot file representing the flow solution.

Outputs:
    A *.npy file containing the initial flow field, stored as a numpy dtype.
        The names for the dtype correspond to names SU2 uses to save
        the variables.
"""
import numpy as np
from scipy import integrate
from scipy.interpolate import griddata
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption, SliceSource
from tecplot.data.operate import execute_equation
import argparse

def ReadTecData(infile, verbose=True):
    """ Read in tecplot data and output it as a numpy dtype object

    Since the incoming tecplot data is unstructured, the output is an array
    of a numpy dtype.  The names of the fields in the dtype are the same
    as the names of the variables in the Tecplot file.

    Args:
        infile: Name(s) of the input files with the solution
        verbose: Print information about the tecplot file.
            Useful for debugging.
    """
    dataset = tp.data.load_tecplot_szl(infile,
                                       initial_plot_type=PlotType.Cartesian3D,
                                       read_data_option=ReadDataOption.Replace)
    if (verbose):
        print(dataset)
    # Supposedly, there's an easier way to do the following line.
    input_keys = [variable.name for variable in dataset.variables("*")]
    equations =['{phi} = atan({z}/{y})',
                '{r} = {y}*cos({phi}) + {z}*sin({phi})',
                '{Momentum_r} =  {Momentum_y}*cos({phi}) + {Momentum_z}*sin({phi})',
                '{Momentum_phi} = -{Momentum_y}*sin({phi}) + {Momentum_z}*cos({phi})']
    for equation in equations:
        execute_equation(equation)

    # Changes axes to conical
    frame = tp.active_frame()
    plot = frame.plot(PlotType.Cartesian3D)
    plot.axes.x_axis.variable = dataset.variable('x')
    plot.axes.y_axis.variable = dataset.variable('r')
    plot.axes.z_axis.variable = dataset.variable('phi')

    # Supposedly, there's an easier way to do the following line.
    input_keys = [variable.name for variable in dataset.variables("*")]
    dt = [(key, np.float64) for key in input_keys]
    if (verbose):
        print(dt)
    output_keys = input_keys

    # Take a slice
    origin = (0, 0, 1.0/360*np.pi)
    surf = tp.data.extract.extract_slice(origin=origin, normal=(0, 0, 1),
                                         source=SliceSource.VolumeZones,
                                         dataset=dataset)

    zones = [zone.name for zone in dataset.zones("*")]
    zone_name = zones[0]
    dt = [(key, np.float64) for key in output_keys]
    if (verbose):
        print(dt)
    temp_data = surf.values(input_keys[0])
    array = np.zeros(temp_data.shape, dtype=dt)
    if verbose:
        print(array.shape)
    for input_key, output_key in zip(input_keys, output_keys):
        array[output_key] = surf.values(input_key).as_numpy_array()
    return array

def main(args):
    data = ReadTecData(args.input)
    np.save(args.output, data)

if __name__ == "__main__":
    short_description = "Interpolate a set of profiles onto an SU2 restart file"
    parser = argparse.ArgumentParser(description=short_description)
    parser.add_argument("-i", "--input", help="The input tecplot binary file",
                        nargs='*',
                        default="flow.szplt")
    parser.add_argument("-o", "--output",
                        help="The output *.npy file",
                        default="coarse_axisymmetric_data")
    args = parser.parse_args()

    main(args)
