from hashlib import new
import pandas as pd
import re

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
    new_date = ''
    new_date += str(months[date.split()[0]])
    new_date += '/'
    day = re.search(' (.*),', date).group(1)
    new_date +=  day if len(day) == 2 else '0'+day
    new_date += '/'
    new_date += date[-5:-1]
    return new_date

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
                data_line = [state_name, splitted_line[0], splitted_line[1]] # State, town, street
                data_line.append(splitted_line[2].split(' (')[0]) # Category
                data_line.append(re.search('#(.*), opened', splitted_line[2]).group(1)) # Store id
                date = splitted_line[2].split('opened ')[1] # opening date
                data_line.append(new_format(date))
                data_line.append(None) # closing date
                data.append(data_line)
            except:
                reluctant_lines.append(line)

df_current = pd.DataFrame(data, columns=['State', 'Town', 'Street', 'Category', 'Store_id', 'Opening_date', 'Closing_date'])

df_reluctant = pd.DataFrame(reluctant_lines)
df_reluctant.to_csv('reluctant_lines')


## Former
data = []


by_states = former.split('!')

for state in by_states:
    lines = state.split('\n')
    state_name = us_state_to_abbrev[lines[0]]
    for line in lines[1:]:
        if line != '':
            splitted_line = line.split(' - ')

            data_line = [state_name, splitted_line[0], splitted_line[1]] # State, town, street
            data_line.append(splitted_line[2].split(' (')[0]) # Category
            
            # Store id
            try:
                raw = re.search('#(.*), ', splitted_line[2]).group(1)
                store_id = raw[:3] if raw[3]==',' else raw[:4] #some id are 3 character long, other 4
                data_line.append(store_id)
            except:
                data_line.append('unknown')
            
            # Opening date
            if 'opened' in splitted_line[2]:
                raw_opening_date = re.search('opened (.*), closed', splitted_line[2]).group(1)
                try: # Try to normalize the format, if day, month and year give
                    opening_date = new_format(raw_opening_date+')')
                except: # Else append the pieces of information
                    opening_date = raw_opening_date
                data_line.append(opening_date)
            else:
                data_line.append('unknown')

            # Closing date
            raw_closing_date = re.search('closed (.*)', splitted_line[2]).group(1)
            closing_date = raw_closing_date[:raw_closing_date.find(')')]
            try:
                closing_date = new_format(closing_date+')')
            except:
                pass
            data_line.append(closing_date)
            
            data.append(data_line)

df_former = pd.DataFrame(data, columns=['State', 'Town', 'Street', 'Category', 'Store_id', 'Opening_date', 'Closing_date'])


df = pd.concat((df_current, df_former))
df = df.set_index('Store_id')
"""
# Closing dates 2016

df_closing_date = pd.read_csv('wallmart_exit2016_données_traitées.csv')

for index, store in df[df.Closing_date == '2016'].iterrows():
    closing_date = '2016'
    if store['Town'] in 
    store['Closing_date'] = closing_date
"""
df.to_csv('fandom_traitées.csv')
