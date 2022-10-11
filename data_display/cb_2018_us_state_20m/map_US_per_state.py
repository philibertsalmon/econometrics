import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv(r'C:\Users\inesn\Documents\Mines\2A\TR\econometrics\data_collection\plein_de_data\fandom_traitées.csv', parse_dates = ["Opening_date", "Closing_date"])

uscities = pd.read_csv('uscities.csv')
uscities = uscities[["city", "state_id", "lat", "lng"]]

#creating boolean columns for entry/exit in 2016 (no entry and exit in 2016 for a single store)
df['opened_2016'] = (df.Opening_date>='2015-01-31')&(df.Opening_date<='2017-01-31')
df['closed_2016'] = (df.Closing_date>='2015-01-31')&(df.Closing_date<='2017-01-31')

#keeping only stores with entry/exit in 2016
df = df[df.opened_2016 | df.closed_2016]

#designing the red-orange-green color code

#assuming that there isn't 2 cities with same name in same state in our database
df_test = df.groupby(['Town','State'])['Store_id'].count().rename("Stores' changes").to_frame()
df2 = df.groupby(['Town','State'])['opened_2016'].any().rename('opened_2016_city').to_frame()
df3 = df.groupby(['Town','State'])['closed_2016'].any().rename('closed_2016_city').to_frame()
df4 = df2.merge(df3, how = "outer", on = ['Town','State'])
df4 = df4.merge(df_test, how = "outer", on = ['Town','State'])

def legend(x):
    if x == 1 :
        return 'Entry only'
    if x == 2 :
        return 'Exit only'
    return 'Both entry and exit'

legend_v = np.vectorize(legend)
df4['Walmart store entry or/and exit (2016, per city)']= legend_v(1*df4['opened_2016_city']+2*df4['closed_2016_city'])

map_data = pd.merge(df4, uscities,  how='inner', left_on=['Town','State'], right_on = ['city','state_id'])
map_data = map_data.rename(columns={'city': 'City', 'state_id': 'State', 'lat' : 'Latitude', 'lng' : 'Longitude'})

#plotting the map

geo_map_data = gpd.GeoDataFrame(
    map_data, geometry=gpd.points_from_xy(map_data.Longitude, map_data.Latitude))
geo_map_data.crs = 'EPSG:4326'
geo_map_data.explore(column='Walmart store entry or/and exit (2016, per city)', tooltip = ["Stores' changes","City","State","Latitude","Longitude"], cmap=["blue","green","red"], 
                     style_kwds={"style_function": lambda x: {"radius": x["properties"]["Stores' changes"]*2}})

print("For each city where there is at least an entry or exit, the circle's radius is proportional to the number of stores' openings and closings (stores' changes) in the city for year 2016 (from January, 1, 2016 to January 31, 2017). This number is displayed when hovering over the circle on the map.")