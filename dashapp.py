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

img = Image.open('./images/nightsky.JPG')
data = pd.read_csv('./data/output/finaldatav01.csv')

def scattergeo(data):

    fig = px.scatter_geo(data, locations="ALPHA3ISO", locationmode="ISO-3",
                        color="STOCK_ABBREV",hover_name="COMPANY", size="REVENUE",color_continuous_scale=px.colors.diverging, 
                        animation_frame="FY",projection="orthographic",size_max=40, title="Global Revenue",width=525, height=375
                        )
    
    #fig.add_layout_image(dict(source=img))
    fig.update_layout(title_text='Global Revenue', title_x=0.5,template="plotly_dark")

    return fig

def sankeyplot(data, srccol,destcol,valcol,title):

    all_nodes = data[srccol].values.tolist() + data[destcol].values.tolist()
    source_indices = [all_nodes.index(src) for src in data[srccol]]
    target_indices = [all_nodes.index(country) for country in data[destcol]]
    colors = px.colors.qualitative.Pastel
    node_colors_mappings = dict([(node,np.random.choice(colors)) for node in all_nodes])
    node_colors = [node_colors_mappings[node] for node in all_nodes]

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

    fig.update_layout(title_text=title, title_x=0.5, font_size=10, template="plotly_dark", width=620, height=375)
    return fig


def sunburstplot(data):

    fig = px.sunburst(data, path=['FY', 'STOCK_ABBREV', 'CONTINENT','COUNTRY_TRNS'], 
                  values='REV_CALC', color='UNITS', hover_data=['REV_CALC'], title="Global revenue for financial year (in B $)",
                  color_continuous_scale='ylgnbu',
                  color_continuous_midpoint=np.average(data['UNITS'], weights=data['REV_CALC']))
    fig.update_layout(title_x=0.5, width=682, height=730,template="plotly_dark")
    #print(fig)
    return fig


def barplotfn(data):
    fig = px.bar(data, x='FY', y='REV_CALC', barmode='group', hover_data=['STOCK_ABBREV', 'REV_CALC', 'COUNTRY_TRNS'], color="STOCK_ABBREV")
    fig.update_layout(width=682, height=330, template="plotly_dark", title = "Revenue(B$) Trend",title_x=0.5,)
    return fig

def scatplot(data):
    fig = px.scatter(data, x="UNIT_PRICE", y="UNITS", size="REV_CALC", color="STOCK_ABBREV",
                 hover_name="REV_CALC", log_y=True, size_max=60)
    fig.update_layout(width=455, height=330, template="plotly_dark", title = "Revenue(B$) Trend",title_x=0.5,)
    return fig


card_geo =  dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="geo-scatter-chart", config={"displayModeBar": False}, className="css-scatter-geo-fig")
                ])
            ],className="css-gscat-card")
    
    
card_san =  dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="sank-chart", config={"displayModeBar": False}, className="css-sankey-fig")
                ])
            ],className="css-sankey-card")
    
    
card_sun =  dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="sunbrst-chart", config={"displayModeBar": False}, className="css-sunbrst-fig")
                ])
            ],className="css-sunbrst-card")


card_bar =  dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="barplot-chart", config={"displayModeBar": False}, className="css-barplot-fig")
                ])
            ], className="css-barplot-card")

card_scat =  dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="scatter-chart", config={"displayModeBar": False}, className="css-scatter-fig")
                ])
            ], className="css-scatter-card")


app.layout = dhc.Div([
    dbc.Card([
        dbc.CardBody([
                dbc.Row([
                dbc.Col([dhc.H3("Market Share Dashboard", className="text-center")], className="css-dash-head")
            ]),

        ])
    ], className="css-header-card"),

    dhc.Br(),

    dbc.Card([
        dbc.CardBody([

            dbc.Row([
                dbc.Col([dhc.H6("Financial Year", className="text-center")], width={'size':3, "offset": 0}, className="css-row-dd-head"),
                dbc.Col([dhc.H6("Company", className="text-center")], width=3, className="css-row-dd-head"),
                dbc.Col([dhc.H6("Country", className="text-center")], width=3, className="css-row-dd-head"),
                dbc.Col([dhc.H6("Region", className="text-center")], width=3, className="css-row-dd-head")
            ], align='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='id-drp-fy', multi=True, value=[2017], searchable=True, 
                    options=[{"label" : fy, "value": fy} for fy in data.FY.unique()],
                    className="css-drp-fy")
                ], width={'size':3, "offset": 0}),

                dbc.Col([
                    dcc.Dropdown(id='id-drp-cp', multi=True, value=["JNJ"], searchable=True,
                    options=[{"label" : cp, "value": cp} for cp in data.STOCK_ABBREV.unique()],
                    className="css-drp-cp")
                ], width={'size':3, "offset": 0}),

                dbc.Col([
                    dcc.Dropdown(id='id-drp-cntry', multi=True, value=["argentina"], searchable=True,
                    options=[{"label" : cntry, "value": cntry} for cntry in data.COUNTRY_TRNS.unique()],
                    className="css-drp-cntry")
                ], width={'size':3}),

                dbc.Col([
                    dcc.Dropdown(id='id-drp-regn', multi=True, value=["Asia"], searchable=True,
                    options=[{"label" : regn, "value": regn} for regn in data.CONTINENT.unique()],
                    className="css-drp-regn")
                ], width={'size':3})

            ], className="css-row-drp"),


        ])

    ],className="css-drp-down-card"),

    dhc.Br(),

    dbc.Row([

        dbc.Col(card_geo, width={'size':4, "offset": 0 }),
        dbc.Col(card_san, width={'size':4, "offset": 0 }),    
        dbc.Col(card_sun, width=4)

    ], justify="around", className="css-plot-row1"),

    dhc.Br(),

    dbc.Row([
        dbc.Col(card_bar, width={'size':5, "offset": 0 }),
        dbc.Col(card_scat,width={'size':3})
    ])


])

@app.callback(
    Output("geo-scatter-chart", 'figure'),
    [
        Input("id-drp-fy", "value"),
        Input("id-drp-cp", "value"),
        Input("id-drp-cntry", "value"),
    ],
)
def update_graph(fy, tic, cntry):

    filtered_data = data[(data["FY"].isin(fy)) & (data["STOCK_ABBREV"].isin(tic)) & (data["COUNTRY_TRNS"].isin(cntry))]
    fig_scatter_geo = scattergeo(filtered_data)
    return fig_scatter_geo

@app.callback(
    Output("sank-chart", 'figure'),
    [
        Input("id-drp-fy", "value"),
        Input("id-drp-cp", "value"),
        Input("id-drp-regn", "value"),
    ],
)
def update_sankey(fy, tic, cntry):

    filtered_data = data[(data["FY"].isin(fy)) & (data["STOCK_ABBREV"].isin(tic)) & (data["CONTINENT"].isin(cntry))]
    srccol = "STOCK_ABBREV"
    destcol = "CONTINENT"
    valcol = "UNITS"
    title = "Units Sold in each region"
    fig_sankey = sankeyplot(filtered_data,srccol,destcol,valcol,title)

    return fig_sankey


@app.callback(
    Output("sunbrst-chart", 'figure'),
    [
        Input("id-drp-fy", "value")
    ],
)
def update_sunbrst(fy):
    dataset = pd.read_csv('./data/output/finaldatav01.csv')
    dataset.drop(columns=['COMPANY', 'PRODUCT_ID', 'PRODUCT_SUBTYPE', 'UNIT_PRICE','Unnamed: 9', 'Unnamed: 10','REVENUE','ALPHA3ISO','COUNTRY'], inplace=True)
    dataset["REV_CALC"] = dataset["REV_CALC"].div(1000000000).round(3)
    fig_snbrst = sunburstplot(dataset)
    return fig_snbrst

@app.callback(
    Output("barplot-chart", 'figure'),
    [
        Input("id-drp-cntry", "value"),
    ],
)
def update_barplot(cntry):
    dataset = pd.read_csv('./data/output/finaldatav01.csv')
    filtered_data = dataset[dataset["COUNTRY_TRNS"].isin(cntry)]
    filtered_data["REV_CALC"] = filtered_data["REV_CALC"].div(1000000000).round(3)
    fig_bar = barplotfn(filtered_data)
    return fig_bar


@app.callback(
    Output("scatter-chart", 'figure'),
    [
        Input("id-drp-cntry", "value"),
    ],
)
def update_barplot(cntry):
    dataset = pd.read_csv('./data/output/finaldatav01.csv')
    fig_scat = scatplot(dataset)
    return fig_scat



if __name__ == '__main__':
    app.run_server(debug=True)
