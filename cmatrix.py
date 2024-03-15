"""
Calculate the camera pointing matrix at each A camera exposure
"""
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
from kwanmath.geodesy import llr2xyz, xyz2llr
from kwanmath.vector import vnormalize, vcomp, vcross, vdot, vlength
from numpy.linalg import inv

moon_r0=1735.455 # distance from Moon center of mass to Ranger 7 impact point, km
r7_timp=datetime(year=1964,month=7,day=31,hour=13,minute=25,second=48,microsecond=799000,tzinfo=timezone.utc)


@dataclass
class ReticlePoint:
    lat:float
    lon:float
    srange:float
    def __init__(self,line:str=None,lat:float=None,lon:float=None,srange:float=None):
        if line is not None:
            parts=line.strip().split(",")
            i_point=int(parts[0].strip())
            lat   =float(parts[1].strip())
            lon   =float(parts[2].strip())
            srange=float(parts[3].strip())
            azn   =float(parts[4].strip())
        self.lat=lat
        self.lon=lon
        self.srange=srange
    def r(self)->np.ndarray:
        return llr2xyz(lat=self.lat,lon=self.lon,deg=True,r=moon_r0)


@dataclass
class TrajectoryPoint:
    timp:float
    alt:float
    ssc_lat:float
    ssc_lon:float
    spd:float
    fpa:float
    az:float
    reticle:dict[int,ReticlePoint]=field(default_factory=dict)
    def __init__(self,line:str=None,timp:float=None,
                      alt:float=None,ssc_lat:float=None,ssc_lon:float=None,
                      spd:float=None,fpa:float=None,az:float=None,
                      reticle:dict[int,ReticlePoint]=None):
        if line is not None:
            parts=line.strip().split(",")
            pod       =int(parts[1].strip())
            timp      =float(parts[ 2].strip())
            alt       =float(parts[ 3].strip())
            ssc_lat   =float(parts[ 4].strip())
            ssc_lon   =float(parts[ 5].strip())
            spd       =float(parts[ 6].strip())
            fpa       =float(parts[ 7].strip())
            az        =float(parts[ 8].strip())
            pt1_lat   =float(parts[ 9].strip())
            pt1_lon   =float(parts[10].strip())
            pt1_srange=float(parts[11].strip())
            pt2_lat   =float(parts[12].strip())
            pt2_lon   =float(parts[13].strip())
            pt2_srange=float(parts[14].strip())
            p18_lat   =float(parts[15].strip())
            p18_lon   =float(parts[16].strip())
            p18_srange=float(parts[17].strip())
            reticle   ={1:ReticlePoint(lat=pt1_lat, lon=pt1_lon, srange=pt1_srange),
                        2:ReticlePoint(lat=pt2_lat, lon=pt2_lon, srange=pt2_srange),
                       18:ReticlePoint(lat=p18_lat, lon=p18_lon, srange=p18_srange)}
        self.timp=timp
        self.alt=alt
        self.ssc_lat=ssc_lat
        self.ssc_lon=ssc_lon
        self.spd=spd
        self.fpa=fpa
        self.az=az
        self.reticle=reticle
    def r(self)->np.ndarray:
        return llr2xyz(lat=self.ssc_lat,lon=self.ssc_lon,deg=True,r=moon_r0+self.alt)


def ray_sphere_intersect(r0:np.ndarray,v:np.ndarray,rsph:float=moon_r0)->np.ndarray|None:
    """
    Calculate the intersection of a ray r(t)=r0+vt and a sphere vlength(r)=r_sph

    :param r0: Initial point of ray, in a coordinate frame centered on sphere center
    :param v:  Direction of ray, in a frame parallel to the frame used for r0
    :param rsph: radius of sphere
    :return: nearer intersection point, or None if ray doesn't intersect sphere
    """
    # See where the velocity vector touches the ground. This is raster point 1
    # A sphere has a radius rm and therefore an equation of \vec{r}.\vec{r}=rm^2.
    # The ray has an equation of \vec{r}(t)=\vec{r}_0+\vec{v}t . So, we have:
    #   (\vec{r}_0+\vec{v}t).(\vec{r}_0+\vec{v}t)=rm^2
    #   \vec{r}_0.(\vec{r}_0+\vec{v}t)+\vec{v}t.(\vec{r}_0+\vec{v}t)=rm^2
    #   \vec{r}_0.\vec{r}_0+\vec{r}_0.\vec{v}t+\vec{v}t.\vec{r}_0+\vec{v}t.\vec{v}t=rm^2
    #   \vec{r}_0.\vec{r}_0+\vec{r}_0.\vec{v}t+\vec{v}t.\vec{r}_0+\vec{v}.\vec{v}(t^2)=rm^2
    #   \vec{r}_0.\vec{r}_0+\vec{r}_0.\vec{v}t+\vec{v}t.\vec{r}_0+\vec{v}.\vec{v}(t^2)-rm^2=0
    #   \vec{r}_0.\vec{r}_0+t(\vec{r}_0.\vec{v}+\vec{v}.\vec{r}_0)+\vec{v}.\vec{v}(t^2)-rm^2=0
    #   \vec{r}_0.\vec{r}_0+2t(\vec{r}_0.\vec{v})+\vec{v}.\vec{v}(t^2)-rm^2=0
    #   A=\vec{v}.\vec{v}, always positive
    #   B=2\vec{r}_0.\vec{v}, positive if
    #   C=\vec{r}_0.\vec{r}_0-rm^2, positive if altitude is positive
    #   t=(-b+-sqrt(b^2-4ac))/2a
    A=vdot(v,v)
    B=2*vdot(r0,v)
    C=vdot(r0,r0)-rsph**2
    D=B**2-4*A*C
    if D<0:
        return np.nan*r0
    tp=(-B+np.sqrt(D))/(2*A)
    tm=(-B-np.sqrt(D))/(2*A)
    rsurfp=r0+tp*v
    rsurfm=r0+tm*v
    assert np.isclose(vlength(rsurfp),rsph)
    assert np.isclose(vlength(rsurfm),rsph)
    # This code only works when ray is pointing towards
    # surface and initial point is outside of sphere
    t=np.min((tp,tm))
    rsurf=r0+t*v
    return rsurf


def lvlh_to_xyz(*,r:np.ndarray, spd:float, fpa:float, az:float, deg:bool=True):
    """
    Given a velocity vector specified in 'local horizon, local vertical' (LVLH)
    spherical coordinates and a point in space at which to calculate the horizon,
    calculate the equivalent vector in XYZ coordinates.

    In this context we use the term 'relative velocity' to mean velocity
    relative to the Moon body-fixed frame. This is in opposition to 'inertial
    velocity' which would be velocity relative to an inertial frame.

    The intended use case is the Ranger 7 trajectory. The given data includes the
    latitude, longitude, and altitude above the reference sphere in planetocentric
    coordinates, and the speed, flight-path angle above the horizon, and azimuth
    of the relative velocity vector. Given all of those, it is possible to get the
    velocity vector in cartesian coordinates in the body-fixed frame.

    :param r:   Position to calculate horizon coordinates. This implies the coordinate
                frame, and the velocity inputs must be relative to the same frame.
                For Ranger, this is the Moon body-fixed frame.
    :param spd: Magnitude of relative velocity vector
    :param fpa: Flight path angle of relative velocity vector
    :param az:  Azimuth east of true North of relative velocity
    :param deg: If True (default), then the input fpa and az are in degrees. If false,
                then they are radians
    :return: Cartesian coordinates of relative velocity vector in body-fixed (not lvlh)
             frame
    """
    # LVLH to xyz
    # basis vectors of enr space in xyz
    r = vnormalize(r)
    z = vcomp((0, 0, 1))
    e = vnormalize(vcross(z, r))
    n = vnormalize(vcross(r, e))
    # Following 3b1b, each column of a square transformation matrix is where
    # the corresponding basis vector lands. We take e, n, and r as basis
    # vectors and compute the matrix that transforms to xyz from enr
    M_xyz_ner = np.hstack((n, e, r))
    M_ner_xyz = inv(M_xyz_ner)
    print(M_ner_xyz @ r)  # should be [[0],[0],[1]]
    # Now we can compute the velocity vector from magnitude, fpa, az
    # in LVLH (ner) space
    v_ner = llr2xyz(lat=fpa, lon=az, r=spd, deg=deg)
    v_xyz = M_xyz_ner @ v_ner
    return v_xyz




def main():
    points={}
    with open("tables/camera_7a_reticle.csv") as inf:
        header=inf.readline().strip().split(",")
        for line in inf:
            parts=line.strip().split(",")
            i_point=int(parts[0].strip())
            points[i_point]=ReticlePoint(line=line)
    trajectory={}
    with open("tables/trajectory_7a.csv") as inf:
        header=inf.readline().strip().split(",")
        for line in inf:
            parts=line.strip().split(",")
            i_tab=int(parts[0].strip())
            trajectory[i_tab]=TrajectoryPoint(line=line)
    tab143=trajectory[143]
    # Position of spacecraft in Moon body-fixed frame
    rsc=tab143.r()
    # Position of reticles in same frame
    v_ret={}
    for i_pt, pt in points.items():
        rret=pt.r()
        v_ret[i_pt]=vnormalize(rret-rsc)
    # reticle point 1 is special -- it's not really a reticle point. Instead, it's
    # the projection of the current velocity vector in a straight line to the surface.
    # If the spacecraft is not rotating, then the images will appear to expand around
    # this point. The following code verifies that the velocity vector given in the table
    # does in fact intersect the ground
    v_xyz = lvlh_to_xyz(r=rsc,spd=tab143.spd,fpa=tab143.fpa,az=tab143.az,deg=True)
    rsurf_xyz_a=ray_sphere_intersect(rsc,v_xyz)
    rsurf_xyz_b=points[1].r()
    lon_a,lat_a,r_a=xyz2llr(rsurf_xyz_a,deg=True)
    lon_b,lat_b,r_b=points[1].lon,points[1].lat,moon_r0
    print(f"projected velocity vector: lon={lon_a:10.6f} lat={lat_a:10.6f} r={r_a:10.6f}")
    print(f"Table reticle point 1:     lon={lon_b:10.6f} lat={lat_b:10.6f} r={r_b:10.6f}")
    assert np.allclose((lon_a,lat_a,r_a),(lon_b,lat_b,r_b),rtol=0, atol=1e-3)
    # Now we can turn all reticle points into a camera frame. Point 2
    # will be along the z axis pointing out, point 18 (on the right center of the image)
    # will be in the +x direction, and "down" on the images will be the +y
    # direction.


if __name__=="__main__":
    main()