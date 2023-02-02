import mysql.connector
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go


DB_NAME = 'liquorSales'



cnx = mysql.connector.connect(user=os.environ['MYSQLUSER'], password=os.environ['MYSQLPASS'],
                                 host='127.0.0.1', database = DB_NAME)

cursor = cnx.cursor()


# fd = open('finance_liquor_sales.sql','r')
# sqlscript = fd.read()
# fd.close()
#
# sqlCommands = sqlscript.split(';')
#
# for command in sqlCommands:
#     try:
#         cursor.execute(command)
#     except:
#         print('Command skipped',command)


cursor.execute('use liquorSales')
cursor.execute('select * from finance_liquor_sales')
fields = [field_md[0] for field_md in cursor.description]
df = pd.DataFrame(data=cursor.fetchall(),
                  columns=fields)

cnx.close()



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
        title_text = 'Average Bottles Sold',
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )


fig.write_html('BottlesSoldMap.html')