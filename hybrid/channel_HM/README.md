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
a WMLES study at: http://dx.doi.org/10.1063/1.5030859 

It can be generated using
[3DChannelPeriodic.py](https://github.com/pecos-hybrid/MeshTools/blob/master/Python/3DChannelPeriodic.py)
and the following command:

```
python ./3DChannelPeriodic.py -n 25 -m 21 -l 21 -x 6.2831853071795864769 -y 3.14159265358979 -z 2.0 -s 0.001 --file=channel_coarse.su2 
```
