import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Walmart_US_map_with_counties import geo_counties_density

#Map
geo_counties_density.explore(
     column="Population Density (people per square kilometer)",  
     scheme="Quantiles", 
     tooltip =["GEOID","NAME_x","State","Population Density (people per square kilometer)"],
#     style_kwds = {'Weight' : 0.01},
     legend=True, # show legend
#    cmap = "jet",
     k=10, # use 10 bins
     legend_kwds=dict(colorbar=False), # do not use colorbar
)

print("For each city where there is at least an entry or exit, the circle's radius is proportional to the number of stores' openings and closings (stores' changes) in the city for year 2016 (from January, 1, 2016 to January 31, 2017). This number is displayed when hovering over the circle on the map.")