from datetime import datetime, date, time
from Kronos.periods import Periods
from Kronos.converters import Converters
from Kronos.costructors import Costructors, TimeZones, datetime_kronos


class Format:
    # valid iso for pandas format
    ISO = 'ISO8601'


class Core(Periods, Converters, Costructors):

    def __init__(self, dt=None, tz=TimeZones.rome, td=None):

        dt = datetime_kronos(dt, tz)

        self.dt = dt  # datetime
        self.td = td  # timedelta

    def __sub__(self, other):
        if self.td is None:
            if isinstance(other, str):  # kronos puo essere sottratto ad un isoformat
                td = self.dt - self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):  # kronost puo essere sottratto ad un datetime
                td = self.dt - self.from_datetime(other).dt
            elif isinstance(other, time):  # kronost puo essere sottratto ad un time
                td = self.dt - self.from_time(other).dt
            else:  # kronos puo essere sottratto ad un altro kronos
                td = self.dt - other.dt
            return self.__class__(td=td)

        else:
            td = self.td - other.td
            return self.__class__(td=td)

    def __add__(self, other):
        if self.td is None:
            if isinstance(other, str):
                td = self.dt + self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                td = self.dt + self.from_datetime(other).dt
            elif isinstance(other, time):
                td = self.dt + self.from_time(other).dt
            else:
                td = self.dt + other.dt
            return self.__class__(td=td)
        else:
            td = self.td + other.td
            return self.__class__(td=td)

    def __eq__(self, other):
        if self.td is None:
            if isinstance(other, str):
                return self.dt == self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                return self.dt == self.from_datetime(other).dt
            elif isinstance(other, time):
                return self.dt == self.from_time(other).dt
            else:
                return self.dt == other.dt
        else:
            return self.td == other.td

    def __le__(self, other):
        if self.td is None:
            if isinstance(other, str):
                return self.dt <= self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                return self.dt <= self.from_datetime(other).dt
            elif isinstance(other, time):
                return self.dt <= self.from_time(other).dt
            else:
                return self.dt <= other.dt
        else:
            return self.td <= other.td

    def __lt__(self, other):
        if self.td is None:
            if isinstance(other, str):
                return self.dt < self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                return self.dt < self.from_datetime(other).dt
            elif isinstance(other, time):
                return self.dt < self.from_time(other).dt
            else:
                return self.dt < other.dt
        else:
            return self.td < other.td

    def __ge__(self, other):
        if self.td is None:
            if isinstance(other, str):
                return self.dt >= self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                return self.dt >= self.from_datetime(other).dt
            elif isinstance(other, time):
                return self.dt >= self.from_time(other).dt
            else:
                return self.dt >= other.dt
        else:
            return self.td >= other.td

    def __gt__(self, other):
        if self.td is None:
            if isinstance(other, str):
                return self.dt > self.from_iso(other).dt
            elif isinstance(other, datetime) or isinstance(other, date):
                return self.dt > self.from_datetime(other).dt
            elif isinstance(other, time):
                return self.dt > self.from_time(other).dt
            else:
                return self.dt > other.dt
        else:
            return self.td > other.td

    def __repr__(self):
        if self.td is None:
            return self.dt.__repr__()
        else:
            return self.td.__repr__()

    def __str__(self):
        if self.td is None:
            return self.dt.__str__()
        else:
            return self.td.__str__()

    def __hash__(self):
        if self.td is None:
            return self.dt.__hash__()
        else:
            return self.td.__hash__()
