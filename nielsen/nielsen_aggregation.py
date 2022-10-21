import pandas as pd
import numpy as np
from tools_nielsen import *

######################## CHOOSING THE DATE ########################

year = 2016

###################################################################

## LOADING THE DATA
# Be careful to write the good file path, with the correct year
panelist = pd.read_table("../../Nielsen/panelists_2016.tsv").set_index('Household_Cd')[['Fips_State_Cd', 'Fips_State_Desc', 'Fips_County_Cd', 'Fips_County_Desc', 'Panelist_ZipCd']]
panelist['household_county_fips'] = np.vectorize(int)(panelist.Fips_State_Cd * 1e3 + panelist.Fips_County_Cd)
panelist['household_zip3'] = panelist.Panelist_ZipCd // 100
panelist = panelist[['Fips_State_Desc', 'Fips_County_Desc', 'household_county_fips', 'household_zip3']].rename(columns={'Fips_State_Desc': 'household_state', 'Fips_County_Desc': 'household_county'})

# Be careful to write the good file path, with the correct year
purchases = pd.read_csv("../../Nielsen/purchases_subset_2016.csv")
purchases['upc_price'] = purchases.total_price_paid / purchases.quantity
purchases = purchases[['trip_code_uc', 'upc', 'upc_ver_uc', 'upc_price']]

# Be careful to write the good file path, with the correct year
trips = pd.read_table("../../Nielsen/trips_2016.tsv", parse_dates=['purchase_date']).set_index('trip_code_uc')[['purchase_date', 'retailer_code', 'store_code_uc', 'store_zip3', 'household_code']]
initial_trips_len = len(trips)

# Some stores are not numbered - we drop them from the data
trips_non_null = trips[trips.store_code_uc != 0]
print(f"Trips - Proportion of unnumerotated stores : {round(len(trips[trips.store_code_uc==0]) / initial_trips_len,4)*100}% (data droped, over {len(trips)} trips)")


## GETTING THE STORE'S STATE
zip_to_state = pd.read_table('zip_prefixes.txt', header=0, names=['zip3','state', 'distib_center', 'towns'])[['zip3', 'state']]
# From the zip3 code, the state can be determined (cf. zip_prefixes.txt)

trips_non_null = trips.merge(zip_to_state, left_on='store_zip3', right_on='zip3')[['purchase_date', 'retailer_code', 'store_code_uc', 'state', 'store_zip3', 'household_code']].rename(columns={'state': 'store_state'})


## GETTING THE STORE'S COUNTY - mode
# The store's county is assumed to be the one where the maximum of households that purchased from this store comes from.

# We first merge trips and panelist to get the household's home county.
trips_merged = trips_non_null.merge(panelist, left_on='household_code', right_on='Household_Cd')[['retailer_code', 'store_code_uc', 'store_state', 'store_zip3', 'household_state', 'household_county_fips', 'household_county', 'household_zip3']]

# Then we delete all househoslds that do not come from the store's state.
trips_state = trips_merged[trips_merged.household_state == trips_merged.store_state]
suppression_rate_state = 1 - len(trips_state) / initial_trips_len
print(f"Trips - Suppression rate : {round(suppression_rate_state, 4)*100}% (after deleting households that do not shop in their own state.)")

# Then we delete all housolds that do not come from the store's zip3 zone.
trips_zip3 = trips_state[trips_state.household_zip3 == trips_state.store_zip3]
print(f"Trips - Suppression rate : {round((1 - len(trips_zip3)/initial_trips_len)*100, 2)}% (after deleting households that do not shop in their own zip3 zone.)")

# Then we select the mode (= for each store, county from where most of the store's purchasers come) :

store_loc = trips_zip3.groupby(['store_code_uc'])[['retailer_code', 'store_state', 'household_county_fips', 'household_county']].agg(my_mode).rename(columns={'household_county_fips': 'guessed_store_county_fips', 'household_county': 'guessed_store_county'})

stat = trips_zip3.groupby(['store_code_uc'])[['household_county_fips', 'household_county']].agg(pd.Series.value_counts)
stat['max_obs'] = stat.household_county.apply(my_max)
stat['nb_obs'] = stat.household_county.apply(my_sum)
stat['max_freq'] = stat.max_obs / stat.nb_obs
stat['distinct_counties'] = stat.household_county.apply(my_len)
stat['nb_min'] = stat.household_county.apply(my_min)
stat['criteria'] = ((stat.max_obs >= 3 * (stat.nb_obs - (stat.distinct_counties - 2) * stat.nb_min - stat.max_obs)) & (stat.distinct_counties!=1)) | ((stat.distinct_counties==1) & (stat.nb_obs>=4))


# We separate Walmart stores from others
store_loc['is_walmart'] = np.isin(store_loc.retailer_code, (6920, 848, 6905))


trips_loc = trips[trips.store_code_uc != 0].reset_index().merge(store_loc.reset_index(), on=['retailer_code', 'store_code_uc']).set_index('trip_code_uc')

# We want to drop all stores that do not pass our criteria, i.e. all stores whose location we're not sure of
trips_loc = trips_loc.reset_index().merge(stat[['criteria']], left_on='store_code_uc', right_index=True)
trips_loc = trips_loc[trips_loc.criteria][['trip_code_uc', 'purchase_date', 'retailer_code', 'store_code_uc', 'store_zip3', 'household_code', 'store_state', 'guessed_store_county_fips', 'guessed_store_county', 'is_walmart']]

print(f"Total trips suppression rate : {round(len(trips_loc)/initial_trips_len, 4) * 100}% (unnumerotated stores + criteria = False (unlocated stores))")


## ADDING UPC GROUP (= product category)

upc_descr = pd.read_table('../../Nielsen/nielsen_extracts/HMS/Master_Files/Latest/products.tsv', encoding = "ISO-8859-1")[['upc', 'upc_ver_uc', 'product_group_code', 'product_group_descr']]

# Some (rare) upc do not have any group (NaN). We drop them.
upc_descr = upc_descr[upc_descr.product_group_code.apply(str)!='nan']
upc_descr = upc_descr.astype({'product_group_code': int})

# A unique product is a combination of upc and upc_ver_uc. Two products having the same upc but a different upc_ver_uc usually are very very similar, but sometimes don't belong to the same group. In this case we drop them.
upc_descr = upc_descr.merge(upc_descr.groupby('upc')['product_group_descr'].nunique(), on='upc').rename(columns={'product_group_descr_y': 'nb_of_groups_per_upc', 'product_group_descr_x': 'product_group_descr'})
upc_descr = upc_descr[upc_descr.nb_of_groups_per_upc == 1][['upc', 'upc_ver_uc', 'product_group_code', 'product_group_descr']]

purchases = purchases.merge(upc_descr, on=['upc', 'upc_ver_uc'])



## AGGREGATING THE DATA

# Merging
prices = purchases.merge(trips_loc, on='trip_code_uc')[['trip_code_uc', 'purchase_date', 'is_walmart', 'store_code_uc', 'store_state', 'guessed_store_county', 'guessed_store_county_fips', 'upc', 'upc_ver_uc','product_group_descr', 'upc_price']]
prices['purchase_month'] = prices.purchase_date.dt.month
prices['purchase_year'] = year

avg = pd.DataFrame(prices.groupby(['is_walmart', 'store_state', 'guessed_store_county', 'guessed_store_county_fips', 'purchase_year', 'purchase_month', 'product_group_descr']).mean()[['upc_price']])

std = pd.DataFrame(prices.groupby(['is_walmart', 'store_state', 'guessed_store_county', 'guessed_store_county_fips', 'purchase_year', 'purchase_month', 'product_group_descr']).std()[['upc_price']]).rename(columns={'upc_price': 'upc_price_std'})

nb_obs = pd.DataFrame(prices.groupby(['is_walmart', 'store_state', 'guessed_store_county', 'guessed_store_county_fips', 'purchase_year', 'purchase_month', 'product_group_descr']).count()[['upc_price']]).rename(columns={'upc_price': 'nb_of_obs'})


avg_prices = avg.merge(std, left_index=True, right_index=True).merge(nb_obs, left_index=True, right_index=True)

print(avg_prices.head(50))

avg_prices.to_csv(f'aggregated_nielsen_{year}.csv')