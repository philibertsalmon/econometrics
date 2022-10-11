import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from map_US_per_state import geo_map_data
from matplotlib.colors import LinearSegmentedColormap

#counties basemap
shape_path = 'cb_2018_us_county_5m.shp'
shape = gpd.read_file(shape_path)

#withdrawal of counties outside of continental America
mask = (shape.STATEFP=="02")|(shape.STATEFP=="15")|(shape.STATEFP=="60")|(shape.STATEFP=="69")|(shape.STATEFP=="66")|(shape.STATEFP=="78")|(shape.STATEFP=="72")
continent_shape = shape.drop(shape[mask].index)

continent_shape = continent_shape.dropna()

#dots' colors
def legend2(x):
    if x == 'Entry only' :
        return 0.6
    if x == 'Exit only' :
        return 1
    return 0

legend2_v = np.vectorize(legend2)
geo_map_data['color']= legend2_v(geo_map_data['Walmart store entry or/and exit (2016, per city)'])
cmap = LinearSegmentedColormap.from_list(
    'mycmap', [(0, 'blue'), (0.6, 'green'), (1, 'red')])


#plot continental US
cont_geo_map_data= geo_map_data.drop(geo_map_data[geo_map_data.State == "AK"].index)
base = continent_shape.boundary.plot(figsize=(15, 7), linewidth = 0.3, zorder = 1)
ax = cont_geo_map_data.plot(ax=base, marker='o', column ='Walmart store entry or/and exit (2016, per city)', legend=True, categorical = True, markersize=(cont_geo_map_data["Stores' changes"]*20), cmap = cmap, edgecolors = "black", linewidth = 0.3, zorder=2)
plt.xlabel("Longitude (°)")
plt.ylabel("Latitude (°)")
plt.title("Walmart stores exit and entry per city in the contiguous United States (January, 1, 2016 - January 31, 2017)")
plt.show()