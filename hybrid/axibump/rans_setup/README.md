How to Set Up the Initial RANS Solution
=======================================

This is how I set up the initial RANS solution.  It is not necessarily the
optimal method. First, a RANS solution on a narrow grid is solved to keep
computational costs low. This RANS solution is calculated in several stages.

The various stages are described as follows:

#### Get a 1-degree RANS solution

1. Steady RANS solution with robust (but inaccurate) RANS settings. For
   example, the dilatational terms are not included in the production of
   turbulent kinetic energy. This is only run until the residuals drop
   slightly.
2. Steady RANS solution with final RANS settings. This is only run until
   the residuals drop slightly.
3. A URANS solution with the same RANS setting and a small timestep. This
   is run for 10,000 timesteps.
4. A URANS solution with the same RANS settings, but a larger timestep.
   This is run for 10,000 timesteps.

For more details, see the `axibump_rans_stage*.cfg` files.

#### Interpolate results onto a wider (15-degree) mesh

The interpolation process takes a single slice from the solution and
fills in the restart file with a new solution that is azimuthally uniform.

1. Generate the ASCII restart file. To do this, run the python script `generate_ascii_restart.py`
  on your wide-mesh cfg file.  The python script is located in the su2 directory, under
  `SU2_PY`.  You must have the environmental variable `SU2_RUN` set correctly to use the python
  script. This script automates the creation of an ASCII restart file from an existing problem.
  The command will look like this:
```
python3 $SU2_RUN/generate_ascii_restart.py -f axibump_rans_wide.cfg
```
2. Extract a slice from your 1-degree simulation. The command will look like this:
```
python3 extract_slice.py -i flow.mesh.szplt flow.sol.szplt -o narrow_span_slice.npy
```
3. Run the interpolation program. The command will look like this:
```
 python3 interpolate_solution.py narrow_span_slice.npy restart_flow_ascii.dat -o interp.dat
```

#### Burn out the transients

Then, the URANS solution is run for another 10,000 timesteps. This
is done with `axibump_rans_wide.cfg`

Possible Improvements
---------------------

+ The URANS solution changes a lot between the narrow and wide
  meshes, which also limits the initial timesteps you can take.
  Does it even make sense to compute a 1-degree result? Or can
  we just take uniform ICs and start with that? Or just use the
  steady-state 1-degree results?
