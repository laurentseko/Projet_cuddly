#!/usr/bin/env python

"""Define some functions.

    The following documentation is automatically generated from the Python
    source files.  It may be incomplete, incorrect or include features that
    are considered implementation detail and may vary between Python
    implementations.  When in doubt, consult the module reference at the
    location listed above."""

# -*- coding: utf8 -*-

import sys
import time
import csv
import datetime
import stop
import trip


def service_date():
    """Load the file calendar.txt, calendar_dates.txt and return a dict."""
    s_d = dict()

    csv_file = open('calendar.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        num = int(row[8])
        s_date = (num // 10000, (num % 10000) // 100, num % 100)
        num = int(row[9])
        e_date = (num // 10000, (num % 10000) // 100, num % 100)
        dates = list()
        for i in range(7):
            if row[1 + i] == '1':
                b_date = datetime.date(*s_date)
                f_date = datetime.date(*e_date)
                dt = datetime.timedelta(days=7)
                while b_date < f_date:
                    dates.append(b_date)
                    b_date = b_date + dt
        if len(dates) > 0:
            s_d[int(row[0])] = dates

    csv_file = open('calendar_dates.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        service_id = int(row[0])
        num = int(row[1])
        date = datetime.date(num // 10000, (num % 10000) // 100, num % 100)
        if row[2] == '1':
            dates = s_d.get(service_id)
            if dates is None:
                dates = list()
                s_d[service_id] = dates
            dates.append(date)
        elif row[2] == '2':
            dates = s_d.get(service_id)
            if dates is not None:
                dates.remove(date)

    return s_d


def route_type_sn(ty=None):
    """Load the file routes.txt and return a dict."""
    r_t_sn = dict()

    csv_file = open('routes.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    if ty is None:
        for row in csv_iter:
            r_t_sn[int(row[0])] = (int(row[5]), row[2])
    else:
        for row in csv_iter:
            t = int(row[5])
            if t not in ty:
                continue
            r_t_sn[int(row[0])] = (t, row[2])
    return r_t_sn


def trip_route_service(r_t_sn):
    """Load the file trips.txt and return a dict."""
    t_r_s = dict()

    csv_file = open('trips.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        r_id = int(row[0])
        if r_id not in r_t_sn:
            continue
        t_id = int(row[2])
        s_id = int(row[1])
        t_r_s[t_id] = (r_id, s_id)
    return t_r_s


def stop_trip(t_r_s):
    s_t = dict()

    csv_file = open('stop_times.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        stop_id = int(row[3])
        if s_t.get(stop_id) is None:
            trip_id = int(row[0])
            if trip_id in t_r_s:
                s_t[stop_id] = trip_id
            # else:
            #     s_t[stop_id] = -1
    return s_t


def load_stops(s_t, t_r_s, r_t_sn):
    """Load the file stops.txt and return a dict."""
    stop_dict = dict()
    i_s_key = dict()
    sn_date_trips = dict()

    csv_file = open('stops.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        stop_id = int(row[0])
        if s_t.get(stop_id) is None:
            continue
        trip_id = s_t[stop_id]
        route_id = t_r_s[trip_id][0]
        (ty, sn) = r_t_sn[route_id]
        s_key = (row[2], sn)
        so = stop_dict.get(s_key)
        if so is None:
            date_trips = sn_date_trips.get(sn)
            if date_trips is None:
                date_trips = dict()
                sn_date_trips[sn] = date_trips
            stop_dict[s_key] = stop.Stop([stop_id], row[2], float(row[4]),
                                         float(row[5]), ty, sn, date_trips=date_trips)
        else:
            so.ids.append(stop_id)
        i_s_key[stop_id] = s_key
    return stop_dict, i_s_key


def transfer(i_s_key):
    """Load the file transfers.txt and return a dict."""
    transfer_cost = dict()

    csv_file = open('transfers.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        from_stop_id = int(row[0])
        to_stop_id = int(row[1])
        from_stop_id = i_s_key.get(from_stop_id)
        to_stop_id = i_s_key.get(to_stop_id)
        if from_stop_id and to_stop_id:
            cost = int(row[3])
            transfer_cost[(from_stop_id, to_stop_id)] = cost
            transfer_cost[(to_stop_id, from_stop_id)] = cost
    return transfer_cost


def load_trips(stop_dict, i_s_key, t_r_s, s_d):
    trip_dict = dict()

    start = time.time()
    csv_file = open('stop_times.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    p = -1.1
    prev_trip_id = None
    p_i = None
    counter = 0

    for row in csv_iter:
        r_i = int(row[3])
        r_key = i_s_key.get(r_i)
        if r_key is None:
            continue
        r = int(row[4])
        trip_id = int(row[0])
        if r - p == 1:
            if stop_dict[r_key] not in stop_dict[p_key].nexts:
                stop_dict[p_key].nexts.append(stop_dict[r_key])
        if prev_trip_id != trip_id:
            service_id = t_r_s[trip_id][1]
            dates = s_d[service_id]
            trip_dict[trip_id] = trip.Trip(trip_id, dates)
        hms = row[2].split(':')
        trip_dict[trip_id].stop_times.append((stop_dict[r_key],
                                             (int(hms[0]), int(hms[1]),
                                              int(hms[2]))))
        p_i = r_i
        p_key = r_key
        p = r
        prev_trip_id = trip_id
    end = time.time()
    print('loaded trips: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    # Add trips to each stop
    # for t in trip_dict:
    size = len(trip_dict)
    i = 0
    list_all = list()
    for to in trip_dict.values():
        so = to.stop_times[0][0]
        for date in to.dates:
            trips = so.date_trips.get(date)
            if trips is None:
                trips = list()
                so.date_trips[date] = trips
            if to not in trips:
                trips.append(to)
        i += 1
        if i % (size // 10) == 0:
            print(i)
        # trips = so.trips
        # if to not in trips:
        #     trips.append(to)
    end = time.time()
    print('trips added: done in', datetime.timedelta(seconds=end-start))
    return trip_dict


def rec_dijkstra(stop_dict, trip_dict, t_c, src, the_moment, d=None):
    """Compute the time."""
    # TODO: priority queue to implement
    M = datetime.datetime.max
    # FIXME: A bit 'expensive' (RAM) the set
    # next_level = set()
    next_level = list()
    if d is None:
        d = dict()
        for k in stop_dict:
            d[k] = [None, None, M]  # so, to, datetime
        d[src][2] = the_moment
        # next_level.add(src)
        next_level.append(src)
    # print(src, the_moment)
    limit_date = datetime.date(the_moment.year, the_moment.month,
                               the_moment.day)\
        + datetime.timedelta(days=2)
    nt_d_t = stop_dict[src].destinations(the_moment, limit_date=limit_date)
    for s_key in nt_d_t:
        if d[s_key][2] > nt_d_t[s_key][1]:
            d[s_key][0] = stop_dict[src]
            d[s_key][1] = nt_d_t[s_key][0]
            d[s_key][2] = nt_d_t[s_key][1]
            # next_level.add(s_key)
            next_level.append(s_key)
    for l_key in next_level:
        # print('Key', l_key, len(stop_dict[l_key].transfers))
        # for t in stop_dict[l_key].transfers:
        #     t_key = (t.name, t.sn)
        #     print(t_key)
        for t in stop_dict[l_key].transfers:
            key = (stop_dict[l_key].ids[0], t.ids[0])
            if stop_dict[l_key].ids[0] > t.ids[0]:
                key = (t.ids[0], stop_dict[l_key].ids[0])
            tt = datetime.timedelta(seconds=t_c[key])
            t_key = (t.name, t.sn)
            if d[t_key][2] > d[l_key][2] + tt:
                d[t_key][0] = stop_dict[l_key]
                d[t_key][1] = None
                d[t_key][2] = d[l_key][2] + tt
                rec_dijkstra(stop_dict, trip_dict, t_c, t_key, d[t_key][2], d)
            elif t_c[key] == 0 and t_key != src:
                # print('Zero transfer', t_key, d[t_key][0].name, d[t_key][2])
                # TODO: ??
                # d[t_key][0] = stop_dict[l_key]
                # d[v_key][1] = None
                # d[t_key][2] = d[l_key][2] + tt
                rec_dijkstra(stop_dict, trip_dict, t_c, t_key, d[t_key][2], d)
    return d


def dijkstra(stop_dict, trip_dict, t_c, srcs, the_moment, d=None):
    """Compute the time."""
    import operator
    M = datetime.datetime.max
    current = list()
    if d is None:
        d = dict()
        for k in stop_dict:
            d[k] = (None, None, M)  # so, to, datetime
        for src in srcs:
            d[src] = (None, None, the_moment)
            current.append(src)
    limit_date = datetime.date(the_moment.year, the_moment.month,
                               the_moment.day)\
        + datetime.timedelta(days=2)

    while len(current) > 0:
        next_level = list()
        # next_level = set()
        for c_key in current:
            cs = stop_dict[c_key]
            # nt_d_t = cs.destinations(d[c_key][2], limit_date=limit_date)
            limit_date = datetime.date(d[c_key][2].year, d[c_key][2].month,
                                       d[c_key][2].day)\
                + datetime.timedelta(days=1)
            nt_d_t = cs.line_dijkstra(d[c_key][2], limit_date=limit_date)
            # nt_d_t = cs.line_dijkstra(d[c_key][2])
            for s_key in nt_d_t:
                so = stop_dict[s_key]
                (next_trip, d_t) = nt_d_t[s_key]
                if d_t and d[s_key][2] > d_t:
                    d[s_key] = (cs, next_trip, d_t)
                    # TODO: why?
                    # if len(stop_dict[s_key].transfers) > 0 and\
                    #         s_key not in next_level:
                    #     next_level.append(s_key)
                    # next_level.add(s_key)
                    for to in so.transfers:
                        t_key = (to.name, to.sn)
                        key = (t_key, s_key)
                        tt = datetime.timedelta(seconds=t_c[key])
                        d_t = d[s_key][2] + tt
                        if d[t_key][2] > d_t:
                            d[t_key] = (so, None, d_t)
                            if t_key not in next_level:
                                next_level.append(t_key)
                            # next_level.add(t_key)
                        elif t_c[key] == 0 and t_key != c_key:
                            if t_key not in next_level:
                                next_level.append(t_key)
                            # next_level.add(t_key)
        current = sorted(next_level, key=lambda s_key: d[s_key][2])
    return d


if __name__ == '__main__':
    start = time.time()
    s_d = service_date()
    end = time.time()
    print('service_date(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    r_t_sn = route_type_sn(ty=[1])  # Only metro/subway
    # r_t_sn = route_type_sn()
    end = time.time()
    print('route_type(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    t_r_s = trip_route_service(r_t_sn)
    end = time.time()
    print('trip_route_service(): done in',
          datetime.timedelta(seconds=end-start))

    # start = time.time()
    # t_s = trip_stop(t_r_s)
    # end = time.time()
    # print('trip_stop(): done in', datetime.timedelta(seconds=end-start))

    # start = time.time()
    # TODO: Why is pandas so slow?
    # stop_times = pd.read_csv('stop_times.txt', header=0, sep=',', engine='c',
    #                          memory_map=True, low_memory=False,
    #                          usecols=['trip_id', 'departure_time',
    #                                   'stop_id', 'stop_sequence'])
    # print(stop_times.info())

    # stop_times = list()
    # csv_file = open('stop_times.txt', 'r')
    # csv_iter = csv.reader(csv_file, delimiter=',')
    # _ = next(csv_iter)

    # for row in csv_iter:
    #     stop_times.append((int(row[0]), row[2], int(row[3]), int(row[4])))
    # end = time.time()
    # print('stop_times.txt: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    s_t = stop_trip(t_r_s)
    end = time.time()
    print('stop_trip(): done in',
          datetime.timedelta(seconds=end-start))

    start = time.time()
    stop_dict, i_s_key = load_stops(s_t, t_r_s, r_t_sn)
    end = time.time()
    print('load_stops(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    t_c = transfer(i_s_key)
    end = time.time()
    print('transfer(): done in', datetime.timedelta(seconds=end-start))

    trip_dict = load_trips(stop_dict, i_s_key, t_r_s, s_d)

    for so in stop_dict.values():
        # TODO: Why?
        # if len(so.nexts) < 2:
        #     continue
        for ns in so.nexts:
            # TODO: use len for precision
            if so not in ns.nexts:
                ns.nexts.append(so)

    start = time.time()
    for s_key in stop_dict:
        so = stop_dict[s_key]
        if len(so.nexts) > 2:
            if so not in so.transfers:
                so.transfers.append(so)
            t_c[(s_key, s_key)] = 0
    end = time.time()
    print('Fix t_c: done in', datetime.timedelta(seconds=end-start))

    # s_key = ('Boulogne-Jean-Jaurès', '10')
    # print(stop_dict[s_key].ids)
    # for t in stop_dict[s_key].transfers:
    #     print(t.name)
    # for drt in [0, 1]:
    #     for n in stop_dict[s_key].nexts[drt]:
    #         print(n.name)

    start = time.time()
    # FIXME: test one transfers
    keys = [('Jussieu', '7'), ('Jussieu', '10'), ("Place d'Italie", '6'),
            ("Place d'Italie", '7')]
    lines = ['7', '10', '6']
    not_all = not True
    # Transfer
    for (key_0, key_1) in t_c:
        if key_0 is None or key_1 is None:
            continue
        # All line if commented
        if not_all and\
                ((not((key_0 in keys and key_1 in keys) or
                 key_0 == key_1)) and
                 not (key_0[1] in lines and key_1[1] in lines)):
            continue
        if stop_dict.get(key_0) is not None and\
                stop_dict.get(key_1) is not None:
            so_0 = stop_dict[key_0]
            so_1 = stop_dict[key_1]
            if so_0 not in so_1.transfers:
                so_1.transfers.append(so_0)
            if so_1 not in so_0.transfers:
                so_0.transfers.append(so_1)
    end = time.time()
    print('Add transfers: done in', datetime.timedelta(seconds=end-start))

    print('Number of stops: ', len(stop_dict))
    print('Number of trips: ', len(trip_dict))

    # the_day = datetime.datetime(2019, 3, 13, 9, 0)
    the_day = datetime.datetime(2019, 3, 20, 9, 0)
    # TODO: find 24h+
    # the_day = datetime.datetime(2019, 6, 3, 0, 1)
    # s_key = i_s_key[1907]
    # print(stop_dict[s_key])
    # print(stop_dict[s_key].trips[0])
    # FIXME: find_trip() is supposed to return two dates
    # now = stop_dict[s_key].find_trip(the_day)
    # print(now)
    # for n in now:
    #     print(n[0].id, the_day < n[1], n[1] - the_day,
    #           n[0].stop_times[-1][0].name)

    # Ping
    # s_key = ("Porte d'Auteuil", '10')
    # print(stop_dict[s_key].ids)
    # for drt in [0, 1]:
    #     line = stop_dict[s_key].line(drt)
    #     print(drt, ':', line)
    # sys.exit(2)

    start = time.time()
    # s_key = i_s_key[1907]
    s_key = ('Villejuif-Louis Aragon', '7')
    # s_key = ('Jussieu', '10')
    # t_key = ('Jussieu', '7')
    # s_key = ('Jussieu', '7')
    # s_key = ("Porte d'Auteuil", '10')
    # d = rec_dijkstra(stop_dict, trip_dict, t_c, s_key, the_day)
    d = dijkstra(stop_dict, trip_dict, t_c, {s_key}, the_day)
    end = time.time()
    # print('rec_dijkstra(): done in', datetime.timedelta(seconds=end-start))
    print('dijkstra(): done in', datetime.timedelta(seconds=end-start))
    limit = len('Villejuif-Paul Vaillant Couturier (Hôpital Paul Brousse)')
    lines = ['7', '10', '6']
    not_all = not True
    for s in d:
        if not_all and s[1] not in lines:
            continue
        if d[s][0] is not None and d[s][1] is not None:
            print(s, stop_dict[s].ty, ' ' * (limit - len(s[0])), d[s][0].name,
                  d[s][1].id, d[s][2])
        elif d[s][0] is not None:
            print(s, stop_dict[s].ty, ' ' * (limit - len(s[0])), d[s][0].name,
                  d[s][1], d[s][2])
        else:
            print(s, stop_dict[s].ty, ' ' * (limit - len(s[0])), d[s][0],
                  d[s][1], d[s][2])
    dst = ('Maison Blanche', '7')
    # dst = ("Eglise d'Auteuil", '10')
    while True:
        if d[dst][0]:
            print(dst, '/', (d[dst][0].name, d[dst][0].sn), '/', d[dst][2])
            dst = (d[dst][0].name, d[dst][0].sn)
        else:
            break

    sys.exit(0)
