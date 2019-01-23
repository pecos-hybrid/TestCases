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

import argparse
import numpy as np
from remapSU2 import RemapData, AddTGNoise, AddRandomNoise, WriteToSU2


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

WriteToSU2(args.restart, args.output, out_arr, num_lines_in_footer)
