from Kronos.hourglass import Core, TimeZones, Format, Converters


def now(tz=None):
    """
    Produce the current datetime

    Args:
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.now(tz=tz)


def today(tz=None):
    """
    Produce the current day
    Args:
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.today(tz=tz)


def primetime(year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tz=None):
    """
    Procude the Kronos element of the specified date

    Args:
        year (int): year
        month (int): month
        day (int): day
        hour (int): hour
        minute (int): minute
        second (int): second
        microsecond (int): microsecond
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.primetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tz=tz)


def from_isoformat(iso, tz=None):
    """
    Convert isoformat string to Kronos
    Args:
        iso (str): isoformat string
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_isoformat(iso=iso, tz=tz)


def from_iso(iso, tz=None):
    """
    Convert isoformat string to Kronos
    Args:
        iso (str): isoformat string
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_iso(iso=iso, tz=tz)


def from_timestamp(timestamp, tz=None):
    """
    convert a timestamp to Kronos
    Args:
        timestamp (int): timestamp
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_timestamp(timestamp=timestamp, tz=tz)


def from_ts(timestamp, tz=None):
    """
    convert a timestamp to Kronos
    Args:
        timestamp (int): timestamp
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_ts(timestamp=timestamp, tz=tz)


def from_datetime(dt, tz=None):
    """
    convert a datetime or date to Kronos

    Args:
        dt (datetime, date):
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_datetime(dt=dt, tz=tz)


def from_dt(dt, tz=None):
    """
    convert a datetime or date to Kronos

    Args:
        dt (datetime, date):
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_dt(dt=dt, tz=tz)


def from_timedelta(td):
    """
    convert a timedelta to Kronos

    Args:
        td (timedelta):

    Returns: Kronos
    """
    return Core.from_timedelta(td)


def from_td(td):
    """
    convert a timedelta to Kronos

    Args:
        td (timedelta):

    Returns: Kronos
    """
    return Core.from_td(td)


def from_time(t, tz=None):
    return Core.from_time(t, tz=tz)


def from_format(string: str, format: str, tz=None):
    """
    convert a string with a given format to Kronos

    Args:
        string (str): string with a date
        format (str): format of the string
        tz: Timezone. Default to Rome

    Returns: Kronos
    """
    return Core.from_format(string=string, format=format, tz=tz)


def from_list_iso_to_datetime(list_iso, tz=None):
    """
    convert a list of string with isoformat into a list of datetime
    Args:
        list_iso (list[str]): list of isoformat string
        tz: Timezone. Default to Rome

    Returns: list[datetime]
    """
    return Core.from_list_iso_to_datetime(list_iso=list_iso, tz=tz)


def from_list_iso(list_iso, tz=None):
    """
    convert a list of string with isoformat into a list of Kronos
    Args:
        list_iso (list[str]): list of isoformat string
        tz: Timezone. Default to Rome

    Returns: list[Kronos]
    """
    return Core.from_list_iso(list_iso=list_iso, tz=tz)

#
# def move_tz_from_list(list_old_tz, tz=None):
#     """
#     modify the time accordingly to a new timezone for a list of Kronos
#     Args:
#         list_old_tz (list[str]): list of Kronos
#         tz: Timezone. Default to Rome
#
#     Returns: list[Kronos]
#     """
#     return Converters.move_tz_from_list(list_old_tz=list_old_tz, tz=tz)
