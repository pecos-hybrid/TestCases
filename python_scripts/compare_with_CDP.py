#!/usr/bin/env python
"""
For a given set of parameters, plot a comparison between SU2 and CDP.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption


def LoadData(filename, keys, labels, z_key, y_key, sort_key):
    """ Loads a Tecplot file as a dict of Numpy arrays

    This is meant to read only a line (a single x and single z) of data.
    It does not read a whole plane (across all z or x).

    Args:
     filename: The path to the file(s) to be loaded.
     keys: The keys to be used to identify the variables in the final dict
     labels: The keys used for the variables in the Tecplot file (e.g. "U-X")
     z_key: The key used to specify the z-direction.
     y_key: The key used to specify the y (or inhomogeneous) direction.
     sort_key: The final data will be sorted by the values under this key
    Returns:
     A python dict containing Numpy arrays with the data from the Tecplot
       file.  The keys of the dict match the input parameter "keys".
    """
    # Load in a slice of the data
    data = tp.data.load_tecplot(filename,
                                read_data_option=ReadDataOption.Replace)
    print(data)
    x_loc = 0.5
    z_loc = 0.0
    frame = tp.active_frame()
    frame.plot_type = PlotType.Cartesian3D
    extraction = tp.data.extract.extract_slice(dataset=data, normal=(1, 0, 0),
                                               origin=(x_loc, 0, 0))
    # Push the data from a particular z into a numpy array
    z = extraction.values(z_key).as_numpy_array()
    mask = np.where(np.abs(z - z_loc) < 1e-6)
    output = {}
    temp = extraction.values(y_key).as_numpy_array()
    output['y'] = temp[mask]
    for key, label in zip(keys, labels):
        temp = extraction.values(key).as_numpy_array()
        output[label] = temp[mask]
    # Sort the data
    idx = np.argsort(output[sort_key])
    output['y'] = np.array(output['y'])[idx]
    for label in labels:
        output[label] = np.array(output[label])[idx]
    # Rescale y by the specified viscous length scale
    nu = 8.0e-6
    u_tau = 4.14872e-02
    viscous_length = nu/u_tau
    output['yp'] = np.divide(output['y'], viscous_length)
    return output


# ----------------------------------------------------------------
# Fill in the following variables to change what is plotted
# -----------------------------------------------------------------
variables = ['u', 'k']  # Unique identifiers for each variable
labels = ['$u$', '$k$']  # The labels to be used for the variables on the plot
cdp_keys = ['U-X', 'TKE']  # The names CDP uses for each variable
su2_keys = ['Conservative_2', 'Conservative_6']
# -----------------------------------------------------------------

short_description = "Plot a comparison between SU2 and CDP."
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("--cdp", help="TecPlot file with CDP results",
                    default="CDP.plt")
parser.add_argument("--su2", help="TecPlot data file with SU2 results",
                    default="SU2")
args = parser.parse_args()

print("Loading the CDP data file...")
cdp = LoadData(args.cdp, cdp_keys, variables, "Z", "Y", "y")

# Either load the SU2 Tecplot file exactly as specified, or find both
# a *.mesh.plt and a *.sol.plt file matching the name specified.
print("Loading the SU2 data file...")
if (".dat" in args.su2) or (".plt" in args.su2):
    su2_filename = args.su2
else:
    su2_filename = [args.su2 + ".mesh.plt", args.su2 + ".sol.plt"]
su2 = LoadData(su2_filename, su2_keys, variables, "z", "y", "y")

# Plot the variables
num_plots = len(variables)
fig, axes = plt.subplots(num_plots, 1, sharex=True)
for axis, variable, label in zip(axes, variables, labels):
    axis.semilogx(cdp["yp"], cdp[variable], "--", label="CDP")
    axis.semilogx(su2["yp"], su2[variable], ":", label="SU2")
    axis.set_ylabel(label)
axes[-1].set_xlabel("$y^+$")
axes[0].legend(loc="best")
plt.show()
