import base64
import copy
import csv
import json as js
import locale
import time
from datetime import datetime
from threading import Thread
from urllib.request import urlopen

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import schedule

from dash.dependencies import Input, Output, ClientsideFunction
from pytz import timezone

import logger
from constants import DATA_DICT

SECONDS = 1000

INHABITANT_RATE = 100000

locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

log = logger.get_logger()
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"},
                         {"property": "og:title", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:image", "content": "https://i.ibb.co/86xLrnK/SARS-Co-V-2-Gellex.jpg"},
                         {"property": "og:description", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:url", "content": "https://www.data-covid.com/"}]
)
server = app.server

image_filename = 'assets/gerardo.png'  # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

url_csv_regional_data = \
    "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
url_csv_italy_data = \
    "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale" \
    "/dpc-covid19-ita-andamento-nazionale.csv"
url_geojson_regions = \
    "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
# API Requests for news
news_requests = requests.get(
    "http://newsapi.org/v2/top-headlines?country=it&category=science&apiKey=b20640c581554761baab24317b8331e7")

field_list_complete = ['ricoverati_con_sintomi', 'terapia_intensiva',
                       'totale_ospedalizzati', 'isolamento_domiciliare',
                       'totale_positivi', 'variazione_totale_positivi',
                       'nuovi_positivi', 'dimessi_guariti',
                       'deceduti', 'totale_casi',
                       'tamponi', 'casi_testati']

field_list_to_rate = ['ricoverati_con_sintomi', 'terapia_intensiva',
                      'totale_ospedalizzati', 'isolamento_domiciliare',
                      'totale_positivi', ''
                                         'nuovi_positivi', 'dimessi_guariti',
                      'deceduti', 'totale_casi',
                      'tamponi', 'casi_testati']


def load_csv_from_file(path):
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
        k, v = row
        d[k] = v
    return d


def load_csv(url):
    data_loaded = pd.read_csv(url, index_col=[0], parse_dates=['data'])
    return data_loaded


def load_geojson(url):
    with urlopen(url) as response:
        json = js.load(response)
    return json


region_population = load_csv_from_file('assets/region_population.csv')
geojson_province = load_geojson(url_geojson_regions)
last_update = None
df_regional_data = None
df_national_data = None
df_rate_regional = None

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    mapbox=dict(
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)


def format_value_string_to_locale(value):
    return locale.format_string('%.0f', value, True)


def get_options(list_value):
    dict_list = []
    for i in list_value:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def get_options_from_list(field_list):
    dict_list = []
    for data in field_list:
        dict_list.append({'label': str(DATA_DICT[data]), 'value': str(data)})

    return dict_list


def create_scatter_plot(data_frame, title, x_axis_data, y_axis_data_mapping):
    scatter_list = []
    # Draw empty figures if an empty list is passed
    if len(y_axis_data_mapping) == 0:
        scatter = go.Scatter(x=x_axis_data, y=[], mode='lines+markers', opacity=0.7, textposition='bottom center')
        scatter_list.append(scatter)
    else:
        for y_data_name, label in y_axis_data_mapping:
            scatter = go.Scatter(x=x_axis_data,
                                 y=data_frame[y_data_name],
                                 mode='lines+markers',
                                 opacity=0.7,
                                 name=label,
                                 textposition='bottom center')
            scatter_list.append(scatter)

    figure = create_figure(scatter_list, title)
    return figure


def create_scatter_plot_by_region(data_frame, title, x_axis_data, y_axis_data_mapping_region):
    scatter_list = []
    y_axis_data_mapping_region.sort(key=lambda tup: tup[1])
    for field, region in y_axis_data_mapping_region:
        scatter = go.Scatter(x=x_axis_data, y=data_frame[data_frame['denominazione_regione'] == region][field],
                             mode='lines+markers',
                             opacity=0.7,
                             name=region,
                             # line=dict(shape="spline", smoothing=1, width=1),
                             textposition='bottom center')
        scatter_list.append(scatter)
    figure = create_figure(scatter_list, title)
    return figure


def create_figure(data, title):
    layout_figure = copy.deepcopy(layout)

    layout_figure['title'] = title
    figure = dict(data=data, layout=layout_figure)
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                                               Input('dropdown_data_selected', 'value')])
def update_graph(region_list, data_selected):
    regions_list_mapping = []
    # if no region selected, create empty figure
    if len(region_list) == 0 or data_selected is None:
        figure = create_scatter_plot(df_regional_data, '', df_regional_data.index, [])
        return figure
    for region in region_list:
        regions_list_mapping.append((data_selected, region))
    x_axis_data = df_regional_data.index.drop_duplicates()
    figure = create_scatter_plot_by_region(df_regional_data, DATA_DICT[data_selected],
                                           x_axis_data, regions_list_mapping)
    log.info('Updating main graph')
    return figure


@app.callback(Output('pie_graph', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                              Input('dropdown_data_selected', 'value')])
def update_pie_graph(region_list, data_selected):
    layout_pie = copy.deepcopy(layout)
    value_list = []
    if len(region_list) == 0 or data_selected is None or data_selected == 'variazione_totale_positivi':
        data = [go.Pie(labels=[],
                       values=value_list)]
        layout_pie['title'] = "Nessun dato selezionato o <br> il dato selezionato <br> non è rappresentabile"
        figure = dict(data=data, layout=layout_pie)
        return figure
    region_list.sort()
    for region in region_list:
        value = df_regional_data[df_regional_data['denominazione_regione'] == region][data_selected][-1]
        value_list.append(value)
    data = [go.Pie(labels=region_list,
                   values=value_list,
                   hoverinfo='text+value+percent',
                   sort=False,
                   textinfo='label+percent',
                   hole=0.5)]
    layout_pie['title'] = "{}".format(DATA_DICT[data_selected])
    layout_pie['legend'] = dict(font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)")
    figure = dict(data=data, layout=layout_pie)
    log.info('Updating pie graph')
    return figure


@app.callback(Output('map_graph', 'figure'), [Input('dropdown_data_selected', 'value')])
def update_map_graph(data_selected):
    df = df_rate_regional.tail(21)
    df['population'] = pd.to_numeric(df['population'], downcast='float')
    df['population'] = df['population'].apply(format_value_string_to_locale)
    date_string = df_national_data.index[-1].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=url_geojson_regions, locations='codice_regione',
                                  featureidkey="properties.reg_istat_code_num",
                                  color=data_selected,
                                  color_continuous_scale="Reds",
                                  hover_name='denominazione_regione',
                                  hover_data=['population'],
                                  range_color=(df[data_selected].min(), df[data_selected].max()),
                                  mapbox_style="carto-positron",
                                  zoom=4, center={"lat": 42.0902, "lon": 11.7129},
                                  opacity=0.5,
                                  labels={data_selected: 'N° Casi'}
                                  )
    figure.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        annotations=[dict(
            x=0.0,
            y=0.01,
            xref='paper',
            yref='paper',
            text='*Incidenza di {} <br>per regione (ogni 100K abitanti)<br>al {}'.format(DATA_DICT[data_selected],
                                                                                         date_string),
            showarrow=False
        )]
    )
    log.info('Updating map graph')
    return figure


@app.callback(Output('bar_graph', 'figure'), [Input('dropdown_data_selected', 'value')])
def update_bar_graph(data_selected):
    layout_bar = copy.deepcopy(layout)
    layout_bar['title'] = '{}'.format(DATA_DICT[data_selected])
    layout_bar['yaxis'] = dict(zeroline=False, showline=False, showgrid=False, showticklabels=False)
    df_sub = df_regional_data.tail(21)
    df_sorted = df_sub.sort_values(by=[data_selected])
    df_sorted = df_sorted.tail(10)
    region_list = df_sorted['denominazione_regione'].values.tolist()
    value_list = df_sorted[data_selected].values.tolist()
    data = [go.Bar(x=value_list,
                   y=region_list,
                   text=region_list,
                   textposition='auto',
                   insidetextanchor="start",
                   orientation='h'
                   )
            ]
    figure = dict(data=data, layout=layout_bar)
    log.info('Updating bar graph in Tab 1')
    return figure


@app.callback(Output('bar_graph_tab2', 'figure'), [Input('dropdown_region_selected', 'value')])
def update_bar_graph_active_cases(region_selected):
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    y_list_1 = df['terapia_intensiva'].values.tolist()
    y_list_2 = df['ricoverati_con_sintomi'].values.tolist()
    y_list_3 = df['isolamento_domiciliare'].values.tolist()
    x_list = df.index.drop_duplicates()
    figure = go.Figure(
        go.Bar(x=x_list, y=y_list_1, name=DATA_DICT['terapia_intensiva'], textposition='auto',
               insidetextanchor="start"))
    figure.add_trace(go.Bar(x=x_list, y=y_list_2, name=DATA_DICT['ricoverati_con_sintomi']))
    figure.add_trace(go.Bar(x=x_list, y=y_list_3, name=DATA_DICT['isolamento_domiciliare']))
    figure.add_annotation(
        x=x_list[14],
        y=y_list_3[14],
        text="Fase-1")
    figure.add_annotation(
        x=x_list[70],
        y=y_list_3[70],
        text="Fase-2")
    figure.add_annotation(
        x=x_list[112],
        y=y_list_3[112],
        text="Fase-3")
    figure.update_annotations(dict(
        xref="x",
        yref="y",
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-60
    ))
    figure.update_layout(barmode='stack',
                         title=region_selected,
                         xaxis={'categoryorder': 'total descending'},
                         autosize=True,
                         margin=dict(l=30, r=30, b=20, t=40),
                         legend=dict(font=dict(size=10), orientation="h")
                         )
    log.info('Updating bar graph in Tab 2')
    return figure


@app.callback([Output('total_positive_text', 'children'),
               Output('total_cases_text', 'children'),
               Output('total_recovered_text', 'children'),
               Output('total_deaths_text', 'children'),
               Output('total_positive_variation', 'children'),
               Output('total_cases_variation', 'children'),
               Output('total_recovered_variation', 'children'),
               Output('total_deaths_variation', 'children'),
               Output('subHeader', 'children')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_text(n):
    log.info('update cards')
    sub_header_text = (df_national_data.index[-1]).strftime('Dati Aggiornati al: %d/%m/%Y %H:%M')
    field_list = ['totale_positivi', 'totale_casi', 'dimessi_guariti', 'deceduti']
    total_text_values = []
    variation_text_values = []
    for field in field_list:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day = df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        total_text = f'{card_value:n}'
        total_text_values.append(total_text)
        sign = '+' if variation_previous_day > 0 else ''
        variation_text = f'{sign}{variation_previous_day:n}'
        variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values), sub_header_text


@app.callback([Output('total_positive_variation', 'style'),
               Output('total_cases_variation', 'style'),
               Output('total_recovered_variation', 'style'),
               Output('total_deaths_variation', 'style')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_color(n):
    field_list = ['totale_positivi', 'totale_casi', 'dimessi_guariti', 'deceduti']
    color_cards_list = []
    for field in field_list:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day = df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if variation_previous_day > 0 and field == 'dimessi_guariti' or \
                variation_previous_day < 0 and field == 'totale_positivi':
            color = 'limegreen'
            color_cards_list.append(color)
        else:
            color = 'red'
            color_cards_list.append(color)
    dictionary_color = [{'color': color_cards_list[0]},
                        {'color': color_cards_list[1]},
                        {'color': color_cards_list[2]},
                        {'color': color_cards_list[3]}]
    return dictionary_color


@app.callback(Output('table_tab1', 'figure'), [Input("dropdown_data_selected", "value")])
def new_positives_table(data_selected):
    df = df_regional_data.tail(21)
    df = df.sort_values(by=[data_selected], ascending=False)
    figure = go.Figure(data=[go.Table(
        header=dict(values=('denominazione_regione', data_selected),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df['denominazione_regione'], df[data_selected]],
                   fill_color='lavender',
                   align='left',
                   font_size=16,
                   height=27))
    ])
    figure.update_layout(height=600, margin=dict(l=0, r=0, b=0, t=0))
    return figure


@app.callback([Output('total_cases_text_tab2', 'children'),
               Output('total_positive_text_tab2', 'children'),
               Output('total_recovered_text_tab2', 'children'),
               Output('total_deaths_text_tab2', 'children'),
               Output('total_hospitalized_w_symptoms_text_tab2', 'children'),
               Output('total_icu_text_tab2', 'children'),
               Output('total_isolation_text_tab2', 'children'),
               Output('total_swabs_text_tab2', 'children'),
               Output('total_cases_variation_tab2', 'children'),
               Output('total_positive_variation_tab2', 'children'),
               Output('total_recovered_variation_tab2', 'children'),
               Output('total_deaths_variation_tab2', 'children'),
               Output('total_hospitalized_w_symptoms_variation_tab2', 'children'),
               Output('total_icu_variation_tab2', 'children'),
               Output('total_isolation_variation_tab2', 'children'),
               Output('total_swabs_variation_tab2', 'children')
               ], [Input("dropdown_region_selected", "value")])
def update_regional_cards_text(region_selected):
    log.info('Update regional cards')
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'ricoverati_con_sintomi', 'terapia_intensiva', 'isolamento_domiciliare', 'tamponi']
    total_text_values = []
    variation_text_values = []
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    for field in field_list:
        card_value = df[field].iloc[-1]
        card_value_previous_day = df[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        total_text = f'{card_value:n}'
        total_text_values.append(total_text)
        sign = '+' if variation_previous_day > 0 else ''
        variation_text = f'{sign}{variation_previous_day:n}'
        variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values),


@app.callback([Output('total_cases_variation_tab2', 'style'),
               Output('total_positive_variation_tab2', 'style'),
               Output('total_recovered_variation_tab2', 'style'),
               Output('total_deaths_variation_tab2', 'style'),
               Output('total_hospitalized_w_symptoms_variation_tab2', 'style'),
               Output('total_icu_variation_tab2', 'style'),
               Output('total_isolation_variation_tab2', 'style'),
               Output('total_swabs_variation_tab2', 'style')
               ], [Input("dropdown_region_selected", "value")])
def update_regional_cards_color(region_selected):
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'ricoverati_con_sintomi', 'terapia_intensiva', 'isolamento_domiciliare', 'tamponi']
    color_cards_list = []
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    for field in field_list:
        card_value = df[field].iloc[-1]
        card_value_previous_day = df[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if variation_previous_day < 1 and field == 'totale_casi' or \
                variation_previous_day < 0 and field == 'totale_positivi' or \
                variation_previous_day > 0 and field == 'dimessi_guariti' or \
                variation_previous_day == 0 and field == 'deceduti' or \
                (variation_previous_day <= 0 and card_value == 0) and field == 'ricoverati_con_sintomi' or \
                (variation_previous_day <= 0 and card_value == 0) and field == 'terapia_intensiva' or \
                variation_previous_day < 0 and field == 'ricoverati_con_sintomi' or \
                variation_previous_day < 0 and field == 'terapia_intensiva' or \
                variation_previous_day < 0 and field == 'isolamento_domiciliare' or \
                variation_previous_day > 0 and field == 'tamponi':
            color = 'limegreen'
            color_cards_list.append(color)
        else:
            color = 'red'
            color_cards_list.append(color)
    dictionary_color = [{'color': color_cards_list[0]},
                        {'color': color_cards_list[1]},
                        {'color': color_cards_list[2]},
                        {'color': color_cards_list[3]},
                        {'color': color_cards_list[4]},
                        {'color': color_cards_list[5]},
                        {'color': color_cards_list[6]},
                        {'color': color_cards_list[7]}]
    return dictionary_color


def create_news():
    json_data = news_requests.json()["articles"]
    df_news = pd.DataFrame(json_data)
    df_news = pd.DataFrame(df_news[["urlToImage", "title", "url"]])
    max_rows = 6
    return html.Div(
        children=[
            html.H5(className="p-news title", children="Italia News Scienza"),
            html.P(
                className="p-news title",
                children="Ultimo Aggiornamento: "
                         + datetime.now().astimezone(timezone('Europe/Berlin')).strftime("%d/%m/%Y %H:%M"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.Img(
                                        src=df_news.iloc[i]["urlToImage"],
                                        style={
                                            "height": "40px",
                                            "width": "60px",
                                            "float": "center",
                                            "border-radius": "8px"
                                        })
                                ]
                            ),
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df_news.iloc[i]["title"],
                                        href=df_news.iloc[i]["url"],
                                        target="_blank"
                                    )]
                            )
                        ]
                    )
                    for i in range(min(len(df_news), max_rows))
                ],
            ),
        ]
    )


encoded_image_gerardo = base64.b64encode(open('assets/gerardo.png', 'rb').read()).decode('ascii')
encoded_image_nicola = base64.b64encode(open('assets/nicola.png', 'rb').read()).decode('ascii')


def create_contacts():
    return html.Div(
        children=[
            html.H5(className="p-news title", children="Contattaci"),
            html.Table(
                className="center",
                children=[
                    html.Tr(
                        className='pretty_container',
                        children=[
                            html.Td(
                                className='td-style',
                                children=[
                                    html.Img(
                                        src='data:image/png;base64,{}'.format(encoded_image_gerardo),
                                        id="gerardo-image",
                                        className='responsive',
                                        style={
                                            "height": "100px",
                                            "width": "100px",
                                            "float": "center",
                                            "border-radius": "8px"
                                        }
                                    ),
                                ]
                            ),
                            html.Td(
                                className='td-style',
                                children=[
                                    html.Img(
                                        src='data:image/png;base64,{}'.format(encoded_image_nicola),
                                        id="nicola-image",
                                        className='responsive',
                                        style={
                                            "height": "100px",
                                            "width": "100px",
                                            "float": "center",
                                            "border-radius": "8px"
                                        }
                                    ),
                                ]
                            )
                        ]
                    ),
                    html.Tr(
                        className='pretty_container',
                        children=[
                            html.Td(
                                className='title-name',
                                children='Lamorte Gerardo'
                            ),
                            html.Td(
                                className='title-name',
                                children='Mastrangelo Nicola'
                            ),
                        ]
                    ),
                    html.Tr(
                        className='pretty_container',
                        children=[
                            html.Td(
                                className='title',
                                children='Java & Python Software Developer'
                            ),
                            html.Td(
                                className='title',
                                children='ICT Specialist & Software Developer'
                            ),
                        ]
                    ),
                    html.Tr(
                        className='pretty_container',
                        children=[
                            html.Td(
                                className='title',
                                children='The Hague (NL)'
                            ),
                            html.Td(
                                className='title',
                                children='Potenza (ITA)'
                            ),
                        ]
                    ),
                    html.Tr(
                        className='pretty_container',
                        children=[
                            html.Td(
                                className='td-style',
                                children=[
                                    html.A(
                                        children=
                                        html.Img(
                                            src=app.get_asset_url("linkedIn.png"),
                                            className='responsive',
                                            style={
                                                "height": "50px",
                                                "width": "50px",
                                                "float": "center"
                                            }
                                        ),
                                        href="https://www.linkedin.com/in/gerardo-lamorte-a25928149/",
                                    ),
                                    html.A(
                                        children=html.Img(
                                            src=app.get_asset_url("gmail.png"),
                                            className='responsive',
                                            style={
                                                "height": "50px",
                                                "width": "50px",
                                                "float": "center"
                                            }
                                        ),
                                        href="mailto:lamorte.gerardo@gmail.com",
                                    )
                                ]
                            ),
                            html.Td(
                                className='td-style',
                                children=[
                                    html.A(
                                        children=html.Img(
                                            src=app.get_asset_url("linkedIn.png"),
                                            className='responsive',
                                            style={
                                                "height": "50px",
                                                "width": "50px",
                                                "float": "center"
                                            }
                                        ),
                                        href="https://www.linkedin.com/in/nicola-mastrangelo-240810107/",
                                    ),
                                    html.A(
                                        children=html.Img(
                                            src=app.get_asset_url("gmail.png"),
                                            className='responsive',
                                            style={
                                                "height": "50px",
                                                "width": "50px",
                                                "float": "center"
                                            }
                                        ),
                                        href="mailto:mastrangelo.nicola@gmail.com",
                                    )
                                ])
                        ]
                    ),
                ],
            ),
        ]
    )


@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news(input):
    log.info('update news')
    return create_news()


# Merge data of P.A Bolzano and P.A. Trento (in Trentino Alto Adige region, with 'codice_regione' = 4) to match
# GeoJson structure
def adjust_region(df_sb):
    trento_row = df_sb.loc[df_sb['codice_regione'] == 22].squeeze()
    bolzano_row = df_sb.loc[df_sb['codice_regione'] == 21].squeeze()
    trentino_row = trento_row
    for field in field_list_to_rate:
        trento_value = trento_row.get(field)
        bolzano_value = bolzano_row.get(field)
        trentino_row.at[field] = trento_value + bolzano_value
    df_sb.drop([trento_row.name, bolzano_row.name], inplace=True)
    trentino_row.at['codice_regione'] = 4
    trentino_row.at['denominazione_regione'] = 'Trentino-Alto Adige'
    df_sb = df_sb.append(trentino_row)
    return df_sb


def load_region_rate_data_frame():
    df_sb = pd.read_csv(url_csv_regional_data, parse_dates=['data'])
    df_sb = df_sb.tail(21)
    df_sb = adjust_region(df_sb)
    df_sb['population'] = list(region_population.values())
    # Convert field to float
    for field in field_list_to_rate:
        df_sb[field] = pd.to_numeric(df_sb[field], downcast='float')
    for i, row in df_sb.iterrows():
        population = row['population']
        for field in field_list_to_rate:
            value = row[field]
            pressure_value = (float(value) / float(population)) * INHABITANT_RATE
            df_sb.at[i, field] = round(pressure_value, 2)
    return df_sb


def load_interactive_data():
    log.info('Start scheduled task to check data updates')
    global df_regional_data, df_national_data, df_rate_regional, region_population, last_update
    df_regional_data = load_csv(url_csv_regional_data)
    df_regional_data.index = df_regional_data.index.normalize()
    df_national_data = load_csv(url_csv_italy_data)
    current_update = df_national_data.index[-1]
    if df_rate_regional is None or current_update != last_update:
        log.info('Update to data required')
        df_rate_regional = load_region_rate_data_frame()
        last_update = current_update
    else:
        log.info('Update is not needed')
    log.info('Update task completed')


def new_positive_regions():
    df = df_regional_data.tail(21)
    df = df.sort_values(by=['nuovi_positivi']).tail(3)
    regions_list = []
    value_list = []
    new_positive_rows = df.loc[df['nuovi_positivi'] > 0]
    regions_list.append(new_positive_rows)
    for region in regions_list:
        value_list = region['denominazione_regione'].tolist()
    return value_list


def app_layout():
    app.layout = html.Div(
        [  # START OF SUPREME INCAPSULATION ############################################
            dcc.Store(id="aggregate_data"),
            # Interval component for updating news list
            dcc.Interval(id="i_news", interval=900 * SECONDS, n_intervals=0),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(  # START OF 1ST INCAPSULATION - (LOGO - HEADING - BUTTON)
                [
                    html.Div(  # START OF LOGO
                        [
                            html.Img(
                                src=app.get_asset_url("dash-logo.png"),
                                id="plotly-image",
                                style={
                                    "height": "180px",
                                    "width": "auto",
                                },
                            )
                        ],
                        className="one-third column",
                    ),  # END OF LOGO
                    html.Div(  # START OF HEADING
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Coronavirus (SARS-CoV-2) Italia"
                                    ),
                                    html.H5(id="subHeader", children='')
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),  # END OF HEADING
                    html.Div(  # START OF GITHUB LOGOS
                        [
                            html.Div(
                                [
                                    html.A(
                                        html.Img(
                                            src=app.get_asset_url("protezione-civile.png"),
                                            id="protezione-civile-image",
                                            style={
                                                "height": "48px",
                                                "width": "auto",
                                                "margin-bottom": "10px",
                                            },
                                        ),
                                        href="https://github.com/pcm-dpc",
                                    ),
                                    html.A(
                                        html.Img(
                                            src=app.get_asset_url("github.svg"),
                                            id="github-image",
                                            style={
                                                "height": "48px",
                                                "width": "auto",
                                                "margin-bottom": "10px",
                                            },
                                        ),
                                        href="https://github.com/gerrygeko/covid-data-analysis",
                                    )
                                ]
                            )
                        ],
                        className="one-third column",
                        id="logos",
                    ),  # END OF GITHUB LOGOS
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "0px", "margin-top": "0px"},
            ),  # END OF 1ST INCAPSULATION -END OF HEADING############################################
            dcc.Tabs(id='tabs', value='tab_national', children=[  # START OF TABS COMPONENT CREATOR
                dcc.Tab(label='Analisi dei dati nazionali', value='tab_national',
                        children=[  # START FIRST TAB
                            html.Div(  # START OF 2ND INCAPSULATION  ############################################
                                [
                                    html.Div(  # START OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                                        [
                                            html.P("Seleziona il dato da analizzare:", className="control_label"),
                                            dcc.Dropdown(
                                                id='dropdown_data_selected',
                                                options=get_options_from_list(field_list_complete),
                                                multi=False,
                                                value='nuovi_positivi',
                                                className='dcc_control'
                                            ),

                                        ],
                                        className="pretty_container four columns",
                                        id="cross-filter-options-tab1",
                                    ),  # END OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                                    html.Div(  # START OF 2ND BLOCK
                                        [
                                            html.H5(id='card_header', children='Totale Dati Nazionali',
                                                    className='title'),
                                            html.Div(  # START OF CARDS #
                                                [
                                                    html.Div(
                                                        [html.H6(id="total_positive_text", children=''),
                                                         html.H6(id="total_positive_variation", children=''),
                                                         html.P(DATA_DICT['totale_positivi'])],
                                                        id="total_positive",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_cases_text", children=''),
                                                         html.H6(id="total_cases_variation", children=''),
                                                         html.P(DATA_DICT['totale_casi'])],
                                                        id="total_cases",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_recovered_text", children=''),
                                                         html.H6(id="total_recovered_variation", children=''),
                                                         html.P(DATA_DICT['totale_ospedalizzati'])],
                                                        id="total_recovered",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_deaths_text", children=''),
                                                         html.H6(id="total_deaths_variation", children=''),
                                                         html.P(DATA_DICT['deceduti'])],
                                                        id="total_deaths",
                                                        className="mini_container",
                                                    ),
                                                ],
                                                id="info-container",
                                                className="row container-display",
                                            ),  # END OF CARDS #
                                            # html.Div(  # START OF THE GRAPH UNDER THE CARDS#
                                            #     [
                                            #
                                            #     ],
                                            #     id="countGraphContainer",
                                            #     className="pretty_container",
                                            # ),  # END OF THE GRAPH #
                                        ],
                                        id="right-column",
                                        className="eight columns",
                                    ),  # END OF 2ND BLOCK
                                ],
                                className="row flex-display",
                            ),  # END OF 2ND INCAPSULATION  ############################################
                            html.Div(  #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                                [
                                    html.Div(
                                        [
                                            html.P("Seleziona una o più regioni italiane da confrontare:",
                                                   className="control_label"),
                                            dcc.Dropdown(id='dropdown_region_list_selected',
                                                         options=get_options(
                                                             df_regional_data[
                                                                 'denominazione_regione'].unique()),
                                                         multi=True,
                                                         value=new_positive_regions(),
                                                         className='dcc_control'
                                                         ),
                                            dcc.Graph(id="pie_graph")
                                        ],
                                        className="pretty_container four columns",
                                    ),
                                    html.Div(
                                        [
                                            dcc.Graph(id='regional_timeseries_linear'),
                                        ],
                                        className="pretty_container eight columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),  # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                            html.Div(  # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
                                [
                                    html.Div(
                                        [
                                            dcc.Graph(id="table_tab1"),

                                        ],
                                        className="pretty_container six columns",
                                    ),
                                    html.Div(
                                        [html.H5(id='bar_header', children='Top10 Regioni:', className='title'),
                                         dcc.Graph(id="bar_graph")],
                                        className="pretty_container six columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),  # END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component
                            html.Div(  # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
                                [
                                    html.Div(
                                        [html.H5(id='map_header', children='N° casi ogni 100.000 abitanti',
                                                 className='title'),
                                         dcc.Graph(id="map_graph")],
                                        className="pretty_container twelve columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),  # END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component

                        ]),  # END OF FIRST TAB
                dcc.Tab(label='Analisi dei dati regionali', value='tab_regional',
                        children=[  # START OF SECOND TAB
                            html.Div(  # START OF 2ND INCAPSULATION  ############################################
                                [
                                    html.Div(  # START OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                                        [
                                            # html.Div(
                                            #     [dcc.Graph(id="table_tab2")],
                                            #     className="pretty_container twelve columns",
                                            # ),
                                            # html.P("Seleziona la regione italiana da analizzare:",
                                            #        className="control_label"),
                                            # dcc.Dropdown(
                                            #     id='dropdown_region_selected',
                                            #     options=get_options(df_regional_data['denominazione_regione'].unique()),
                                            #     multi=False,
                                            #     value=df_regional_data['denominazione_regione'].sort_values()[0],
                                            #     className='dcc_control'
                                            # ),
                                        ],
                                        className="pretty_container four columns",
                                        id="cross-filter-options-tab2",
                                    ),
                                    html.Div(  # START OF 2ND BLOCK
                                        [
                                            html.P("Seleziona la regione italiana da analizzare:",
                                                   className="control_label"),
                                            dcc.Dropdown(
                                                id='dropdown_region_selected',
                                                options=get_options(df_regional_data['denominazione_regione'].unique()),
                                                multi=False,
                                                value=df_regional_data['denominazione_regione'].sort_values()[0],
                                                className='dcc_control'
                                            ),
                                            # html.H5(id='card_header_tab2', children='Dati Regionali',
                                            #         className='title'),
                                            html.Div(  # START OF CARDS #
                                                [
                                                    html.Div(
                                                        [html.H6(id="total_cases_text_tab2", children=''),
                                                         html.H6(id="total_cases_variation_tab2", children=''),
                                                         html.P("Totale Casi")],
                                                        id="total_cases_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_positive_text_tab2", children=''),
                                                         html.H6(id="total_positive_variation_tab2", children=''),
                                                         html.P("Casi Attivi")],
                                                        id="total_positive_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_recovered_text_tab2", children=''),
                                                         html.H6(id="total_recovered_variation_tab2", children=''),
                                                         html.P("Guariti")],
                                                        id="total_recovered_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_deaths_text_tab2", children=''),
                                                         html.H6(id="total_deaths_variation_tab2", children=''),
                                                         html.P("Decessi")],
                                                        id="total_deaths_tab2",
                                                        className="mini_container",
                                                    ),
                                                ],
                                                id="info-container_1_tab2",
                                                className="row container-display",
                                            ),
                                            html.Div(  # START OF CARDS #
                                                [
                                                    html.Div(
                                                        [html.H6(id="total_hospitalized_w_symptoms_text_tab2",
                                                                 children=''),
                                                         html.H6(id="total_hospitalized_w_symptoms_variation_tab2",
                                                                 children=''),
                                                         html.P("Ospedalizzati con sintomi")],
                                                        id="total_hospitalized_w_symptoms_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_icu_text_tab2", children=''),
                                                         html.H6(id="total_icu_variation_tab2", children=''),
                                                         html.P("Terapia intensiva")],
                                                        id="total_icu_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_isolation_text_tab2", children=''),
                                                         html.H6(id="total_isolation_variation_tab2", children=''),
                                                         html.P("Isolamento domiciliare")],
                                                        id="total_isolation_tab2",
                                                        className="mini_container",
                                                    ),
                                                    html.Div(
                                                        [html.H6(id="total_swabs_text_tab2", children=''),
                                                         html.H6(id="total_swabs_variation_tab2", children=''),
                                                         html.P("Tamponi effettuati")],
                                                        id="total_swabs_tab2",
                                                        className="mini_container",
                                                    ),
                                                ],
                                                id="info-container_2_tab2",
                                                className="row container-display",
                                            ),
                                        ],
                                        id="right-column_tab2",
                                        className="eight columns",
                                    ),  # END OF 2ND BLOCK
                                ],
                                className="row flex-display",
                            ),  # END OF 2ND INCAPSULATION  ############################################
                            html.Div(  # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
                                [
                                    html.Div(
                                        [html.H5(id='bar_header_tab2', children='Casi Attivi per giorno:',
                                                 className='title'),
                                         dcc.Graph(id="bar_graph_tab2")],
                                        className="pretty_container twelve columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),  # END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component

                        ]),  # END OF SECOND TAB
            ]),  # END OF TABS COMPONENT CREATOR

            html.Div(  # START 4TH INCAPS
                [
                    html.Div(  # START OF NEWS FEEDER
                        children=[html.Div(id="news", children=create_news())],
                        className="pretty_container six columns",
                    ),  # END OF NEWS FEEDER
                    html.Div(  # START OF NEWS FEEDER
                        children=[html.Div(id="contacts", children=create_contacts())],
                        className="pretty_container six columns",
                    ),
                ],
                className="row flex-display",
            ),  # END OF 4TH INCAPSULATION
            html.A(
                html.P(
                    id="version_text",
                    className="p-version changelog",
                    children="v1.0.7"
                ),
                href="https://github.com/gerrygeko/covid-data-analysis/blob/master/CHANGELOG.md"
            )
        ],  # END OF SUPEREME INCAPSULATION ############################################
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )


schedule.every(30).minutes.do(load_interactive_data)
schedule.every().day.at("18:05").do(load_interactive_data)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(10)


def initialize_thread():
    log.info('Starting schedule thread')
    t = Thread(target=run_schedule)
    t.start()


initialize_thread()
load_interactive_data()
app.config.suppress_callback_exceptions = True
# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("regional_timeseries_linear", "figure")],
)
app.title = "SARS-CoV-2-Gellex"
app_layout()
new_positive_regions()

if __name__ == '__main__':
    app.server.run(debug=False)  # debug=True active a button in the bottom right corner of the web page
