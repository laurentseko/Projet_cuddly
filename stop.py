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
                 'date_trips']

    def __init__(self, ids, name=None, lat=None, lon=None, ty=-1,
                 short_name=' ', nexts=None, transfers=None,
                 date_trips=dict()):
        self.ids = ids
        self.name = name or ''
        self.lat = lat or 0.
        self.lon = lon or 0.
        self.ty = ty  # type
        self.sn = short_name  # short_name
        self.nexts = nexts or list()
        self.transfers = transfers or list()
        self.date_trips = date_trips

    def __repr__(self):
        return 'Stop(ids=%s, name=\'%s\', lat=%f, lon=%f, ty=%d, '\
               'short_name=\'%s\', nexts=[.], transfers=[.], trips=[.])' \
                % (self.ids, self.name, self.lat, self.lon, self.ty, self.sn)
        #           self.nexts, self.transfers, self.trips)

    def __eq__(self, other):
        # Overengineered?
        if id(self) == id(other):
            return True
        if isinstance(other, Stop):
            return self.name == other.name and self.sn == other.sn
        return False

    def find_trip(self, the_date):
        """Find a trip at a given date."""
        the_trip = None
        d_t = None
        trip_date = None
        date = the_date.date()
        for tr in self.date_trips[date]:
            (t, dt) = tr.time(self)
            if t is None:
                continue
            tmp_d_t = datetime.datetime.combine(date, t) + dt
            if d_t is None or d_t > tmp_d_t:
                d_t = tmp_d_t
                the_trip = tr
        return the_trip, d_t

    def line_dijkstra(self, the_date, others=None, limit_date=None):
        """Find trips connecting self and the others stops."""
        if others is None:
            others = self.line()
        s_key = (self.name, self.sn)
        if s_key in others:
            others.remove(s_key)
        tr_d_t = dict()
        for s_key in others:
            tr_d_t[s_key] = (None, None)  # trip, date_time
        date = the_date.date()
        dt = datetime.timedelta(days=1)
        while (not limit_date or date <= limit_date) and len(others) > 0:
            trips = self.date_trips.get(date)
            if trips is None:
                date += dt
                continue
            for t in trips:
                sp_t_iter = iter(t.stop_times)
                bad_time = True
                d_t = None
                for v in sp_t_iter:
                    if v[0] == self:
                        d_t = datetime.datetime(date.year, date.month,
                                                date.day,
                                                v[1][0] % 24, v[1][1],
                                                v[1][2])\
                            + datetime.timedelta(days=v[1][0]//24)
                        if the_date < d_t:
                            bad_time = False
                        break
                if bad_time:
                    continue
                for v in sp_t_iter:
                    v_key = (v[0].name, v[0].sn)
                    if v_key not in others:
                        continue
                    d_t = datetime.datetime(date.year, date.month, date.day,
                                            v[1][0] % 24, v[1][1], v[1][2])\
                        + datetime.timedelta(days=v[1][0]//24)
                    if tr_d_t[v_key][1] is None or tr_d_t[v_key][1] > d_t:
                        tr_d_t[v_key] = (t, d_t)
            for v_key in tr_d_t:
                if v_key in others and tr_d_t[v_key]:
                    others.remove(v_key)
            date += dt
        return tr_d_t

    def line(self, the_line=None):
        """Find stops of a line."""
        if the_line is None:
            the_line = {(self.name, self.sn)}
        for n in self.nexts:
            n_key = (n.name, n.sn)
            if n_key not in the_line:
                the_line.add(n_key)
                # the_line.update(n.line())  # Not right
                n.line(the_line)
        return the_line


if __name__ == '__main__':
    print('Test class Stop')
    s = Stop(0)
    s.name = 'Jussieu'
    print(s)
