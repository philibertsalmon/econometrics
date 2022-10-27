#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


# In[35]:


nielsen15 = pd.read_csv('../../Nielsen/aggregated_nielsen_2015.csv')
nielsen16 = pd.read_csv('../..//Nielsen/aggregated_nielsen_2016.csv')
nielsen15['year'] = 2015
nielsen16['year'] = 2016

nielsen = pd.concat((nielsen15, nielsen16))


# In[36]:


density_path = r"C:\Users\inesn\Documents\Mines\2A\TR\econometrics\data_collection\plein_de_data\Average_Household_Size_and_Population_Density_-_County.csv"
density = pd.read_csv(density_path)


# In[37]:


density = density[["GEOID", "B01001_calc_PopDensity"]]


# In[41]:


# We choose to focus on milk prices
milk = nielsen[nielsen.product_group_descr == 'MILK']
#print(milk.shape[0])


# In[40]:


milk_d = pd.merge(milk, density,  how='inner', left_on='guessed_store_county_fips', right_on='GEOID')
#print(milk_d.shape[0])
#milk_d.head()


# In[43]:


## Entriy/exit dates
fandom = pd.read_csv('../data_collection/plein_de_data/fandom_traitées.csv', parse_dates=['Opening_date', 'Closing_date'])[['State', 'County_name', 'County_fips', 'Opening_date', 'Closing_date']]

# We drop the state in which we do not trust our data (some mistakes stil remain)
fandom = fandom[~np.isin(fandom.State, ('CA', 'GA', 'KS', 'LA', 'TX'))]

# We concentrate our study on the movements (entries & exits) during the fiscal years 2015 and 2016
movements = fandom[((fandom.Opening_date >= '2015-01-31') & (fandom.Opening_date <= '2017-01-31')) | ((fandom.Closing_date >= '2015-01-31') & (fandom.Closing_date <= '2017-01-31'))]
#movements['year'] = movements.Opening_date.dt.year
#movements['month'] = movements.Opening_date.dt.month


# In[66]:


# The control group is composed by all states where nothing (no entry nor exit) happened.
control = milk_d[~np.isin(milk_d.guessed_store_county_fips, movements)].copy()
print(f"Size of the control group: {len(control.guessed_store_county_fips.unique())}.")


# The treatment group is composed by the states where one entry took place in 2016 and where this entry is the only movement
count = movements.groupby('County_fips').count()
count = count[count.Opening_date + count.Closing_date == 1] # No more than one movement in the treatement group
treatment_movements = movements[(np.isin(movements.County_fips, count.index))]

treatment = milk_d[np.isin(milk_d.guessed_store_county_fips, treatment_movements.County_fips )].copy()
treatment = treatment.merge(treatment_movements, left_on='guessed_store_county_fips', right_on='County_fips')
print(f"Size of the treatment group: {len(treatment.guessed_store_county_fips.unique())}.")


# We create our dummies for the regression
control['treat'] = False
control['interaction'] = False
treatment['treat'] = True
treatment['interaction'] = (treatment.purchase_month > treatment.Opening_date.dt.month) & (treatment.purchase_year >= treatment.Opening_date.dt.year)
treatment.describe()


# In[82]:


treatment_d = treatment[["GEOID","B01001_calc_PopDensity"]]
density_per_county_t = treatment_d.groupby("GEOID").agg(["mean"])
density_per_county_t.describe()


# In[83]:


#criterium for control group : values in same range as for treatment
min_d = density_per_county_t.min()[('B01001_calc_PopDensity','mean')]
max_d = density_per_county_t.max()[('B01001_calc_PopDensity','mean')]
print(min_d, max_d)
print(control.shape[0])
control_m = control[(control['B01001_calc_PopDensity']>=min_d)&(control['B01001_calc_PopDensity']<=max_d)]
print(control_m.shape[0], control_m.shape[0]/control.shape[0])


# In[86]:


first_quartile = density_per_county_t.quantile(q=0.25)[('B01001_calc_PopDensity','mean')]
third_quartile = density_per_county_t.quantile(q=0.75)[('B01001_calc_PopDensity','mean')]
control_m2 = control[(control['B01001_calc_PopDensity']>=first_quartile)&(control['B01001_calc_PopDensity']<=third_quartile)]
print(control_m2.shape[0], control_m2.shape[0]/control.shape[0])


# In[ ]:




