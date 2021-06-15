"""
Quick hack to add the missing set of points from a periodic restart
"""
import numpy as np

input_file = "restart_flow_05001.dat"
output_file = "slice_restart.dat"
with open(input_file, 'r') as inf:
    with open(output_file, 'w') as outf:
        for line in inf.readlines():
            outf.write(line)
            data = line.split()
            try:
                x_coord = float(data[1])
            except ValueError:
                # Header, continue without parsing
                continue
            if np.abs(x_coord - 16*np.pi) < 1E-8:
                data[1] = f"{0:19.17e}"
                outf.write("\t".join(data) + "\n")
