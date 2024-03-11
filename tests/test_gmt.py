import pytest

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from gmt import calc_jd, tai, tdb, tdt

@pytest.mark.parametrize(
    "year,month,day,hour,minute,second,microsecond,tzinfo,jd",
    [(1995,10, 9,12, 0, 0,     0,timezone.utc,2_450_000.0),
     (1995,10, 9,12, 0, 0,     0,ZoneInfo("America/Denver"),2_450_000.0),
     (1995,10, 9,12, 0, 0,     0,tai,2_450_000.0),
     (1995,10, 9,12, 0, 0,     0,tdb,2_450_000.0),
     (1995,10, 9,12, 0, 0,     0,tdt,2_450_000.0),
     (1995,10, 9,12, 0, 0,     0,None,2_450_000.0),
     ]
)
def test_calc_jd(year,month,day,hour,minute,second,microsecond,tzinfo,jd):
    assert calc_jd(datetime(year=year,month=month,day=day,
                            hour=hour,minute=minute,second=second,microsecond=microsecond,
                            tzinfo=tzinfo))==jd


def test_TAI():
    # naive datetime
    ndt=datetime(year=1995,month=10,day=9,hour=12,minute=0,second=0)
    # This just slaps the UTC timezone on it and doesn't change anything
    udt=datetime(year=1995,month=10,day=9,hour=12,minute=0,second=0,tzinfo=timezone.utc)
    taidt=udt.astimezone(tai)
    udt_rt=taidt.astimezone(timezone.utc)
    taidt=datetime(year=1995,month=10,day=9,hour=12,minute=0,second=0,tzinfo=tai)
    # Ranger 7 lunar impact
    gmt_r7imp=datetime(year=1964,month=7,day=31,hour=13,minute=25,second=48,microsecond=799000,tzinfo=timezone.utc)
    tai_r7imp=gmt_r7imp.astimezone(tai)
    tdt_r7imp=gmt_r7imp.astimezone(tdt)
    tdb_r7imp=gmt_r7imp.astimezone(tdb)
    gmt_r7imp_rt=tai_r7imp.astimezone(timezone.utc)
    print(gmt_r7imp)
    print(tai_r7imp)
    print(tdt_r7imp)
    print(tdb_r7imp)
    print(gmt_r7imp_rt)