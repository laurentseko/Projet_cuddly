#!/usr/bin/env python

"""Trip is a data structure that represent a trip for transit.

    The following documentation is automatically generated from the Python
    source files.  It may be incomplete, incorrect or include features that
    are considered implementation detail and may vary between Python
    implementations.  When in doubt, consult the module reference at the
    location listed above."""

# -*- coding: utf8 -*-

import datetime


class Trip():
    """The class Trip is defined here."""

    __slots__ = ['id', 'dates', 'stop_times']

    def __init__(self, t_id, dates=list(), stop_times=None):
        self.id = t_id
        self.dates = sorted(dates)
        self.stop_times = stop_times or list()

    def __repr__(self):
        return 'Trip(id=%d, dates=%s, stop_times=[.])' % (self.id, self.dates)
        #                                                  self.stop_times)

    def closest(self, so, date_time):
        """Find the date of the next transport and the date of the first
        stop."""
        for v in self.stop_times:
            if v[0] == so:
                good_date = None
                trip_date = None
                for date in reversed(self.dates):
                    the_date = datetime.datetime(date.year, date.month,
                                                 date.day, v[1][0] % 24,
                                                 v[1][1], v[1][2])\
                        + datetime.timedelta(days=v[1][0] // 24)
                    if date_time >= the_date:
                        # return good_date, trip_date
                        break
                    good_date = the_date
                    trip_date = date
                # date is not None if len(self.dates) > 0
                return good_date, trip_date
        return None, None

    def date_time(self, stop_id, d_t):
        """The date of a stop."""
        dd_t = None
        # TODO: Avoid research, return a list()
        for v in self.stop_times:
            if stop_id == v[0]:
                dd_t = datetime.datetime(d_t.year, d_t.month, d_t.day,
                                         v[1][0] % 24, v[1][1], v[1][2])\
                        + datetime.timedelta(days=v[1][0]//24)
                break
        return dd_t


if __name__ == '__main__':
    print('Test class Trip')
    t = Trip(1, dates=[datetime.date(1970, 1, 2)])
    print(t.closest(0, datetime.datetime(2020, 1, 1)))
    t.stop_times.append((1, (1, 0, 0)))
    t.stop_times.append((0, (24, 2, 0)))
    d_t = datetime.datetime(2020, 1, 1)
    print(d_t, t.closest(0, d_t))
    d_t = datetime.datetime(1970, 1, 3, 0, 4)
    print(d_t, t.closest(0, d_t))
    d_t = datetime.datetime(1970, 1, 3, 0, 0)
    print(d_t, t.closest(0, d_t))
    print(t)
