#!/usr/bin/env python

"""Define some functions."""

# -*- coding: utf8 -*-

import sys
import time
import csv
import datetime
import stop
import trip


def transfer():
    """Load the file transfers.txt and return a dict."""
    transfer_cost = dict()

    csv_file = open('transfers.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        from_stop_id = int(row[0])
        to_stop_id = int(row[1])
        if from_stop_id > to_stop_id:
            from_stop_id, to_stop_id = to_stop_id, from_stop_id
        cost = int(row[3])
        transfer_cost[(from_stop_id, to_stop_id)] = cost
    return transfer_cost


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
            if s_d.get(service_id) is None:
                s_d[service_id] = list()
            s_d[service_id].append(date)
        elif row[2] == '2':
            if s_d.get(service_id) is not None:
                s_d[service_id].remove(date)

    return s_d


def route_type():
    """Load the file routes.txt and return a dict."""
    r_t = dict()

    csv_file = open('routes.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        r_t[int(row[0])] = int(row[5])
    return r_t


def trip_route_service():
    """Load the file trips.txt and return a dict."""
    t_r_s = dict()

    csv_file = open('trips.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        # print(row)
        # print(int(row[2]), int(row[0]), int(row[1]))
        # t_r_s[int(row[2])] = (int(row[0], int(row[1])))
        t_id = int(row[2])
        r_id = int(row[0])
        s_id = int(row[1])
        t_r_s[t_id] = (r_id, s_id)
    return t_r_s


def load_stops():
    """Load the file stops.txt and return a dict."""
    stop_dict = dict()

    csv_file = open('stops.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        stop_id = int(row[0])
        stop_dict[stop_id] = stop.Stop(stop_id, row[2], float(row[4]),
                                       float(row[5]))
    return stop_dict


# 'Fix' some Stop object to save space (RAM)
def propagate(stop_id, stop_dict):
    """Fix the objects Stop."""
    s_trips = stop_dict[stop_id].trips
    neighbors = stop_dict[stop_id].neighbors
    for n in neighbors:
        # print(id(stop_dict[n].trips), id(s_trips))
        if id(stop_dict[n].trips) != id(s_trips):
            stop_dict[n].trips = s_trips
            propagate(n, stop_dict)


def rec_dijkstra(stop_dict, trip_dict, t_c, src, the_date, d=None, level=0):
    """Compute the time."""
    M = datetime.timedelta.max
    # FIXME: A bit 'expensive' (RAM) the set
    # next_level = set()
    next_level = list()
    if d is None:
        d = dict()
        for k in stop_dict:
            d[k] = M
        d[src] = datetime.timedelta(days=0)
        # next_level.add(src)
        next_level.append(src)
    a_trip = stop_dict[src].find_trip(the_date, trip_dict)
    date = a_trip[2]
    # FIXME: look for another one
    if a_trip[1] is None:
        return d
    # TODO: why?
    # if d[src] == M:
    #     d[src] = datetime.timedelta(seconds=0)
    for v in trip_dict[a_trip[0]].stop_times:
        d_t = datetime.datetime(date.year, date.month, date.day, v[1][0] % 24,
                                v[1][1], v[1][2])\
              + datetime.timedelta(days=v[1][0]//24)
        dt = None
        if d_t >= a_trip[1]:
            dt = d_t - a_trip[1]
        else:
            continue
        # print(v[0], src)
        # print(stop_dict[v[0]].name, stop_dict[src].name)
        # print(d[v[0]], d[src], dt)
        if d[v[0]] > d[src] + dt:
            d[v[0]] = d[src] + dt
            # next_level.add(v[0])
            next_level.append(v[0])
    for v in next_level:
        for t in stop_dict[v].transfers:
            key = (v, t)
            if v > t:
                key = (t, v)
            tt = datetime.timedelta(seconds=t_c[key])
            if d[t] > d[v] + tt:
                d[t] = d[v] + tt
            else:
                continue
            # if tt == zero_tt:
            # or
            if v == src:
                # TODO: why not +1 to level?
                rec_dijkstra(stop_dict, trip_dict, t_c, t, the_date + d[t], d,
                             level)
            else:
                rec_dijkstra(stop_dict, trip_dict, t_c, t, a_trip[1] + d[t], d,
                             level + 1)
    return d


def dijkstra(stop_dict, trip_dict, t_c, srcs, the_date, d=None, level=0):
    """Compute the time."""
    if len(srcs) == 0:
        # TODO: finish it
        d = dict()
        return d
    srcs_iter = iter(srcs)
    src = next(srcs_iter)
    d = rec_dijkstra(stop_dict, trip_dict, t_c, src, the_date)
    for src in srcs_iter:
        d[src] = datetime.timedelta(seconds=0)
        rec_dijkstra(stop_dict, trip_dict, t_c, src, the_date, d)
    return d


if __name__ == '__main__':
    start = time.time()
    t_c = transfer()
    end = time.time()
    print('transfer(): done in', datetime.timedelta(seconds=end-start))
    start = time.time()
    s_d = service_date()
    end = time.time()
    print('service_date(): done in', datetime.timedelta(seconds=end-start))
    start = time.time()
    r_t = route_type()
    end = time.time()
    print('route_type(): done in', datetime.timedelta(seconds=end-start))
    start = time.time()
    t_r_s = trip_route_service()
    end = time.time()
    print('trip_route_service(): done in',
          datetime.timedelta(seconds=end-start))
    start = time.time()
    stop_dict = load_stops()
    end = time.time()
    print('load_stops(): done in', datetime.timedelta(seconds=end-start))
    trip_dict = dict()

    start = time.time()
    csv_file = open('stop_times.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    header = next(csv_iter)

    prev = next(csv_iter)
    p = int(prev[4])
    trip_id = int(prev[0])
    p_i = int(prev[3])

    service_id = t_r_s[trip_id][1]
    dates = s_d[service_id]
    trip_dict[trip_id] = trip.Trip(trip_id, dates)
    prev_trip_id = trip_id

    for row in csv_iter:
        r = int(row[4])
        trip_id = int(row[0])
        r_i = int(row[3])
        if r - p == 1:
            if r_i not in stop_dict[p_i].neighbors:
                stop_dict[p_i].neighbors.append(r_i)
                route_id = t_r_s[trip_id][0]
                ty = r_t[route_id]
                stop_dict[p_i].ty = ty
                stop_dict[r_i].ty = ty
        if prev_trip_id != trip_id:
            service_id = t_r_s[trip_id][1]
            dates = s_d[service_id]
            trip_dict[trip_id] = trip.Trip(trip_id, dates)
        hms = row[2].split(':')
        trip_dict[trip_id].stop_times.append((r_i, (int(hms[0]), int(hms[1]),
                                                    int(hms[2]))))
        prev_trip_id = trip_id
        p_i = r_i
        p = r
    end = time.time()
    print('stop_times.txt: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    # Two lists per route_short_name
    for s in stop_dict:
        propagate(s, stop_dict)
    ok = False
    while not ok:
        ok = True
        for s in stop_dict:
            s_neighbors = stop_dict[s].neighbors
            for n in s_neighbors:
                n_trips = stop_dict[n].trips
                if id(n_trips) != id(stop_dict[s].trips):
                    stop_dict[s].trips = n_trips
                    ok = False
    end = time.time()
    print('route_short_name: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    # Add trips to each stop
    for t in trip_dict:
        stop_id = trip_dict[t].stop_times[0][0]
        trips = stop_dict[stop_id].trips
        if t not in trips:
            trips.append(t)
    end = time.time()
    print('trips added: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    # FIXME: Bad design, now O(n^2) in my hands
    stop_ids = [k for k in stop_dict]
    while len(stop_ids) > 0:
        s_i = stop_ids.pop()
        i = len(stop_ids) - 1
        for stop_id in reversed(stop_ids):
            if stop_dict[s_i].name == stop_dict[stop_id].name and\
                    stop_dict[s_i].lat == stop_dict[stop_id].lat and\
                    stop_dict[s_i].lon == stop_dict[stop_id].lon:
                s_id = s_i
                s_jd = stop_id
                if s_i > stop_id:
                    s_id = stop_id
                    s_jd = s_i
                if t_c.get((s_id, s_jd)) is None:
                    t_c[(s_id, s_jd)] = 0
                break  # TODO: Justify
            i -= 1
        # stop_ids.remove(i)
        stop_ids.pop(i)
    # i = 0
    # for i in range(len(stop_ids)):
    #     s_i = stop_ids[i]
    #     for j in range(i + 1, len(stop_ids)):
    #         s_j = stop_ids[j]
    #         if stop_dict[s_i].name == stop_dict[s_j].name and\
    #                 stop_dict[s_i].lat == stop_dict[s_j].lat and\
    #                 stop_dict[s_i].lon == stop_dict[s_j].lon:
    #             s_id = s_i
    #             s_jd = s_j
    #             if s_i > s_j:
    #                 s_id = s_j
    #                 s_jd = s_i
    #             if t_c.get((s_id, s_jd)) is None:
    #                 t_c[(s_id, s_jd)] = 0
    #             break  # TODO: Justify
    end = time.time()
    print('Nice O(n^2): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    # Transfer
    for k in t_c:
        if stop_dict.get(k[0]) is not None and stop_dict.get(k[1]) is not None:
            if stop_dict[k[0]].ty != 1 or stop_dict[k[1]].ty != 1:
                continue
            stop_dict[k[0]].transfers.append(k[1])
            stop_dict[k[1]].transfers.append(k[0])
    end = time.time()
    print('Fix t_c: done in', datetime.timedelta(seconds=end-start))

    print('Number of stops: ', len(stop_dict))
    print('Number of trips: ', len(trip_dict))

    # stop_dict[1907].trips.append(1)
    # stop_dict[2232].trips.append(1)
    # TODO: find 24h+
    # the_day = datetime.datetime(2019, 3, 9, 11, 26)
    the_day = datetime.datetime(2019, 6, 3, 0, 1)
    # now = stop_dict[2232].find_trip(the_day, trip_dict)
    now = stop_dict[1907].find_trip(the_day, trip_dict)
    print(now, the_day < now[1], now[1] - the_day)
    day = trip_dict[now[0]].date_time(1907, now[2])
    print('day', day)
    # print(trip_dict[now[0]])

    start = time.time()
    d = rec_dijkstra(stop_dict, trip_dict, t_c, 1907, the_day)
    end = time.time()
    print('rec_dijkstra(): done in', datetime.timedelta(seconds=end-start))
    for s in d:
        print(stop_dict[s].ty, stop_dict[s].name, ' ' * (len('Villejuif-Paul'
              ' Vaillant Couturier (Hôpital Paul Brousse)') - len(
              stop_dict[s].name)), d[s])
    # print(t_c)
    # print(stop_dict[1907])
    # print(t_c[(1907, 2232)])
    # for s in stop_dict:
    #     #print(s, stop_dict[s], id(stop_dict[s].trips))
    #     print(s, stop_dict[s].name)
    # while True: pass
    sys.exit(0)
