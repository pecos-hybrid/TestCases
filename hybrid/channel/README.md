Creating the grid
-----------------

Use the `3DChannelPeriodic.py` script to create the grid.  Here is an
example usage:

```
python3 3DChannelPeriodic.py -f channel_102x39x110.su2 -n 102 -m 39 -l 110 -x 25.1327412287 -y 9.42477796077 -z 2 -s 0.000192
```

Without additional nondimensionalization, the average (not centerline) velocity is
approximately 25.  For a domain that is 8 pi long in the streamwise direction,
that makes a FT time of approximately 1 (more precisely, 1.005).

Running the Hybrid Simulation
----------------------------

In order to ease the transient solution, several stages are currently
used. The current stages are used, but are far from ideal:

+ `channel_rans_stage1.cfg`
+ `channel_rans_stage2.cfg`
+ `channel_rans_stage3.cfg`
+ `channel_hybrid.cfg`

Tips
----

+ The Roe scheme is used with the NTS upwind/central blending. The JST
scheme was tried briefly, but was found to be much less stable for this
particular problem.  Even with the fourth-order JST coefficient set to
zero, the timesteps required for stability when using SMR-RK
were excessively small.

Known Issues
--------------

Because this is low-Mach and periodic, the kinematic solution is not
sensitive to the density, temperature, or the absolute value of the pressure.
Only the density, temperature, and pressure gradients are important.  This
leads to a slow drift in these quantities, and prevents true convergence.
The density residuals do not disappear, but the turbulent variables may
convergence.
