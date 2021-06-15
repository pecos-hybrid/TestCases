Low-Mach Spatially Developing Channel
=====================================

Grid Generation
---------------

The `3DChannel_Periodic.py` script used for the temporally developing
channel test cases is hardcoded to produce periodic boundary conditions in
both the streamwise and the spanwise directions.  This is due to the
inherent shortcomings of the Fortran `SU2_PER` script and the C++
`SU2_MSH` scripts.  They cannot handle multiple intersecting periodic
boundary conditions.  However, the spatially developing channels only
have a single set of periodic boundary conditions (in the spanwise
direction). So the normal `SU2_PER` script can be used.  This is located
at [this github
repo](https://github.com/pecos-hybrid/MeshTools/tree/master/SU2_PER).

Two grids need to be generated: 

1. A 2D grid needs to be generated to setup the inlet. This will have a
   different set of periodic boundaries.  It will be periodic in the streamwise
   direction, to get a fully developed flow.
2. A 3D grid, for the actual run.

### 2D Case

```
python3 tanh_2DChannel.py -n 102 -m 110  -x 25.132741228718345 -y 2 -s 0.0001923 --file=channel_lm_102x110_nonper.su2
```
Then you have to convert the non-periodic grid into a periodic grid.
```
ln -s channel_lm_102x110_nonper.su2 chan_nonper.su2
SU2_PER < channel_lm_2D_PER.su2
mv chan_per.su2 channel_lm_102x110.su2
```

### 3D Case

```
python3 tanh_3DChannel.py -n 204 -m 39 -l 110  -x 50.26548245743669 -y 9.42477796076938 -z 2 -s 0.0001923 --file=channel_lm_204x39x110_nonper.su2 
```

Then you have to convert the non-periodic grid into a periodic grid.
```
ln -s channel_lm_204x39x110_nonper.su2 chan_nonper.su2
SU2_PER < channel_lm_3D_PER.su2
mv chan_per.su2 channel_lm_204x39x110.su2
```

### Creating the 2D Solution


