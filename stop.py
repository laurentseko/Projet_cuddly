#!/usr/bin/env python

"""The class Stop is defined here."""

# -*- coding: utf8 -*-


class Stop():
    """The class Stop is defined here."""
    __slots__ = ['id', 'name', 'lat', 'lon', 'ty', 'neighbors', 'transfers',
                 'trips']

    def __init__(self, s_id, name=None, lat=None, lon=None, ty=None,
                 neighbors=None, transfers=None, trips=None):
        self.id = s_id
        self.name = name or ''
        self.lat = lat or 0.
        self.lon = lon or 0.
        self.ty = ty or -1
        self.neighbors = neighbors or list()
        self.transfers = transfers or list()
        self.trips = trips or list()

    def __repr__(self):
        return 'Stop(id=%d, name=\'%s\', lat=%f, lon=%f, ty=%d, neighbors=%s,'\
               ' transfers=%s, trips=%s)' % (self.id, self.name, self.lat,
                                             self.lon, self.ty, self.neighbors,
                                             self.transfers, self.trips)

    def find_trip(self, the_date, trip_dict):
        """Find a trip given a date."""
        next_trip = None
        d_t = None
        date = None
        for t in self.trips:
            tmp_d_t = trip_dict[t].closest(self.id, the_date)
            if d_t is None or (tmp_d_t[0] is not None and d_t > tmp_d_t[0]):
                d_t = tmp_d_t[0]
                date = tmp_d_t[1]
                next_trip = t
        return next_trip, d_t, date


if __name__ == '__main__':
    print('Test class Stop')
    s = Stop(0)
    s.name = 'Jussieu'
    print(s)
