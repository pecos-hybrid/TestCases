"""
"""

import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib import colors, ticker
from progress.bar import IncrementalBar
from numpy import sin, cos, sqrt, tanh, pi
import seaborn as sns
sns.set()


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


su2 = ReadTecData(("channel/flow.mesh.plt", "channel/flow_00001.sol.plt"))
cdp = ReadTecData("channel/old_channel.plt")

# Undo the scaling by dt in CDP
dt = 1E-3
forcing_keys = ["G_RND-" + var for var in ["X", "Y", "Z"]]
for key in forcing_keys:
    cdp[key] /= dt

recalculate_forcing = False
if (recalculate_forcing):
    # Initialize scalar fields
    v2f_tke = cdp["TKE"]
    v2f_v2 = cdp["V2F_V2"]
    v2f_tdr = cdp["TDR"]
    nz = np.where(cdp["TKE"] > 1E-8)
    tke_lim = cdp["TKE"].clip(min=1E-8)
    k_ratio = (tke_lim - cdp["K_RESOLVED"])/tke_lim
    k_ratio = k_ratio.clip(min=1E-8, max=1)
    fd_here = cdp["FD_AVE"]
    dist_w = np.minimum(cdp["Y"], 2.0-cdp["Y"])

    # Initialize vector fields
    nPoints = cdp["X"].shape[0]
    cv_cc = np.zeros([3, nPoints])
    u = np.zeros([3, nPoints])
    u_ave = np.zeros([3, nPoints])
    g_inst = np.zeros([3, nPoints])
    for i, key in zip(range(3), ["X", "Y", "Z"]):
        cv_cc[i, :] = cdp[key]
        u[i, :] = cdp["U-" + key]
        u_ave[i, :] = cdp["U_AVERAGE-" + key]

    # Initialize constants
    TKE_MIN = 1E-8
    TDR_MIN = 1E-8
    V2F_CT = 6.0
    V2F_CETA = 70.0
    AF_LPX = 3.14159265359
    AF_LPY = 0.25
    AF_LPZ = 1.1780972451
    FORCING_CL = 4.0
    FORCING_FACTOR = 8.0
    BL_T = 1
    BL_KOL = 1
    constant_nu_value = 1.9283055e-4
    time = 1.0
    dt = 1.0E-3

    # Clean up some machine-precision problems
    mask = np.where(np.abs(cdp["X"]) < 1E-10)
    cdp["X"][mask] = 0.0
    x_vals = np.sort(np.unique(cdp["X"]))
    y_vals = np.sort(np.unique(cdp["Y"]))
    z_vals = np.sort(np.unique(cdp["Z"]))

    def GetSpacing(x_array, x_pos):
        index = np.where(x_array == x_pos)[0]
        if (index == 0):
            delta = x_array[index+1] - x_array[index]
        elif (index == len(x_array)-1):
            delta = x_array[index] - x_array[index - 1]
        else:
            delta = (x_array[index+1] - x_array[index - 1])/2
        return delta

    bar = IncrementalBar('Calculating forcing', max=nPoints, suffix='%(percent)d%%')
    for icv in range(nPoints):

        dx = GetSpacing(x_vals, cdp["X"][icv])
        dy = GetSpacing(y_vals, cdp["Y"][icv])
        dz = GetSpacing(z_vals, cdp["Z"][icv])
        dims = np.array([dx, dy, dz])[:, 0]
        metric = np.diag(dims)

        # if using total k method, must adjust length here
        c_k = max(v2f_tke[icv], TKE_MIN)
        c_v2 = max(v2f_v2[icv], 2.0 / 3.0 * TKE_MIN)
        c_d = max(v2f_tdr[icv], TDR_MIN)
        c_a = k_ratio[icv]

        # XXX: Hacked to force v2f_tke to be positive
        length = FORCING_CL * (c_a * c_k)**1.5 / c_d
        length = max(length, V2F_CETA * (constant_nu_value**(0.75)) / (c_d**(0.25)))
        T_alpha = c_a * c_k / c_d
        T_alpha = max(T_alpha, V2F_CT * sqrt(constant_nu_value / c_d))
        T_alpha = BL_T * T_alpha
        T_kol = sqrt(constant_nu_value / c_d)
        zeta_lcl = 1.5 * v2f_v2[icv] / c_k

        xp = cv_cc[:, icv] + u_ave[:, icv] * time

        # for channel only, makes forcing symmetric
        xp[1] = xp[1] - 1.0

        # FIX ax,ay,az for non-structured grids

        # channel chunk x=2pi, z=1pi
        length = min(length, dist_w[icv])
        ax = pi / (AF_LPX / float(np.rint((AF_LPX) / min(max(length, 2.0 * metric[0, 0]), AF_LPX))))
        ay = pi / (AF_LPY / float(np.rint((AF_LPY) / min(max(length, 2.0 * metric[1, 1]), AF_LPY))))
        az = pi / (AF_LPZ / float(np.rint((AF_LPZ) / min(max(length, 2.0 * metric[2, 2]), AF_LPZ))))

        # ideal TG forcing field, somewhat biased
        g1 = 1.0 * cos(ax * xp[0]) * sin(ay * xp[1]) * sin(az * xp[2])
        g2 = -3.0 * sin(ax * xp[0]) * cos(ay * xp[1]) * sin(az * xp[2])
        g3 = 2.0 * sin(ax * xp[0]) * sin(ay * xp[1]) * cos(az * xp[2])

        # scale and make dimensionless
        g_inst[0, icv] = g1 / 3.0
        g_inst[1, icv] = g2 / 3.0
        g_inst[2, icv] = g3 / 3.0

        # + sqrt(c_d*dt)*g_inst(1:3,icv)
        u_prime = u[:, icv] - u_ave[:, icv]

        F_target = FORCING_FACTOR * sqrt(c_a * c_v2) / T_alpha  # C_FF=8

        prod_r = np.inner((F_target * dt) * g_inst[:, icv], u_prime)

        arg = sqrt(fd_here[icv]) - 1.0
        if (arg < 0.0):
            arg = 1.0 - 1.0 / sqrt(fd_here[icv])
        a_sign = tanh(arg)

        # DaDt manufactured portion
        Sa = a_sign
        a_kol = min(BL_KOL * sqrt(constant_nu_value * c_d) / (c_k), 1.0)

        if (a_sign < 0.0):  # refining
            if(c_a <= a_kol):
                Sa = Sa - (1.0 + a_kol - c_a) * a_sign

        else:  # coarsening
            if(c_a >= 1.0):
                Sa = Sa - c_a * a_sign

        prod_temp = (c_a * c_k / T_alpha) * Sa
        fd_temp = fd_here[icv]

        # scaling for vector stream function <moops>
        # apply clipping here if necesary...
        if(fd_temp < 1.0 and prod_r >= 0.0):

            C_F = -1.0 * F_target * Sa

        else:  # disagreement, just turn off locally
            C_F = 0.0

        # dt here is to get in terms for divfree projection
        norm = C_F  # XXX: Removed dt to make comparison fair

        g_inst[0, icv] = norm * g_inst[0, icv]  # Fi, has units L/T^2 * dt here
        g_inst[1, icv] = norm * g_inst[1, icv]
        g_inst[2, icv] = norm * g_inst[2, icv]

        bar.next()
    bar.finish()

    np.save("g_field", g_inst)
else:
    g_inst = np.load("g_field.npy")

"""
z_loc = np.pi / 2
cdp_mask = np.where(abs(cdp["Z"] - z_loc) < 1E-5)
su2_mask = np.where(abs(su2["z"] - z_loc) < 1E-5)
cdp_points = (cdp["X"][cdp_mask], cdp["Y"][cdp_mask])
su2_points = (su2["x"][su2_mask], su2["y"][su2_mask])

cdp_qoi = g_inst[2, :][cdp_mask]
su2_qoi = su2["F<sub>3</sub>"][su2_mask]
cdp_interp = griddata(cdp_points, cdp_qoi, su2_points, method='nearest')

abs_error = np.abs(cdp_interp - su2_qoi)
nz = np.where(np.abs(cdp_interp) > 1E-8)
rel_error = np.zeros(cdp_interp.shape)
rel_error[nz] = np.abs(np.divide(abs_error[nz], cdp_interp[nz]))
z_mask = np.where(np.abs(cdp_interp) <= 1E-8)
rel_error[z_mask] = np.ma.masked

print("Median of absolute error: {0}".format(np.median(abs_error)))
print("Median of relative error: {0}".format(np.median(rel_error)))
print("Std. of absolute error: {0}".format(np.std(abs_error)))
print("Std. of relative error: {0}".format(np.std(rel_error)))

cmap = 'YlOrRd_r'
fig, ax = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
cs = ax[0, 0].tricontourf(su2["x"][su2_mask], su2["y"][su2_mask],
                          abs_error, 20, cmap=cmap, extend="both")
fig.colorbar(cs, ax=ax[0, 0], shrink=0.9)
ax[0, 0].set_title("Absolute Error")
ax[0, 0].set_ylim([0.05, 0.25])
cs = ax[1, 0].tricontourf(cdp["X"][cdp_mask], cdp["Y"][cdp_mask],
                          cdp_qoi, 20, cmap=cmap, extend="both")
fig.colorbar(cs, ax=ax[1, 0], shrink=0.9)
ax[1, 0].set_title("CDP Forcing Field")
cs = ax[1, 1].tricontourf(su2["x"][su2_mask], su2["y"][su2_mask],
                          su2_qoi, levels=cs.levels, cmap=cmap, extend="both")
fig.colorbar(cs, ax=ax[1, 1], shrink=0.9)
ax[1, 1].set_title("SU2 Forcing Field")
cs = ax[0, 1].tricontourf(su2["x"][su2_mask], su2["y"][su2_mask],
                          rel_error, 20, cmap=cmap, extend="both")
cbar = fig.colorbar(cs, ax=ax[0, 1], shrink=0.9)
cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter())
ax[0, 1].set_title("Relative Error")

for axis in ax[1, :]:
    axis.set_xlabel("$x$")
for axis in ax[:, 0]:
    axis.set_ylabel("$y$")
fig.set_size_inches(10, 8)
plt.show()
"""

z_loc = np.pi / 2
y_loc = 1.32734030e-01
cdp_mask = np.where((abs(cdp["Z"] - z_loc) < 1E-5) &
                    (abs(cdp["Y"] - y_loc) < 1E-3))
su2_mask = np.where((abs(su2["z"] - z_loc) < 1E-5) &
                    (abs(su2["y"] - y_loc) < 1E-3))

# Sort the values
indices = np.argsort(cdp["X"][cdp_mask])
for data in [cdp["X"], g_inst[0, :], g_inst[1, :], g_inst[2, :]]:
    data[cdp_mask] = np.array(data[cdp_mask])[indices]
indices = np.argsort(su2["x"][su2_mask])
for data in [su2["x"], su2["F<sub>1</sub>"], su2["F<sub>2</sub>"],
             su2["F<sub>3</sub>"]]:
    data[su2_mask] = np.array(data[su2_mask])[indices]


fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
for i in range(3):
    ax[i].plot(cdp["X"][cdp_mask], g_inst[i, :][cdp_mask], "-",
               label="CDP")
    su2_key = "F<sub>{0}</sub>".format(i+1)
    ax[i].plot(su2["x"][su2_mask], su2[su2_key][su2_mask], "--",
               label="SU2")
    ax[i].set_ylabel("$F_" + str(i+1) + "$")
    ax[i].legend(loc="best")
ax[2].set_xlabel("$x$")
plt.show()

z_loc = np.pi / 2
x_loc = 3.170
cdp_mask = np.where((abs(cdp["Z"] - z_loc) < 1E-5) &
                    (abs(cdp["X"] - x_loc) < 1E-2))
su2_mask = np.where((abs(su2["z"] - z_loc) < 1E-5) &
                    (abs(su2["x"] - x_loc) < 1E-2))

# Sort the values
indices = np.argsort(cdp["Y"][cdp_mask])
for data in [cdp["Y"], g_inst[0, :], g_inst[1, :], g_inst[2, :]]:
    data[cdp_mask] = np.array(data[cdp_mask])[indices]
indices = np.argsort(su2["y"][su2_mask])
for data in [su2["y"], su2["F<sub>1</sub>"], su2["F<sub>2</sub>"],
             su2["F<sub>3</sub>"]]:
    data[su2_mask] = np.array(data[su2_mask])[indices]


fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
for i in range(3):
    ax[i].plot(cdp["Y"][cdp_mask], g_inst[i, :][cdp_mask], "-",
               label="CDP")
    su2_key = "F<sub>{0}</sub>".format(i+1)
    ax[i].plot(su2["y"][su2_mask], su2[su2_key][su2_mask], "--",
               label="SU2")
    ax[i].set_ylabel("$F_" + str(i+1) + "$")
    ax[i].legend(loc="best")
ax[2].set_xlabel("$y$")
plt.show()
