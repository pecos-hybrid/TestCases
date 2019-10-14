import numpy as np
import matplotlib.pyplot as plt
from tectools import ReadTecData
from scipy import integrate
from scipy.interpolate import interp1d

gamma = 1.4
R = 287.058  # [J/(kg*K)]

def Sutherland(T):
    mu_ref = 1.716e-5
    T_ref = 273.15
    S = 110.4
    return mu_ref * (T/T_ref)**1.5 * (T_ref + S)/(T + S)

# -----------------
# Experimental data
# -----------------

def RetrieveDNS():
    # From paper
    M_t = 0.065
    M_b = 1.5
    # From data file
    # B_q = -3.8240695343E-02
    # C_f = 0.00417804298582042
    Re_b = 17000.0
    Re_t = 1010.9241194
    # Computed from DNS
    T_ratio = 1.35827299333

    # T_w is estimated using the DNS data (T vs mu relationship)
    T_w = 267.558
    h = 1

    # Derived quantities
    T_b = T_w * T_ratio

    mu_w = Sutherland(T_w)
    c_w = np.sqrt(gamma * R * T_w)
    u_t = M_t * c_w
    u_b = u_t * M_b / M_t
    rho_w = Re_t * mu_w / (u_t * h)
    rho_b = rho_w * (Re_b / Re_t) * (M_t / M_b)

    names = ("y", "yp", "u", "sqrt_rho", "T")
    columns = [0, 1, 3, 10, 11]
    DNS_nondim = np.genfromtxt("CH15C.dat", skip_header=18, usecols=columns, names=names)
    DNS_dim = {}
    DNS_dim["y"] = DNS_nondim["y"]
    DNS_dim["yp"] = DNS_nondim["yp"]
    DNS_dim["rho"] = DNS_nondim["sqrt_rho"]**2 * rho_w

    DNS_dim["T"] = DNS_nondim["T"] * T_w
    DNS_dim["u"] = DNS_nondim["u"] * u_t
    return DNS_nondim, DNS_dim

#----------------------
# SU2 quantities
# ---------------------

def RetrieveSU2(mesh_file, sol_file):
    data = ReadTecData((mesh_file, sol_file))
    if 'z' in data.dtype.names:
        y_key = 'z'
    else:
        y_key = 'y'

    SU2_dim = {}
    SU2_dim["y"] = np.unique(np.round(data[y_key], decimals=7))
    for key in ["T", "rho", "u", "rhou", "mu"]:
        SU2_dim[key] = np.zeros(SU2_dim["y"].shape)
    for z, i in zip(SU2_dim["y"], range(len(SU2_dim["y"]))):
        mask = (np.abs(data[y_key] - z) < 1E-7)
        SU2_dim["T"][i] = np.mean(data["Temperature"][mask])
        SU2_dim["rho"][i] = np.mean(data["Density"][mask])
        SU2_dim["u"][i] = np.mean(data["X-Momentum"][mask]/data["Density"][mask])
        SU2_dim["rhou"][i] = np.mean(data["X-Momentum"][mask])
        SU2_dim["mu"][i] = np.mean(data["<greek>m</greek>"][mask])

    # Aliases for wall coefficients
    mu_w = SU2_dim["mu"][0]
    T_w = SU2_dim["T"][0]
    rho_w = SU2_dim["rho"][0]
    c_w = np.sqrt(gamma * R * T_w)
    du = SU2_dim["u"][1] - SU2_dim["u"][0]
    dy = SU2_dim["y"][1] - SU2_dim["y"][0]
    tau_w = mu_w * du/dy
    u_t = np.sqrt(tau_w / rho_w)

    # Redefine density as sqrt(rho / rho_w)
    SU2_nondim = {}
    SU2_nondim["y"] = SU2_dim["y"]
    SU2_nondim["sqrt_rho"] = np.sqrt(SU2_dim["rho"]/rho_w)
    SU2_nondim["rho"] = SU2_dim["rho"]/rho_w
    SU2_nondim["u"] = SU2_dim["u"]/u_t
    SU2_nondim["T"] = SU2_dim["T"]/T_w

    # Calculate bulk coefficients
    verbose = True
    if (verbose):
        h = 1.0
        L = np.max(SU2_dim["y"]) - np.min(SU2_dim["y"])
        rho_b = integrate.simps(SU2_dim["rho"], SU2_dim["y"]) / L
        u_b = integrate.simps(SU2_dim["rho"]*SU2_dim["u"], SU2_dim["y"]) / (rho_b * L)
        T_b = integrate.simps(SU2_dim["rho"]*SU2_dim["u"]*SU2_dim["T"], SU2_dim["y"]) / (rho_b *u_b * L)
        print("---- From SU2 -----")
        print("rho_b  : {}".format(rho_b))
        print("u_b    : {}".format(u_b))
        print("rhou_b : {}".format(rho_b*u_b))
        print("u_b    : {}".format(u_b))
        print("T_b    : {}".format(T_b))

        Re_b = rho_b * u_b * h / mu_w
        M_b = u_b / c_w
        M_t = u_t / c_w
        print("Re_b = {0}".format(Re_b))
        print("M_b =  {0}".format(M_b))
        print("M_t  = {0}".format(M_t))
    return SU2_nondim, SU2_dim

DNS_nondim, DNS_dim = RetrieveDNS()

folder = "./"
mesh_file = folder + "3D/flow.mesh.plt"
sol_file = folder + "3D/flow10000.sol.plt"
SU2_nondim, SU2_dim = RetrieveSU2(mesh_file, sol_file)

mesh_file = folder + "3D/flow.mesh.plt"
sol_file = folder + "3D/flow15000.sol.plt"
SU22_nondim, SU22_dim = RetrieveSU2(mesh_file, sol_file)

yp_interp = interp1d(DNS_nondim["y"], DNS_nondim["yp"], fill_value="extrapolate")
SU2_nondim["yp"] = yp_interp(SU2_nondim["y"])
SU2_dim["yp"] = yp_interp(SU2_dim["y"])
SU22_nondim["yp"] = yp_interp(SU22_nondim["y"])
SU22_dim["yp"] = yp_interp(SU22_dim["y"])

fig, ax = plt.subplots(nrows=3, sharex=True)
styles = ("-", "-o")
for dataset, label in zip([DNS_nondim, SU2_nondim, SU22_nondim], ["DNS", "SU2", "SU22"]):
    ax[0].semilogx(dataset["yp"], dataset['sqrt_rho'], label=label)
    ax[0].set_ylabel("$\sqrt{\\rho/ \\rho_w}$")
    ax[0].legend(loc="best")
    ax[1].semilogx(dataset["yp"], dataset['u'], label=label)
    ax[1].set_ylabel("$u^+$")
    ax[2].semilogx(dataset["yp"], dataset['T'], label=label)
    ax[2].set_ylabel("$T/T_w$")
ax[-1].set_xlim([1E-1, 1100])
ax[-1].set_xlabel("$z$")
ax[0].legend(loc="best")

plt.show()

fig, ax = plt.subplots(nrows=3, sharex=True)
for dataset, label in zip([DNS_dim, SU2_dim, SU22_dim], ["DNS", "SU2", "SU22"]):
    ax[0].semilogx(dataset["y"], dataset['rho'], "-o", label=label)
    ax[0].set_ylabel("$\\rho$")
    ax[0].legend(loc="best")
    ax[1].semilogx(dataset["y"], dataset['u'], label=label)
    ax[1].set_ylabel("$u$")
    ax[2].semilogx(dataset["y"], dataset['T'], label=label)
    ax[2].set_ylabel("$T$")
ax[-1].set_xlim([1E-4, 1])
ax[-1].set_xlabel("$z$")
ax[0].legend(loc="best")

plt.show()
