import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from Walmart_US_map import geo_map_data

#databases' treatment

#counties' data
shape_path = 'cb_2018_us_county_5m.shp'
shape = gpd.read_file(shape_path)
shape["GEOID"]=shape.STATEFP+shape.COUNTYFP
shape["GEOID"]=shape["GEOID"].astype(int)

#density data
density_path = r"C:\Users\inesn\Documents\Mines\2A\TR\econometrics\data_collection\plein_de_data\Average_Household_Size_and_Population_Density_-_County.csv"
density = pd.read_csv(density_path)
density = pd.merge(density, shape,  how='inner', on='GEOID')
density = density.rename(columns={"B01001_calc_PopDensity" : "Population Density (people per square kilometer)"})

#GeoDataFrame's creation

geo_counties_density = gpd.GeoDataFrame(density)
geo_counties_density.crs = 'EPSG:4326'

#Map

m = geo_counties_density.explore(
#    column="Population Density (people per square kilometer)",  
     scheme="Quantiles", 
     tooltip =["GEOID","NAME_x","State","Population Density (people per square kilometer)"],
#    style_kwds = {'Weight' : 0.01},
     color = '#f4d9a0',
     legend=True,
#    cmap = "jet",
     k=10, #use 10 bins
     style_kwds={'opacity' : 0.6, 'fillOpacity' : 0.1},
     legend_kwds=dict(colorbar=False), # do not use colorbar
     name = "Counties"
     )

geo_map_data.explore(m=m, 
                     column='Walmart store entry or/and exit (2016, per city)', 
                     tooltip = ["Stores' changes","City","State","Latitude","Longitude"], 
                     cmap=["blue","green","red"], 
                     style_kwds={"style_function": lambda x: {"radius": x["properties"]["Stores' changes"]*2}},
                     name = "Walmart Data"
                    )

#folium.TileLayer('Stamen Toner', control=True).add_to(m)  # use folium to add alternative tiles
folium.LayerControl().add_to(m)  # use folium to add layer control
m  # show map

print("For each city where there is at least an entry or exit, the circle's radius is proportional to the number of stores' openings and closings (stores' changes) in the city for year 2016 (from January, 1, 2016 to January 31, 2017). This number is displayed when hovering over the circle on the map.")