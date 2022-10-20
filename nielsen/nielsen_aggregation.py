import pandas as pd
import numpy as np
from tools_nielsen import *

## LOADING THE DATA
panelist = pd.read_table("../../Nielsen/panelists_2016.tsv").set_index('Household_Cd')[['Fips_State_Cd', 'Fips_State_Desc', 'Fips_County_Cd', 'Fips_County_Desc', 'Panelist_ZipCd']]
panelist['household_county_fips'] = np.vectorize(int)(panelist.Fips_State_Cd * 1e3 + panelist.Fips_County_Cd)
panelist['household_zip3'] = panelist.Panelist_ZipCd // 100
panelist = panelist[['Fips_State_Desc', 'Fips_County_Desc', 'household_county_fips', 'household_zip3']].rename(columns={'Fips_State_Desc': 'household_state', 'Fips_County_Desc': 'household_county'})

purchases = pd.read_csv("../../Nielsen/purchases_subset_2016.csv")
purchases['upc_price'] = purchases.total_price_paid / purchases.quantity
purchases = purchases[['trip_code_uc', 'upc', 'upc_ver_uc', 'upc_price']]

trips = pd.read_table("../../Nielsen/trips_2016.tsv", parse_dates=['purchase_date']).set_index('trip_code_uc')[['purchase_date', 'retailer_code', 'store_code_uc', 'store_zip3', 'household_code']]

# Some store are unnumerotated - we drop them from the data
print(f"Proportion of unnumerotated stores : {round(len(trips[trips.store_code_uc==0])/len(trips),4)*100}% (data droped, over {len(trips)} trips)")
trips = trips[trips.store_code_uc != 0]


## GETTING THE STORE STATE
zip_to_state = pd.read_table('zip_prefixes.txt', header=0, names=['zip3','state', 'distib_center', 'towns'])[['zip3', 'state']]
# From the zip3 code, the state can be determined (cf. zip_prefixes.txt)

trips = trips.merge(zip_to_state, left_on='store_zip3', right_on='zip3')[['purchase_date', 'retailer_code', 'store_code_uc', 'state', 'store_zip3', 'household_code']].rename(columns={'state': 'store_state'})


## GETTING THE STORE COUNTY - mode
# The store county is assumed to be the one where the maximum of households that visited this store comes form.

# We first merge trips and panelist to get the origin county of the households.
trips_merged = trips.merge(panelist, left_on='household_code', right_on='Household_Cd')[['retailer_code', 'store_code_uc', 'store_state', 'store_zip3', 'household_state', 'household_county_fips', 'household_county', 'household_zip3']]

# Then, we delete all the househoslds that do not come from the store state.
before_deletion = len(trips_merged)
trips_state = trips_merged[trips_merged.household_state == trips_merged.store_state] # TOUT RENOMMER
suppression_rate_state = 1-len(trips_state)/before_deletion
print(f"Suppression rate : {round(suppression_rate_state, 4)*100}* (proportion of households that do not shop in their own state.)")

# Then, we delete all the housolds that do not come from the store zip3 zone.
trips_zip3 = trips_state[trips_state.household_zip3 == trips_state.store_zip3]
suppression_rate_zip3 = 1-len(trips_zip3)/len(trips_state)
suppression_rate = 1 - (1 - suppression_rate_state) * (1 - suppression_rate_zip3)
print(f"Suppression rate : {round(suppression_rate, 4)*100}% (proportion of households that do not shop in their own zip3 zone.)")

# Then, we select the mode :

store_loc = trips_zip3.groupby(['store_code_uc'])[['retailer_code', 'store_state', 'household_county_fips', 'household_county']].agg(my_mode).rename(columns={'household_county_fips': 'guessed_store_county_fips', 'household_county': 'guessed_store_county'})

stat = df.groupby(['store_code_uc'])[['household_county_fips', 'household_county']].agg(pd.Series.value_counts)
stat['max_obs'] = stat.household_county.apply(my_max)
stat['nb_obs'] = stat.household_county.apply(my_sum)
stat['max_freq'] = stat.max_obs / stat.nb_obs
stat['distinct_counties'] = stat.household_county.apply(my_len)
stat['criteria'] = stat.max_obs >= 4 / 3 * (stat.nb_obs - (stat.distinct_counties + 2) - stat.nb_obs)

stat['nb_min'] = stat.household_county.apply(my_min)
stat['criteria'] = ((stat.max_obs >= 3 * (stat.nb_obs - (stat.distinct_counties - 2)*stat.nb_min - stat.max_obs)) & (stat.distinct_counties!=1)) | ((stat.distinct_counties==1) & (stat.nb_obs>=4))
