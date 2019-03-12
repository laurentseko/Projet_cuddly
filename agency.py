#!/usr/bin/env python

# -*- coding: utf8 -*-

import csv
import datetime

agencies = []
csv_file = open('agency.txt', 'r')
csv_iter = csv.reader(csv_file, delimiter=',')
header = next(csv_iter)
for row in csv_iter:
    agency = {}
    for k, v in zip(header, row):
        agency[k] = v
    agencies.append(agency)

print(agencies)
#print('agencies[0][\'a\']', agencies[0]['a'])
d = datetime.date(2019, 1, 1)
print(d)
