Transonic, axisymmetric bump case
=================================


Overview
--------

This test case is transonic (freestream Mach number 0.875) flow over an
axisymmetric bump.  Reynolds number (based on bump chord and freestream
conditions) is 2.763e6.  Additional details of the case, including
experimental data for comparison, can be found (as of 11/18/2019) at

https://turbmodels.larc.nasa.gov/axibump_val.html

The primary reference for the experimental data is

```
Bachalo, W. D. and Johnson, D. A., Transonic, Turbulent
Boundary-Layer Separation Generated on an Axisymmetric Flow Model,
AIAA Journal, Vol. 24, No. 3, 1986, pp. 437-443.
https://doi.org/10.2514/3.9286
```

Additional papers of interest include:

+ IDDES, mixed DNS and IDDES, and RANS
```
Spalart, Belyaev, Garbaruk, Shur, Strelets, and Travin, Large-Eddy and
Direct Numerical Simulations of the Bachalo-Johnson Flow with
Shock-Induced Separation, Flow, Turbulence and Combustion, Vol. 99,
No. 3, 2017, pp. 865-885. https://doi.org/10.1007/s10494-017-9832-z
```
+ WMLES
```
Iyer, Park, and Malik, Wall–Modeled Large Eddy Simulation of Transonic
Flow over an Axisymmetric Bump with Shock-Induced Separation, AIAA
2017-3953.
```
+ WRLES
```
Uzun, A., & Malik, M. R. (2019). Wall-resolved large-eddy simulations
of transonic shock-induced flow separation. AIAA Journal, 57(5),
1955–1972. https://doi.org/10.2514/1.J057850
```

Domain and Meshing
------------------

The mesh was generated in Pointwise and processed using SU2_MSH (or the
su2perio script) to add periodicity information required by SU2.

The pointwise glyph is: `generate_grid.glf`. There are a number of
variables, including the number of grid points and the streamwise
spacing, that can be controlled using the script variables.  The script
uses the grid file `bump_newaxi_721.p2dfmt` from the NASA TMR website as
a starting point.  You will need to edit the script to point to a local
copy of this file.

Running RANS
------------

See the folder `rans_setup` for more details on the initial RANS setup.

Generating the slice
-------------------

Creating a 3D slice from a RANS file is a two part process. First, you
extract the data from a tecplot binary as a npy file.  Then you use
that write that raw data to a restart slice.  The commands are similar
to the following.

```
python3 extract_slice.py -i flow.szplt -o axibump_sst_1731x251
python3 write_slice_to_restart_fmt.py axibump_sst_1731x251.npy -o slice_restart_sst_1731x251.dat
```

Currently, starting a hybrid simulation from a restart slice is not
supported.  So you have to run the RANS solution for a few timesteps, save
a normal restart file, then start the hybrid.

Running hybrid
--------------

The SU2 configuration file `axibump_v2f_timestep.cfg` provides a sample
hybrid configuration file.

Notes and tips
--------------

- For some cases, the RANS solution in hybrid RANS/LES was observed to
  become unstable. The solution crashed with negative densities. The
  culprit was a negative dissipation, which destroyed the RANS solution
  locally. Forcing v2 production to stay positive prevented this
  abnormality.
