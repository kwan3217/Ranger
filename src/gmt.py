"""
Convert GMT times to modern time scales

Usage:

Given a time in the Ranger documentation, we can interpret it as GMT
which is by definition the same as UTC. For instance, the impact time
of Ranger 7 is 1964-07-31T13:25:48.799 GMT. We represent this as:

```
>>> gmt_r7imp=datetime(year=1964,month=7,day=31,hour=13,minute=25,second=48,microsecond=799000,tzinfo=timezone.utc)
>>> print(gmt_r7imp)
1964-07-31 13:25:48.799000+00:00
```

Now if we want to use this time in Spice, we can use the TDB timezone
object:

```
>>> from gmt import tdb
>>> tdb_r7imp=gmt_r7imp.astimezone(tdb)
>>> print(tdb_r7imp)
1964-07-31 13:26:24.322391+00:00:35.523391
```

Note that:
* This time is ahead of the time in GMT (IE 13:26:24 is after 13:25:48)
* The difference is about 35s
* The exact difference is shown as the timezone offset, given to microsecond precision

The Ranger documentation always uses the term Greenwich Mean Time, GMT
and never UTC. We will treat GMT as the name of time scale *actually*
used by Ranger.

Universal Time (UT) isn't really a time at all, but a measure of the Earth
Rotation angle relative to the stars. When navigators compute longitude by
timing difference and measurements of the stars through a sextant, they are
using UT. Universal time is subject to all the physical effects which make
the rotation of the Earth irregular, such as tidal drag from the Moon,
seasonal shift of water mass, earthquakes, etc. It is a physical property
which must be measured -- these days it is measured by observation of the
position in the sky of distant radio sources such as quasars. The SI second
was designed to be "close" to the original UT second, but since the tides
continually retard the rotation of the Earth, the UT second has been getting
measurably longer over time. The SI second was therefore designed to match
UT in the year 1900 (even though that decision was made in the 1950s). UT
is available in the form of the Earth Orientation Parameters published by
the International Earth Rotation Service. Using these, it is possible to
construct the best-estimate measured orientation of the Earth relative to
the stars as a function of any of the atomic or theoretical time scales
shown below.

Terrestrial Time, known as Ephemeris Time (ET) from 1952 to 1984, Terrestrial
Dynamic Time (TDT) from 1984 to 1991, and Terrestrial time (TT) from then on,
is a theoretical time scale which is consistent with general relativity, with
its unit being one SI second of proper time elapsing on the Earth geoid. A
theoretically perfect cesium atom ticks at exactly 9,192,631,770 times per
proper second at the atom. If this atom is on the geoid (a precise definition
of the colloquial phrase "at sea level"), then it ticks at exactly the same
rate as TT. Terrestrial time was approximately in sync with UT during 1900.
Since then, due to the retardation of the Earth rotation, ET has drifted ahead
of UT by a continually increasing amount.

International Atomic Time (TAI) is the weighted average of many atomic clocks,
and can be considered to be a perfect count of seconds with no breaks or changes
in rate. To take into account general and special relativity, the time scale
increases by 1 second every proper second on the Earth geoid. If there were a
perfect atomic clock operating at exactly sea level, it would count the
exact standard number of Cesium vibrations during each TAI second. TAI was
set to match UT at its conventional origin on 1958-01-01. Over the 58 years from
1900 to 1958, UT had retarded a total of about 32s, so ET was ahead of UT (and
therefore TAI) by that amount. Since that time, ET and TAI have been in
perfect lockstep, and in 1976, the difference between the two timescales
was estimated to be 32.184s. We say estimate because no atomic clocks existed
in 1900, and it is difficult but just barely possible to pull millisecond-level
precision from astronomincal observations from then. After 1976, the difference
between ET and TAI was defined to be 32.184s by convention. TAI is practically
available. Each clock used in the weighted average is tracked so that its
difference from the ensemble TAI is known, and each weight and offset is
adjusted once a month. For users who want to use TAI but don't have a tracked
atomic clock, the scale is also available by radio broadcast. The WWV broadcast
has always been based on a clock which is traceable to TAI. GPS time is also
traceable to TAI. So in practice, a GPS receiver can emit PPS pulses and
timestamps which are aligned to TAI to within a tiny fraction of a second.

Coordinated Universal Time (UTC, GMT before about 1967), is the most accessable
time scale, as it is the time scale used in almost all radio broadcasts. All mere
mortals who don't maintain a timekeeping laboratory with a roomful of atomic clocks
ultimately use UTC as their reference. Civil time (Time zones) in the United States
have been defined to be different from GMT/UTC by an exact integer number of hours.
Despite its name, is *not* related to UT. It is an atomic time scale which attempts
to straddle the difference between a nearly-perfect atomic time scale and the actual
rotation of the Earth. From 1961 through 1972, the difference between TAI and GMT/UTC
was tracked as a linear function of the julian date. During this era, the difference
had both an offset and a slope. The length of the GMT/UTC second is therefore *not
the same* as the length of a TAI second. The length of a GMT/UTC second is dependent
on the derivative of the difference function, or in other words is dependent on the
slope term of the difference. We call this the "rubber second" era, and in all my
code, I refer to times in this era as GMT. After 1972, the powers-that-be gave up on
some of this straddling, and defined the difference between TAI and UTC to be an
integer number of seconds. This number of seconds is occasionally changed in order
to keep the top of the UTC second within 0.9s of the top of the UT second. The
change is implemented by inserting a second labeled 23:59:60 UTC on either the
last day of June or the last day of December. This second is referred to as a
"leap second". The system allows for a negative leap second by skipping 23:59:59,
but this has not yet occurred in practice. I consistently refer to time in this
"leap second" era as UTC.

Ranger was flown during the GMT era. Ranger 7 was timed with the WWV
time signal. Its exact time of impact was recorded at DSS-12 (Echo Station
in Goldstone, CA) on a strip chart recorder which measured the received
signal strength, along with the NASA time code from WWV.  I haven't seen
any reference yet which shows that the distance from WWV to DSS-12 was
accounted for in the timing -- WWV is 3545km from DSS-12, creating a
light-time delay of 11.825ms. The uncertainty on the impact time is given as
+20,-30ms. Interestingly, the difference between the two brackets is the same
order of magnitude as the light-time delay from WWV, so maybe other errors
swamp the propagation delay. Until I see otherwise, I am going to assume
that the engineers knew about and corrected for this propagation delay,
and that the given times are as if the propagation from WWV station
to DSS-12 was instantaneous.

"""
from collections import namedtuple
from datetime import datetime, tzinfo, timedelta, timezone

import numpy as np

_dt0 = datetime(year=2000, month=1, day=1, hour=12, minute=0, second=0, microsecond=0, tzinfo=None)
_jd0 = 2_451_545.0
_mjd0= 2_400_000.5


def calc_jd(dt:datetime)->float:
    """
    Calculate the JD of any datetime object in its own timezone
    :param dt: date time
    :return: julian day number
    """
    # Strip off any timezone information from the given time stamp.
    naive=dt.replace(tzinfo=None)
    # Calculate the JD as the number of days from the epoch, plus the
    # JD count on the epoch.
    return _jd0+(naive-_dt0).total_seconds()/86400.0


def calc_et(dt:datetime)->float:
    """
    Calculate the number of seconds from the J2000 epoch of any datetime object
    in its own timezone. If the time zone is TDB, this will be exactly the Spice
    ephemeris time count.

    :param dt: Datetime object. Will work for any time zone (or no time zone)
               but only produces a true Spice ET for datetime objects with the
               TDB time zone.
    :return: count of seconds after J2000. Will be negative for times before then.

    Usage:
    Given a time in any timezone, first convert it to TDB:
        dt_tdb=dt_utc.astimezone(tdb)
    Then, use this function to get spice
        et=calc_et(dt_tdb)
    """
    # Strip off any timezone information from the given time stamp.
    naive=dt.replace(tzinfo=None)
    # Calculate the JD as the number of days from the epoch, plus the
    # JD count on the epoch.
    return (naive-_dt0).total_seconds()


# Time conversion table, including rubber seconds. This covers the entire era of
# "rubber seconds" and the entire "leap second" era up to at least 2024-03. Each
# row has a start date, followed by a formula which gives the amount of time that
# the TAI time scale is *ahead* of the GMT/UTC time scale.
# This table is copied verbatim from https://maia.usno.navy.mil/ser7/tai-utc.dat
# as downloaded on 2024-03-10.
                # 0         1         2         3         4         5         6         7
                # 01234567890123456789012345678901234567890123456789012345678901234567890123456789
_tai_utc_dat = """ 1961 JAN  1 =JD 2437300.5  TAI-UTC=   1.4228180 S + (MJD - 37300.) X 0.001296 S
 1961 AUG  1 =JD 2437512.5  TAI-UTC=   1.3728180 S + (MJD - 37300.) X 0.001296 S
 1962 JAN  1 =JD 2437665.5  TAI-UTC=   1.8458580 S + (MJD - 37665.) X 0.0011232S
 1963 NOV  1 =JD 2438334.5  TAI-UTC=   1.9458580 S + (MJD - 37665.) X 0.0011232S
 1964 JAN  1 =JD 2438395.5  TAI-UTC=   3.2401300 S + (MJD - 38761.) X 0.001296 S
 1964 APR  1 =JD 2438486.5  TAI-UTC=   3.3401300 S + (MJD - 38761.) X 0.001296 S
 1964 SEP  1 =JD 2438639.5  TAI-UTC=   3.4401300 S + (MJD - 38761.) X 0.001296 S
 1965 JAN  1 =JD 2438761.5  TAI-UTC=   3.5401300 S + (MJD - 38761.) X 0.001296 S
 1965 MAR  1 =JD 2438820.5  TAI-UTC=   3.6401300 S + (MJD - 38761.) X 0.001296 S
 1965 JUL  1 =JD 2438942.5  TAI-UTC=   3.7401300 S + (MJD - 38761.) X 0.001296 S
 1965 SEP  1 =JD 2439004.5  TAI-UTC=   3.8401300 S + (MJD - 38761.) X 0.001296 S
 1966 JAN  1 =JD 2439126.5  TAI-UTC=   4.3131700 S + (MJD - 39126.) X 0.002592 S
 1968 FEB  1 =JD 2439887.5  TAI-UTC=   4.2131700 S + (MJD - 39126.) X 0.002592 S
 1972 JAN  1 =JD 2441317.5  TAI-UTC=  10.0       S + (MJD - 41317.) X 0.0      S
 1972 JUL  1 =JD 2441499.5  TAI-UTC=  11.0       S + (MJD - 41317.) X 0.0      S
 1973 JAN  1 =JD 2441683.5  TAI-UTC=  12.0       S + (MJD - 41317.) X 0.0      S
 1974 JAN  1 =JD 2442048.5  TAI-UTC=  13.0       S + (MJD - 41317.) X 0.0      S
 1975 JAN  1 =JD 2442413.5  TAI-UTC=  14.0       S + (MJD - 41317.) X 0.0      S
 1976 JAN  1 =JD 2442778.5  TAI-UTC=  15.0       S + (MJD - 41317.) X 0.0      S
 1977 JAN  1 =JD 2443144.5  TAI-UTC=  16.0       S + (MJD - 41317.) X 0.0      S
 1978 JAN  1 =JD 2443509.5  TAI-UTC=  17.0       S + (MJD - 41317.) X 0.0      S
 1979 JAN  1 =JD 2443874.5  TAI-UTC=  18.0       S + (MJD - 41317.) X 0.0      S
 1980 JAN  1 =JD 2444239.5  TAI-UTC=  19.0       S + (MJD - 41317.) X 0.0      S
 1981 JUL  1 =JD 2444786.5  TAI-UTC=  20.0       S + (MJD - 41317.) X 0.0      S
 1982 JUL  1 =JD 2445151.5  TAI-UTC=  21.0       S + (MJD - 41317.) X 0.0      S
 1983 JUL  1 =JD 2445516.5  TAI-UTC=  22.0       S + (MJD - 41317.) X 0.0      S
 1985 JUL  1 =JD 2446247.5  TAI-UTC=  23.0       S + (MJD - 41317.) X 0.0      S
 1988 JAN  1 =JD 2447161.5  TAI-UTC=  24.0       S + (MJD - 41317.) X 0.0      S
 1990 JAN  1 =JD 2447892.5  TAI-UTC=  25.0       S + (MJD - 41317.) X 0.0      S
 1991 JAN  1 =JD 2448257.5  TAI-UTC=  26.0       S + (MJD - 41317.) X 0.0      S
 1992 JUL  1 =JD 2448804.5  TAI-UTC=  27.0       S + (MJD - 41317.) X 0.0      S
 1993 JUL  1 =JD 2449169.5  TAI-UTC=  28.0       S + (MJD - 41317.) X 0.0      S
 1994 JUL  1 =JD 2449534.5  TAI-UTC=  29.0       S + (MJD - 41317.) X 0.0      S
 1996 JAN  1 =JD 2450083.5  TAI-UTC=  30.0       S + (MJD - 41317.) X 0.0      S
 1997 JUL  1 =JD 2450630.5  TAI-UTC=  31.0       S + (MJD - 41317.) X 0.0      S
 1999 JAN  1 =JD 2451179.5  TAI-UTC=  32.0       S + (MJD - 41317.) X 0.0      S
 2006 JAN  1 =JD 2453736.5  TAI-UTC=  33.0       S + (MJD - 41317.) X 0.0      S
 2009 JAN  1 =JD 2454832.5  TAI-UTC=  34.0       S + (MJD - 41317.) X 0.0      S
 2012 JUL  1 =JD 2456109.5  TAI-UTC=  35.0       S + (MJD - 41317.) X 0.0      S
 2015 JUL  1 =JD 2457204.5  TAI-UTC=  36.0       S + (MJD - 41317.) X 0.0      S
 2017 JAN  1 =JD 2457754.5  TAI-UTC=  37.0       S + (MJD - 41317.) X 0.0      S"""
_tai_utc_row = namedtuple("tai_utc_row", "jd_boundary,ofs,mjd_intercept,slope")
_tai_utc = [
    _tai_utc_row(jd_boundary  =float(row[17:26]),ofs  =float(row[37:48]),
                 mjd_intercept=float(row[60:66]),slope=float(row[70:78]))
    for row in _tai_utc_dat.split("\n")
]


def tai_utc(*,jd:float=None,dt:datetime=None)->timedelta:
    """
    Calculate the difference between TAI and GMT/UTC. This
    works both in the era of rubber seconds, and the leap
    second era.

    :param jd:
    :param dt:
    :return: Timedelta object describing difference between TAI
    and UTC on the given date.
    """
    if jd is None:
        jd=calc_jd(dt)
    # find correct row of table
    row_i=0
    while True:
        if row_i==len(_tai_utc)-1:
            break
        elif _tai_utc[row_i].jd_boundary <= jd < _tai_utc[row_i + 1].jd_boundary:
            break
        row_i+=1
    row=_tai_utc[row_i]
    mjd=jd-_mjd0
    return timedelta(microseconds=int(1_000_000*row.ofs+(mjd-row.mjd_intercept)*row.slope))


def tdt_tai(*,jd:float=None,dt:datetime=None)->timedelta:
    return timedelta(microseconds=32_184_000)


def tdb_tdt(*,jd:float=None,dt:datetime=None)->timedelta:
    if jd is None:
        jd=calc_jd(dt)
    T=(jd-_jd0)/36525
    g=2*np.pi*(357.528+35_999.050*T)/360.0
    TDB_TDT=0.001658*np.sin(g+0.0167*np.sin(g))
    return timedelta(microseconds=int(1_000_000*TDB_TDT))


class TAI(tzinfo):
    """
    Implement TAI as a proper time zone.
    """
    def dst(self, dt):
        # a fixed-offset class:  doesn't account for DST
        return timedelta(0)
    def utcoffset(self,dt:datetime)->timedelta:
        """

        :param dt: Date and time. If given a naive datetime object (no tzinfo)
                   then assume the time is GMT/UTC.
        :return: difference between UTC and TAI. Will have microsecond precision,
                 and a nonzero microsecond count during the era of rubber seconds.
        """
        return tai_utc(dt=dt)
    def tzname(self,dt:datetime)->str:
        return "TAI"


class TDT(tzinfo):
    """
    Implement Terrestrial Time (TDT) as a proper time zone.
    """
    def dst(self, dt):
        # a fixed-offset class:  doesn't account for DST
        return timedelta(0)
    def utcoffset(self,dt:datetime)->timedelta:
        """

        :param dt: Date and time. If given a naive datetime object (no tzinfo)
                   then assume the time is GMT/UTC.
        :return: difference between UTC and TDT. Will have microsecond precision,
                 and a nonzero microsecond count at all times.
        """
        return tai_utc(dt=dt)+tdt_tai(dt=dt)
    def tzname(self,dt:datetime)->str:
        return "TDT"


class TDB(tzinfo):
    """
    Implement Barycentric Dynamical Time (TDB) as a proper time zone.
    """
    def dst(self, dt):
        # a fixed-offset class:  doesn't account for DST
        return timedelta(0)
    def utcoffset(self,dt:datetime)->timedelta:
        """

        :param dt: Date and time. If given a naive datetime object (no tzinfo)
                   then assume the time is GMT/UTC.
        :return: difference between UTC and TDB. Will have microsecond precision.
        """
        return tai_utc(dt=dt)+tdt_tai(dt=dt)+tdb_tdt(dt=dt)
    def tzname(self,dt:datetime)->str:
        return "TDB"


tai=TAI()
tdt=TDT()
tdb=TDB()

