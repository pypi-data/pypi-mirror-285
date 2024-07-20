from typing import List
from datetime import timezone, timedelta, datetime, date, time
from Kronos.sliders import sliders


def datetime_kronos(dt, tz):
    if not isinstance(dt, datetime) and not isinstance(dt, date) and not isinstance(dt, time) and dt is not None:
        raise ValueError('dt inserted is not a datetime or date or time')

    if isinstance(tz, str): tz = TimeZones.dict_zones[tz]

    if type(dt) == date and dt is not None:  # permette di identificare le date, senza prendere i datetime
        # le date vengono trasformate in datetime senza tz, che viene aggiunta dopo
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0, microsecond=0)

    if type(dt) == time and dt is not None:  # permette di identificare le time
        # le time vengono trasformate in datetime
        if dt.tzinfo is None:
            dt = datetime(2000, 10, 10, dt.hour, dt.minute, dt.second, dt.microsecond)
        else:
            dt = datetime(2000, 10, 10, dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=dt.tzinfo)

    if isinstance(dt, datetime):  # serve per leggere i datetime
        if dt.tzinfo is None:
            if tz is None:
                tz = TimeZones(dt).rome
            dt = dt.replace(tzinfo=tz)
    return dt


class TimeZones:
    utc = timezone.utc
    rome = timezone(timedelta(hours=1))  # time zone invernale o solare
    rome_legal = timezone(timedelta(hours=2))  # timezone estiva o legale

    # +2 tra le 2:00 del mattino dell'ultima domenica di marzo e le 3:00 del mattino dell'ultima domenica di ottobre
    # +1 le 3:00 del mattino dell'ultima domenica di ottobre e le 2:00 del mattino dell'ultima domenica di marzo
    dict_zones = {'utc': utc, 'rome': rome, 'rome_legal': rome_legal}

    def __init__(self, now: datetime = datetime.now()):
        weekday_last_day_of_march = datetime(year=now.year, month=3, day=31).weekday()
        last_sun_of_march = datetime(year=now.year, month=3, day=31 - (weekday_last_day_of_march + 1), hour=2)

        weekday_last_day_of_oct = datetime(year=now.year, month=10, day=31).weekday()
        last_sun_of_oct = datetime(year=now.year, month=10, day=31 - (weekday_last_day_of_oct + 1), hour=3)

        is_legal = last_sun_of_march < now < last_sun_of_oct
        if is_legal:
            # rome
            self.rome = self.rome_legal
            self.dict_zones['rome'] = self.rome_legal


class Costructors(sliders):

    def __init__(self, dt=None, tz=None, td=None):

        dt = datetime_kronos(dt, tz)

        self.dt = dt  # datetime
        self.td = td  # timedelta

    @classmethod
    def now(cls, tz=None):
        """
        Produce the current datetime

        Args:
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]
        return cls(datetime.now(), tz=tz)

    @classmethod
    def today(cls, tz=None):
        """
        Produce the current day
        Args:
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]
        return cls.now(tz).start_of_day()

    @classmethod
    def primetime(cls, year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tz=None):
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
        return cls(datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                            microsecond=microsecond), tz=tz)

    @classmethod
    def from_isoformat(cls, iso: str, tz=None):
        """
        Convert isoformat string to Kronos
        Args:
            iso (str): isoformat string
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]
        try:
            dt = datetime.fromisoformat(iso)
            return cls(dt, tz=tz)
        except:
            t = time.fromisoformat(iso)
            return cls(t, tz=tz)


    @classmethod
    def from_iso(cls, iso, tz=None):
        """
        Convert isoformat string to Kronos
        Args:
            iso (str): isoformat string
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        return cls.from_isoformat(iso, tz)

    @classmethod
    def from_timestamp(cls, timestamp, tz=None):
        """
        convert a timestamp to Kronos
        Args:
            timestamp (int): timestamp
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]
        dt = datetime.fromtimestamp(timestamp, tz=TimeZones.utc)
        if tz is not None: dt = dt.astimezone(tz=tz)
        return cls(dt)

    @classmethod
    def from_ts(cls, timestamp, tz=None):
        """
        convert a timestamp to Kronos
        Args:
            timestamp (int): timestamp
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        return cls.from_timestamp(timestamp, tz)

    @classmethod
    def from_datetime(cls, dt: [datetime, date], tz=None):
        """
        convert a datetime or date to Kronos

        Args:
            dt (datetime, date):
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]
        if tz is None: tz = TimeZones.rome
        return cls(dt, tz=tz)

    @classmethod
    def from_dt(cls, dt: [datetime, date], tz=None):
        """
        convert a datetime or date to Kronos

        Args:
            dt (datetime, date):
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        cls.from_datetime(dt, tz=tz)

    @classmethod
    def from_timedelta(cls, td: [timedelta]):
        """
        convert a timedelta to Kronos

        Args:
            td (timedelta):

        Returns: Kronos
        """
        return cls(td=td)

    @classmethod
    def from_td(cls, td: [timedelta]):
        """
        convert a timedelta to Kronos

        Args:
            td (timedelta):

        Returns: Kronos
        """
        return cls(td=td)

    @classmethod
    def from_time(cls, t: [time], tz=None):
        """
        convert a timedelta to Kronos

        Args:
            t (time):
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        return cls(t, tz=tz)

    @classmethod
    def from_format(cls, string: str, format: str, tz=None):
        """
        convert a string with a given format to Kronos

        Args:
            string (str): string with a date
            format (str): format of the string
            tz: Timezone. Default to Rome

        Returns: Kronos
        """
        return cls(datetime.strptime(string, format), tz=tz)

    @classmethod
    def from_list_iso_to_datetime(cls, list_iso: List[str], tz=None):
        """
        convert a list of string with isoformat into a list of datetime
        Args:
            list_iso (list[str]): list of isoformat string
            tz: Timezone. Default to Rome

        Returns: list[datetime]
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]

        def iso_datetime(iso):
            return cls.from_iso(iso, tz).dt

        return list(map(iso_datetime, list_iso))

    @classmethod
    def from_list_iso(cls, list_iso, tz=None):
        """
        convert a list of string with isoformat into a list of Kronos
        Args:
            list_iso (list[str]): list of isoformat string
            tz: Timezone. Default to Rome

        Returns: list[Kronos]
        """
        if isinstance(tz, str): tz = TimeZones.dict_zones[tz]

        def iso_kronos(iso):
            return cls.from_iso(iso, tz)

        return list(map(iso_kronos, list_iso))
