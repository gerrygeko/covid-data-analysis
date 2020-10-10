import copy
import csv
import json as js
import locale
import time
from email.utils import parsedate_to_datetime
from threading import Thread
from urllib.request import urlopen

import dash
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import requests
import schedule
from dash.dependencies import Input, Output, ClientsideFunction
from dash.exceptions import PreventUpdate

import logger
from constants import DATE_PROPERTY_NAME_EN, NUMBER_OF_WORLD_COUNTRIES, DATE_PROPERTY_NAME_IT, \
    LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA, INHABITANT_RATE, URL_GEOJSON_REGIONS, URL_GEOJSON_WORLD_COUNTRIES, \
    URL_CSV_REGIONAL_DATA, URL_CSV_ITALY_DATA, URL_CSV_WORLDWIDE_AGGREGATE_DATA, URL_CSV_WORLD_COUNTRIES_DATA, \
    LIST_OF_SHIPS
from html_components import create_news, create_page_components, locale_language
from resources import load_resource, start_translation
from utils import is_debug_mode_enabled

locale.setlocale(locale.LC_ALL, 'it_IT.utf8')
debug_mode_enabled = is_debug_mode_enabled()

log = logger.get_logger()
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"},
                         {"property": "og:title", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:image", "content": "https://i.ibb.co/r5JFMRY/splash-metatag.png"},
                         {"property": "og:description", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:url", "content": "https://www.data-covid.com/"}]
)
server = app.server

field_list_to_rate_italian_regions = ['ricoverati_con_sintomi', 'terapia_intensiva',
                                      'totale_ospedalizzati', 'isolamento_domiciliare',
                                      'totale_positivi', 'nuovi_positivi', 'dimessi_guariti',
                                      'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'totale_casi',
                                      'tamponi', 'casi_testati']

field_list_to_rate_country_world = ['Confirmed', 'Recovered', 'Deaths', 'Active_cases']


def load_csv_from_file(path):
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
        k, v = row
        d[k] = v
    return d


def load_csv(url, data_string):
    data_loaded = pd.read_csv(url, parse_dates=[data_string])
    return data_loaded


def load_geojson(url):
    with urlopen(url) as response:
        json = js.load(response)
    return json


italy_regional_population = load_csv_from_file('assets/italy_region_population_2020.csv')
world_population = load_csv_from_file('assets/worldwide_population_2020.csv')
geojson_province = load_geojson(URL_GEOJSON_REGIONS)
last_update_content_regional_data = 0
last_update_content_national_data = 0
last_update_content_worldwide_aggregate_data = 0
last_update_content_country_world_data = 0
df_regional_data = None
df_national_data = None
df_worldwide_aggregate_data = None
df_country_world_data = None
df_rate_regional = None
df_rate_country_world = None
date_last_update_world_aggregate = None
date_last_update_italy = None
date_last_update_regional = None

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


def create_figure(data, title):
    layout_figure = copy.deepcopy(layout)

    layout_figure['title'] = title
    layout_figure['hovermode'] = 'x unified'
    figure = dict(data=data, layout=layout_figure)
    return figure


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


def create_scatter_plot_by_country_world(data_frame, title, x_axis_data, y_axis_data_mapping_country_world):
    scatter_list = []
    y_axis_data_mapping_country_world.sort(key=lambda tup: tup[1])
    for field, country in y_axis_data_mapping_country_world:
        scatter = go.Scatter(x=x_axis_data, y=data_frame[data_frame['Country'] == country][field],
                             mode='lines+markers',
                             opacity=0.7,
                             name=country,
                             line=dict(shape="spline", smoothing=1, width=1),
                             textposition='bottom center')
        scatter_list.append(scatter)
    figure = create_figure(scatter_list, title)
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                                               Input('dropdown_italy_data_selected', 'value')])
def update_regions_line_chart(region_list, data_selected):
    regions_list_mapping = []
    # if no region selected, create empty figure
    x_axis_data = df_regional_data[df_regional_data['denominazione_regione'] == "Abruzzo"]['data']
    if len(region_list) == 0 or data_selected is None:
        figure = create_scatter_plot(df_regional_data, '', x_axis_data, [])
        return figure
    for region in region_list:
        regions_list_mapping.append((data_selected, region))
    title = load_resource(data_selected)
    figure = create_scatter_plot_by_region(df_regional_data, title,
                                           x_axis_data, regions_list_mapping)
    log.info('Updating main graph')
    return figure


# Callback for timeseries/country
@app.callback(Output('country_world_linear_chart', 'figure'), [Input('dropdown_country_list_selected', 'value'),
                                                               Input('dropdown_country_data_selected', 'value')])
def update_country_world_line_chart(country_list, data_selected):
    countries_list_mapping = []
    # if no country was selected, create empty figure
    x_axis_data = df_country_world_data[df_country_world_data['Country'] == "Italy"][DATE_PROPERTY_NAME_EN]
    if len(country_list) == 0 or data_selected is None:
        figure = create_scatter_plot(df_country_world_data, '', x_axis_data, [])
        return figure
    for country in country_list:
        countries_list_mapping.append((data_selected, country))
    title = load_resource(data_selected)
    figure = create_scatter_plot_by_country_world(df_country_world_data, title,
                                                  x_axis_data, countries_list_mapping)
    log.info('Updating Country World Line chart')
    return figure


@app.callback(Output('map_graph', 'figure'), [Input('dropdown_italy_data_selected', 'value')])
def update_map_graph(data_selected):
    df = df_rate_regional.tail(21)
    df['population'] = pd.to_numeric(df['population'], downcast='float')
    df['population'] = df['population'].apply(format_value_string_to_locale)
    date_string = df_national_data.iloc[-1]['data'].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=URL_GEOJSON_REGIONS, locations='codice_regione',
                                  featureidkey="properties.reg_istat_code_num",
                                  color=data_selected,
                                  color_continuous_scale="Blues",
                                  hover_name='denominazione_regione',
                                  hover_data=['population'],
                                  range_color=(df[data_selected].min(), df[data_selected].max()),
                                  mapbox_style="carto-positron",
                                  zoom=4, center={"lat": 42.0902, "lon": 11.7129},
                                  opacity=0.5,
                                  labels={data_selected: (load_resource('label_persone'))}
                                  )
    figure.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        annotations=[dict(
            x=0.0,
            y=0.01,
            xref='paper',
            yref='paper',
            text='*{} <br>'.format(load_resource(data_selected))
                 + load_resource('label_hover_map')
                 + '<br> {}'.format(date_string),
            showarrow=False
        )]
    )
    log.info('Updating map graph')
    return figure


@app.callback(Output('bar_graph', 'figure'), [Input('dropdown_italy_data_selected', 'value')])
def update_bar_graph(data_selected):
    df_sub = df_regional_data.tail(21)
    df_sorted = df_sub.sort_values(by=[data_selected])
    df_sorted = df_sorted.tail(10)
    region_list = df_sorted['denominazione_regione'].values.tolist()
    value_list = df_sorted[data_selected].values.tolist()
    data = [go.Bar(x=value_list,
                   y=region_list,
                   text=region_list,
                   textposition='auto',
                   hovertemplate='<i><b>Regione</b></i>: %{y}' +
                                 '<br><b>N.</b>: %{x}<br>' +
                                 '<extra></extra>',
                   insidetextanchor="start",
                   orientation='h'
                   )
            ]
    layout_bar = copy.deepcopy(layout)
    layout_bar['title'] = '{}'.format(load_resource(data_selected))
    layout_bar['yaxis'] = dict(zeroline=False, showline=False, showgrid=False, showticklabels=False)
    figure = dict(data=data, layout=layout_bar)
    log.info('Updating bar graph in Tab 1')
    return figure


@app.callback(Output('world_map', 'figure'), [Input('dropdown_country_data_selected', 'value')])
def update_world_map(data_selected):
    df = df_rate_country_world.copy()
    df = df[~df['Country'].isin(LIST_OF_SHIPS)]
    df['Population'] = pd.to_numeric(df['Population'], downcast='float')
    df['Population'] = df['Population'].apply(format_value_string_to_locale)
    df.sort_values(by=['Country'], inplace=True)
    date_string = df.iloc[-1][DATE_PROPERTY_NAME_EN].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=URL_GEOJSON_WORLD_COUNTRIES, locations='Country',
                                  featureidkey="properties.ADMIN",
                                  color=data_selected,
                                  color_continuous_scale='Blues',
                                  hover_name='Country',
                                  hover_data=['Population'],
                                  range_color=(df[data_selected].min(), df[data_selected].max()),
                                  mapbox_style="carto-positron",
                                  zoom=1, center={"lat": 42.0902, "lon": 11.7129},
                                  opacity=0.5,
                                  labels={data_selected: (load_resource('label_persone'))}
                                  )
    figure.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        annotations=[dict(
            x=0.0,
            y=0.01,
            xref='paper',
            yref='paper',
            text='*{} <br>'.format(load_resource(data_selected))
                 + load_resource('label_hover_map')
                 + '<br> {}'.format(date_string),
            showarrow=False
        )]
    )
    log.info('Updating World Choropleth Map')
    return figure


@app.callback(Output('linear_chart_italy', 'figure'), [Input('dropdown_italy_data_selected', 'value')])
def update_italian_linear_chart(data_selected):
    layout_italian_active_cases = copy.deepcopy(layout)
    df = df_national_data
    colors = ["rgb(204, 51, 0)", "rgb(4, 74, 152)", "rgb(123, 199, 255)"]
    x_list = df[DATE_PROPERTY_NAME_IT]
    y_data_selected = df[data_selected].values.tolist()
    y_active_cases_list_1 = df['terapia_intensiva'].values.tolist()
    y_active_cases_list_2 = df['ricoverati_con_sintomi'].values.tolist()
    y_active_cases_list_3 = df['isolamento_domiciliare'].values.tolist()
    data_list = [
        dict(
            type="scatter",
            x=x_list,
            y=y_active_cases_list_3,
            name=load_resource('isolamento_domiciliare'),
            fill='tozeroy',
            marker=dict(color=colors[2]),
        ),
        dict(
            type="scatter",
            x=x_list,
            y=y_active_cases_list_2,
            name=load_resource('ricoverati_con_sintomi'),
            fill='tozeroy',
            marker=dict(color=colors[1])
        ),
        dict(
            type="scatter",
            x=x_list,
            y=y_active_cases_list_1,
            name=load_resource('terapia_intensiva'),
            fill='tozeroy',
            marker=dict(color=colors[0]),
        ),
        dict(
            type="scatter",
            x=x_list,
            y=y_data_selected,
            name=load_resource(data_selected),
            fill='tozeroy',
            marker=dict(color=colors[2])
        )
    ]
    if data_selected == 'totale_positivi':
        data = [data_list[0], data_list[1], data_list[2]]
        layout_italian_active_cases["title"] = load_resource('label_casi_attivi')
    else:
        data = [data_list[3]]
        layout_italian_active_cases["title"] = load_resource(data_selected)

    layout_italian_active_cases["showlegend"] = True
    layout_italian_active_cases["autosize"] = True
    figure = dict(data=data, layout=layout_italian_active_cases)

    log.info('Updating Italian Linear Graph')
    return figure


@app.callback(Output('linear_chart_world', 'figure'), [Input('dropdown_country_data_selected', 'value')])
def update_world_linear_chart(data_selected):
    layout_world_linear_chart = copy.deepcopy(layout)
    df = df_worldwide_aggregate_data
    y_list_1 = df[data_selected].values.tolist()
    x_list = df[DATE_PROPERTY_NAME_EN]
    colors = ["rgb(204, 51, 0)", "rgb(4, 74, 152)", "rgb(123, 199, 255)"]
    data = [
        dict(
            type="scatter",
            x=x_list,
            y=y_list_1,
            name=load_resource(data_selected),
            fill='tozeroy',
            marker=dict(color=colors[2])
        )
    ]

    layout_world_linear_chart["title"] = load_resource(data_selected)
    layout_world_linear_chart["showlegend"] = True
    layout_world_linear_chart["autosize"] = True

    figure = dict(data=data, layout=layout_world_linear_chart)
    log.info('Updating World Linear Chart')
    return figure


@app.callback(Output('bar_graph_tab2', 'figure'), [Input('dropdown_region_selected', 'value')])
def update_regional_graph_active_cases(region_selected):
    layout_italian_active_cases = copy.deepcopy(layout)
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    # Since we filter based on the region, our indexes are not sequential anymore
    # so we reindex to access to specific row easier later
    df.reset_index(inplace=True)
    y_list_1 = df['terapia_intensiva'].values.tolist()
    y_list_2 = df['ricoverati_con_sintomi'].values.tolist()
    y_list_3 = df['isolamento_domiciliare'].values.tolist()
    x_list = df['data']
    colors = ["rgb(204, 51, 0)", "rgb(4, 74, 152)", "rgb(123, 199, 255)"]
    data = [
        dict(
            type="scatter",
            x=x_list,
            y=y_list_3,
            name=load_resource('isolamento_domiciliare'),
            fill='tozeroy',
            marker=dict(color=colors[2]),
        ),
        dict(
            type="scatter",
            x=x_list,
            y=y_list_2,
            name=load_resource('ricoverati_con_sintomi'),
            fill='tozeroy',
            marker=dict(color=colors[1])
        ),
        dict(
            type="scatter",
            x=x_list,
            y=y_list_1,
            name=load_resource('terapia_intensiva'),
            fill='tozeroy',
            marker=dict(color=colors[0]),
        )
    ]

    layout_italian_active_cases["title"] = load_resource('label_casi_attivi')
    layout_italian_active_cases["showlegend"] = True
    layout_italian_active_cases["autosize"] = True

    figure = dict(data=data, layout=layout_italian_active_cases)
    log.info('Updating bar graph in Tab 2')
    return figure


@app.callback([Output('total_positive_text', 'children'),
               Output('total_cases_text', 'children'),
               Output('total_recovered_text', 'children'),
               Output('total_deaths_text', 'children'),
               Output('total_icu_text', 'children'),
               Output('total_swabs_text', 'children'),
               Output('total_positive_variation', 'children'),
               Output('total_cases_variation', 'children'),
               Output('total_recovered_variation', 'children'),
               Output('total_deaths_variation', 'children'),
               Output('total_icu_variation', 'children'),
               Output('total_swabs_variation', 'children'),
               Output('sub_header_italian_update', 'children')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_text(self):
    log.info('update cards')
    sub_header_italian_text = date_last_update_italy
    field_list = ['totale_positivi', 'totale_casi', 'dimessi_guariti', 'deceduti', 'terapia_intensiva', 'tamponi']
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
    return (*total_text_values), (*variation_text_values), sub_header_italian_text


@app.callback([Output('total_positive_variation', 'style'),
               Output('total_cases_variation', 'style'),
               Output('total_recovered_variation', 'style'),
               Output('total_deaths_variation', 'style'),
               Output('total_icu_variation', 'style'),
               Output('total_swabs_variation', 'style')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_color(self):
    field_list = ['totale_positivi', 'totale_casi', 'dimessi_guariti', 'deceduti', 'terapia_intensiva', 'tamponi']
    color_cards_list = []
    for field in field_list:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day = df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if variation_previous_day > 0 and field == 'dimessi_guariti' or \
                variation_previous_day > 0 and field == 'tamponi' or \
                variation_previous_day < 0 and field == 'terapia_intensiva' or \
                variation_previous_day < 0 and field == 'totale_positivi':
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
                        {'color': color_cards_list[5]}]
    return dictionary_color


@app.callback([Output('confirmed_text_worldwide_aggregate', 'children'),
               Output('recovered_text_worldwide_aggregate', 'children'),
               Output('deaths_text_worldwide_aggregate', 'children'),
               Output('increase_rate_text_worldwide_aggregate', 'children'),
               Output('confirmed_variation_worldwide_aggregate', 'children'),
               Output('recovered_variation_worldwide_aggregate', 'children'),
               Output('deaths_variation_worldwide_aggregate', 'children'),
               Output('increase_rate_variation_worldwide_aggregate', 'children'),
               Output('sub_header_worldwide_update', 'children')
               ], [Input("i_news", "n_intervals")])
def update_world_cards_text(self):
    log.info('Update World Cards')
    sub_header_worldwide_text = date_last_update_world_aggregate
    field_list = ['Confirmed', 'Recovered', 'Deaths', 'Increase rate']
    total_text_values = []
    variation_text_values = []
    for field in field_list:
        card_value = df_worldwide_aggregate_data[field].iloc[-1]
        card_value_previous_day = df_worldwide_aggregate_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        total_text = f'{card_value:n}'
        total_text_values.append(total_text)
        sign = '+' if variation_previous_day > 0 else ''
        variation_text = f'{sign}{variation_previous_day:n}'
        variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values), sub_header_worldwide_text


@app.callback([Output('confirmed_variation_worldwide_aggregate', 'style'),
               Output('recovered_variation_worldwide_aggregate', 'style'),
               Output('deaths_variation_worldwide_aggregate', 'style'),
               Output('increase_rate_variation_worldwide_aggregate', 'style')
               ], [Input("i_news", "n_intervals")])
def update_world_cards_color(self):
    field_list = ['Confirmed', 'Recovered', 'Deaths', 'Increase rate']
    color_cards_list = []
    for field in field_list:
        card_value = df_worldwide_aggregate_data[field].iloc[-1]
        card_value_previous_day = df_worldwide_aggregate_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if variation_previous_day <= 0 and field == 'Confirmed' or \
                variation_previous_day > 0 and field == 'Recovered':
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


@app.callback(Output('table_tab_country_world', 'figure'), [Input("dropdown_country_data_selected", "value")])
def update_data_table_country_world(data_selected):
    df_sub = df_country_world_data
    df = df_sub.copy()
    df = df.sort_values(by=[DATE_PROPERTY_NAME_EN])
    df = df.tail(NUMBER_OF_WORLD_COUNTRIES)
    df.sort_values(by=[data_selected], ascending=False, inplace=True)
    df[data_selected] = pd.to_numeric(df[data_selected], downcast='float')
    df[data_selected] = df[data_selected].apply(format_value_string_to_locale)
    figure = go.Figure(data=[go.Table(
        header=dict(values=(load_resource('Country'), load_resource(data_selected)),
                    fill_color='lightskyblue',
                    font_color='white',
                    font_size=15,
                    align='left'),
        cells=dict(values=[df['Country'], df[data_selected]],
                   fill_color='whitesmoke',
                   align='center',
                   font_size=13,
                   height=20))
    ])
    figure.update_layout(height=520, margin=dict(l=0, r=0, b=0, t=0))
    return figure


@app.callback(Output('table_tab1', 'figure'), [Input("dropdown_italy_data_selected", "value")])
def update_data_table_national(data_selected):
    df = df_regional_data.tail(21)
    df = df.sort_values(by=[data_selected], ascending=False)
    df[data_selected] = pd.to_numeric(df[data_selected], downcast='float')
    df[data_selected] = df[data_selected].apply(format_value_string_to_locale)
    figure = go.Figure(data=[go.Table(
        header=dict(values=(load_resource('denominazione_regione'), load_resource(data_selected)),
                    fill_color='lightskyblue',
                    font_color='white',
                    font_size=15,
                    align='left'),
        cells=dict(values=[df['denominazione_regione'], df[data_selected]],
                   fill_color='whitesmoke',
                   align='center',
                   font_size=13,
                   height=20))
    ])
    figure.update_layout(height=470, margin=dict(l=0, r=0, b=0, t=0))
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
               Output('total_swabs_variation_tab2', 'children'),
               Output('sub_header_ita_regions_update', 'children'),
               ], [Input("dropdown_region_selected", "value")])
def update_regional_cards_text(region_selected):
    log.info('Update regional cards')
    sub_header_ita_regions_text = date_last_update_regional
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
    return (*total_text_values), (*variation_text_values), sub_header_ita_regions_text


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


@app.callback([Output('mean_total_cases', 'children'),
               Output('string_max_date_new_positives', 'children'),
               Output('string_max_value_new_positives', 'children'),
               ], [Input("dropdown_region_selected", "value")])
def update_regional_details_card(region_selected):
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    rounded_mean = round(df['nuovi_positivi'].mean())
    max_value_new_positives = df['nuovi_positivi'].max()
    df_sub = df.loc[df['nuovi_positivi'] == max_value_new_positives]
    date_max_value = df_sub['data']
    string_max_date = ""
    for date in date_max_value:
        string_max_date = string_max_date + str(date.strftime('%d/%m/%Y')) + '\n'
    string_max_value = str(max_value_new_positives)
    return rounded_mean, string_max_date, string_max_value


@app.callback([Output('total_confirmed_text_world', 'children'),
               Output('total_active_cases_text_world', 'children'),
               Output('total_recovered_text_world', 'children'),
               Output('total_deaths_text_world', 'children'),
               Output('total_confirmed_variation_world', 'children'),
               Output('total_active_cases_variation_world', 'children'),
               Output('total_recovered_variation_world', 'children'),
               Output('total_deaths_variation_world', 'children'),
               ], [Input("dropdown_country_selected", "value")])
def update_country_world_cards_text(country_selected):
    log.info('Update Country cards')
    field_list = ['Confirmed', 'Active_cases', 'Recovered', 'Deaths']
    total_text_values = []
    variation_text_values = []
    df_sub = df_country_world_data[df_country_world_data['Country'] == country_selected]
    df = df_sub.copy()
    df_sorted = df.sort_values(by=[DATE_PROPERTY_NAME_EN])
    df_sorted = df_sorted.tail(NUMBER_OF_WORLD_COUNTRIES + len(LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA))
    for field in field_list:
        if country_selected in LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
            total_text_values = ['N/D'] * 4
            variation_text_values = ['N/D'] * 4
        else:
            card_value = df_sorted[field].iloc[-1]
            card_value_previous_day = df_sorted[field].iloc[-2]
            variation_previous_day = card_value - card_value_previous_day
            total_text = f'{card_value:n}'
            total_text_values.append(total_text)
            sign = '+' if variation_previous_day > 0 else ''
            variation_text = f'{sign}{variation_previous_day:n}'
            variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values),


@app.callback([Output('total_confirmed_variation_world', 'style'),
               Output('total_active_cases_variation_world', 'style'),
               Output('total_recovered_variation_world', 'style'),
               Output('total_deaths_variation_world', 'style'),
               ], [Input("dropdown_country_selected", "value")])
def update_country_world_cards_color(country_selected):
    field_list = ['Confirmed', 'Active_cases', 'Recovered', 'Deaths']
    color_cards_list = []
    df_sub = df_country_world_data[df_country_world_data['Country'] == country_selected]
    df = df_sub.copy()
    for field in field_list:
        if country_selected in LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
            color = 'grey'
            color_cards_list.append(color)
        else:
            card_value = df[field].iloc[-1]
            card_value_previous_day = df[field].iloc[-2]
            variation_previous_day = card_value - card_value_previous_day
            if variation_previous_day > 0 and field == 'Recovered' or \
                    variation_previous_day <= 0 and field == 'Active_cases' or \
                    variation_previous_day == 0 and field == 'Confirmed' or \
                    variation_previous_day == 0 and field == 'Deaths':
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


@app.callback(Output('mainContainer', 'children'),
              [Input('dropdown_language_selected', 'value')])
def update_language(language):
    if language == locale_language.language:
        # Check required otherwise during startup the page is loaded twice
        log.info("Preventing language update since no language changes was detected")
        raise PreventUpdate
    locale_language.language = language
    log.info(f"User switching language to: {language}")
    return create_page_components(app, df_regional_data)


@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news(input):
    log.info('Update news')
    return create_news()


# Merge data of P.A Bolzano and P.A. Trento (in Trentino Alto Adige region, with 'codice_regione' = 4) to match
# GeoJson structure
def adjust_region(df_sb):
    trento_row = df_sb.loc[df_sb['codice_regione'] == 22].squeeze()
    bolzano_row = df_sb.loc[df_sb['codice_regione'] == 21].squeeze()
    trentino_row = trento_row
    df_sb.reindex(list(range(0, 21)))
    for field in field_list_to_rate_italian_regions:
        trento_value = trento_row.get(field)
        bolzano_value = bolzano_row.get(field)
        trentino_row.at[field] = trento_value + bolzano_value
    df_sb.drop([trento_row.name, bolzano_row.name], inplace=True)
    trentino_row.at['codice_regione'] = 4
    trentino_row.at['denominazione_regione'] = 'Trentino-Alto Adige'
    df_sb = df_sb.append(trentino_row)
    return df_sb


def load_country_world_rate_data_frame(df):
    # We create a copy of the original DataFrame to avoid working on the original DataFrame and to suppress warning
    df_sb = df.copy()
    df_sb = df_sb.sort_values(by=[DATE_PROPERTY_NAME_EN])
    df_sb = df_sb.tail(NUMBER_OF_WORLD_COUNTRIES + len(LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA))
    df_sb.sort_values(by=['Country'], inplace=True)
    df_sb['Population'] = list(world_population.values())
    # Convert field to float
    for field in field_list_to_rate_country_world:
        df_sb[field] = pd.to_numeric(df_sb[field], downcast='float')
    for i, row in df_sb.iterrows():
        population = row['Population']
        for field in field_list_to_rate_country_world:
            value = row[field]
            pressure_value = (float(value) / float(population)) * INHABITANT_RATE
            df_sb.at[i, field] = round(pressure_value, 2)
    return df_sb


def load_region_rate_data_frame(df):
    # We create a copy of the original DataFrame to avoid working on the original DataFrame and to suppress warning
    df_sb = df.copy()
    df_sb = df_sb.tail(21)
    df_sb = adjust_region(df_sb)
    df_sb['population'] = list(italy_regional_population.values())
    # Convert field to float
    for field in field_list_to_rate_italian_regions:
        df_sb[field] = pd.to_numeric(df_sb[field], downcast='float')
    for i, row in df_sb.iterrows():
        population = row['population']
        for field in field_list_to_rate_italian_regions:
            value = row[field]
            pressure_value = (float(value) / float(population)) * INHABITANT_RATE
            df_sb.at[i, field] = round(pressure_value, 2)
    return df_sb


def adjust_df_world_to_geojson(df):
    df['Country'] = df['Country'].replace(['US', 'Congo (Kinshasa)', 'Congo (Brazzaville)', 'Korea, South',
                                           'Cote d\'Ivoire', 'Czechia', 'Serbia', 'Taiwan*', 'Tanzania',
                                           'North Macedonia'],
                                          ['United States of America', 'Democratic Republic of the Congo',
                                           'Republic of Congo', 'South Korea',
                                           'Ivory Coast', 'Czech Republic', 'Republic of Serbia', 'Taiwan',
                                           'United Republic of Tanzania', 'Macedonia']
                                          )
    return df


# for adding country not included in the df_country world source
# useful for mapping countries with geojson data
def add_excluded_country_world(df):
    last_date_df = df.iloc[-1][DATE_PROPERTY_NAME_EN]
    list_of_row = []
    for country_without_data in LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
        list_of_row.append({'Date': last_date_df,
                            'Country': country_without_data,
                            'Confirmed': 0,
                            'Recovered': 0,
                            'Deaths': 0,
                            'Active_cases': 0
                            })

    for row in list_of_row:
        df = df.append(row, ignore_index=True)
    return df


def get_content_length(url):
    resp = requests.head(url)
    if resp.status_code != 200:
        log.error(f"Request failed trying to contact URL: {url}")
        return -1
    size = resp.headers["Content-Length"]
    return size


def get_last_update(url):
    resp = requests.head(url)
    if resp.status_code != 200:
        log.error(f"Request failed trying to contact URL: {url}")
        last_update = 'Time not available'
    else:
        date_update_string = resp.headers["Date"]
        last_update = parsedate_to_datetime(date_update_string).astimezone(tz=pytz.timezone('Europe/Rome'))
    string_date_update = last_update.strftime(load_resource('label_last_update') + " %d/%m/%Y %H:%M:%S")
    return string_date_update


def load_interactive_data():
    log.info('Start scheduled task to check data updates')
    global df_regional_data, df_national_data, df_country_world_data, df_worldwide_aggregate_data, df_rate_regional, \
        df_rate_country_world, last_update_content_regional_data, last_update_content_national_data, \
        last_update_content_worldwide_aggregate_data, last_update_content_country_world_data, \
        date_last_update_world_aggregate, date_last_update_italy, date_last_update_regional
    current_update_content_regional_data = int(get_content_length(URL_CSV_REGIONAL_DATA))
    current_update_content_national_data = int(get_content_length(URL_CSV_ITALY_DATA))
    current_update_content_worldwide_aggregate_data = int(get_content_length(URL_CSV_WORLDWIDE_AGGREGATE_DATA))
    current_update_content_country_world_data = int(get_content_length(URL_CSV_WORLD_COUNTRIES_DATA))

    # Check if updates for Worldwide Aggregate data is required
    if current_update_content_worldwide_aggregate_data == -1:
        log.info("Provider's server for Worldwide Aggregate data is unresponsive, retrying later")
    elif current_update_content_worldwide_aggregate_data != last_update_content_worldwide_aggregate_data:
        log.info('Worldwide Aggregate data update required')
        df_worldwide_aggregate_data = load_csv(URL_CSV_WORLDWIDE_AGGREGATE_DATA, DATE_PROPERTY_NAME_EN)
        df_worldwide_aggregate_data['Active_cases'] = df_worldwide_aggregate_data['Confirmed'] - \
                                                      (df_worldwide_aggregate_data['Recovered'] +
                                                       df_worldwide_aggregate_data['Deaths'])
        date_last_update_world_aggregate = get_last_update(URL_CSV_WORLDWIDE_AGGREGATE_DATA)
        log.info(f"Old Content-length: {last_update_content_worldwide_aggregate_data} bytes")
        log.info(f"New Content-length: {current_update_content_worldwide_aggregate_data} bytes")
        last_update_content_worldwide_aggregate_data = current_update_content_worldwide_aggregate_data
    else:
        log.info('No updates required for Worldwide Aggregate data')

    # Check if updates for World data is required
    if current_update_content_country_world_data == -1:
        log.info("Provider's server for Country World data is unresponsive, retrying later")
    elif current_update_content_country_world_data != last_update_content_country_world_data:
        log.info('Country World data update required')
        df_country_world_data = load_csv(URL_CSV_WORLD_COUNTRIES_DATA, DATE_PROPERTY_NAME_EN)
        df_country_world_data['Active_cases'] = df_country_world_data['Confirmed'] - \
                                                (df_country_world_data['Recovered'] + df_country_world_data['Deaths'])
        df_country_world_data = adjust_df_world_to_geojson(df_country_world_data)
        df_country_world_data = add_excluded_country_world(df_country_world_data)
        df_rate_country_world = load_country_world_rate_data_frame(df_country_world_data)
        log.info(f"Old Content-length: {last_update_content_country_world_data} bytes")
        log.info(f"New Content-length: {current_update_content_country_world_data} bytes")
        last_update_content_country_world_data = current_update_content_country_world_data
    else:
        log.info('No updates required for Country World data')

    # Check if updates for National data is required
    if current_update_content_national_data == -1:
        log.info("Provider's server for National data is unresponsive, retrying later")
    elif current_update_content_national_data != last_update_content_national_data:
        log.info('National data update required')
        df_national_data = load_csv(URL_CSV_ITALY_DATA, DATE_PROPERTY_NAME_IT)
        date_last_update_italy = get_last_update(URL_CSV_ITALY_DATA)
        log.info(f"Old Content-length: {last_update_content_national_data} bytes")
        log.info(f"New Content-length: {current_update_content_national_data} bytes")
        last_update_content_national_data = current_update_content_national_data
    else:
        log.info('No updates required for National data')

    # Check if updates for Regional data is required
    if current_update_content_regional_data == -1:
        log.info("Provider's server for Regional Data is unresponsive, retrying later")
    elif current_update_content_regional_data != last_update_content_regional_data or df_rate_regional is None:
        log.info('Regional data update required')
        df_regional_data = load_csv(URL_CSV_REGIONAL_DATA, DATE_PROPERTY_NAME_IT)
        df_rate_regional = load_region_rate_data_frame(df_regional_data)
        date_last_update_regional = get_last_update(URL_CSV_REGIONAL_DATA)
        log.info(f"Old Content-length: {last_update_content_regional_data} bytes")
        log.info(f"New Content-length: {current_update_content_regional_data} bytes")
        last_update_content_regional_data = current_update_content_regional_data
    else:
        log.info('No updates required for Regional data')
    log.info('Update task completed')


def app_layout():
    app.layout = html.Div(
        children=create_page_components(app, df_regional_data, df_country_world_data),
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )


schedule.every(30).minutes.do(load_interactive_data)
schedule.every().day.at("08:15").do(load_interactive_data)
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
if not debug_mode_enabled:
    start_translation()

if __name__ == '__main__':
    app.server.run(debug=False)  # debug=True active a button in the bottom right corner of the web page
