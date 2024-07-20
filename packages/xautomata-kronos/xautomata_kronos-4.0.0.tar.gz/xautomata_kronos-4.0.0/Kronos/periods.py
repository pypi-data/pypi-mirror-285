class Periods:
    td = None

    def in_periods(self, period='seconds'):
        """
        convert a time difference into the chosen time period
        """
        if period in 'seconds':
            td = int(self.td.total_seconds())
        elif period in 'minutes':
            td = int(self.td.total_seconds()/60)
        elif period in 'hours':
            td = int(self.td.total_seconds()/(60*60))
        elif period in 'days':
            td = int(self.td.total_seconds()/(60*60*24))
        elif period in 'weeks':
            td = int(self.td.total_seconds()/(60*60*24*7))
        elif period in 'months':
            td = int((self.td.total_seconds()/(60*60*24*7*(52/12))))
        elif period in 'years':
            td = int(self.td.total_seconds()/(60*60*24*7*52))
        else:
            raise NotImplementedError

        return td

    def in_seconds(self):
        """
        convert a time difference into seconds
        """
        return self.in_periods('seconds')

    def in_minutes(self):
        """
        convert a time difference into minutes
        """
        return self.in_periods('minutes')

    def in_hours(self):
        """
        convert a time difference into hours
        """
        return self.in_periods('hours')

    def in_days(self):
        """
        convert a time difference into days
        """
        return self.in_periods('days')

    def in_weeks(self):
        """
        convert a time difference into weeks
        """
        return self.in_periods('weeks')

    def in_months(self):
        """
        convert a time difference into months
        """
        return self.in_periods('months')

    def in_years(self):
        """
        convert a time difference into years
        """
        return self.in_periods('years')