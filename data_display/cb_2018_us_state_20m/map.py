import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# fond de carte us
shape_path = 'cb_2018_us_state_20m.shp'
shape = gpd.read_file(shape_path)
shape = shape.dropna()
shape = shape[~shape['NAME'].isin(['Alaska', 'Hawaii', 'Puerto Rico'])]

# cities df
uscities = pd.read_csv('uscities.csv')
uscities = uscities[["city", "state_id", "lat", "lng"]]

# our df
df = pd.read_csv(r'C:\Users\inesn\Documents\Mines\2A\TR\econometrics\data_collection\plein_de_data\fandom_traitées.csv', parse_dates = ["Opening_date", "Closing_date"])

#creating boolean columns for entry/exit in 2016 (no entry and exit in 2016 for a single store)
df['opened_2016'] = (df.Opening_date>='2016-01-31')&(df.Opening_date<'2017-01-31')
df['closed_2016'] = (df.Closing_date>='2016-01-31')&(df.Closing_date<'2017-01-31')

#keeping only stores with entry/exit in 2016
df = df[df.opened_2016 | df.closed_2016]

#designing the red-blue-green color code
df2 = df.groupby(['Town','State'])['opened_2016'].any().rename('opened_2016_city').to_frame()
df3 = df.groupby(['Town','State'])['closed_2016'].any().rename('closed_2016_city').to_frame()
df4 = df2.merge(df3, how = "outer", on = ['Town','State'])
def colors(x):
    if x == 1 :
        return 'g'
    if x == 2 :
        return 'r'
    return 'b'
colors_v = np.vectorize(colors)
df4['color']= colors_v(1*df4['opened_2016_city']+2*df4['closed_2016_city'])

#merging color data and location data
map_data = pd.merge(df4, uscities,  how='inner', left_on=['Town','State'], right_on = ['city','state_id'])

#getting a geodf
geo_map_data = gpd.GeoDataFrame(
    map_data, geometry=gpd.points_from_xy(map_data.lng, map_data.lat))
geo_map_data.crs = 'EPSG:4326'
geo_map_data = geo_map_data.to_crs(shape.crs)

#plot
base = shape.boundary.plot(figsize=(10, 5))
geo_map_data.plot(ax=base, marker='o', color=geo_map_data['color'], markersize=1);
plt.show()
