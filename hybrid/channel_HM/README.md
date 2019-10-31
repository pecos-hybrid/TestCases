High Mach Channel
=================

This is a high-Mach channel test case, matching the following DNS study
by Modesti and Pirozzoli:

```
D. Modesti, S. Pirozzoli, Reynolds and Mach number effects in
compressible turbulent channel flow, Int. J. Heat Fluid Flow. 59 (2016)
33–49. doi:10.1016/j.ijheatfluidflow.2016.01.007.
```

The specific case chosen is `CH15C`, which corresponds to:

- Bulk Reynolds number: 34000
- Friction Reynolds number: 1015
- Bulk Mach number: 1.5

As of 9/16/2019, the DNS data can be found at:
http://newton.dima.uniroma1.it/supchan/stat/

The original paper used Sutherland's law for the viscosity model.
Sutherland's law requires a reference temperature.  Based on the
relationship between viscosity and temperature in the DNS data, the
wall temperature used in the study was approximately 267 K. This
temperature does not appear in the DNS paper. 

The grid for the SU2 case was generated based on the grid sizes used in
a WMLES study at: http://dx.doi.org/10.1063/1.5030859 . Since the near-wall
region needs to RANS (and not WMLES), the wall-normal grid needed to be
more resolved than the WMLES mesh.

The mesh be generated using
[3DChannelPeriodic.py](https://github.com/pecos-hybrid/MeshTools/blob/master/Python/3DChannelPeriodic.py)
and the following command:

```
python ./3DChannelPeriodic.py -n 25 -m 21 -l 61 -x 6.2831853071795864769 -y 3.14159265358979 -z 2.0 -s 0.001 --file=channel_hm_25x21x61.su2 
```

Times
-----

The bulk velocity is 491.869, and the channel length is 6.283.  That
makes each flow-through 0.0127.

CFL = 1 corresponds to dt = 3E-4 (approximately).

Steps to Recreate Results
-------------------------

First, recreate the initial RANS field. I used two RANS stages to create the
initial RANS field.  The first had temperature forcing.  This helps to avoid
a very long transient as the temperature approaches the desired value.  The
second stage is with momentum forcing but no temperature forcing.  This is
allowed to run a long time to help eliminate any transient behavior.

I could have used a 2D channel simulation, then initialized the 3D rans
channel with the 2D results.  In practice, I found that SU2 still had some
transient behavior after initializing the 3D case with a 2D flow.  To keep
the computational pipeline, I just used the full 3D case as the starter for
the hybrid problem.

Steps:

1. Go to the `TestCases/rans/channel_HM/3D` folder.
2. Run SU2 with the `rans_hm_channel_stage1.cfg` file.
3. Run SU2 with the `rans_hm_channel_stage2.cfg` file.

You should end up with a `restart_flow_15000.dat` file. This is the initial
field used for the hybrid calculation.

4. Go to `TestCases/rans/channel_HM/` folder.
5. Run SU2 with the `channel_hybrid.cfg` file.
