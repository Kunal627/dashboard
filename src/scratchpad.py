import pandas as pd
import csv

import plotly
print(plotly.__version__)
def fixcsv(row):
    
    # fix the financial year values
    yeardict = {"17": "2017", "'17" : "2017", "18" : "2018", "'18" : "2018", "19" : "2019", "'19" : "2019", "20": "2020", "'20" : "2020" }
    year = yeardict.get(row[0], 9999)
    if year != 9999:
        row[0] = year
    
    return row



csvfile = open('./data/input/testinput.csv', newline='')
data = csv.reader(csvfile)
outdata = []
for row in data: 
    if len(row) != 0:
        row = fixcsv(row)
        outdata.append(row)

print(outdata)
outfile = open('./data/output/finaldata.csv', 'w', newline='')
writer = csv.writer(outfile)
writer.writerows(outdata)




#############
    dhc.Div(
        children=[
            dhc.Div(children=[
            dhc.Div([dhc.H6("Financial Year")], className="div-dd-label-fy"),

            dhc.Div(
                [dcc.Dropdown(id="filter-dropdown-fy", options=[{"label" : fy, "value": fy} for fy in data.FY.unique() ], 
                value=[2017], clearable=False, multi=True, className="dd-fy")],
                className="div-drop-fy")], className="dd-grp1"),

            dhc.Div(children=[
            dhc.Div([dhc.H6("Company")], className="div-dd-label-cp"),

            dhc.Div(
                [dcc.Dropdown(id="filter-dropdown-tic", options=[{"label" : tic, "value": tic} for tic in data.STOCK_ABBREV.unique()], 
                value=["MDT"],multi=True, clearable=False, className="dd-tic")],
                className="div-drop-tic")], className="dd-grp2"),

            dhc.Div(children=[
            dhc.Div([dhc.H6("Country")], className="div-dd-label-ct"),

            dhc.Div(
                [dcc.Dropdown(id="filter-dropdown-country",options=[{"label" : cntry, "value": cntry} for cntry in data.COUNTRY_TRNS.unique()
                ], value=["india"], multi=True, clearable=False, className="dd-cntry")], 
                className="div-drop-cntry")], className="dd-grp3")

        ], className="div-drop-select"
    ),