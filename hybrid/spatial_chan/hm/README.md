Steps to Reproduce
==================

There are three steps necessary:

1. Set up the inlet condition.  This requires running a 2D channel that
   is periodic in the streamwise direction using the target timesteps,
   turbulence model, and numerical scheme.
2. Set up the RANS initial field.  This can be done with a steady-state
   solver, instead of a time-accurate solver.  This is done on the
   target grid, i.e., a grid that is periodic in the spanwise direction
   and has inlet/outlet boundary conditions.


Creating the grid
-----------------

The number of wall-normal points was chosen to match the centerline
spacing (y/d ~= 0.066) and the wall spacing (y+ ~= 1) of the Re=5200
channel case in the AMS paper by Sigfried.

This is similar to the grid generation for the low mach (`lm`) case.

### 2D Case

```
python3 tanh_2DChannel.py -n 102 -m 88  -x 25.132741228718345 -y 2 -s 0.0009 --file=channel_hm_102x88_nonper.su2
```
Then you have to convert the non-periodic grid into a periodic grid.
```
ln -s channel_hm_102x88_nonper.su2 chan_nonper.su2
SU2_PER < channel_lm_2D_PER.su2
mv chan_per.su2 channel_hm_102x88.su2
```

### 3D Case

```
python3 tanh_3DChannel.py -n 204 -m 39 -l 88  -x 50.26548245743669 -y 9.42477796076938 -z 2 -s 0.0009 --file=channel_hm_204x39x8_nonper.su2 
```

Then you have to convert the non-periodic grid into a periodic grid.
```
ln -s channel_hm_204x39x88_nonper.su2 chan_nonper.su2
SU2_PER < channel_lm_3D_PER.su2
mv chan_per.su2 channel_hm_204x39x88.su2
```

Setting Up the Inlet
--------------------

### Running the 2D RANS Case

In the directory `rans_inlet_setup` are the cfg files to set up the 2D
solution. The solution was initialized in two stages.

### Creating the inlet file

First, you need the example inlet file with the inlet coordinates.  Run
the RANS cfg for the 3D problem, e.g. `SU2_CFD channel_rans_stage1.cfg`.
That will create an inlet file named `inlet_example.dat`. You
will need this as a template for the third step.

Second, run the python script to extract the inlet variables from the tecplot
solution. This python script is the `extract_inlet_profile.py` in the
`postproc/channel_LM/` directory. This will produce an hdf5 file containing
1D profiles, averaged over homogeneous directions.

Third, run `create_inlet_file.py` in the `postproc/spatial_chan` folder.
Make sure it uses the inlet example file you created and the extracted inlet
data.

Starting the RANS Solution
--------------------------

The RANS solution is best started by using the "slice restart" feature.
You can always start the RANS solution from uniform freestream conditions,
but this will take a lot of compute time to converge to a reasonably
uniform solution.  In this case, we can just take our 2D solution and
use it as a restart.

The slice restart can be a simple ASCII solution.  I set up the "stage 4"
cfg file to output such an ASCII restart file.  The only catch is that
periodic boundaries chop off the first line of points, at the inlet. When
you jump to a spatially developing channel, you need that first row of points.
The `quick_fix_to_add_inlet.py` script is a quick hack to introduce an extra
set of points. Use this 2D restart file as the slice restart for the 3D
simulation.

After that, I run the solution for a brief period (about 3000 iterations) to
burn out any transients.  That's the `channel_rans_stage1.cfg` file.

Post-processing
---------------

There is a script for extracting profiles in `postproc/spatial_chan`.  It
really needs to be refactored so that all of the boundary-layer scripts pull
from a common post-processing library.

Inlet Labels
------------

Inlet c11

- JST = 0.5, 0.01
- c4 = 2.0
- Domain = 32x88


Inlet c12

- JST = 0.5, 0.01
- c4 = 2.0
- Domain = 39x88

Inlet c14

- Roe, 1st order
- Domain = 3x88
