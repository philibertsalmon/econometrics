import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd

#uscities df
uscities = pd.read_csv('uscities.csv')
uscities = uscities[["city", "state_id", "lat", "lng"]]

#our df
df = pd.read_csv('../../data_collection/plein_de_data/fandom_traitées.csv', parse_dates = ["Opening_date", "Closing_date"])

#creating boolean columns for entry/exit in 2016 (no entry and exit in 2016 for a single store)
df['opened_2016'] = (df.Opening_date>='2016-01-31')&(df.Opening_date<'2017-01-31')
df['closed_2016'] = (df.Closing_date>='2016-01-31')&(df.Closing_date<'2017-01-31')

#keeping only stores with entry/exit in 2016
df = df[df.opened_2016 | df.closed_2016]

#designing the red-orange-green color code and the size code
#assuming that there isn't 2 cities with same name in same state in our database
df_test = df.groupby(['Town','State'])['Store_id'].count().rename('count').to_frame()
df2 = df.groupby(['Town','State'])['opened_2016'].any().rename('opened_2016_city').to_frame()
df3 = df.groupby(['Town','State'])['closed_2016'].any().rename('closed_2016_city').to_frame()
df4 = df2.merge(df3, how = "outer", on = ['Town','State'])
df4 = df4.merge(df_test, how = "outer", on = ['Town','State'])
def legend(x):
    if x == 1 :
        return 'Entry'
    if x == 2 :
        return 'Exit'
    return 'Both'
legend_v = np.vectorize(legend)
df4['Walmart entry or/and exit (2016, per city)']= legend_v(1*df4['opened_2016_city']+2*df4['closed_2016_city'])
map_data = pd.merge(df4, uscities,  how='inner', left_on=['Town','State'], right_on = ['city','state_id'])

#plotting the map
geo_map_data = gpd.GeoDataFrame(
    map_data, geometry=gpd.points_from_xy(map_data.lng, map_data.lat))
geo_map_data.crs = 'EPSG:4326'
geo_map_data.explore(column='Walmart entry or/and exit (2016, per city)', cmap=["blue","green","red"], 
                     style_kwds={"style_function": lambda x: {"radius": x["properties"]["count"]*2}})

plt.show()