import dash
import dash_core_components as dcc
import dash_html_components as dhc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Output, Input
from PIL import Image
import numpy as np
import plotly.graph_objects as go
import copy
import plotly.io as pio


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])


data = pd.read_csv('./data/output/finaldatav02.csv')


def indplot(data, growth, fy):

    fig = go.Figure()
    dataset = data[(data["STOCK_ABBREV"] == "MDT") & (data["FY"] == fy)]
    dataset = dataset[["FY", "ALPHA3ISO"]].groupby(["FY"])["ALPHA3ISO"].count().reset_index()
    no_cnt = int(dataset["ALPHA3ISO"])

    dataset = data[(data["STOCK_ABBREV"] == "MDT") & (data["FY"] == fy)]
    dataset = dataset[["FY","UNITS", "REV_BIL"]].groupby(["FY"]).agg({'REV_BIL' :"sum", "UNITS" : "sum"}).reset_index()
    revenue = float(dataset["REV_BIL"])
    units = int(dataset["UNITS"])

    growth = growth[growth["STOCK_ABBREV"] == "MDT"]
    rate = growth[growth["FY"] == fy]
    rate = float(rate["Growth Rate"])
    ref = revenue/(100.0 + rate) * 100.0
    if ref == 0.0:
        ref = revenue

    share = growth[(growth["FY"] == fy) & (growth["STOCK_ABBREV"] == "MDT")]
    share = float(share["Percent Share"])

    fig.add_trace(go.Indicator(
        mode = "number+delta",number={"font":{"size":18, "color": "#F9F1E0"}},
        value = revenue,
        title = {"text": "Revenue B$", "font": { "family": "Open Sans" , "size" : 18 , "color":"#1D617A"}},
        domain = {'row': 0, 'column': 0},
        delta = {'reference': ref , "font":{"size":18}, 'relative': True, 'position' : "bottom"}))

    fig.add_trace(go.Indicator(
        mode = "number",number={"font":{"size":18, "color": "#F9F1E0"}},
        value = no_cnt,
        title = {'text': "Countries", "font": { "family": "Open Sans" , "size" : 18 , "color":"#1D617A"}},
        domain = {'row': 0, 'column': 5}
        ))

    fig.add_trace(go.Indicator(
        mode = "number",number={"font":{"size":18, "color": "#F9F1E0"}},
        value = units,
        title = {'text': "Units Sold", "font": { "family": "Open Sans" , "size" : 18 , "color":"#1D617A"}},
        domain = {'row': 4, 'column': 0}
        ))

    fig.add_trace(go.Indicator(
        mode = "number",number={"font":{"size":18, "color": "#F9F1E0"}},
        value = share,
        title = {'text': "Maket Share (%)", "font": { "family": "Open Sans" , "size" : 18 , "color":"#1D617A"}},
        domain = {'row': 4, 'column': 5}
        ))

    fig.update_layout(
        grid = {'rows': 6, 'columns': 6, 'pattern': "independent"},
        font=dict(family="Open Sans", size=18, color="#1D617A"),
        template="plotly_dark", title_text="MDT - KPI(s)", title_x=0.5)

    return fig


def bar_plot(data, cntry):

    dataset = data[data["COUNTRY_TRNS"].isin(cntry)][["FY","STOCK_ABBREV","REV_BIL","COUNTRY_TRNS"]]

    fig = px.bar(dataset, x='FY', y='REV_BIL', barmode='group',color="STOCK_ABBREV", hover_data={"Country": dataset["COUNTRY_TRNS"], 
        "STOCK_ABBREV": False, "REV_BIL": False, "Revenue (B$)": (':.3f' ,dataset['REV_BIL'])}, 
        labels={"REV_BIL" : "Revenue (in B$)", "FY" : "Financial Year"})
    fig.update_layout(template="plotly_dark", title = "Revenue(B$) Trend",title_x=0.5,
         font=dict(family="Open Sans", size=18, color="#1D617A"), legend_title="Stock Code", legend_font=dict(family="Open Sans", size=12),
        legend_borderwidth=1, legend_bordercolor="#1D617A", legend_title_font=dict(family="Open Sans", size=14))
    fig.update_xaxes(title_font=dict(family="Open Sans", size=15))
    fig.update_yaxes(title_font=dict(family="Open Sans", size=15))

    return fig


def scatplot(data):

    dataset = data[['FY', 'STOCK_ABBREV', 'UNIT_PRICE', 'UNITS', 'REV_BIL']]
    dataset = dataset.groupby(['FY', 'STOCK_ABBREV', 'UNIT_PRICE']).agg({'UNITS' : "sum", 'REV_BIL' :"sum"}).reset_index()
    dataset['Share'] = round((dataset.REV_BIL / dataset.groupby(['FY'])['REV_BIL'].transform('sum')) * 100, 2)
    dataset['FY'] = dataset['FY'].astype(str)

    fig = px.scatter(dataset, x="FY", y="REV_BIL", color="STOCK_ABBREV", size='UNITS', size_max=20, 
        labels={"Share" : False, "REV_BIL" : "Revenue (in B$)", "FY" : "Financial Year"}, hover_name="STOCK_ABBREV",
        hover_data={"STOCK_ABBREV": False, "FY": False, "UNITS": False, "Units Sold": dataset["UNITS"], "Mkt Share (in %)": dataset["Share"]})

    fig.update_layout(title_text="Market Share and Revenue", title_x=0.5, template="plotly_dark", legend_title="Stock Code",
        font=dict(family="Open Sans", size=18, color="#1D617A"), legend_font=dict(family="Open Sans", size=12),
        legend_borderwidth=1, legend_bordercolor="#1D617A",legend_title_font=dict(family="Open Sans", size=14))

    fig.update_xaxes(title_font=dict(family="Open Sans", size=15))
    fig.update_yaxes(title_font=dict(family="Open Sans", size=15))

    return fig


def mapboxplot(data, fy):
    px.set_mapbox_access_token(open("./data/input/mapboxtoken").read())
    data = data[data["FY"] == fy]
    dataset = data[['FY', 'STOCK_ABBREV', 'ALPHA3ISO', 'COUNTRY_TRNS', 'CONTINENT','REV_BIL', 'UNITS', 'Lat', 'Long']]
    #dataset = dataset[dataset["FY"] == fy]

    fig = px.scatter_mapbox(data, lat="Lat", lon="Long", color="STOCK_ABBREV", size="REV_BIL", 
        color_continuous_scale=px.colors.sequential.Blackbody, color_discrete_sequence=px.colors.qualitative.Bold, size_max=25, zoom=10,
        hover_data={"Company": dataset["STOCK_ABBREV"], "Lat": False, "Long": False, "FY": False, "ALPHA3ISO": False, 
        "STOCK_ABBREV": False, "REV_BIL": False, "Country": dataset["COUNTRY_TRNS"], "Revenue (B$)": (':.3f' ,dataset['REV_BIL']), 
        "Units Sold": dataset['UNITS']}, animation_frame="FY", opacity=.5)

    fig.update_layout(mapbox = {'style': "dark", 'zoom': 1},font=dict(family="Open Sans", size=18, color="#1D617A"),
        title_text='Global Presence', title_x=0.5,template="plotly_dark", legend_title="Stock Code", legend_font=dict(family="Open Sans", size=12),
        legend_borderwidth=1, legend_bordercolor="#1D617A", legend_title_font=dict(family="Open Sans", size=14))

    return fig

card_head = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dhc.H5("Market Share Dashboard", className="text-center")], className="css-col-card-head")
                     ]),
                ])
            ], className="css-card-head",color="#19222B", inverse=True)

card_drdn =  dbc.Card([
                dbc.CardBody([

                    dbc.Row([
                        dbc.Col([dhc.H6("Financial Year", className="text-center css-card-drdn-row1-txt")], width={'size':3, "offset": 3}),
                        dbc.Col([dhc.H6("Country", className="text-center css-card-drdn-row1-txt")], width=3, className=""),
                    ], align='center', className="css-card-drdn-row1"),

                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(id='id-drdn-fy', multi=False, value=2017, searchable=True, 
                            options=[{"label" : fy, "value": fy} for fy in data.FY.unique()],
                            className="css-card-drdn-fy")
                    ], width={'size':3, "offset": 3}),

                    dbc.Col([
                        dcc.Dropdown(id='id-drdn-cntry', multi=True, value=["argentina"], searchable=True,
                            options=[{"label" : cntry, "value": cntry} for cntry in data.COUNTRY_TRNS.unique()],
                            className="css-card-drdn-cntry")
                    ], width={'size':3}),

                    ], className="css-card-drdn-row2"),

               ])

            ],className="css-card-drdn",color="#2F3B4A", inverse=True)


card_indc = dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="id-indc-chart", config={"displayModeBar": False}, className="css-indc-fig")
                ])
            ], className="css-card-indc")

card_bar = dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="id-bar-chart", config={"displayModeBar": False}, className="css-bar-fig")
                ])
            ], className="css-card-bar")

card_scat = dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="id-scat-chart", config={"displayModeBar": False}, className="css-scat-fig")
                ])
            ], className="css-card-scat")

card_mapb = dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="id-mapbox-chart", config={"displayModeBar": False}, className="css-mapbox-fig")
                ])
            ], className="css-card-mapbox")

app.layout = dhc.Div([
                dbc.Row([
                    dbc.Col(card_head, width={'size':12, "offset": 0 })
                ]),

#                dhc.Br(),

                dbc.Row([
                    dbc.Col(card_drdn, width={'size':12, "offset": 0 })
                ]),

                dbc.Row([
                    dbc.Col(card_indc, width={'size':3, "offset": 0 }),
                    dbc.Col(card_bar, width={'size': 5, "offset": 0 }),
                    dbc.Col(card_scat, width={'size': 4, "offset": 0 })
                ],  className="css-app-row1", no_gutters=True),

                dbc.Row([
                    dbc.Col(card_mapb, width={'size':6, "offset": 0 }),
                ])

            ])



@app.callback(
    Output("id-indc-chart", 'figure'),
    [
        Input("id-drdn-fy", "value"),
    ],
)
def update_indplot(fy):
    dataset = pd.read_csv('./data/output/finaldatav02.csv')
    growth = pd.read_csv('./data/output/growthrate.csv')

    fig_ind = indplot(dataset, growth, fy)
    return fig_ind

@app.callback(
    Output("id-bar-chart", 'figure'),
    [
        Input("id-drdn-cntry", "value"),
    ],
)
def update_barplot(cntry):
    dataset = pd.read_csv('./data/output/finaldatav02.csv')
    fig_bar = bar_plot(dataset, cntry)
    return fig_bar

@app.callback(
    Output("id-scat-chart", 'figure'),
    [
        Input("id-drdn-cntry", "value"),
    ],
)
def update_scatplot(cntry):
    dataset = pd.read_csv('./data/output/finaldatav02.csv')
    fig_scat = scatplot(dataset)
    return fig_scat


@app.callback(
    Output("id-mapbox-chart", 'figure'),
    [
        Input("id-drdn-fy", "value"),
    ],
)
def update_scatplot(fy):
    dataset = pd.read_csv('./data/output/finaldatav02.csv')
    fig_map = mapboxplot(dataset, fy)
    return fig_map


if __name__ == '__main__':
    app.run_server(debug=True)