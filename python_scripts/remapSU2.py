"""A set of tools for working with python and SU2 restart files


"""

import numpy as np
from scipy.interpolate import interp1d


def RemapData(old_data, profiles):
    """ Take an old array of data and interpolate new data on the same grid.

    The remapping uses a 1-D linear interpolation.
    Poor results were observed using a cubic interpolation where sharp
    gradients exist (e.g. in the dissipation near the wall).

    Because this script uses a linear interpolation, the grid points in the
    profile do not have to match the grid points in the old data.

    The script currently assumes that the profiles are 1D, and they are
    constant in the x and y directions.

    Args:
        old_data: The data to be overwritten
        profiles: The interpolation data

    Returns:
        A new array with the same coordinates as old_data, but with
        the field variables interpolated from the profiles file.
    """
    interp = {}
    for key in profiles.dtype.names:
        interp[key] = interp1d(profiles['y'], profiles[key],
                               kind="linear")
    out = np.array(old_data)
    y = old_data['y']
    if 'TKE' in old_data.dtype.names:
        flow_vars = ['Density', 'XMomentum', 'YMomentum', 'Energy',
                     'TKE', 'Dissipation', 'v2', 'f']
    elif 'Nu_Tilde' in old_data.dtype.names:
        flow_vars = ['Density', 'XMomentum', 'YMomentum', 'Energy', 'Nu_Tilde']
    else:
        raise KeyError("Could not find turbulence variables in restart file!")
    for key in flow_vars:
        out[key] = interp[key](y)
    if "ZMomentum" in out.dtype.names:
        out['ZMomentum'] = 0.0
    if "Alpha" in out.dtype.names:
        out["Alpha"] = 1.0
    return out


def AddTGNoise(data, num_freqs=20, magnitude=0.2):
    """ Add random Taylor-Green vortex fields to a set of data.

    This function adds incompressible noise to a velocity field.
    Taylor-Green vortex fields are added to the x-z plane, and a
    simple wall-damping function is added to the y direction to ensure
    that u=0 at the walls.

    Args:
        data: The field containing x,y,z coordinates and momentums
        num_freqs: The number of different vortex fields to add
        magnitude: The amplitude of the TG field for X-Momentum.
           This value is rescaled by the maximum value of the
           X-Momentum field, such that setting magnitude = 1 gives
           the noise an actual amplitude equal to the maximum value
           of the X-Momentum.

    Returns:
        A field identical in structure and coordinates to the input
        data, but with additional noise.
    """
    x = data['x']
    y = data['y']
    z = data['z']
    u_TG = np.zeros(x.shape)
    v_TG = np.zeros(x.shape)
    w_TG = np.zeros(x.shape)
    umax = np.max(data["XMomentum"])
    A = 1.0
    C = -1.0
    x_frequencies = np.random.uniform(1.0, 30.0, num_freqs)
    y_frequencies = np.random.randint(1, 20, num_freqs)
    z_frequencies = np.random.uniform(1.0, 30.0, num_freqs)
    u_magnitudes = np.random.uniform(0.0, magnitude*umax, num_freqs)
    params = zip(x_frequencies, y_frequencies, z_frequencies, u_magnitudes)
    for x_freq, y_freq, z_freq, u_mag in params:
        # Wall damping to enforce no-slip
        B = np.sin(y_freq*np.pi*y/2)
        # Rescale to give high frequencies low magnitudes
        rescale = 1.0/max(x_freq, z_freq)
        a = x_freq
        c = z_freq
        A = u_mag
        # Ensure that incompressibility is satisfied
        C = -(A*a)/c
        # Create the fields
        u_TG += A*np.cos(a*x)*np.sin(c*z)*B*rescale
        w_TG += C*np.sin(a*x)*np.cos(c*z)*B*rescale
    data["XMomentum"] += u_TG
    data["ZMomentum"] += w_TG
    return data


def AddRandomNoise(data, magnitude=0.005):
    """ Add random normally-distributed noise to a set of data.

    Adds random noise to a velocity field. The noise is normally
    distributed, with a mean of zero and a standard deviation defined by
    both the X-Momentum field and the magnitude.

    Args:
        data: The field containing x,y,z coordinates and momentums
        magnitude: The standard deviation of the noise.  This standard
           deviation is rescaled by the X-Momentum field, such that
           setting magnitude = 1 gives the noise an actual standard
           deviation equal to the local value of the X-Momentum.
           Setting magnitude=0.01 gives the noise an actual standard
           deviation equal to 1% of the local X-Momentum.

    Returns:
        A field identical in structure and coordinates to the input
        data, but with additional noise.
    """
    N = data["XMomentum"].size
    u_noise = np.multiply(np.random.normal(0, magnitude, N), data["XMomentum"])
    v_noise = np.multiply(np.random.normal(0, magnitude, N), data["XMomentum"])
    w_noise = np.multiply(np.random.normal(0, magnitude, N), data["XMomentum"])
    data["XMomentum"] += u_noise
    data["YMomentum"] += v_noise
    data["ZMomentum"] += w_noise
    return data


def WriteToSU2(restart_file, outfile, array, num_footer_lines=9):
    """ Write an array to an SU2 restart file, using another file as a template

    This function assumes that the array has all the data necessary for SU2.

    Args:
        restart_file: An ASCII restart file for SU2, whose points should
            match the array's points
        outfile: The name of the file to be written, including the extension
        array: The array to be saved
        num_footer_lines: The number of lines in the footer of the SU2 restart
    """
    # Get the header and footer from interpolated file
    print("Saving results to " + outfile)
    with open(restart_file, 'r') as infile:
        header = infile.readline().strip()
        footer = ""
        # Skip over the data
        for i in range(array['x'].size):
            infile.readline()
        for i in range(num_footer_lines):
            footer += infile.readline()
        footer = footer.strip()

    # Write the results to a file
    fmt_str = "%d"
    for i in range(len(array.dtype.names) - 1):
        fmt_str += "\t%.15e"
    np.savetxt(outfile, array, fmt=fmt_str, header=header, footer=footer,
               comments="")
