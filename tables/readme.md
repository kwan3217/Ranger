The Ranger 7 mission is heavily documented
in the form of tables. This folder contains
data from the tables.

* `trajectory_7A.csv` - timing of camera A
  images from [Ranger VII Photographic Parameters](https://ntrs.nasa.gov/citations/19670002488).
  This is from the green (manually entered) data
  on `Ranger 7 Trajectory.ods`, tab `Image A Parameters`.
  This is sufficient information to construct a position
  kernel for the spacecraft, as well as a C-matrix kernel for
  the A camera, from camera activation through impact.
  * TAB - Table number (also Atlas photo number)
  * POD - Primary Original mission Data frame
  * Timp - Time before impact, s. Impact occured
    at 1964-07-31 13:25:48.799 GMT.
  * alt - altitude above reference sphere, km.
    Reference sphere is 1735.455 radius, which
    is historical best estimate of lunar radius
    at the impact point.
  * ssc_lat - latitude of subspacecraft point
  * ssc_lon - longitude of subspacecraft point
  * v - spacecraft speed, km/s. This value and the
    two below specify a complete velocity vector,
    believed to be v_rel, IE relative to the Moon
    body-fixed frame.
  * pth - flight path angle, deg above horizon. 
    All values are negative, since the flight path
    is below the local horizon, IE downward.
  * az - flight azimuth, deg E of N.
  * pt1_lat - latitude of point 1. This is the intersection
    of the ray from the current spacecraft position along
    the current velocity vector, and the reference surface.
    Note that this is *not* the impact point, since lunar
    gravity is continaully bending the trajectory downward.
  * pt1_lon - longitude of point 1.
  * pt1_srange - slant range to point 1
  * pt2_lat - latitude of point 2, center reticle mark.
    To be specific, all locations of reticle marks are
    the intersection of the ray from the camera in the
    direction of the reticle mark, and the reference
    sphere centered on the Moon center of mass and with
    radius equal to radius of surface at impact point.
  * pt2_lon - longitude of point 2
  * pt2_srange - slant range from spacecraft to point 2.
  * p18_lat - latitude of point 18, reticle mark on the
    right end of the center row of marks. This can be
    used along with the point-toward algorithm to determine
    the complete orientation of the camera.
  * p18_lon - longitude of point 18
  * p18_srange - slant range to point 18
* `camera_7a_reticle.csv` - For a single TAB (POD 292, TAB 143)
  get the latitude, longitude, and slant range for each
  reticle point. Every TAB has all of these values, but
  that is way too much to type. The time, latitude, longitude,
  altitude, and velocity vector of the spacecraft at that point 
  are available from the TAB143 row of `trajectory_7a.csv` .
* `geocentric_7.csv` Geocentric state vector in Earth Equatorial
  True of Date frame, from [Ranger VII Flight Path and its
  Determination from Tracking Data](https://ntrs.nasa.gov/citations/19650003678).
  This table includes both the pre-maneuver (Appendix B, pp89-95)
  and post-maneuver (Appendix C, pp96-110) vectors, at about 1 hour
  intervals. The last position is about 75ms before impact.
* `selenocentric_7.csv` Selenocentric state vector from Appendix C
  above. The vectors are still in 