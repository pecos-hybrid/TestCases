Transonic, axisymmetric bump case
=================================


Overview
--------

This test case is transonic (freestream Mach number 0.875) flow over
an axisymmetric bump.  Reynolds number (based on bump chord and
freestream conditions) is 2.763e6.  Additional details of the case,
including experimental data for comparison, can be found (as of
11/18/2019) at

https://turbmodels.larc.nasa.gov/axibump_val.html

The primary reference for the experimental data is

```
Bachalo, W. D. and Johnson, D. A., Transonic, Turbulent
Boundary-Layer Separation Generated on an Axisymmetric Flow Model,
AIAA Journal, Vol. 24, No. 3, 1986, pp. 437-443.
https://doi.org/10.2514/3.9286
```

Additional papers of interest include

```
Spalart, Belyaev, Garbaruk, Shur, Strelets, and Travin, Large-Eddy and
Direct Numerical Simulations of the Bachalo-Johnson Flow with
Shock-Induced Separation, Flow, Turbulence and Combustion, Vol. 99,
No. 3, 2017, pp. 865-885. https://doi.org/10.1007/s10494-017-9832-z
```

which shows IDDES, mixed DNS and IDDES, and RANS results, and

```
Iyer, Park, and Malik, Wall–Modeled Large Eddy Simulation of Transonic
Flow over an Axisymmetric Bump with Shock-Induced Separation, AIAA
2017-3953.
```

which shows WMLES.


Domain and Meshing
------------------

The domain extends from x/c = -3.2 to x/c = 4.4 in the streamwise
direction, with the bump occupying the region 0 <= x/c <= 1.  In the
wall normal direction, outside the bump, the wall is at y/c = 0.375
and the "top" of the domain is at y/c = 4.  This corresponds to the
domain from the NASA turbulence modeling resource website.  In the
azimuthal direction, we simulate a wedge of 15 degrees, which
corresponds to the small domain used for the DNS in the Spalart et
al. paper.

The mesh consists of 512x256x32 (streamwise x wall-normal x
azimuthal) points.  These are uniformly spaced in the azimuthal but
clustered in the streamwise and wall-normal directions to improve
resolution near the shock and near the wall.  The mesh was generated
in Pointwise and processed using SU2_MSH to add periodicity
information required by SU2.

TODO: Add details on mesh generation procedure and pointwise script.


Running RANS
------------

The SU2 configuration file axibump_rans.cfg can be used to generate a
RANS solution to use as an initial condition for a hybrid solution.

Some notes about the RANS:

* `DIVU_IN_TKE_PRODUCTION= NO` is currently used to improve stability
  through the initial transient.  After iterating through this
  transient, this flag should be switched to YES, but I have not done
  this yet.
* `KIND_V2F_LIMIT= T_L_LIMIT` is used; the impact of `KIND_V2F_LIMIT=
  EDDY_VISC` has not been assessed.
* A uniform inlet condition is used, which appears to correspond to
  the way the NASA results were generated
  (https://turbmodels.larc.nasa.gov/axibump_val.html).  We could
  shorten the domain by imposing an inlet profile.
* TODO: Add notes about iterations to solution, etc once converged solution reached.


Running hybrid
--------------

The SU2 configuration file axibump_hybrid.cfg provides a sample hybrid
configuration file.
