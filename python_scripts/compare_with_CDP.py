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
# The labels to be used for plotting
labels = ['$\\alpha$', '$k_{res}$', '$P_k$', '$\\nu_t$']
# cdp_keys = ['K_RATIO', 'K_RESOLVED', 'PROD', 'NU_T']
# su2_keys = ['<greek>a</greek>', 'k<sub>res</sub>', 'Production',
#             '<greek>m</greek><sub>t</sub>']
cdp_keys = ['NU_SGS', 'TDR', 'FD_AVE']
su2_keys = ["Resolution_Tensor_11",
            "Resolution_Tensor_22", "Resolution_Tensor_33",
            "mu<sup>SGET</sup><sub>11</sub>",
            "mu<sup>SGET</sup><sub>22</sub>",
            "mu<sup>SGET</sup><sub>33</sub>", 'Dissipation']

# -----------------------------------------------------------------

short_description = "Plot a comparison between SU2 and CDP."
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("--cdp", help="TecPlot file with CDP results",
                    default="CDP.plt")
parser.add_argument("--su2", help="TecPlot data file with SU2 results",
                    default="SU2")
args = parser.parse_args()

print("Loading the CDP data file...")
cdp = LoadData(args.cdp, cdp_keys, cdp_keys, "Z", "Y", "y")

# Either load the SU2 Tecplot file exactly as specified, or find both
# a *.mesh.plt and a *.sol.plt file matching the name specified.
print("Loading the SU2 data file...")
if (".dat" in args.su2) or (".plt" in args.su2):
    su2_filename = args.su2
else:
    su2_filename = [args.su2 + ".mesh.plt", args.su2 + "_00002.sol.plt"]
su2 = LoadData(su2_filename, su2_keys, su2_keys, "z", "y", "y")
d_norm = np.sqrt(np.power(su2["Resolution_Tensor_11"], 2) +
                 np.power(su2["Resolution_Tensor_22"], 2) +
                 np.power(su2["Resolution_Tensor_33"], 2))
d_norm_43 = np.power(d_norm, 4.0/3)
interp = interp1d(cdp["yp"], cdp["FD_AVE"])
r_M = interp(su2["yp"])


M_factor = {}
nu_sgs = {}
for comp in ["11", "22", "33"]:
    M_43 = np.power(su2["Resolution_Tensor_" + comp], 4.0/3)
    M_factor[comp] = np.divide(M_43, d_norm_43)
    mu_sget_label = "mu<sup>SGET</sup><sub>" + comp + "</sub>"
    nu_sgs[comp] = np.divide(su2[mu_sget_label], M_factor[comp])
    factor = np.power(np.minimum(r_M, np.ones(r_M.shape)*10), 4.0/3)
    nu_sgs[comp] = np.multiply(factor, nu_sgs[comp])


# Plot the variables
fig, axes = plt.subplots(3, 1)
axes[0].semilogx(cdp["yp"], cdp["NU_SGS"], "--", label="CDP")
axes[0].set_ylabel("$\\nu_{SGS}$")
axes[0].semilogx(su2["yp"], nu_sgs["11"], ":", label="SU2_11")
axes[0].semilogx(su2["yp"], nu_sgs["22"], ":", label="SU2_22")
axes[0].semilogx(su2["yp"], nu_sgs["33"], ":", label="SU2_33")
axes[0].set_ylabel("$\\nu_{SGS}$")
axes[2].semilogx(cdp["yp"], cdp["TDR"], "--", label="SU2")
axes[2].semilogx(su2["yp"], su2["Dissipation"], ":", label="SU2")
axes[2].set_ylabel("$\\varepsilon$")
axes[-1].set_xlabel("$y^+$")
axes[0].legend(loc="best")
axes[1].legend(loc="best")
axes[2].legend(loc="best")
plt.show()

# num_plots = len(cdp_keys)
# fig, axes = plt.subplots(num_plots, 1, sharex=True)
# for axis, variable, label in zip(axes, cdp_keys, labels):
#     axis.semilogx(cdp["yp"], cdp[variable], "--", label="CDP")
#     axis.semilogx(su2["yp"], su2[variable], ":", label="SU2")
#     axis.set_ylabel(label)
# axes[-1].set_xlabel("$y^+$")
# axes[0].legend(loc="best")
# plt.show()
