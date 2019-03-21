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
    se_d = dict()

    csv_file = open('calendar.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        num = int(row[8])
        se_date = (num // 10000, (num % 10000) // 100, num % 100)
        num = int(row[9])
        e_date = (num // 10000, (num % 10000) // 100, num % 100)
        dates = list()
        for i in range(7):
            if row[1 + i] == '1':
                b_date = datetime.date(*se_date)
                f_date = datetime.date(*e_date)
                dt = datetime.timedelta(days=7)
                while b_date < f_date:
                    dates.append(b_date)
                    b_date = b_date + dt
        if len(dates) > 0:
            se_d[int(row[0])] = dates
    csv_file.close()

    csv_file = open('calendar_dates.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        service_id = int(row[0])
        num = int(row[1])
        date = datetime.date(num // 10000, (num % 10000) // 100, num % 100)
        if row[2] == '1':
            dates = se_d.get(service_id)
            if dates is None:
                dates = list()
                se_d[service_id] = dates
            dates.append(date)
        elif row[2] == '2':
            dates = se_d.get(service_id)
            if dates is not None:
                dates.remove(date)
    csv_file.close()

    return se_d


def route_type_sn(ty=None):
    """Load the file routes.txt and return a dict."""
    r_ty_sn = dict()

    csv_file = open('routes.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    if ty is None:
        for row in csv_iter:
            r_ty_sn[int(row[0])] = (int(row[5]), row[2])
    else:
        for row in csv_iter:
            t = int(row[5])
            if t not in ty:
                continue
            r_ty_sn[int(row[0])] = (t, row[2])
    csv_file.close()
    return r_ty_sn


def trip_route_service(r_ty_sn):
    """Load the file trips.txt and return a dict."""
    tr_r_se = dict()

    csv_file = open('trips.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        r_id = int(row[0])
        if r_id not in r_ty_sn:
            continue
        t_id = int(row[2])
        s_id = int(row[1])
        tr_r_se[t_id] = (r_id, s_id)
    csv_file.close()
    return tr_r_se


def stop_trip(tr_r_se):
    """Load partially the file stop_times.txt and return a dict."""
    s_tr = dict()

    csv_file = open('stop_times.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        stop_id = int(row[3])
        if s_tr.get(stop_id) is None:
            trip_id = int(row[0])
            if trip_id in tr_r_se:
                s_tr[stop_id] = trip_id
            # else:
            #     s_tr[stop_id] = -1
    csv_file.close()
    return s_tr


def load_stops(s_tr, tr_r_se, r_ty_sn):
    """Load the file stops.txt and return a dict."""
    stop_dict = dict()
    i_s_key = dict()
    sn_date_trips = dict()

    csv_file = open('stops.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    for row in csv_iter:
        stop_id = int(row[0])
        trip_id = s_tr.get(stop_id)
        if trip_id is None:
            continue
        route_id = tr_r_se[trip_id][0]
        (ty, sn) = r_ty_sn[route_id]
        s_key = (row[2], sn)
        so = stop_dict.get(s_key)
        if so is None:
            date_trips = sn_date_trips.get(sn)
            if date_trips is None:
                date_trips = dict()
                sn_date_trips[sn] = date_trips
            stop_dict[s_key] = stop.Stop([stop_id], row[2], float(row[4]),
                                         float(row[5]), ty, sn,
                                         date_trips=date_trips)
        else:
            so.ids.append(stop_id)
        i_s_key[stop_id] = s_key
    csv_file.close()
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
        if from_stop_id and to_stop_id and\
                transfer_cost.get((from_stop_id, to_stop_id)) is None:
            cost = int(row[3])
            transfer_cost[(from_stop_id, to_stop_id)] = cost
            transfer_cost[(to_stop_id, from_stop_id)] = cost
    csv_file.close()
    return transfer_cost


def load_trips(stop_dict, i_s_key, tr_r_se, se_d):
    """Load the file stop_times.txt and return a dict."""
    trip_dict = dict()

    csv_file = open('stop_times.txt', 'r')
    csv_iter = csv.reader(csv_file, delimiter=',')
    _ = next(csv_iter)

    p = -1.1
    prev_trip_id = None
    # p_i = None
    p_key = None

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
            service_id = tr_r_se[trip_id][1]
            dates = se_d[service_id]
            trip_dict[trip_id] = trip.Trip(trip_id, dates)
        hms = row[2].split(':')
        trip_dict[trip_id].stop_times.append((stop_dict[r_key],
                                             (int(hms[0]), int(hms[1]),
                                              int(hms[2]))))
        # TODO: inspect
        # else:
        #     if stop_dict[r_key] not in stop_dict[p_key].nexts:
        #         stop_dict[p_key].nexts.append(stop_dict[r_key])
        # p_i = r_i
        p_key = r_key
        p = r
        prev_trip_id = trip_id
    csv_file.close()

    return trip_dict


def add_trips(trip_dict):
    """Add trips to each stop."""
    # Add trips to each stop
    # for t in trip_dict:
    for to in trip_dict.values():
        so = to.stop_times[0][0]
        for date in to.dates:
            trips = so.date_trips.get(date)
            if trips is None:
                trips = list()
                so.date_trips[date] = trips
            if to not in trips:
                trips.append(to)


def nexts_transfers(stop_dict, tf_c):
    """Add connections and some zero-transfers."""
    for so in stop_dict.values():
        for ns in so.nexts:
            # TODO: use len for precision
            if so not in ns.nexts:
                ns.nexts.append(so)
            # TODO: inspect
            if len(so.ids) > 1:
                s_key = (so.name, so.sn)
                key = (s_key, s_key)
                if tf_c.get(key) is None:
                    tf_c[key] = 0
    for s_key in stop_dict:
        so = stop_dict[s_key]
        if len(so.nexts) > 2:
            if so not in so.transfers:
                so.transfers.append(so)
            key = (s_key, s_key)
            if tf_c.get(key) is None:
                tf_c[key] = 0


def connect_stops(stop_dict, tf_c, lines=None, stops=None):
    """Add connections."""
    not_all = False
    if (lines and len(lines) > 0) or (stops and len(stops) > 0):
        not_all = True
    # Transfer
    for (key_0, key_1) in tf_c:
        if key_0 is None or key_1 is None:
            continue
        if not_all and\
                ((not((key_0 in stops and key_1 in stops) or
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


def dijkstra(stop_dict, trip_dict, tf_c, srcs, the_moment, d=None,
             patience=datetime.timedelta(hours=4)):
    """Compute the time."""
    M = datetime.datetime.max
    current = list()
    if d is None:
        d = dict()
        for k in stop_dict:
            d[k] = (None, None, M)  # so, to, datetime
        for src in srcs:
            d[src] = (None, None, the_moment)
            current.append(src)

    while len(current) > 0:
        next_level = list()
        # next_level = set()
        for c_key in current:
            cs = stop_dict[c_key]
            limit_date = (d[c_key][2] + patience).date()
            nt_d_t = cs.line_dijkstra(d[c_key][2], limit_date=limit_date)
            # Infinite mode, not recommended
            # nt_d_t = cs.line_dijkstra(d[c_key][2])
            for s_key in nt_d_t:
                so = stop_dict[s_key]
                (next_trip, d_t) = nt_d_t[s_key]
                if d_t and d[s_key][2] > d_t:
                    d[s_key] = (cs, next_trip, d_t)
                    for ts in so.transfers:
                        t_key = (ts.name, ts.sn)
                        key = (t_key, s_key)
                        tt = datetime.timedelta(seconds=tf_c[key])
                        d_t = d[s_key][2] + tt
                        if d[t_key][2] > d_t:
                            d[t_key] = (so, None, d_t)
                            if t_key not in next_level:
                                next_level.append(t_key)
                            # next_level.add(t_key)
                        elif tf_c[key] == 0 and t_key != c_key:
                            if t_key not in next_level:
                                next_level.append(t_key)
                            # next_level.add(t_key)
        current = sorted(next_level, key=lambda s_key: d[s_key][2])
    return d


def get_path(d, src, dst, stop_dict):
    """Make a path and return a list."""
    paths = list()
    d_t = d[src][2]
    date = d_t.date()
    while d[dst][0]:
        path = list()
        (so, tr, d_t) = d[dst]
        sp_t_iter = iter(tr.stop_times)
        for v in sp_t_iter:
            if so == v[0]:
                t = datetime.time(v[1][0] % 24, v[1][1], v[1][2])
                dt = datetime.timedelta(days=v[1][0]//24)
                path.append((v[0], datetime.datetime.combine(date, t) + dt))
                break
        for v in sp_t_iter:
            v_key = (v[0].name, v[0].sn)
            t = datetime.time(v[1][0] % 24, v[1][1], v[1][2])
            dt = datetime.timedelta(days=v[1][0]//24)
            path.append((v[0], datetime.datetime.combine(date, t) + dt))
            if dst == v_key:
                break
        paths.append(path)
        dst = (d[dst][0].name, d[dst][0].sn)
    return paths


def show_path(d, dst):
    """Show a path to arrive to dst if it exists."""
    while True:
        if d[dst][0]:
            print(dst, '/', (d[dst][0].name, d[dst][0].sn), '/', d[dst][2])
            dst = (d[dst][0].name, d[dst][0].sn)
        else:
            break


def save_map(paths, where):
    """Save a html page to visualize the path."""
    try:
        import folium
        import random
    except ImportError:
        print('The module folium isn\'t available to save a map')
        return
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray',
              'black', 'lightgray']
    prev_color = None
    color = None
    once = False
    for path in paths:
        coordinates_list = list()
        for v in path:
            (so, d_t) = v
            coordinates_list.append((so.lat, so.lon))
        (so, _) = path[0]
        if not once:
            m = folium.Map(location=(so.lat, so.lon))
            once = True
        folium.Marker((so.lat, so.lon), popup=so.name).add_to(m)
        if len(path[0]) > 1:
            (so, _) = path[-1]
            folium.Marker((so.lat, so.lon), popup=so.name).add_to(m)
        while True:
            color = random.choice(colors)
            if color != prev_color:
                prev_color = color
                break
        folium.vector_layers.PolyLine(locations=coordinates_list, weight=5, color=color)\
            .add_to(m)
    m.save(where)


if __name__ == '__main__':
    start = time.time()
    se_d = service_date()
    end = time.time()
    print('service_date(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    r_ty_sn = route_type_sn(ty=[1])  # Only metro/subway
    # WARNING: no intensive tests have been done
    # r_ty_sn = route_type_sn(ty=[0, 1, 2])  # 0 tram, 1 subway/metro, 2 rail
    # r_ty_sn = route_type_sn(ty=[3])  # 3 bus WARNING: it doesn't work
    # r_ty_sn = route_type_sn()
    end = time.time()
    print('route_type(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    tr_r_se = trip_route_service(r_ty_sn)
    end = time.time()
    print('trip_route_service(): done in',
          datetime.timedelta(seconds=end-start))

    start = time.time()
    s_tr = stop_trip(tr_r_se)
    end = time.time()
    print('stop_trip(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    stop_dict, i_s_key = load_stops(s_tr, tr_r_se, r_ty_sn)
    end = time.time()
    print('load_stops(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    tf_c = transfer(i_s_key)
    end = time.time()
    print('transfer(): done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    trip_dict = load_trips(stop_dict, i_s_key, tr_r_se, se_d)
    end = time.time()
    print('loaded trips: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    add_trips(trip_dict)
    end = time.time()
    print('trips added: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    nexts_transfers(stop_dict, tf_c)
    end = time.time()
    print('Fix tf_c: done in', datetime.timedelta(seconds=end-start))

    start = time.time()
    stops = [('Jussieu', '7'), ('Jussieu', '10'), ("Place d'Italie", '6'),
             ("Place d'Italie", '7')]
    lines = ['7', '10', '6']
    # connect_stops(stop_dict, tf_c, lines=lines, stops=stops)
    connect_stops(stop_dict, tf_c)
    end = time.time()
    print('connect lines: done in', datetime.timedelta(seconds=end-start))

    print('Number of stops: ', len(stop_dict))
    print('Number of trips: ', len(trip_dict))

    # the_day = datetime.datetime(2019, 3, 13, 9, 0)
    the_day = datetime.datetime(2019, 3, 20, 9, 0)
    # TODO: find 24h+
    # the_day = datetime.datetime(2019, 6, 3, 0, 1)
    # s_key = i_s_key[1907]
    # print(stop_dict[s_key])

    start = time.time()
    # s_key = i_s_key[1907]
    s_key = ('Villejuif-Louis Aragon', '7')
    # s_key = ('Jussieu', '10')
    # t_key = ('Jussieu', '7')
    # s_key = ('Jussieu', '7')
    # s_key = ("Porte d'Auteuil", '10')
    d = dijkstra(stop_dict, trip_dict, tf_c, {s_key}, the_day)
    end = time.time()
    print('dijkstra(): done in', datetime.timedelta(seconds=end-start))
    limit = len('Villejuif-Paul Vaillant Couturier (Hôpital Paul Brousse)')
    lines = ['7', '10', '6']
    not_all = not True
    for s_key in d:
        if not_all and s_key[1] not in lines:
            continue
        if d[s_key][0] is not None and d[s_key][1] is not None:
            print(s_key, stop_dict[s_key].ty, ' ' * (limit - len(s_key[0])),
                  d[s_key][0].name, d[s_key][1].id, d[s_key][2])
        elif d[s_key][0] is not None:
            print(s_key, stop_dict[s_key].ty, ' ' * (limit - len(s_key[0])),
                  d[s_key][0].name, d[s_key][1], d[s_key][2])
        else:
            print(s_key, stop_dict[s_key].ty, ' ' * (limit - len(s_key[0])),
                  d[s_key][0], d[s_key][1], d[s_key][2])
    # dst = ('Maison Blanche', '7')
    dst = ('Mairie d\'Ivry', '7')
    # dst = ("Eglise d'Auteuil", '10')
    show_path(d, dst)
    path = get_path(d, s_key, dst, stop_dict)
    save_map(path, '/tmp/index.html')
    the_date = the_day.date()
    for s_key in d:
        v = d[s_key]
        so = stop_dict[s_key]
        if v[0] is None:
            print(s_key, len(so.nexts), len(so.transfers))
            trips = so.date_trips.get(the_date)
            dates = sorted(so.date_trips)
            for date in dates:
                print(date, len(so.date_trips[date]))
            if trips is None:
                print(trips)
            else:
                print(len(trips))
            for ns in so.nexts:
                print('next', (ns.name, ns.sn))
            for ts in so.transfers:
                print('tran', (ts.name, ts.sn))

    sys.exit(0)
