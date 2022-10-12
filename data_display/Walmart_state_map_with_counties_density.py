import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from Walmart_US_map import geo_map_data
from Walmart_US_map_with_counties import geo_counties_density

#state to plot
state = "Alabama"

#Map
geo_counties_density2 = geo_counties_density[geo_counties_density.State == state]
geo_map_data2= geo_map_data[geo_map_data.state_name == state]
m = geo_counties_density2.explore(column="Population Density (people per square kilometer)",  
                                  scheme="Quantiles", 
                                  tooltip =["GEOID","NAME_x","State","Population Density (people per square kilometer)"],
#                                 style_kwds = {'Weight' : 0.01},
                                  legend=True, # show legend
#                                 cmap = "jet",
                                  k=10, # use 10 bins
                                  legend_kwds={'colorbar': False, 'loc': 'lower right'}, # do not use colorbar
                                  name = "Counties Density"
                                 )

geo_map_data2.explore(m=m, 
                      column='Walmart store entry or/and exit (2016, per city)', 
                      tooltip = ["Stores' changes","City","State","Latitude","Longitude"], 
                      cmap=["blue","green","red"], 
                      style_kwds={"style_function": lambda x: {"radius": x["properties"]["Stores' changes"]*2}},
                      name = "Walmart Data")

folium.LayerControl().add_to(m)  # use folium to add layer control

m  # show map

print("For each city where there is at least an entry or exit, the circle's radius is proportional to the number of stores' openings and closings (stores' changes) in the city for year 2016 (from January, 1, 2016 to January 31, 2017). This number is displayed when hovering over the circle on the map.")