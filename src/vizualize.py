import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# get iso country codes and convert them to dict
isocountry = pd.read_csv('./data/input/continents2.csv')
isocountry["cntr_trns"] = isocountry["name"].str.lower().str.strip().str.replace(" ", "")
isodict = dict(zip(isocountry["cntr_trns"], isocountry["alpha-3"]))
isocontinent = dict(zip(isocountry["alpha-3"], isocountry["region"]))
#isocontinent = dict(zip(isocountry["alpha-3"], isocountry["sub-region"]))

# add columns for transformed country names and add iso country code
data = pd.read_csv('./data/input/finaldatav01.csv')
data["COUNTRY_TRNS"] = data["COUNTRY"].str.lower().str.strip().str.replace(" ", "")
data["ALPHA3ISO"] = data["COUNTRY_TRNS"].apply(lambda x: isodict[x].replace('"', "").strip())
data["CONTINENT"] = data["ALPHA3ISO"].apply(lambda x: isocontinent[x])
data = data[data['REVENUE'].notna()]
data["REV_CALC"] = data["UNITS"] * data["UNIT_PRICE"]
data = data.drop_duplicates(subset=["FY", "STOCK_ABBREV","ALPHA3ISO"])
#data["SCALE"] = (data["REVENUE"] - data["REVENUE"].min()) / data["REVENUE"].max()
data.to_csv('./data/output/finaldatav01.csv', index=False)
#






# geop scatter plot
def scattergeo(data):

    fig = px.scatter_geo(data, locations="ALPHA3ISO", locationmode="ISO-3",
                        color="STOCK_ABBREV",hover_name="COMPANY", size="REVENUE",color_continuous_scale=px.colors.diverging, 
                        animation_frame="FY",projection="orthographic",size_max=40, title="Global Revenue",width=1400, height=700
                        )
    return fig


#Sankey plot
def sankeyplot(data, srccol,destcol,valcol,title):
    #all_nodes = data[srccol].values.tolist() + data[destcol].values.tolist() + data["FY"].values.tolist()
    all_nodes = data[srccol].values.tolist() + data[destcol].values.tolist()
    source_indices = [all_nodes.index(src) for src in data[srccol]]
    target_indices = [all_nodes.index(country) for country in data[destcol]]
    colors = px.colors.qualitative.Pastel
    node_colors_mappings = dict([(node,np.random.choice(colors)) for node in all_nodes])
    print(node_colors_mappings)
    node_colors = [node_colors_mappings[node] for node in all_nodes]
    #edge_colors = [node_colors_mappings[node] for node in data["FY"]]

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 30,
          thickness = 30,
          line = dict(color = "black", width = 1.0),
          label =  all_nodes,
          color =  node_colors
        ),

        link = dict(
          source =  source_indices,
          target =  target_indices,
          value =  data[valcol],
          color = node_colors
    ))])

    fig.update_layout(title_text=title,
                      font_size=10)
    return fig



data = pd.read_csv('./data/output/finaldatav01.csv')


##=================================
### Scatter geo plot
#fig = scattergeo(data)
#fig.show()

#### Sankey Region level
#srccol = "STOCK_ABBREV"
#destcol = "CONTINENT"
#valcol = "UNITS"
#title = "Units Sold in each region"
#fig = sankeyplot(data, srccol,destcol,valcol, title)
#fig.show()


##=================================

#data = data[data["STOCK_ABBREV"] == "MDT"]
data = data[["FY", "STOCK_ABBREV" ,"CONTINENT" ,"UNITS"]]
data = data.groupby(["STOCK_ABBREV" ,"CONTINENT" ]).agg({"UNITS": "sum"}).reset_index()

srccol = "STOCK_ABBREV"
destcol = "CONTINENT"
valcol = "UNITS"
title = "Units Sold in each region"
fig = sankeyplot(data, srccol,destcol,valcol, title)
fig.show()
