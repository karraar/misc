#!/usr/bin/env python3

import folium
import pandas

data = pandas.read_csv("Volcanoes.txt")
lat = list(data["LAT"])
lon = list(data["LON"])
elev = list(data["ELEV"])


def color_producer(elevation):
    if elevation < 1000:
        return 'green'
    elif 1000 <= elevation < 3000:
        return 'orange'
    else:
        return 'red'


map = folium.Map(location=[38.58, -99.09], zoom_start=5) #, tiles="Mapbox Bright")

fgv = folium.FeatureGroup(name="Volcanoes")

for lt, ln, el in zip(lat, lon, elev):
    fgv.add_child(folium.CircleMarker(location=[lt, ln],
                                     radius=6,
                                     popup=str(el) + " m",
                                     tooltip=str(el) + " m",
                                     fill_color=color_producer(el),
                                     color='grey',
                                     fill_opacity=0.7))

#fg.add_child(folium.GeoJson(data=open('world.json', 'r').read()))

map.add_child(fgv)

map.add_child(folium.LayerControl())
map.save("map.html")
