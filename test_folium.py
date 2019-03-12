#!/usr/bin/env python

# -*- coding: utf8 -*-

import folium

if __name__ == '__main__':
    c = [48.845968, 2.354807]
    #m = folium.Map(location=[48.845968, 2.354807], tiles='ex-UPMC', attr='Jussieu')
    m = folium.Map(location=[48.845968, 2.354807])
    folium.Marker([48.845968, 2.354807], popup='Jussieu').add_to(m)
    m.save('/tmp/index.html')
