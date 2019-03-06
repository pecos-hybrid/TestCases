#!/usr/bin/env python
"""
For a given set of parameters, plot a comparison between SU2 and CDP.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption
from scipy.interpolate import interp1d


def LoadData(filename, z_key, y_key, sort_key):
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
    # Supposedly, there's an easier way to do the following line.
    # keys = [variable.name for variable in data.variables("*")]
    keys = ["X", "Y", "Z", "FD", "FD_AVE", "G_RND-X"]
    print(data)
    frame = tp.active_frame()
    frame.plot_type = PlotType.Cartesian3D
    # A convoluted way to get the y values
    x_loc = 0.5
    z_loc = np.pi/2
    extraction = tp.data.extract.extract_slice(dataset=data, normal=(1, 0, 0),
                                               origin=(x_loc, 0, 0))
    # Push the data from a particular z into a numpy array
    z = extraction.values(z_key).as_numpy_array()
    mask = np.where(np.abs(z - z_loc) < 1e-6)
    output = {}
    temp = extraction.values(y_key).as_numpy_array()
    output['y'] = np.sort(temp[mask])
    # Adjust end points so they remain inside the domain
    output['y'][0] += 0.001*(output['y'][1] - output['y'][0])
    output['y'][-1] -= 0.001*(output['y'][-1] - output['y'][-2])
    # Clip out values below the log layer
    mask = np.where((output['y'] > 0.005) & (output['y'] < 0.5))
    output['y'] = output['y'][mask]

    Ny = output['y'].size
    # Get the average values of each slice
    for key in keys:
        if key == 'y':
            continue
        output[key] = np.zeros(Ny)
    for i in range(Ny):
        y = output['y'][i]
        extraction = tp.data.extract.extract_slice(dataset=data, normal=(0, 1, 0),
                                                   origin=(0, y, 0))
        for key in keys:
            temp = extraction.values(key).as_numpy_array()
            if ("G_RND" in key) or ("F<sub>" in key):
                output[key][i] = np.std(temp)
            else:
                output[key][i] = np.mean(temp)
        # Rescale y by the specified viscous length scale
        nu = 8.0e-6
        u_tau = 4.14872e-02
        viscous_length = nu/u_tau
        output['yp'] = np.divide(output['y'], viscous_length)
    return output


short_description = "Plot a comparison between SU2 and CDP."
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("--cdp", help="TecPlot file with CDP results",
                    default="CDP.plt")
parser.add_argument("--su2", help="TecPlot data file with SU2 results",
                    default="SU2")
args = parser.parse_args()

print("Loading the CDP data file...")
cdp = LoadData(args.cdp, "Z", "Y", "y")

# Either load the SU2 Tecplot file exactly as specified, or find both
# a *.mesh.plt and a *.sol.plt file matching the name specified.
# print("Loading the SU2 data file...")
# if (".dat" in args.su2) or (".plt" in args.su2):
#     su2_filename = args.su2
# else:
#     su2_filename = [args.su2 + ".mesh.plt", args.su2 + "_00001.sol.plt"]
# su2 = LoadData(su2_filename, "z", "y", "y")
# d_norm = np.sqrt(np.power(su2["Resolution_Tensor_11"], 2) +
#                  np.power(su2["Resolution_Tensor_22"], 2) +
#                  np.power(su2["Resolution_Tensor_33"], 2))
# d_norm_43 = np.power(d_norm, 4.0/3)
# interp = interp1d(cdp["yp"], cdp["FD_AVE"])
# 
# M_factor = {}
# nu_sgs = {}
# for comp in ["11", "22", "33"]:
#     M_43 = np.power(su2["Resolution_Tensor_" + comp], 4.0/3)
#     M_factor[comp] = np.divide(M_43, d_norm_43)
#     mu_sget_label = "mu<sup>SGET</sup><sub>" + comp + "</sub>"
#     nu_sgs[comp] = np.divide(su2[mu_sget_label], M_factor[comp])

# --------------------------------------------------
# Plot the variables
# --------------------------------------------------

variables = [["FD", "r<sub>M</sub>", "$r_{\mathcal{M}}$"],
             ["FD_AVE", "avgr<sub>M</sub>",
              "$\langle r_{\mathcal{M}} \\rangle$"],
             ["K_RATIO", "<greek>a</greek>", "$\\alpha$"],
             ["PROD", "Production", "$\mathcal{P}_k$"],
             ["K_RESOLVED", "k<sub>res</sub>", "$k_{res}$"],
             ["NU_T", "<greek>m</greek><sub>t</sub>", "$\mu_{t}$"]]

fig, axis = plt.subplots()
axis.semilogy(cdp["yp"], cdp["FD_AVE"], "--")
axis.semilogy(cdp["yp"], np.ones(cdp["yp"].shape), "k:")
ax2 = axis.twinx()
ax2.plot(cdp["yp"], cdp["G_RND-X"], "--")
plt.show()
# nPlots = len(variables)+1
# fig, axes = plt.subplots(nPlots, 1, sharex=True)
# for variable, axis in zip(variables, axes):
#     if "FD" in variable[0]:
#         axis.loglog(cdp["yp"], cdp[variable[0]], "--", label="CDP")
#         axis.loglog(su2["yp"], su2[variable[1]], ":", label="SU2")
#         axis.set_ylim([1e-1, 1e2])
#     else:
#         axis.semilogx(cdp["yp"], cdp[variable[0]], "--", label="CDP")
#         axis.semilogx(su2["yp"], su2[variable[1]], ":", label="SU2")
#     axis.set_ylabel(variable[2])
#     axis.legend(loc="best")
# axes[-1].semilogx(cdp["yp"], cdp["NU_SGS"], "--", label="CDP")
# axes[-1].semilogx(su2["yp"], nu_sgs["11"], ":", label="SU2")
# axes[-1].set_ylabel("$\\nu_{SGS}$")
# # Overall plot settings
# axes[-1].set_xlabel("$y^+$")
# for axis in axes:
#     axis.legend(loc="best")
# plt.show()
#
# variables = [["G_RND-X", "$g_1$"],
#              ["G_RND-Y", "$g_2$"],
#              ["G_RND-Z", "$g_3$"]]
# dt = 1E-3
# g = []
# for i in range(3):
#     key = "F<sub>" + str(i+1) + "</sub>"
#     g.append(su2[key]*dt)
#
# nPlots = len(variables)
# fig, axes = plt.subplots(nPlots, 1, sharex=True)
# for variable, axis, g_i in zip(variables, axes, g):
#     axis.semilogx(cdp["yp"], cdp[variable[0]], "--x", label="CDP")
#     axis.semilogx(su2["yp"], g_i, "o:", label="SU2")
#     axis.set_ylabel(variable[1])
#     axis.legend(loc="best")
# # Overall plot settings
# axes[-1].set_xlabel("$y^+$")
# for axis in axes:
#     axis.legend(loc="best")
# plt.show()
