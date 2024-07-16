import zoneinfo
from datetime import datetime, date, time, timedelta
from typing import Union

from nsanic.libs.consts import GLOBAL_TZ


MONTH_MAP = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def check_tz(tz: Union[str, zoneinfo.ZoneInfo] = None):
    if tz and isinstance(tz, str):
        return zoneinfo.ZoneInfo(tz)
    return tz if tz else zoneinfo.ZoneInfo(GLOBAL_TZ)


def check_leap(year: int):
    """检查年份是否是闰年"""
    return (year % 4) if (not year % 100) else (year % 400)


def get_month_days(year: int, month: int):
    if check_leap(year) and month == 2:
        return 29
    return MONTH_MAP.get(month)


def cur_dt(tz: Union[str, zoneinfo.ZoneInfo] = None):
    """当前日期"""
    return datetime.now(tz=check_tz(tz))


def cur_time(ms=False, tz: Union[str, zoneinfo.ZoneInfo] = None):
    """当前时间戳"""
    t = cur_dt(tz=tz).timestamp()
    return int(t * 1000) if ms else int(t)


def dt_str(dt: Union[datetime, date, int, float, str] = None,
           fmt='%Y-%m-%d %H:%M:%S',
           tz: Union[str, zoneinfo.ZoneInfo] = None):
    """日期时间字符串格式输出, 不指定时间将输出当前时间"""
    if not dt:
        return cur_dt(tz=tz).strftime(fmt)
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    elif isinstance(dt, date):
        fmt = (fmt.replace('%H:', '').replace('%H', '').replace('%M:', '').
               replace('%M', '')).replace('%S.', '').replace('%S', '').replace('%f', '')
        return dt.strftime(fmt)
    elif isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt, tz=check_tz(tz))
        return dt.strftime(fmt)
    elif isinstance(dt, str):
        dt.replace('/', '-').replace('T', ' ')
        if len(dt) > 10:
            return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').strftime(fmt)
        return datetime.strptime(dt, '%Y-%m-%d').strftime(fmt)


def to_datetime(dt: Union[date, datetime, str, int, float],
                fmt='%Y-%m-%d %H:%M:%S',
                tz: Union[str, zoneinfo.ZoneInfo] = None):
    if dt is None:
        return
    if isinstance(dt, str):
        dt = datetime.strptime(dt, fmt)
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, date):
        return datetime.combine(dt, time(), tzinfo=check_tz(tz))
    elif isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt, tz=check_tz(tz))
    return


def create_dt(
        year=2023,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        misecond=0,
        tz: Union[str, zoneinfo.ZoneInfo] = None):
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=misecond,
                    tzinfo=check_tz(tz))


def day_begin(dt: Union[datetime, date] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not dt:
        dt = cur_dt(tz)
    if isinstance(dt, datetime):
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(dt.timestamp())
    return int(datetime.combine(dt, time(), tzinfo=check_tz(tz)).timestamp())


def day_end(dt: Union[datetime, date] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not dt:
        dt = cur_dt(tz)
    if isinstance(dt, date):
        dt = datetime.combine(dt, time(), tzinfo=check_tz(tz))
    dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return int(dt.timestamp())


def month_begin(dt: Union[datetime, date] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not dt:
        dt = cur_dt(tz)
    if isinstance(dt, datetime):
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return int(dt.timestamp())
    ndt = datetime.combine(dt, time(), tzinfo=check_tz(tz))
    ndt.replace(day=1)
    return int(ndt.timestamp())


def get_day_interval(dt: Union[datetime, date, int, float] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not dt:
        dt = cur_dt(tz)
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt, tz=check_tz(tz))
    if isinstance(dt, date):
        dt = datetime.combine(dt, time(), tzinfo=check_tz(tz))
    s_dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    e_dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return int(s_dt.timestamp()), int(e_dt.timestamp())


def get_day_hours(dt: Union[datetime, date, int, float] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    st, et = get_day_interval(dt, tz=tz)
    hour_list = []
    start = st
    for i in range(st, et, 3600):
        end = start + 3600 - 1
        if end >= et:
            end = et
        hour_list.append((start, end))
        start = end + 1
    return hour_list


def date_range(start: Union[datetime, date],
               end: Union[datetime, date] = None,
               tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not end:
        end = cur_dt(tz).date()
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()
    delta = end - start
    m_date = min(start, end)
    return [m_date + timedelta(days=i) for i in range(abs(delta.days) + 1)]


def get_date_arr(days: int, set_date: Union[datetime, date] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not set_date:
        set_date = cur_dt(tz).date()
    else:
        if isinstance(set_date, datetime):
            set_date = set_date.date()
    return [(set_date - timedelta(days=days - 1 - i)) for i in range(days)]


def get_day_before(days: int, set_date: Union[datetime, date] = None, tz: Union[str, zoneinfo.ZoneInfo] = None):
    if not set_date:
        set_date = cur_dt(tz)
    return set_date - timedelta(days)
