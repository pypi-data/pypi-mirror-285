from __future__ import annotations
import datetime as dt
from typing import Union

from .. import dsl

# Custom types
_Date = Union[dt.date, dsl.Producer]
_DateTime = Union[dt.datetime, dsl.Producer]
_Integer = Union[int, dsl.Producer]
_String = Union[str, dsl.Producer]

# NOTE: Right now, common contains all Rel stdlib relations.
# If the stdlib is split into multiple namespaces, this will have to be updated.
_date_ns = dsl.global_ns.std.common

#--------------------------------------------------
# Types
#--------------------------------------------------

Date = _date_ns.Date
DateTime = _date_ns.DateTime


#--------------------------------------------------
# Constructors
#--------------------------------------------------

_make_date = getattr(_date_ns, "^Date")
_make_datetime = getattr(_date_ns, "^DateTime")

def _date(year: _Integer, month: _Integer, day: _Integer) -> dsl.Expression:
    return _make_date(year, month, day)

def _date_fromordinal(ordinal: _Integer) -> dsl.Expression:
    return _make_date(ordinal)

def _date_fromdatetime(datetime: _DateTime, tz: dt.tzinfo | _String | None = None) -> dsl.Expression:
    if tz is None:
        if isinstance(datetime, dt.datetime):
            tz = datetime.tzname() or "UTC"
        else:
            tz = "UTC"
    return _make_date(datetime, tz)

date = _date
date.fromordinal = _date_fromordinal
date.fromdatetime = _date_fromdatetime

def _datetime(
        year: _Integer,
        month: _Integer,
        day: _Integer,
        hour: _Integer = 0,
        minute: _Integer = 0,
        second: _Integer = 0,
        millisecond: _Integer = 0,
        tz: dt.tzinfo | _String = "UTC"
) -> dsl.Expression:
    if isinstance(tz, dt.tzinfo):
        tz = str(tz)
    return _make_datetime(year, month, day, hour, minute, second, millisecond, tz)

def _datetime_fromordinal(ordinal: _Integer) -> dsl.Expression:
    # Convert ordinal to milliseconds, since ordinals in Python are days but RAI DateTime expects milliseconds.
    ordinal_milliseconds = ordinal * 24 * 60 * 60 * 1000
    return _make_datetime(ordinal_milliseconds)

def _datetime_fromdate(
    date: _Date,
    hour: _Integer = 0,
    minute: _Integer = 0,
    second: _Integer = 0,
    millisecond: _Integer = 0,
    tz: _String = "UTC"
) -> dsl.Expression:
    return _make_datetime(date, hour, minute, second, millisecond, tz)

datetime = _datetime
datetime.fromordinal = _datetime_fromordinal
datetime.fromdate = _datetime_fromdate

#--------------------------------------------------
# Arithmetic
#--------------------------------------------------

def _date_dispatch(model: dsl.Graph, method: str, date: _Date | _DateTime, period: dsl.Producer) -> dsl.Expression:
    with model.match() as matched:
        with Date(date):
            matched.add(getattr(_date_ns,f"date_{method}")(date, period))
        with DateTime(date):
            matched.add(getattr(_date_ns, f"datetime_{method}")(date, period))
    return matched

def date_add(date: _Date | _DateTime, period: dsl.Producer) -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime, dsl.Producer)):
        return _date_dispatch(dsl.get_graph(), "add", date, period)
    else:
        raise TypeError(f"date_add expects a date or datetime, got {type(date)}: {date!r}")

def date_subtract(date: _Date | _DateTime, period: dsl.Producer) -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime, dsl.Producer)):
        return _date_dispatch(dsl.get_graph(), "subtract", date, period)
    else:
        raise TypeError(f"date_subtract expects a date or datetime, got {type(date)}: {date!r}")

#--------------------------------------------------
# Date Parts
#--------------------------------------------------

def year(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.year
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _year:
            with Date(date):
                _year.add(_date_ns.date_year(date))
            with DateTime(date):
                _year.add(_date_ns.datetime_year(date, tz))
        return _year
    else:
        raise TypeError(f"year expects a date or datetime, got {type(date)}: {date!r}")


def month(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.month
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _month:
            with Date(date):
                _month.add(_date_ns.date_month(date))
            with DateTime(date):
                _month.add(_date_ns.datetime_month(date, tz))
        return _month
    else:
        raise TypeError(f"month expects a date or datetime, got {type(date)}: {date!r}")


def day(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.day
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _day:
            with Date(date):
                _day.add(_date_ns.date_day(date))
            with DateTime(date):
                _day.add(_date_ns.datetime_day(date, tz))
        return _day
    else:
        raise TypeError(f"day expects a date or datetime, got {type(date)}: {date!r}")

def hour(date: _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, dt.datetime):
        return date.hour
    elif isinstance(date, dsl.Producer):
        return _date_ns.datetime_hour(date, tz)
    else:
        raise TypeError(f"hour expects a datetime, got {type(datetime)}: {datetime!r}")

def minute(date: _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, dt.datetime):
        return date.minute
    elif isinstance(date, dsl.Producer):
        return _date_ns.datetime_minute(date, tz)
    else:
        raise TypeError(f"minute expects a datetime, got {type(datetime)}: {datetime!r}")

def second(date: _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, dt.datetime):
        return date.second
    elif isinstance(date, dsl.Producer):
        return _date_ns.datetime_second(date)
    else:
        raise TypeError(f"second expects a datetime, got {type(datetime)}: {datetime!r}")

def week(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.isocalendar()[1]
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _week:
            with Date(date):
                _week.add(_date_ns.date_week(date))
            with DateTime(date):
                _week.add(_date_ns.datetime_week(date, tz))
        return _week
    else:
        raise TypeError(f"week expects a date or datetime, got {type(date)}: {date!r}")

def quarter(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return (date.month - 1) // 3 + 1
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _quarter:
            with Date(date):
                _quarter.add(_date_ns.date_quarterofyear(date))
            with DateTime(date):
                _quarter.add(_date_ns.datetime_quarterofyear(date, tz))
        return _quarter
    else:
        raise TypeError(f"quarter expects a date or datetime, got {type(date)}: {date!r}")

def weekday(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.weekday()
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _weekday:
            with Date(date):
                _weekday.add(_date_ns.date_dayofweek(date))
            with DateTime(date):
                _weekday.add(_date_ns.datetime_dayofweek(date, tz))
        return _weekday - 1  # Rel uses Monday=1, Python uses Monday=0
    else:
        raise TypeError(f"weekday expects a date or datetime, got {type(date)}: {date!r}")

def isoweekday(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.isoweekday()
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _isoweekday:
            with Date(date):
                _isoweekday.add(_date_ns.date_dayofweek(date))
            with DateTime(date):
                _isoweekday.add(_date_ns.datetime_dayofweek(date, tz))
        return _isoweekday
    else:
        raise TypeError(f"isoweekday expects a date or datetime, got {type(date)}: {date!r}")

def dayofyear(date: _Date | _DateTime, tz: _String = "UTC") -> dsl.Expression:
    if isinstance(date, (dt.date, dt.datetime)):
        return date.timetuple().tm_yday
    elif isinstance(date, dsl.Producer):
        model = dsl.get_graph()
        with model.match() as _yearday:
            with Date(date):
                _yearday.add(_date_ns.date_dayofyear(date))
            with DateTime(date):
                _yearday.add(_date_ns.datetime_dayofyear(date, tz))
        return _yearday
    else:
        raise TypeError(f"yearday expects a date or datetime, got {type(date)}: {date!r}")

#--------------------------------------------------
# Periods
#--------------------------------------------------

nanoseconds = getattr(_date_ns, "^Nanosecond")
microseconds = getattr(_date_ns, "^Microsecond")
milliseconds = getattr(_date_ns, "^Millisecond")
seconds = getattr(_date_ns, "^Second")
minutes = getattr(_date_ns, "^Minute")
hours = getattr(_date_ns, "^Hour")
days = getattr(_date_ns, "^Day")
weeks = getattr(_date_ns, "^Week")
months = getattr(_date_ns, "^Month")
years = getattr(_date_ns, "^Year")

def date_range(start: _Date | _DateTime | None = None, end: _Date | _DateTime | None = None, periods: int = 1, freq: str = "D") -> dsl.Expression:
    model = dsl.get_graph()
    period = {
        "us": microseconds,
        "ms": milliseconds,
        "s": seconds,
        "m": minutes,
        "H": hours,
        "D": days,
        "W": weeks,
        "M": months,
        "Y": years,
    }
    days2 = {
        "us": 86_400_000_000,
        "ms": 86_400_000,
        "s": 86_400,
        "m": 1440,
        "H": 24,
        "D": 1,
        "W": 1/7,
        "M": 1/(365/12),
        "Y": 1/365,
    }
    milliseconds2 = {
        "us": 1_000,
        "ms": 1,
        "s": 1/1_000,
        "m": 1/60_000,
        "H": 1/3_600_000,
        "D": 1/86_400_000,
        "W": 1/(86_400_000*7),
        "M": 1/(86_400_000*(365/12)),
        "Y": 1/(86_400_000*365),
    }
    date_func = date_add
    if start is None:
        start = end
        end = None
        date_func = date_subtract
    with model.match() as matched:
        with Date(start):
            if end is not None:
                num_days = dsl.rel.pyrel_dates_period_days(start, end)
                if freq in ["W", "M", "Y"]:
                    range_end = dsl.rel.float_int_convert(dsl.rel.ceil(num_days * days2[freq]))
                else:
                    range_end = num_days * days2[freq]
                ix = dsl.global_ns.std.common.range(0, range_end, 1)
            else:
                ix = dsl.global_ns.std.common.range(0, periods-1, 1)
            # if the frequency is less than a day, cast the dates to datetimes
            if freq in ["us", "ms", "s", "m", "H"]:
                _start = datetime.fromdate(start)
                if end is not None:
                    _end = datetime.fromdate(end)
            else:
                _start = start
                if end is not None:
                    _end = end
            _date = date_func(_start, period[freq](ix))
            if end is not None:
                _date <= _end
            matched.add(_date)
        with DateTime(start):
            if end is not None:
                num_ms = dsl.rel.pyrel_datetimes_period_milliseconds(start, end)
                if freq not in ["us", "ms"]:
                    _end = dsl.rel.float_int_convert(dsl.rel.ceil(num_ms * milliseconds2[freq]))
                else:
                    _end = num_ms * milliseconds2[freq]
                ix = dsl.global_ns.std.common.range(0, _end, 1)
            else:
                ix = dsl.global_ns.std.common.range(0, periods-1, 1)
            _date = date_func(start, period[freq](ix))
            if end is not None:
                _date <= end
            matched.add(_date)
    return matched

#--------------------------------------------------
# Exports
#--------------------------------------------------

__all__ = [
    "Date",
    "date",
    "DateTime",
    "datetime",
    "date_add",
    "date_subtract",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "week",
    "quarter",
    "weekday",
    "isoweekday",
    "dayofyear",
    "nanoseconds",
    "microseconds",
    "milliseconds",
    "seconds",
    "minutes",
    "hours",
    "days",
    "weeks",
    "months",
    "years",
    "date_range",
]