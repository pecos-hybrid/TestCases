"""
"""

import numpy as np
import tecplot as tp
from tecplot.constant import PlotType, ReadDataOption
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar


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


def RemapTecData(array):
    print("Remapping Tecplot data to a structured grid")
    x = np.unique(array["X"])
    y = np.unique(array["Y"])
    z = np.unique(array["Z"])
    shape = (len(x), len(y), len(z))
    output = np.zeros(shape, dtype=array.dtype)
    output["X"], output["Y"], output["Z"] = np.meshgrid(x, y, z, indexing="ij")
    output_points = (output["X"], output["Y"], output["Z"])
    old_points = (array["X"], array["Y"], array["Z"])
    bar = IncrementalBar('Interpolating', max=len(array.dtype.names)-3)
    for key in array.dtype.names:
        if key not in ["X", "Y", "Z"]:
            output[key] = griddata(old_points, array[key], output_points,
                                   method="nearest")
            bar.next()
    bar.finish()
    return output


data = ReadTecData("channel/channel.plt")
remap = RemapTecData(data)
np.save("structured_channel_data", remap)

Nz = remap.shape[2]
z_index = int(Nz/2)
z_loc = remap["Z"][0, 0, z_index]
fig, ax = plt.subplots()
im = ax.pcolormesh(remap["X"][:, :, z_index],
                   remap["Y"][:, :, z_index],
                   remap["U-X"][:, :, z_index])
fig.colorbar(im, ax=ax)
ax.set_title("$z = {:.3f}$".format(z_loc))
plt.show()
