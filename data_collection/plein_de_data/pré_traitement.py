import pandas as pd

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

df = pd.DataFrame(data, columns=['', 'Street', 'Town', 'State', 'Date of exit'])

df.to_csv('wallmart_exit2016_données_traitées.csv')"""
