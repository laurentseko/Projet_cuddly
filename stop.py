#!/usr/bin/env python

"""Stop is a data structure that represent a stop point in transit.

    The following documentation is automatically generated from the Python
    source files.  It may be incomplete, incorrect or include features that
    are considered implementation detail and may vary between Python
    implementations.  When in doubt, consult the module reference at the
    location listed above."""

# -*- coding: utf8 -*-

import datetime


class Stop():
    """The class Stop is defined here."""
    __slots__ = ['ids', 'name', 'lat', 'lon', 'ty', 'sn', 'nexts', 'transfers',
                 'trips']

    def __init__(self, ids, name=None, lat=None, lon=None, ty=None, sn=None,
                 nexts=None, transfers=None, trips=None):
        self.ids = ids
        self.name = name or ''
        self.lat = lat or 0.
        self.lon = lon or 0.
        self.ty = ty or -1
        self.sn = sn or ''
        self.nexts = nexts or (list(), list())
        self.transfers = transfers or list()
        self.trips = trips or list()

    def __repr__(self):
        return 'Stop(ids=%s, name=\'%s\', lat=%f, lon=%f, ty=%d, sn=\'%s\', '\
               'nexts=[.], transfers=[.], trips=[.])' % (self.ids,
                                                             self.name,
                                                             self.lat,
                                                             self.lon,
                                                             self.ty, self.sn)
        #                                                     self.nexts,
        #                                                     self.transfers,
        #                                                     self.trips)

    def __eq__(self, other):
        # Overengineered?
        if id(self) == id(other):
            return True
        if isinstance(other, Stop):
            return self.name == other.name and self.sn == other.sn
        return False

    def find_trip(self, the_date):
        """Find a trip given a date."""
        next_trip = None
        d_t = None
        date = None
        # Not nice
        for t in self.trips:
            # print(t)
            tmp_d_t = t.closest(self, the_date)
            if d_t is None or (tmp_d_t[0] is not None and d_t > tmp_d_t[0]):
                d_t = tmp_d_t[0]
                date = tmp_d_t[1]
                next_trip = t
        return next_trip, d_t, date

    def destinations(self, the_date, others=None, limit_date=None):
        """Find a trip for all destinations in 'others'."""
        # The line Dijkstra?
        # TODO: rename others
        if others is None:
            others = set()
            for drt in [0, 1]:
                one_side = self.line(drt)
                others.update(one_side)
        s_key = (self.name, self.sn)
        if s_key in others:
            others.remove(s_key)
        nt_d_t = dict()
        for s_key in others:
            nt_d_t[s_key] = (None, None)
        for t in self.trips:
            sp_t_iter = iter(t.stop_times)
            stop_found = False
            for v in sp_t_iter:
                if v[0] == self:
                    stop_found = True
                    break
            if not stop_found:
                continue
            bad_date = False
            for date in reversed(t.dates):
                if limit_date and date > limit_date:
                    continue
                sp_t_iter = iter(t.stop_times)
                for v in sp_t_iter:
                    if v[0] == self:
                        d_t = datetime.datetime(date.year, date.month,
                                                date.day,
                                                v[1][0] % 24, v[1][1],
                                                v[1][2])\
                            + datetime.timedelta(days=v[1][0]//24)
                        if the_date >= d_t:
                            bad_date = True
                        break
                if bad_date:
                    break
                for v in sp_t_iter:
                    v_key = (v[0].name, v[0].sn)
                    if v_key not in others:
                        continue
                    d_t = datetime.datetime(date.year, date.month, date.day,
                                            v[1][0] % 24, v[1][1], v[1][2])\
                        + datetime.timedelta(days=v[1][0]//24)
                    if nt_d_t[v_key][1] is None or nt_d_t[v_key][1] > d_t:
                        nt_d_t[v_key] = (t, d_t)
        return nt_d_t

    def line(self, direction, the_line=None):
        """Find stops of a line."""
        if the_line is None:
            the_line = {(self.name, self.sn)}
        for n in self.nexts[direction]:
            n_key = (n.name, n.sn)
            if n_key not in the_line:
                the_line.add(n_key)
                # the_line.update(n.line())  # Not right
                n.line(direction, the_line)
        return the_line


if __name__ == '__main__':
    print('Test class Stop')
    s = Stop(0)
    s.name = 'Jussieu'
    print(s)
