"""
Process the terminal trajectory as listed in
[Ranger 7 Photographic Parameters](https://ntrs.nasa.gov/citations/19670002488).
We will focus on Camera A first.

"""
from collections import namedtuple
from datetime import datetime, timezone
from typing import Iterable

import numpy as np
from bmw import su_to_cu, gauss, kepler
from kwanmath.geodesy import llr2xyz, ray_sphere_intersect
from kwanmath.vector import vcross, vlength, vdecomp
from matplotlib import pyplot as plt
from spiceypy import furnsh, gdpool, sxform

from gmt import tdb, calc_et

furnsh('kernels/Ranger7Background.tm')

# mu_moon=4904.8695     #Value from Vallado of gravitational parameter of Moon in km and s
# mu_earth=398600.4415  #Value from Vallado of gravitational parameter of Earth in km and s
mu_moon =gdpool("BODY301_GM",0,1)[0]  #DE431 value of gravitational parameter of Moon in km and s
mu_earth=gdpool("BODY399_GM",0,1)[0] #DE431 value of gravitational parameter of Earth in km and s

# third basis vector
zhat=np.array([[0],[0],[1]])

# Documented Ranger 7 impact points. All seem to be in Mean-Earth-Pole coordinates
# From Image A, last row (value is actually from point 1 from the previous row, 2.5s before impact)
# lat: -10.630   lon: -20.588   r: 1735.455   GMT: 1961-Jul-31 13:25:48.799
ImageALLR=(-10.630,-20.588,1735.455)
# From Wagner 02/2017 (https://doi.org/10.1016/j.icarus.2016.05.011)
# lat: -10.6340  lon: 339.3230  r: 1735.609
#                   (-20.6770)
WagnerLLR=(-10.6340,-20.6770,1735.609)
# From http://lroc.sese.asu.edu/posts/650 (2013 update)
# lat: -10.6340  lon: 339.3229
#                   (-20.6771)
# From http://lroc.sese.asu.edu/posts/938 (same as Wagner 02/2017 above)
# lat: -10.6340  lon: 339.3230  el: -1.791
#                   (-20.6770)
# From Trajectory table selenocentric (copied from program output below)
# lat: -10.693   lon: -20.676   r: 1735.600   GMT: 1964-Jul-31 13:25:48.724
TrajLLR=(-10.693,-20.676,1735.600)

# Reported radius of Moon at impact point. Take this from one of the LLRs
r_moon=ImageALLR[2]


image_a_tuple = namedtuple('image_a_tuple',
                           'TAB, POD,Timp    ,alt       ,ssc_lat,ssc_lon,v    ,pth    ,az     ,pt1_lat,pt1_lon,pt1_srange,pt2_lat,pt2_lon,pt2_srange,p18_lat,p18_lon,p18_srange')
timp_r7 = datetime(year=1964, month=7, day=31,
                   hour=13, minute=25, second=48, microsecond=799_000,
                   tzinfo=timezone.utc).astimezone(tdb)
etimp_r7 = calc_et(timp_r7)


def readImageA(latofs: float = 0.0, lonofs: float = 0.0, rofs: float = 0.0) -> list[image_a_tuple]:
    """
    Read the Image A table.

    :param float lonofs: offset in longitude to subtract from all longitudes in the file. This is used to make the trajectory
                         match a given impact longitude from another source.
    :rtype: list of namedtuple
    """
    result = []

    with open('tables/terminal_7a.csv', 'rt') as inf:
        # Read the header line
        header = [field.strip() for field in inf.readline().strip().split(",")]
        # Read the rows
        for line in inf:
            row = line.strip().split(",")
            values = {}
            for name, value in zip(header, row):
                this_value = int(value) if name == "TAB" else float(value)
                if "lat" in name:
                    this_value -= latofs
                if "lon" in name:
                    this_value -= lonofs
                if name == "alt":
                    this_value -= rofs
                values[name] = this_value
            result.append(image_a_tuple(**values))
    return result


def processImageA(image_a: Iterable[image_a_tuple], plot: bool = False) -> tuple[np.array, np.array]:
    """
    Convert Image A table to usable state vectors, and calculate the check values

    :param array of namedtuple image_a: Rows from original table, n elements
    :param bool plot: If true, plot the check value residuals
    :return: First element is stack of position vectors in Moon-fixed mean-earth-polar frame, shape 3xn
             Second element is stack of velocity vectors in same frame, shape 3xn
             Third element is array of Spice ET of each state

    The tables include the spacecraft position in lat/lon/alt coordinates. Altitude is defined to be zero at impact,
    so the reference surface is a sphere centered on the Moon's center of mass and has radius equal to the radius at
    impact. The latitude and longitude are referenced to the Mean-Earth/Polar (MEP) system, as realized by this report.
    This system has:
      * x axis towards mean sub-Earth point (IE after averaging out all periodic librations)
      * z axis towards mean rotation axis (similarly after averaging)
      * y axis completes the right-handed frame and is in the equatorial plane at 90deg E.
    This is the "obvious" frame to use for a synchronous rotator like the Moon. However there is
    another competing frame which we will detail here just to contrast. The principal-axis (PA)
    frame uses the gravity field of the moon to figure the inertia tensor of the whole body,
    then uses a frame such that the inertia tensor is a diagonal matrix. The axes of this frame
    are also the axes of minimum, medium, and maximum inertia. We would expect the Moon to eventually
    settle into basically a "gravity gradient" state with the rotation axis parallel to the
    shortest principal axis, and the longest axis pointing towards the Earth. The actual case
    is close to this, but measurably different. For whatever reason, the principal axes aren't
    *quite* aligned to the mean-Earth axes. It's within a few arc seconds, but not perfect.
    Fortunately the offset between these is almost constant over the relevant time-scale
    (from 1950 on). The PA frame is the physically significant one, the one used in the integration
    that creates the DE4xx series of planetary ephemerides. Conversely, the MEP frame is more
    observable. The Lunar Recon Orbiter team is the current authority on mapping the Moon, and
    they publish all products exclusively in MEP coordinates.

    The best estimate from the Ranger 7 Photographic parameters of the impact point is about
    2700m away from where LRO found the impact crater.

    All reticle marks are numbered, with point 2 being the center mark. Point 1 is the velocity
    vector as described above. For all such marks, the table includes the latitude and longitude
    on the reference surface, the distance from the spacecraft to that point, several azimuths
    including the azimuth between the image vertical and true North.

    Table "Point 1" is the point on the Lunar surface that the spacecraft is moving directly towards, based on
    its instantaneous velocity vector in a lunar body-fixed frame. This is the point that doesn't move as the
    spacecraft approaches the moon. The image appears to zoom in centered around this point.

    Table "Point 2" is the point on the Lunar surface covered by the center reticle mark. It also has latitude,
    longitude, and slant range

    Much of the data which was entered is redundant - point 1 is completely determined by the spacecraft position
    and velocity vector. Slant ranges are always calculable from the point latitudes and longitudes and the spacecraft
    position. These values were transcribed anyway, to validate the position and velocity transcription. Ideally, the
    calculated values will be exactly equal to the table values, but due to limited precision in the table, particularly
    the latitudes and longitudes, the values will be inconsistent on the few-meter level. Any discrepancy of more than
    10m drew my attention, and any larger than 20m indicated a transcription error, which was corrected.

    """
    n = len(image_a)
    rs_mep = np.zeros((3, n), np.float64)
    vs_mep = np.zeros((3, n), np.float64)
    # dsrange2 is the difference between the table slant range to point 2 and that calculated from the spacecraft lat/lon/alt
    # and point 2 lat/lon
    dsrange2s = np.zeros(n, np.float64)
    # dsrange1a is the difference between the table slant range to point 1 and that calculated from the spacecraft lat/lon/alt
    dsrange1as = np.zeros(n, np.float64)
    # dsrange1b is the difference between the table slant range to point 1 and that calculated from the spacecraft pos/vel
    # and the quadratic method (quadratic parameter t is the calculated distance between the ray origin and the ray/sphere
    # intersect point)
    dsrange1bs = np.zeros(n, np.float64)
    # dsrange1c is the distance between the table point 1 calculated from lat/lon and that calculated by the quadratic
    # method. This isn't a difference in srange like the others are, but it is measured in the same units. However, dsrange1c
    # will always be positive, while the other measures can be positive or negative.
    dsrange1cs = np.zeros(n, np.float64)
    # dv is the difference between the table velocity and that calculated by dividing the distance from the previous row's
    # position to this row's position by the difference in time. Keep track of last row position in r_last, use constant
    # 5.12s as dt. Note that this will be biased from zero because it doesn't take into account the acceleration of gravity
    # over the time step.
    dvs = np.zeros(n, np.float64)
    dvs[0] = float('NaN')
    r_last = None
    # Size of 1 millidegree of latitude at the current spacecraft altitude. This is an idea of the precision we can expect
    # in using vectors with latitudes and longitudes specified in millidegree precision.
    mds = np.zeros(n, dtype=np.float64)
    ts = np.zeros(n, dtype=np.float64)
    for i, row in enumerate(image_a):
        # Zenith vector
        rbar = llr2xyz(lat=row.ssc_lat, lon=row.ssc_lon, deg=True)
        # Position in selenocentric moon-fixed mean-earth/pole coordinates
        r = rbar * (row.alt + r_moon)
        mds[i] = (row.alt + r_moon) * np.pi * 2.0 / 360000.0
        rs_mep[:, None, i] = r
        # East vector
        e = vcross(zhat, rbar)
        ebar = e / vlength(e)
        # North vector
        nbar = vcross(rbar, ebar)
        # Velocity in selenocentric moon-fixed mean-earth/pole coordinates
        vbar_topo = llr2xyz(lat=row.pth, lon=90 - row.az, deg=True)
        (vbare, vbarn, vbarr) = vdecomp(vbar_topo)
        vbar = vbarr * rbar + vbare * ebar + vbarn * nbar
        v = vbar * row.v
        vs_mep[:, None, i] = v
        # p2 position
        p2 = llr2xyz(lat=row.pt2_lat, lon=row.pt2_lon, deg=True, r=r_moon)
        pt2_srange_calc = vlength(r-p2)
        dsrange2 = row.pt2_srange - pt2_srange_calc
        dsrange2s[i] = dsrange2
        # p1 position from table
        p1a = llr2xyz(lat=row.pt1_lat, lon=row.pt1_lon, deg=True, r=r_moon)
        p1a_srange_calc = vlength(r-p1a)
        dsrange1a = row.pt1_srange - p1a_srange_calc
        dsrange1as[i] = dsrange1a
        # p1 position from velocity vector
        (t, p1c) = ray_sphere_intersect(r, vbar, r_moon)
        # Since vbar is a unit vector, and r is measured in units of km, t has units of km itself,
        # and is therefore directly comparable to p1_srange.
        dsrange1b = row.pt1_srange - t
        dsrange1bs[i] = dsrange1b
        dsrange1c = vlength(p1c-p1a)
        dsrange1cs[i] = dsrange1c
        # Calculate velocity from last row
        ts[i] = etimp_r7 - row.Timp
        if r_last is not None:
            dt = ts[-1] - ts[-2]
            dr = vlength(r - r_last)
            dv = dr / dt - row.v
            dvs[i] = dv
        r_last = r
        # print(row.GMT, gmt, etcal(gmt), mjd,tai_utc,tai,et, etcal(et))

    if plot:
        # This plot is meant to duplicate the residual plot on the spreadsheet
        plt.plot(ts - ts[-1], dsrange2s, 'b+', label='dsrange2')
        plt.plot(ts - ts[-1], dsrange1as, 'r+', label='dsrange1a')
        plt.plot(ts - ts[-1], dsrange1bs, 'y+', label='dsrange1b')
        plt.plot(ts - ts[-1], dsrange1cs, 'g+', label='dsrange1c')
        plt.plot(ts - ts[-1], np.array(mds) * 0.5, 'k--', label='1 millidegree')
        plt.plot(ts - ts[-1], -np.array(mds) * 0.5, 'k--')
        plt.legend()
    return rs_mep, vs_mep, ts


def convertImageACanonical(rs_a_mep:np.ndarray, vs_a_mep:np.ndarray, ets_a:np.ndarray)->tuple[np.ndarray,np.ndarray,np.ndarray]:
    """
    Convert vectors from Moon-centered fixed (Mean-Earth/Polar) in km and s
    to Moon-centered but in an inertial frame parallel to Earth-centered Inertial True-of-date.
    This latter frame has:
    * xy plane parallel to true Earth equator (including precession and nutation) of the given epoch
    *  z vector parallel to true rotation axis at given epoch
    *  x vector parallel to true equinox (intersection of equator and ecliptic of date)
    Converted canonical units are using Moon reference radius and Moon gravitational parameter

    :param rs_a_mep: Position vectors in MEP frame in km. Expected to be 3xn
    :param vs_a_mep: Velocity vectors in MEP frame in km/s. Must be same shape as rs_a_mep
    :param ets_a:    Time of each state vector in Spice ET. Must have same number of elements as n
    :return: Tuple of:
      * Position vectors in Moon-centered frame parallel to ECI_TOD
      * Velocity vectors in same frame
      * Time from initial state in canonical time units.
    """
    n=len(ets_a)
    rcus_a_mcetod=np.zeros((3,n))
    vcus_a_mcetod=np.zeros((3,n))
    tcus         =np.zeros(   n )
    for i in range(n):
        r_a_mep= rs_a_mep[:, None, i]
        v_a_mep= vs_a_mep[:, None, i]
        et_a=ets_a[i]
        M_mcetod_mep=sxform("IAU_MOON","ECI_TOD",et_a)
        s_a_mep=np.concatenate((r_a_mep,v_a_mep))
        s_a_mcetod=M_mcetod_mep @ s_a_mep
        rcus_a_mcetod[:,None,i]=su_to_cu(s_a_mcetod[0:3],r_moon,mu_moon,1, 0)
        vcus_a_mcetod[:,None,i]=su_to_cu(s_a_mcetod[3:6],r_moon,mu_moon,1,-1)
    tcus=su_to_cu(ets_a-ets_a[0],r_moon,mu_moon,0, 1)
    return rcus_a_mcetod, vcus_a_mcetod, tcus


def wrap_kepler(r0_cu:np.ndarray, v0_cu:np.ndarray, ts:np.ndarray)->tuple[np.ndarray,np.ndarray]:
    """
    Use bmw.kepler to evaluate the trajectory at many times.

    :param r0_cu: Start position in canonical units
    :param v0_cu: Start velocity in canonical units
    :param ts: Times to propagate to.
    :return: First element is numpy array of position vectors, second element is numpy array of velocities
    """
    n=len(ts)
    rs=np.zeros((3,n))
    vs=np.zeros((3,n))
    for i in range(n):
        (r,v)=kepler(r0_cu, v0_cu, ts[i])
        rs[:,None,i]=r
        vs[:,None,i]=v
    return rs,vs


def plot_residuals(rcalcs,vcalcs,rs,vs,ts,subplot=411, title=''):
    #Use the fit trajectory, use
    #Kepler propagation to evaluate at each image time, and graph the difference
    n=len(ts)
    drs=rs-rcalcs
    dvs=vs-vcalcs
    mdegs=su_to_cu(vlength(rs)*2*np.pi/360000.0,r_moon,mu_moon,1,0,inverse=True)
    plt.subplot(subplot)
    plt.title(title+', pos residuals')
    plt.ylabel('pos residual/(m)')
    plt.xlabel('Time from impact/s')
    tsus=su_to_cu(ts-ts[-1],r_moon,mu_moon,0,1,inverse=True)
    dxs,dys,dzs=vdecomp(drs)
    plt.plot(tsus,su_to_cu(dxs,r_moon,mu_moon,1,0,inverse=True)*1000,'rx',label='dx')
    plt.plot(tsus,su_to_cu(dys,r_moon,mu_moon,1,0,inverse=True)*1000,'gx',label='dy')
    plt.plot(tsus,su_to_cu(dzs,r_moon,mu_moon,1,0,inverse=True)*1000,'bx',label='dz')
    plt.plot(tsus,mdegs*500,'k--',label='1 millidegree')
    plt.plot(tsus,mdegs*-500,'k--')
    plt.legend()
    plt.subplot(subplot+1)
    plt.title(title+', vel residuals')
    plt.ylabel('vel residual/(m/s)')
    plt.xlabel('Time from impact/s')
    dvxs,dvys,dvzs=vdecomp(dvs)
    plt.plot(tsus,su_to_cu(dvxs,r_moon,mu_moon,1,-1,inverse=True),'r+',label='dvx')
    plt.plot(tsus,su_to_cu(dvys,r_moon,mu_moon,1,-1,inverse=True),'g+',label='dvy')
    plt.plot(tsus,su_to_cu(dvzs,r_moon,mu_moon,1,-1,inverse=True),'b+',label='dvz')
    plt.legend()


def write_terminal(rs_):
    Ranger7Terminal_txt = """
    Ranger 7 - first completely successful Ranger lunar impact mission. Data from
    'Ranger VII Photographic Parameters', JPL Technical Report No. 32-964, 1 Nov 1966
    available at NTRS as document number 19670002488 

    The report had a table of camera parameters including the position of the spacecraft
    in a selenocentric body-fixed (Mean-earth-polar) frame for each picture published in
    the photo atlases. This spice segment uses the positions from the A camera, starting 
    about 15min before impact at {image_a[0].GMT}, and ending with the last A
    camera image 2.5s before impact at {image_a[-2].GMT}. There is also a 
    calculated state at impact, at {image_a[-1].GMT}. 

    The table seems to have had a bias in longitude, as it matches neither the previous
    segments nor the actual location of the crater as found by LRO/LROC. This bias is 
    corrected in this spice segment, such that the final longitude matches that of LRO, and
    matches the selenocentric trajectory from the other segments much better.

    These table values were manually entered into a spreadsheet and verified by checking
    the slant ranges, which were consistent with the table values to the precision allowed
    by the table latitude and longitude (several errors were caught this way).

    \\begindata
    INPUT_DATA_TYPE = 'STATES'
    OUTPUT_SPK_TYPE = 5
    OBJECT_ID=-1007
    OBJECT_NAME='RANGER 7'
    CENTER_ID=301
    CENTER_NAME='MOON'
    REF_FRAME_NAME='ECI_TOD'
    PRODUCER_ID='C. Jeppesen, Kwan Systems'
    DATA_ORDER='EPOCH X Y Z VX VY VZ'
    TIME_WRAPPER='# ETSECONDS'
    INPUT_DATA_UNITS = ('ANGLES=DEGREES' 'DISTANCES=km')
    DATA_DELIMITER=';'
    LINES_PER_RECORD=1
    CENTER_GM={mu_moon:9.4f}
    FRAME_DEF_FILE='kernels/fk/eci_tod.tf'
    LEAPSECONDS_FILE='kernels/lsk/naif0012.tls'
    """
    with open('scratch/terminal.txt', 'w') as ouf_seleno2:
        for i in range(aug_tas.size):
            print("%23.6f;%23.15e;%23.15e;%23.15e;%23.15e;%23.15e;%23.15e" % (aug_tas[i],
                                                                              rs_for_spice[i, 0],
                                                                              rs_for_spice[i, 1],
                                                                              rs_for_spice[i, 2],
                                                                              vs_for_spice[i, 0],
                                                                              vs_for_spice[i, 1],
                                                                              vs_for_spice[i, 2]), file=ouf_seleno2)





def main():
    image_a = readImageA()  # Read table A
    print(image_a[-1])
    (rs_a_mep, vs_a_mep, ts_a) = processImageA(image_a, plot=True)

    # Convert the coordinates from moon body-fixed SI to moon-centered inertial canonical
    (rs_cua_mcetod, vs_cua_mcetod, ts_cua) = convertImageACanonical(rs_a_mep, vs_a_mep, ts_a)

    #Use Gauss targeting to get a trajectory from the initial to final positions,
    #without any target bias
    (v0_gauss_cua_mcetod,v1_gauss_cua_mcetod)=gauss(rs_cua_mcetod[:,None,0],rs_cua_mcetod[:,None,-1],ts_cua[-1],Type=1)

    #Show that just using Kepler and lunar two-body gravity is inadequate, thereby
    #showing that we need to consider Earth tide.
    (rs_kepler_cua_mcetod,vs_kepler_cua_mcetod)=wrap_kepler(rs_cua_mcetod[:,None,0],v0_gauss_cua_mcetod,ts_cua)
    plt.figure(0)
    plot_residuals(rs_kepler_cua_mcetod,vs_kepler_cua_mcetod,rs_cua_mcetod,vs_cua_mcetod,ts_cua,subplot=211,title='Kepler propagation')
    plt.show()




if __name__=="__main__":
    main()
