# Assignment Plots
## Marios Paschalidis Python Workearly Assignment
### Imports
```commandline
import mysql.connector
import pandas as pd
import os
```
### MYSQL Server Connection & Database Creation
```commandline

cnx = mysql.connector.connect(user=os.environ['MYSQLUSER'], password=os.environ['MYSQLPASS'],
                                 host='127.0.0.1', database = DB_NAME)
                            
fd = open('finance_liquor_sales.sql','r')
sqlscript = fd.read()
fd.close()

sqlCommands = sqlscript.split(';')

for command in sqlCommands:
    try:
        cursor.execute(command)
    except:
        print('Command skipped',command)
```

### Importing Table to Pandas Dataframe

```commandline
cursor.execute('use liquorSales')
cursor.execute('select * from finance_liquor_sales')
fields = [field_md[0] for field_md in cursor.description]
df = pd.DataFrame(data=cursor.fetchall(),
                  columns=fields)

cnx.close()
```


```commandline
df.head()

  invoice_and_item_number       date  ...  volume_sold_liters volume_sold_gallons
0         INV-31797900035 2020-11-10  ...                0.37                0.09
1         INV-23548800092 2019-11-27  ...                6.00                1.58
2         INV-23609300026 2019-12-02  ...                1.12                0.29
3         INV-39482900037 2021-08-24  ...                0.24                0.06
4         INV-39520400088 2021-08-25  ...                4.00                1.05

[5 rows x 24 columns]
```


### Assigning Longitute & Latitude to Each City

```commandline
df['year'] = df.date.apply(lambda x: x.year)
df.loc[:,'city'] = df.city.str.upper()
df.loc[:,'county'] = df.county.str.upper()
cities = df.city.unique()
df = df.groupby(['county','city'])[['bottle_volume_ml',
       'state_bottle_cost', 'state_bottle_retail', 'bottles_sold',
       'sale_dollars', 'volume_sold_liters', 'volume_sold_gallons']].mean()


uscities = open('mariusp_assignment\\uscities.csv','r')
ctdf = pd.read_csv(uscities)
uscities.close()
ctdf.loc[:,'city'] = ctdf.city.str.upper()
ctdf.loc[:,'county_name'] = ctdf.county_name.str.upper()

ctdf = ctdf[ctdf.city.isin(cities)][['county_name','city','lng','lat']]
ctdf.rename(columns={'county_name':'county'},inplace=True)
ctdf = ctdf.set_index(['county','city'])

df = df.join(ctdf,on=['county','city'])

df.reset_index(inplace=True)
```

### Plotting Bubble Map For Bottle Sold by City

```commandline
df['text'] = df.city + ', ' + df.county + '\nBottles Sold: ' + df.bottles_sold.astype(str)

import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(go.Scattergeo(
    locationmode='USA-states',
    lon=df['lng'],
    lat=df['lat'],
    text=df['text'],
    marker=dict(
        size=df['bottles_sold']*10,
        sizemode='area'
    )
))
fig.update_layout(
        title_text = 'Bottles Sold<br>(Click legend to toggle traces)',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )


fig.write_html('BottlesSoldMap.html')
```

<img src="C:\Users\pasch\PycharmProjects\Final-Assignment\mariusp_assignment\FigureScreenshot.png" title="Figure Screenshot"/>


