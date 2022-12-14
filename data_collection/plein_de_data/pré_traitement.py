from hashlib import new
import pandas as pd
import re
import datetime

# Pour wallmart_exit2016.txt :
"""
with open('wallmart_exit2016.txt') as f:
    content = f.read()

content = content.replace('    \n', '\n')
content = content.replace('   \n', '\n')
content = content.replace('#', '')
content = content.replace(':', ',')
content = content.replace('    ', ', ')
categories = content.split('!')

data =[]

for category in categories:
    lines = category.split('\n')
    category_name = lines[0]
    for line in lines[1:]:
        splitted_line = line.split(', ')
        if line!='':
            data.append(splitted_line)

df = pd.DataFrame(data, columns=['Store_id', 'Street', 'Town', 'State', 'Closing_date']).set_index('Store_id')

df.to_csv('wallmart_exit2016_données_traitées.csv')
"""

# Pour fandom.txt :

with open('fandom.txt') as f:
    content = f.read()

current = content.split('####\n')[0]
former = content.split('####\n')[1]

# tools :
months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05','June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
}
us_state_to_abbrev = {
    "Alabama": "AL","Alaska": "AK","Arizona": "AZ","Arkansas": "AR","California": "CA","Colorado": "CO","Connecticut": "CT","Delaware": "DE","Florida": "FL","Georgia": "GA","Hawaii": "HI","Idaho": "ID","Illinois": "IL","Indiana": "IN","Iowa": "IA","Kansas": "KS","Kentucky": "KY","Louisiana": "LA","Maine": "ME","Maryland": "MD","Massachusetts": "MA","Michigan": "MI","Minnesota": "MN","Mississippi": "MS","Missouri": "MO","Montana": "MT","Nebraska": "NE","Nevada": "NV","New Hampshire": "NH","New Jersey": "NJ","New Mexico": "NM","New York": "NY","North Carolina": "NC","North Dakota": "ND","Ohio": "OH","Oklahoma": "OK","Oregon": "OR","Pennsylvania": "PA","Rhode Island": "RI","South Carolina": "SC","South Dakota": "SD","Tennessee": "TN","Texas": "TX","Utah": "UT","Vermont": "VT","Virginia": "VA","Washington": "WA","West Virginia": "WV","Wisconsin": "WI","Wyoming": "WY","District of Columbia": "DC","American Samoa": "AS","Guam": "GU","Northern Mariana Islands": "MP","Puerto Rico": "PR","United States Minor Outlying Islands": "UM","U.S. Virgin Islands": "VI",
}

def new_format(date):
    month = int(months[date.split()[0]])
    day = int(re.search(' (.*),', date).group(1))
    year = int(date[-5:-1])
    return datetime.date(year, month, day)

data = []
reluctant_lines = []

## Current

by_states = current.split('!')


for state in by_states:
    lines = state.split('\n')
    state_name = us_state_to_abbrev[lines[0]]
    for line in lines[1:]:
        if line != '':
            try:
                splitted_line = line.split(' - ')

                # State
                data_line = [state_name]

                # Town
                data_line.append(splitted_line[0])

                # Street
                data_line.append(splitted_line[1])
                
                # Category
                data_line.append(splitted_line[2].split(' (')[0])

                # Store id
                data_line.append(re.search('#(.*), opened', splitted_line[2]).group(1))

                # Opening date
                date = splitted_line[2].split('opened ')[1]
                data_line.append(new_format(date))

                # Closing date
                data_line.append(None)
                data.append(data_line)

            except:
               reluctant_lines.append(line)

df_current = pd.DataFrame(data, columns=['State', 'Town', 'Street', 'Category', 'Store_id', 'Opening_date', 'Closing_date'])




## Former
data = []


by_states = former.split('!')

for state in by_states:
    lines = state.split('\n')
    state_name = us_state_to_abbrev[lines[0]]
    for line in lines[1:]:
        if line != '':
            splitted_line = line.split(' - ')
            
            # State
            data_line = [state_name]

            # Town
            data_line.append(splitted_line[0])

            # Street
            data_line.append(splitted_line[1])

            # Category
            data_line.append(splitted_line[2].split(' (')[0])
            
            # Store id
            try:
                raw = re.search('#(.*), ', splitted_line[2]).group(1)
                store_id = raw[:3] if raw[3]==',' else raw[:4] #some id are 3 character long, other 4
                data_line.append(store_id)
            except:
                data_line.append(pd.NaT)
            
            # Opening date
            if 'opened' in splitted_line[2]:

                raw_opening_date = re.search('opened (.*), closed', splitted_line[2]).group(1)
                try: # Try to normalize the format, if day, month and year give
                    opening_date = new_format(raw_opening_date+')')
                except: # Else append the pieces of information
                    opening_date = pd.NaT
                    reluctant_lines.append(line)
                data_line.append(opening_date)
            else:
                data_line.append(pd.NaT)

            # Closing date
            raw_closing_date = re.search('closed (.*)', splitted_line[2]).group(1)
            closing_date = raw_closing_date[:raw_closing_date.find(')')]
            try:
                closing_date = new_format(closing_date+')')
            except:
                reluctant_lines.append(line)
            data_line.append(closing_date)
            
            data.append(data_line)

df_former = pd.DataFrame(data, columns=['State', 'Town', 'Street', 'Category', 'Store_id', 'Opening_date', 'Closing_date'])


df = pd.concat((df_current, df_former))
df.Opening_date = pd.to_datetime(df.Opening_date, errors='coerce', format = '%Y-%m-%d')
df.Closing_date = pd.to_datetime(df.Closing_date, errors='coerce', format = '%Y-%m-%d')


# Merging for County, latitude and longitude
uscities = pd.read_csv('../../data_display/uscities.csv')[["city", "state_id", "lat", "lng", "county_name", "county_fips"]]

df = pd.merge(df, uscities,  how='inner', left_on=['Town','State'], right_on = ['city','state_id'])


# Cosmetic finalization
df = df.rename(columns={'lat': 'Town_lat', 'lng': 'Town_lng', 'county_name': 'County_name', 'county_fips': 'County_fips'})[['State', 'County_name', 'County_fips', 'Town', 'Town_lat', 'Town_lng', 'Street', 'Category', 'Store_id', 'Opening_date', 'Closing_date']]
df = df.set_index('Store_id')
df.to_csv('fandom_traitées.csv')


df_reluctant = pd.DataFrame(reluctant_lines)
df_reluctant.to_csv('reluctant_lines.csv')