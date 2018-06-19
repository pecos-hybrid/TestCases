import numpy as np
import argparse


short_description = "Extract a set of profiles from an ASCII SU2 restart file."
parser = argparse.ArgumentParser(description=short_description)
parser.add_argument("restart", help="ASCII SU2 restart file")
parser.add_argument("-o", "--output", help="Output data file",
                    default="profiles.dat")
args = parser.parse_args()


num_lines_footer = 8
data = np.genfromtxt(args.restart, names=True, skip_footer=num_lines_footer)

# Pull in the y coordinates
# We have to round because of precision problems in the SU2 mesh
# and/or restart file. Otherwise we get duplicate y values
profiles = {}
profiles['y'] = np.sort(np.unique(data['y'].round(decimals=13)))
num_points = profiles['y'].size

# Compute the y+ values
u_tau = 4.14872e-02
nu = 8.0e-6
delta_viscous = nu / u_tau
profiles['y+'] = profiles['y']/delta_viscous

# Set up arrays
flow_vars = ['Density', 'XMomentum', 'YMomentum', 'Energy',
             'TKE', 'Dissipation', 'v2', 'f']
for key in flow_vars:
    profiles[key] = np.zeros(num_points)

# Average across the y points
for i in range(len(profiles['y'])):
    y_loc = profiles['y'][i]
    mask = np.where((np.abs(data['y'] - y_loc) < 1e-10))
    for key in flow_vars:
        if (y_loc < 1e-8 and (key == 'X-Momentum' or key == 'Y-Momentum')):
            profiles[key][i] = 0.0
        else:
            profiles[key][i] = np.mean(data[key][mask])

# Save to file
table = np.vstack([profiles['y'], profiles['y+'],
                   profiles['Density'], profiles['XMomentum'],
                   profiles['YMomentum'], profiles['Energy'],
                   profiles['TKE'], profiles['Dissipation'],
                   profiles['v2'], profiles['f']])
header = "y/delta, y+, Density, X-Momentum, Y-Momentum, Energy, k, diss, v2, f"
np.savetxt(args.output, table.transpose(), delimiter=', ', header=header)
