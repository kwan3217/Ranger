# Spice Kernels
Some of the Spice kernels are generated
by the code from this project. Others are generated
by me *for* this project. Still others are 
directly from JPL and are not included
in this repository. You will have to go get
them.

* [`spk/de440.bsp`](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp) --
  Dynamical Epheperis 440, 2020-05-25. This is
  the current best trajectory for all the 
  planets, including Pluto. If you are tight for space,
  you can get de440s.bsp from the same place. That file
  is 40MB vs 115MB.
* [`pck/pck00011.tpc`](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc) --
  Planetary Constant Kernel. This contains sizes of the
  reference ellipsoids for the Sun, all the planets (including
  Pluto), and many of the moons and asteroids. It also
  contains rotation constants for many of these objects.
* [`pck/gm_de440.tpc`](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc) --
  Gravitational constant kernel. This contains the
  gravitational constants (Universal gravitational
  constant *G* times object mass *M*) for the Sun,
  all the planets (including Pluto) and many of the
  moons. The exact values are consistent with the
  values used when calculating DE440 above. All values
  are in units of km^3/s^2, consistent with the native
  units of Spice, km and s.
