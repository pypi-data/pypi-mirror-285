from typing import Literal
from math import copysign
from datetime import datetime, date, timedelta

# The month lengths in non-leap and leap years respectively.
DAYS_PER_MONTHS = (
    (-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    (-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
)


class sliders:

    def __init__(self, dt=None):
        self.dt = dt

    def start_of(self, period: Literal['minute', 'hour', 'day', 'week', 'month', 'year'] = 'day'):
        """
        function that set to the start of the selected period
        """
        if period in 'minutes':
            dt = self.dt.replace(second=0, microsecond=0)
        elif period in 'hours':
            dt = self.dt.replace(minute=0, second=0, microsecond=0)
        elif period in 'days':
            dt = self.dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period in 'weeks':
            if (self.dt.day - self.dt.weekday()) < 1:
                month = self.dt.month - 1
                year = self.dt.year
                if month < 1:
                    month = 12
                    year = self.dt.year - 1
                day = DAYS_PER_MONTHS[int(_is_leap(year))][month] - (self.dt.weekday() - self.dt.day)
            else:
                day = self.dt.day - self.dt.weekday()
                month = self.dt.month
                year = self.dt.year
            dt = self.dt.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
        elif period in 'months':
            dt = self.dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period in 'years':
            dt = self.dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise NotImplementedError
        return self.__class__(dt)

    def start_of_minute(self):
        """
        set to the start of the selected minut
        """
        return self.start_of('minute')

    def start_of_hour(self):
        """
        set to the start of the selected hour
        """
        return self.start_of('hour')

    def start_of_day(self):
        """
        set to the start of the selected day
        """
        return self.start_of('day')

    def start_of_week(self):
        """
        set to the start of the selected week
        """
        return self.start_of('week')

    def start_of_month(self):
        """
        set to the start of the selected month
        """
        return self.start_of('month')

    def start_of_year(self):
        """
        set to the start of the selected year
        """
        return self.start_of('year')

    def end_of(self, period: Literal['minute', 'hour', 'day', 'week', 'month', 'year'] = 'day'):
        """
        function that set to the end of the selected period
        """
        if period in 'minutes':
            dt = self.dt.replace(second=59, microsecond=0)
        elif period in 'hours':
            dt = self.dt.replace(minute=59, second=59, microsecond=0)
        elif period in 'days':
            dt = self.dt.replace(hour=23, minute=59, second=59, microsecond=0)
        elif period in 'weeks':
            delta = 6 - self.dt.weekday()  # trasformo lunedi in 6 e domenica in 0 e poi calcolo qual'è il giorno di arrivo con day + delta
            if (self.dt.day + delta) > DAYS_PER_MONTHS[int(_is_leap(self.dt.year))][self.dt.month]:
                to_end_month = DAYS_PER_MONTHS[int(_is_leap(self.dt.year))][self.dt.month] - self.dt.day
                day = delta - to_end_month
                month = self.dt.month + 1
                year = self.dt.year
                if month > 12:
                    month = 1
                    year = self.dt.year + 1
            else:
                day = self.dt.day + delta
                month = self.dt.month
                year = self.dt.year
            dt = self.dt.replace(year=year, month=month, day=day, hour=23, minute=59, second=59, microsecond=0)
        elif period in 'months':
            dt = self.dt.replace(day=DAYS_PER_MONTHS[int(_is_leap(self.dt.year))][self.dt.month], hour=23, minute=59, second=59,
                                 microsecond=0)
        elif period in 'years':
            dt = self.dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
        else:
            raise NotImplementedError
        return self.__class__(dt)

    def end_of_minute(self):
        """
        set to the end of the selected minute
        """
        return self.end_of('minute')

    def end_of_hour(self):
        """
        set to the end of the selected hour
        """
        return self.end_of('hour')

    def end_of_day(self):
        """
        set to the end of the selected day
        """
        return self.end_of('day')

    def end_of_week(self):
        """
        set to the end of the selected week
        """
        return self.end_of('week')

    def end_of_month(self):
        """
        set to the end of the selected month
        """
        return self.end_of('month')

    def end_of_year(self):
        """
        set to the end of the selected year
        """
        return self.end_of('year')

    def add_duration(self,
                     years=0,
                     months=0,
                     weeks=0,
                     days=0,
                     hours=0,
                     minutes=0,
                     seconds=0,
                     microseconds=0):

        """
        Adds a duration to a kronos instance.
        """
        days += weeks * 7

        if (
                isinstance(self.dt, date)
                and not isinstance(self.dt, datetime)
                and any([hours, minutes, seconds, microseconds])
        ):
            raise RuntimeError("Time elements cannot be added to a date instance.")

        # Normalizing
        if abs(microseconds) > 999999:
            s = _sign(microseconds)
            div, mod = divmod(microseconds * s, 1000000)
            microseconds = mod * s
            seconds += div * s

        if abs(seconds) > 59:
            s = _sign(seconds)
            div, mod = divmod(seconds * s, 60)
            seconds = mod * s
            minutes += div * s

        if abs(minutes) > 59:
            s = _sign(minutes)
            div, mod = divmod(minutes * s, 60)
            minutes = mod * s
            hours += div * s

        if abs(hours) > 23:
            s = _sign(hours)
            div, mod = divmod(hours * s, 24)
            hours = mod * s
            days += div * s

        if abs(months) > 11:
            s = _sign(months)
            div, mod = divmod(months * s, 12)
            months = mod * s
            years += div * s

        year = self.dt.year + years
        month = self.dt.month

        if months:
            month += months
            if month > 12:
                year += 1
                month -= 12
            elif month < 1:
                year -= 1
                month += 12

        day = min(DAYS_PER_MONTHS[int(_is_leap(year))][month], self.dt.day)

        dt = self.dt.replace(year=year, month=month, day=day)

        return self.__class__(dt + timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        ))

    def subtract_duration(self,
                          years=0,
                          months=0,
                          weeks=0,
                          days=0,
                          hours=0,
                          minutes=0,
                          seconds=0,
                          microseconds=0):
        """
        Subtract a duration to a kronos instance.
        """
        return self.add_duration(years=-years,
                                 months=-months,
                                 weeks=-weeks,
                                 days=-days,
                                 hours=-hours,
                                 minutes=-minutes,
                                 seconds=-seconds,
                                 microseconds=-microseconds
                                 )

    def from_interval(self, interval: int, offset: int, scale: Literal['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years'] = 'days'):
        """
        produce the start and end of a period based on the interval and offset
        """
        start = self.subtract_duration(**{scale: interval+offset})
        stop = self.subtract_duration(**{scale: offset})
        return start, stop


def _sign(x):
    return int(copysign(1, x))


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)