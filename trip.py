#!/usr/bin/env python

"""The class Trip is defined here."""
# -*- coding: utf8 -*-

import datetime


class Trip():
    """The class Trip is defined here."""

    __slots__ = ['id', 'dates', 'stop_times']

    def __init__(self, t_id, dates=None, stop_times=None):
        self.id = t_id
        self.dates = sorted(dates or list())
        self.stop_times = stop_times or list()

    def __repr__(self):
        return 'Trip(id=%d, dates=%s, stop_times=%s)' % (self.id, self.dates,
                                                         self.stop_times)

    def closest(self, stop_id, date_time, dt=datetime.timedelta(minutes=2)):
        """Find the date of the next transport and the date of the first
        stop."""
        # d = datetime.date(date_time.year, date_time.month, date_time.day)
        for v in self.stop_times:
            if v[0] == stop_id:
                good_date = None
                date = None
                for date in reversed(self.dates):
                    the_date = datetime.datetime(date.year, date.month,
                                                 date.day, v[1][0] % 24,
                                                 v[1][1], v[1][2])\
                        + datetime.timedelta(days=v[1][0] // 24)
                    # print(good_date, the_date, date_time,
                    #       date_time >= the_date)
                    if date_time >= the_date:
                        return good_date, date
                    good_date = the_date
                # date is not None if len(self.dates) > 0
                return good_date, date
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
