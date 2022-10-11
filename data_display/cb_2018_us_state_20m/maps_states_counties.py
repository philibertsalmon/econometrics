import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from map_US_per_state import geo_map_data, cmap

#counties basemap
shape_path = 'cb_2018_us_county_5m.shp'
shape = gpd.read_file(shape_path)

#plot state by state
geo_map_data['State_nb']= geo_map_data['county_fips'].astype(str).str[0:-3]
for state in geo_map_data.State.unique():
    fig = plt.figure()
    geo_map_data2= geo_map_data[geo_map_data.State == state]
    statefp = geo_map_data2['State_nb'].iloc[0]
    if len(statefp)==1:
        statefp = '0'+statefp
    base = shape[shape.STATEFP == statefp].boundary.plot(figsize=(18, 9), linewidth = 0.5)
    ax = geo_map_data2.plot(ax=base, marker='o', column ='Walmart store entry or/and exit (2016, per city)', legend=True, markersize=(geo_map_data["Stores' changes"]*20), cmap = cmap, alpha = 1, edgecolors = "black", linewidth = 0.5)
    plt.xlabel("Longitude (°)")
    plt.ylabel("Latitude (°)")
    plt.title(f"{state} - Walmart stores exit and entry per city (January, 1, 2016 - January 31, 2017)")
    plt.show()