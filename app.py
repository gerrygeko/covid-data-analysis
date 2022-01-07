import copy
import datetime
import locale
import threading
import time
from email.utils import parsedate_to_datetime
from threading import Thread

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
from datetime import timedelta

import logger
import constants
from html_components import create_news, create_page_components, locale_language
from resources import load_resource, start_translation
from utils import is_debug_mode_enabled, layout, load_csv_from_file, load_csv

app_start_time = time.time()
threading.current_thread().name = "main-thread"
locale.setlocale(locale.LC_ALL, 'it_IT.utf8') # remove # before commit
logger.initialize_logger()
log = logger.get_logger()
debug_mode_enabled = is_debug_mode_enabled()


if not debug_mode_enabled:
    t = Thread(name="translation-thread", target=start_translation)
    t.start()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"},
                         {"property": "og:title", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:image", "content": "https://i.ibb.co/86dGbRM/metatag-splash-1200x630.png"},
                         {"property": "og:description", "content": "SARS-CoV-2-Gellex"},
                         {"property": "og:url", "content": "https://www.data-covid.com/"}]
)

server = app.server

field_list_to_rate_italian_regions = ['ricoverati_con_sintomi', 'terapia_intensiva',
                                      'totale_ospedalizzati', 'isolamento_domiciliare',
                                      'totale_positivi', 'nuovi_positivi', 'dimessi_guariti',
                                      'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'totale_casi',
                                      'tamponi', 'casi_testati']

italy_regional_population = load_csv_from_file('assets/italy_region_population_2020.csv')
italy_ICU = load_csv_from_file('assets/italian_ICU_19_10_2020.csv')
world_population = load_csv_from_file('assets/worldwide_population_2020.csv')
last_update_content_regional_data = 0
last_update_content_national_data = 0
last_update_content_worldwide_aggregate_data = 0
last_update_content_country_world_data = 0
last_update_content_vaccines_italy_data = 0
df_regional_data = None
df_national_data = None
df_vaccines_italy_summary_latest = None
df_vaccines_italy_registry_summary_latest = None
df_vaccines_italy_admin_summary_latest = None
df_vaccines_italy_admin_summary_latest_grouped_by_ITA = None
df_vaccines_italy_daily_summary_latest_grouped_by_ITA = None
df_vaccines_italy_administration_point = None
df_worldwide_aggregate_data = None
df_country_world_data = None
df_rate_regional = None
df_rate_country_world = None
date_last_update_world_aggregate = None
date_last_update_italy = None
date_last_update_regional = None
date_last_update_vaccines_italy = None
last_check_for_update = None


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
        scatter = go.Scatter(x=x_axis_data, y=[], mode='lines', opacity=0.7, textposition='bottom center')
        scatter_list.append(scatter)
    else:
        for y_data_name, label in y_axis_data_mapping:
            scatter = go.Scatter(x=x_axis_data,
                                 y=data_frame[y_data_name],
                                 mode='lines',
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
                             mode='lines',
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
                             mode='lines',
                             opacity=0.7,
                             name=country,
                             # line=dict(shape="spline", smoothing=1, width=1),
                             textposition='bottom center')
        scatter_list.append(scatter)
    figure = create_figure(scatter_list, title)
    return figure


@app.callback(Output('dropdown_region_list_selected', 'value'), [Input('dropdown_italy_data_selected', 'value')])
def initialize_dropdown_region_data_selected(data_selected):
    df = df_regional_data.tail(21)
    df = df.sort_values(by=[data_selected]).tail(3)
    return df['denominazione_regione'].tolist()


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
    log.info('Updating Italy Line chart')
    return figure


@app.callback(Output('dropdown_country_list_selected', 'value'), [Input('dropdown_country_data_selected', 'value')])
def initialize_dropdown_country_data_selected(data_selected):
    df_country_world_data.sort_values(by=[constants.DATE_PROPERTY_NAME_EN], inplace=True)
    df = df_country_world_data.tail(constants.NUMBER_OF_WORLD_COUNTRIES)
    df = df.sort_values(by=[data_selected]).tail(3)
    return df['Country'].tolist()


# Callback for timeseries/country
@app.callback(Output('country_world_linear_chart', 'figure'), [Input('dropdown_country_list_selected', 'value'),
                                                               Input('dropdown_country_data_selected', 'value')])
def update_country_world_line_chart(country_list, data_selected):
    countries_list_mapping = []
    # if no country was selected, create empty figure
    x_axis_data = df_country_world_data[df_country_world_data['Country'] == "Italy"][constants.DATE_PROPERTY_NAME_EN]
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


@app.callback(Output('italy_map', 'figure'), [Input('dropdown_italy_data_selected', 'value')])
def update_italy_map(data_selected):
    df = df_rate_regional.tail(21)
    df['population'] = pd.to_numeric(df['population'], downcast='float')
    df['population'] = df['population'].apply(format_value_string_to_locale)
    date_string = df_national_data.iloc[-1]['data'].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=constants.URL_GEOJSON_REGIONS, locations='codice_regione',
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
    log.info('Updating Italy Choropleth Map')
    return figure


@app.callback(Output('world_map', 'figure'), [Input('dropdown_country_data_selected', 'value')])
def update_world_map(data_selected):
    df = df_rate_country_world.copy()
    df = df[~df['Country'].isin(constants.LIST_OF_NOT_LOCATED_COUNTRIES_ON_MAP)]
    df['Population'] = pd.to_numeric(df['Population'], downcast='float')
    df['Population'] = df['Population'].apply(format_value_string_to_locale)
    df.sort_values(by=['Country'], inplace=True)
    date_string = df.iloc[-1][constants.DATE_PROPERTY_NAME_EN].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=constants.URL_GEOJSON_WORLD_COUNTRIES, locations='Country',
                                  featureidkey="properties.ADMIN",
                                  color=data_selected,
                                  color_continuous_scale='Blues',
                                  hover_name='Country',
                                  hover_data=['Population'],
                                  range_color=(df[data_selected].min(), df[data_selected].max()),
                                  mapbox_style="carto-positron",
                                  zoom=0.95, center={"lat": 27.0902, "lon": 2.7129},
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
            text=f"*{load_resource(data_selected)} <br>"
            f"{load_resource('label_hover_world_map')} <br>"
            f"{date_string}",
            showarrow=False
        )]
    )
    log.info('Updating World Choropleth Map')
    return figure


@app.callback(Output('linear_chart_italy', 'figure'), [Input('dropdown_italy_data_selected', 'value')])
def update_italian_line_chart(data_selected):
    layout_italian_active_cases = copy.deepcopy(layout)
    df = df_national_data
    colors = ["rgb(204, 51, 0)", "rgb(4, 74, 152)", "rgb(123, 199, 255)"]
    x_list = df[constants.DATE_PROPERTY_NAME_IT]
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
def update_world_line_chart(data_selected):
    layout_world_linear_chart = copy.deepcopy(layout)
    df = df_worldwide_aggregate_data
    y_list_1 = df[data_selected].values.tolist()
    x_list = df[constants.DATE_PROPERTY_NAME_EN]
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


@app.callback([Output('total_cases_text', 'children'),
               Output('total_positive_text', 'children'),
               Output('total_recovered_text', 'children'),
               Output('total_deaths_text', 'children'),
               Output('total_icu_text', 'children'),
               Output('pressure_ICU_text', 'children'),
               Output('total_swabs_text', 'children'),
               Output('ratio_n_pos_tamponi_text', 'children'),
               Output('total_cases_variation', 'children'),
               Output('total_positive_variation', 'children'),
               Output('total_recovered_variation', 'children'),
               Output('total_deaths_variation', 'children'),
               Output('total_icu_variation', 'children'),
               Output('pressure_ICU_variation', 'children'),
               Output('total_swabs_variation', 'children'),
               Output('ratio_n_pos_tamponi_variation', 'children'),
               Output('sub_header_italian_update', 'children')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_text(self):
    log.info('Updating cards')
    sub_header_italian_text = load_resource('header_last_update_italy') + \
                              get_last_df_data_update(df_national_data, constants.DATE_PROPERTY_NAME_IT)
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'terapia_intensiva', 'pressure_ICU', 'tamponi', 'ratio_n_pos_tamponi']
    percentage_list = ['ratio_n_pos_tamponi', 'pressure_ICU']
    total_text_values = []
    variation_text_values = []
    for field in field_list:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day = df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        percentage = ' %' if field in percentage_list else ''
        total_text = f'{card_value:n}{percentage}'
        total_text_values.append(total_text)
        sign = '+' if variation_previous_day > 0 else ''
        variation_text = f'{sign}{variation_previous_day:n}{percentage}'
        variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values), sub_header_italian_text


@app.callback([Output('total_cases_variation', 'style'),
               Output('total_positive_variation', 'style'),
               Output('total_recovered_variation', 'style'),
               Output('total_deaths_variation', 'style'),
               Output('total_icu_variation', 'style'),
               Output('pressure_ICU_variation', 'style'),
               Output('total_swabs_variation', 'style'),
               Output('ratio_n_pos_tamponi_variation', 'style')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_color(self):
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'terapia_intensiva', 'pressure_ICU', 'tamponi', 'ratio_n_pos_tamponi']
    green_positive_results = ['tamponi', 'dimessi_guariti']
    green_negative_results = ['terapia_intensiva', 'totale_positivi', 'ratio_n_pos_tamponi', 'pressure_ICU']
    color_cards_list = []
    for field in field_list:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day = df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if field in green_positive_results and variation_previous_day > 0 or \
                field in green_negative_results and variation_previous_day < 0:
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
    log.info('Updating World Cards')
    sub_header_worldwide_text = load_resource('header_last_update_world') + \
                                get_last_df_data_update(df_worldwide_aggregate_data, constants.DATE_PROPERTY_NAME_EN)
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
    df = df.sort_values(by=[constants.DATE_PROPERTY_NAME_EN])
    df = df.tail(constants.NUMBER_OF_WORLD_COUNTRIES)
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


@app.callback(Output('table_tab_italy', 'figure'), [Input("dropdown_italy_data_selected", "value")])
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
    figure.update_layout(height=450, margin=dict(l=0, r=0, b=0, t=0))
    return figure


@app.callback([Output('total_cases_text_tab2', 'children'),
               Output('total_positive_text_tab2', 'children'),
               Output('total_recovered_text_tab2', 'children'),
               Output('total_deaths_text_tab2', 'children'),
               Output('total_icu_text_tab2', 'children'),
               Output('pressure_ICU_text_tab2', 'children'),
               Output('total_isolation_text_tab2', 'children'),
               Output('total_swabs_text_tab2', 'children'),
               Output('total_cases_variation_tab2', 'children'),
               Output('total_positive_variation_tab2', 'children'),
               Output('total_recovered_variation_tab2', 'children'),
               Output('total_deaths_variation_tab2', 'children'),
               Output('total_icu_variation_tab2', 'children'),
               Output('pressure_ICU_variation_tab2', 'children'),
               Output('total_isolation_variation_tab2', 'children'),
               Output('total_swabs_variation_tab2', 'children'),
               Output('sub_header_ita_regions_update', 'children'),
               ], [Input("dropdown_region_selected", "value")])
def update_regional_cards_text(region_selected):
    log.info('Updating regional cards')
    sub_header_ita_regions_text = load_resource('header_last_update_italy') + \
                                  get_last_df_data_update(df_regional_data, constants.DATE_PROPERTY_NAME_IT)
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'terapia_intensiva', 'pressure_ICU', 'isolamento_domiciliare', 'tamponi']
    total_text_values = []
    variation_text_values = []
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    for field in field_list:
        card_value = df[field].iloc[-1]
        card_value_previous_day = df[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        percentage = ' %' if field == 'pressure_ICU' else ''
        total_text = f'{card_value:n}{percentage}'
        total_text_values.append(total_text)
        sign = '+' if variation_previous_day > 0 else ''
        variation_text = f'{sign}{variation_previous_day:n}{percentage}'
        variation_text_values.append(variation_text)
    return (*total_text_values), (*variation_text_values), sub_header_ita_regions_text


@app.callback([Output('total_cases_variation_tab2', 'style'),
               Output('total_positive_variation_tab2', 'style'),
               Output('total_recovered_variation_tab2', 'style'),
               Output('total_deaths_variation_tab2', 'style'),
               Output('total_icu_variation_tab2', 'style'),
               Output('pressure_ICU_variation_tab2', 'style'),
               Output('total_isolation_variation_tab2', 'style'),
               Output('total_swabs_variation_tab2', 'style')
               ], [Input("dropdown_region_selected", "value")])
def update_regional_cards_color(region_selected):
    field_list = ['totale_casi', 'totale_positivi', 'dimessi_guariti', 'deceduti',
                  'terapia_intensiva', 'pressure_ICU', 'isolamento_domiciliare', 'tamponi']
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
                variation_previous_day > 0 and field == 'tamponi' or \
                variation_previous_day < 0 and field == 'pressure_ICU':
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
    log.info('Updating Country cards')
    field_list = ['Confirmed', 'Active_cases', 'Recovered', 'Deaths']
    total_text_values = []
    variation_text_values = []
    df_sub = df_country_world_data[df_country_world_data['Country'] == country_selected]
    df = df_sub.copy()
    df_sorted = df.sort_values(by=[constants.DATE_PROPERTY_NAME_EN])
    df_sorted = df_sorted.tail(
        constants.NUMBER_OF_WORLD_COUNTRIES + len(constants.LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA))
    for field in field_list:
        if country_selected in constants.LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
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
        if country_selected in constants.LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
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


@app.callback([Output('administered_doses_text', 'children'),
               Output('delivered_doses_text', 'children'),
               Output('total_people_vaccinated_text', 'children'),
               Output('percentage_vaccinated_population_text', 'children'),
               Output('sub_header_vaccines_italy_update', 'children'),
               Output('herd_immunity_date', 'children'),
               ], [Input("i_news", "n_intervals")])
def update_vaccines_italy_cards_text(self):
    log.info('Updating cards')
    herd_immunity_date = load_resource('string_italy_herd_immunity') + calculate_date_of_herd_immunity()
    sub_header_vaccines_italy_text = load_resource('header_last_update_vaccines_italy') + \
                                     get_last_df_data_update(df_vaccines_italy_summary_latest,
                                                             constants.DATE_PROPERTY_NAME_VACCINES_ITA_LAST_UPDATE)
    field_list = ['dosi_somministrate', 'dosi_consegnate', 'seconda_dose']
    df_custom = pd.concat([df_vaccines_italy_summary_latest[field_list[0]],
                           df_vaccines_italy_summary_latest[field_list[1]],
                           df_vaccines_italy_registry_summary_latest[field_list[2]]], axis=1,
                          keys=[field_list[0], field_list[1], field_list[2]])
    df_custom = df_custom.fillna(0)
    total_text_values = []
    for field in field_list:
        card_value = int(df_custom[field].sum())
        total_text = f'{card_value:n}'
        total_text_values.append(total_text)
    card_value = round((float(df_custom['seconda_dose'].sum()) / constants.VACCINABLE_ITALIAN_POPULATION) * 100, 2)
    percentage = ' %'
    total_text = f'{card_value:n}{percentage}'
    total_text_values.append(total_text)

    return (*total_text_values), sub_header_vaccines_italy_text, herd_immunity_date


@app.callback(Output('bar_chart_administrations_daily_total', 'figure'), [Input("i_news", "n_intervals")])
def update_bar_chart_administrations_italy_daily_total(self):
    layout_administrations_by_day = copy.deepcopy(layout)
    df_by_day = df_vaccines_italy_daily_summary_latest_grouped_by_ITA
    # by convention, we exclude the data of last day, which could be partial
    # we use head funct 'cause is  about 6 times fasting than drop func
    df_by_day = df_by_day.head(-1)
    colors = ["rgb(123, 199, 255)", "rgb(244, 0, 161)"]
    data = [
        dict(
            type="bar",
            x=df_by_day["data_somministrazione"],
            y=df_by_day["totale"],
            name=load_resource('daily_administrations'),
            marker=dict(color=colors[0]),
            yaxis='y1'
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            x=df_by_day["data_somministrazione"],
            y=df_by_day["mov_avg"],
            name=load_resource('rolling_average_7_days'),
            marker=dict(color=colors[1]),
            yaxis='y2'
        )
    ]

    layout_administrations_by_day["title"] = load_resource('daily_administrations')
    layout_administrations_by_day["showlegend"] = True
    layout_administrations_by_day["autosize"] = True
    layout_administrations_by_day["yaxis"] = dict(color=colors[0])
    layout_administrations_by_day["yaxis2"] = dict(overlaying='y',
                                                   side='right',
                                                   showgrid=False,
                                                   showline=False,
                                                   zeroline=False,
                                                   showticklabels=False,
                                                   color=colors[1]
                                                   )

    figure = dict(data=data, layout=layout_administrations_by_day)
    return figure


@app.callback(Output('bar_chart_administrations_by_age', 'figure'),
              [Input("radio_buttons_italian_vaccines_data", "value")])
def update_bar_chart_vaccines_italy_administrations_by_age(data_selected):
    layout_administrations_by_age = copy.deepcopy(layout)
    df = df_vaccines_italy_registry_summary_latest

    colors = dict(light_blue="rgb(123, 199, 255)",
                  dark_blue="rgb(4, 74, 152)",
                  pink="rgb(244, 0, 161)",
                  aqua="rgb(0, 204, 153)",
                  azure="rgb(51, 133, 255)")

    bar_total = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["totale"],
                                         name=load_resource('administrations_by_age'), color=colors.get("light_blue"))
    bar_men = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["sesso_maschile"],
                                       name=load_resource('sex_male'), color=colors.get("dark_blue"))
    bar_women = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["sesso_femminile"],
                                         name=load_resource('sex_female'), color=colors.get("pink"))
    bar_first_dose = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["prima_dose"],
                                              name=load_resource('first_vaccine_dose'), color=colors.get("light_blue"))
    bar_second_dose = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["seconda_dose"],
                                               name=load_resource('second_vaccine_dose'), color=colors.get("dark_blue"))
    bar_previous_infection_vaccine_dose = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["pregressa_infezione"],
                                                   name=load_resource('previous_infection_vaccine_dose'),
                                                   color=colors.get("pink"))
    bar_additional_dose = create_data_dict_for_bar(data_x=df["fascia_anagrafica"], data_y=df["dose_addizionale_booster"],
                                               name=load_resource('additional_vaccine_dose'), color=colors.get("aqua"))

    layout_administrations_by_age["title"] = load_resource('administrations_by_age')
    layout_administrations_by_age["showlegend"] = True
    layout_administrations_by_age["autosize"] = True
    layout_administrations_by_age["xaxis"] = dict(type='category')

    if data_selected == 'totale':
        data = [bar_total]
    elif data_selected == 'sex_group':
        data = [bar_men, bar_women]
    elif data_selected == 'first_second_doses_group':
        data = [bar_first_dose, bar_second_dose]
    elif data_selected == 'additional_doses_group':
        data = [bar_previous_infection_vaccine_dose, bar_additional_dose]

    figure = dict(data=data, layout=layout_administrations_by_age)
    return figure


def create_data_dict_for_bar(data_x=None, data_y=None, color=None, name=""):
    return dict(
        type="bar",  # 11
        x=data_x,
        y=data_y,
        name=name,
        marker=dict(color=color),
    )


@app.callback(Output('bar_chart_daily_administrations', 'figure'), [Input("i_news", "n_intervals")])
def update_bar_chart_vaccines_italy_daily_administrations(self):
    layout_administrations_by_day = copy.deepcopy(layout)
    df_by_day_ITA = df_vaccines_italy_admin_summary_latest_grouped_by_ITA
    colors = ["rgb(123, 199, 255)", "rgb(4, 74, 152)"]
    data = [
        dict(
            type="bar",
            x=df_by_day_ITA["data_somministrazione"],
            y=df_by_day_ITA["totale"],
            name=load_resource('administrations_by_day'),
            marker=dict(color=colors[0]),
            yaxis='y1'
        ),
        dict(
            type="scatter",
            mode="markers",
            x=df_by_day_ITA["data_somministrazione"],
            y=df_by_day_ITA["total_on_today"],
            name=load_resource('total_administrations'),
            marker=dict(color=colors[1]),
            yaxis='y2'
        )
    ]

    layout_administrations_by_day["title"] = load_resource('administrations_by_day')
    layout_administrations_by_day["showlegend"] = True
    layout_administrations_by_day["autosize"] = True
    layout_administrations_by_day["yaxis"] = dict(color=colors[0])
    layout_administrations_by_day["yaxis2"] = dict(overlaying='y',
                                                   side='right',
                                                   showgrid=False,
                                                   showline=False,
                                                   zeroline=False,
                                                   color=colors[1]
                                                   )

    figure = dict(data=data, layout=layout_administrations_by_day)
    return figure


@app.callback(Output('table_italy_vaccines', 'figure'), [Input("i_news", "n_intervals")])
def update_data_table_italy_vaccines(self):
    df = df_vaccines_italy_summary_latest.copy()
    df['dosi_consegnate'] = df['dosi_consegnate'].apply(format_value_string_to_locale)
    df['dosi_somministrate'] = df['dosi_somministrate'].apply(format_value_string_to_locale)
    df = df.sort_values(by=['percentuale_somministrazione'], ascending=False)
    df['percentuale_somministrazione'] = df['percentuale_somministrazione'].astype(str) + '%'
    df['percentuale_somministrazione'] = [x.replace('.', ',') for x in df['percentuale_somministrazione']]
    figure = go.Figure(data=[go.Table(
        header=dict(values=(load_resource('denominazione_regione'), load_resource('percentage_administrations'),
                            load_resource('delivered_doses'), load_resource('administered_doses')
                            ),
                    fill_color='lightskyblue',
                    font_color='white',
                    font_size=15,
                    align='center'),
        cells=dict(values=[df['nome_area'], df['percentuale_somministrazione'], df['dosi_consegnate'],
                           df['dosi_somministrate']
                           ],
                   fill_color='whitesmoke',
                   align='center',
                   font_size=13,
                   height=20))
    ])
    figure.update_layout(height=450, margin=dict(l=0, r=0, b=0, t=0))
    return figure


@app.callback(Output('mainContainer', 'children'),
              [Input('dropdown_language_selected', 'value')])
def update_language(language):
    if language == locale_language.language:
        # Check required otherwise during startup the page is loaded twice
        log.info("Preventing language update since no language changes was detected")
        raise PreventUpdate
    locale_language.language = language
    log.info(f"User switching language to: {language}")
    return create_page_components(app, df_regional_data, df_country_world_data)


@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news(self):
    log.info('Updating news')
    return create_news()


@app.callback(Output("last_check_update_text", "children"), [Input("i_news", "n_intervals")])
def update_last_data_check(self):
    log.info('Updating last data check')
    string_last_data_check = load_resource('label_last_check_update') + last_check_for_update + ' CET'
    return string_last_data_check


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
    df_sb = df_sb.sort_values(by=[constants.DATE_PROPERTY_NAME_EN])
    df_sb = df_sb.tail(constants.NUMBER_OF_WORLD_COUNTRIES + len(constants.LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA))
    df_sb.sort_values(by=['Country'], inplace=True)
    df_sb['Population'] = ''
    for index, row in df_sb.iterrows():
        nation_name = row["Country"]
        if nation_name not in world_population:
            continue
        population = int(world_population[nation_name])
        df_sb.at[index, 'Population'] = population
        for field in constants.LIST_OF_WORLD_FIELDS_TO_RATE:
            value = row[field]
            pressure_value = (value / population) * constants.INHABITANT_RATE
            df_sb.at[index, field] = round(pressure_value, 2)
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
            pressure_value = (float(value) / float(population)) * constants.INHABITANT_RATE
            df_sb.at[i, field] = round(pressure_value, 2)
    return df_sb


def load_region_available_ICU(df_sb):
    df_sb['available_ICU'] = ''
    for index, row in df_sb.iterrows():
        region_name = row["denominazione_regione"]
        if region_name not in italy_ICU:
            continue
        available_ICU = int(italy_ICU[region_name])
        df_sb.at[index, 'available_ICU'] = available_ICU
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
    last_date_df = df.iloc[-1][constants.DATE_PROPERTY_NAME_EN]
    list_of_row = []
    for country_without_data in constants.LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA:
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


def get_content_date_last_download_data(url):
    resp = requests.head(url)
    if resp.status_code != 200:
        log.error(f"Request failed trying to contact URL: {url}")
        last_update = 'Time not available'
    else:
        date_update_string = resp.headers["Date"]
        last_update = parsedate_to_datetime(date_update_string).astimezone(tz=pytz.timezone('Europe/Rome'))
    string_date_update = last_update.strftime(" %d/%m/%Y %H:%M:%S")
    return string_date_update


def get_last_data_check():
    last_check_update = datetime.datetime.now(pytz.timezone('Europe/Rome')).strftime(" %d/%m/%Y %H:%M:%S")
    return last_check_update


def get_last_df_data_update(df, date_property_name):
    string_date_update = (df[date_property_name].iloc[-1]).strftime(" %d/%m/%Y")
    return string_date_update


def add_variation_new_swabs_column_df_italy(df):
    df['nuovi_tamponi'] = 0
    previous_row = ""
    for index, row in df.iterrows():
        if index == 0:
            previous_row = row
        else:
            variation_value = row['tamponi'] - previous_row['tamponi']
            df.at[index, "nuovi_tamponi"] = variation_value
            previous_row = row
    return df


def add_variation_columns_for_world_aggregate_data(df):
    df['New Confirmed'], df['New Recovered'], df['New Deaths'] = [0, 0, 0]
    for index, row in df.iterrows():
        for col in df.columns:
            if col in ('Confirmed', 'Recovered', 'Deaths') and (index != 0):
                df.at[index, f"New {col}"] = row[col] - df.loc[index - 1, f"{col}"]
    return df


def add_variation_columns_for_world_countries(df):
    df['New Confirmed'], df['New Recovered'], df['New Deaths'] = [0.0, 0.0, 0.0]
    country = ""
    previous_row = ""
    for index, row in df.iterrows():
        if (index == 0) or country != row['Country']:
            country = row['Country']
            previous_row = row
        else:
            for col in df.columns:
                if col in ('Confirmed', 'Recovered', 'Deaths'):
                    variation_value = row[col] - previous_row[col]
                    df.at[index, f"New {col}"] = variation_value
            previous_row = row
    return df


def add_total_on_day_administrations_vaccines_italy(df):
    df['total_on_today'] = 0
    df = df.groupby('data_somministrazione').sum()
    df.reset_index(inplace=True)
    df['total_on_today'] = df['totale'].cumsum()
    return df


def add_daily_administrations_italy(df):
    df['administrated_people'] = 0
    df = df.groupby('data_somministrazione').sum()
    df.reset_index(inplace=True)
    df['administrated_people'] = df['seconda_dose'].cumsum() + df['pregressa_infezione'].cumsum()
    previous_row = ""
    for index, row in df.iterrows():
        if index == 0:
            previous_row = row
        else:
            variation_value = row['administrated_people'] - previous_row['administrated_people']
            df.at[index, "totale"] = variation_value
            previous_row = row
    # df.drop(df[df.seconda_dose == 0].index, inplace=True)
    df['mov_avg'] = round(df.totale.rolling(window=7, min_periods=1).mean(), 0)
    return df


def calculate_date_of_herd_immunity():
    df = df_vaccines_italy_daily_summary_latest_grouped_by_ITA
    df = df.head(-1)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    first_useful_date = df['data_somministrazione'].iloc[-1]
    last_update_administrated_people = df['administrated_people'].iloc[-1]
    last_update_rolling_avg = df['mov_avg'].iloc[-1]
    remaining_administrations = round(((constants.VACCINABLE_ITALIAN_POPULATION * 90) / 100), 0)
    days_to_herd_immunity = round((remaining_administrations - last_update_administrated_people) /
                                  last_update_rolling_avg, 0)
    date_herd_immunity = (first_useful_date + timedelta(days=days_to_herd_immunity)).strftime('%d/%m/%Y')
    return date_herd_immunity


def add_percentage_vaccination_italy_phases(df):
    df['percentage_vaccinated_population'] = 0
    df = df.groupby('data_somministrazione').sum()
    df.reset_index(inplace=True)
    df['percentage_vaccinated_population'] = round(((df['seconda_dose'] + df['pregressa_infezione'])
                                                   / constants.VACCINABLE_ITALIAN_POPULATION) * 100, 2)
    df['percentage_vaccinated_population'] = df['percentage_vaccinated_population'].cumsum()
    return df


def load_data_from_web():
    log.info('Start scheduled task to check data updates')

    load_worldwide_aggregate_data()
    load_country_world_data()
    load_national_data()
    load_regional_data()
    load_vaccines_italy_data()

    global last_check_for_update
    last_check_for_update = get_last_data_check()
    log.info(f'Update task completed at: {last_check_for_update}')


def load_regional_data():
    global df_regional_data, df_rate_regional, date_last_update_regional, last_update_content_regional_data
    # Check if updates for Regional data is required
    current_update_content_regional_data = int(get_content_length(constants.URL_CSV_REGIONAL_DATA))
    if current_update_content_regional_data == -1:
        log.info("Provider's server for Regional Data is unresponsive, retrying later")
    elif current_update_content_regional_data != last_update_content_regional_data or df_rate_regional is None:
        log.info('Regional data update required')
        df_regional_data = load_csv(constants.URL_CSV_REGIONAL_DATA, constants.DATE_PROPERTY_NAME_IT)
        df_regional_data = load_region_available_ICU(df_regional_data)
        df_regional_data['available_ICU'] = pd.to_numeric(df_regional_data['available_ICU'], downcast='float')
        df_regional_data['pressure_ICU'] = round(((df_regional_data['terapia_intensiva'] /
                                                   df_regional_data['available_ICU']) * 100), 2)
        df_rate_regional = load_region_rate_data_frame(df_regional_data)
        date_last_update_regional = get_content_date_last_download_data(constants.URL_CSV_REGIONAL_DATA)
        log.info(f"Old Content-length: {last_update_content_regional_data} bytes")
        log.info(f"New Content-length: {current_update_content_regional_data} bytes")
        last_update_content_regional_data = current_update_content_regional_data
    else:
        log.info('No updates required for Regional data')


def load_national_data():
    global df_national_data, date_last_update_italy, last_update_content_national_data
    # Check if updates for National data is required
    current_update_content_national_data = int(get_content_length(constants.URL_CSV_ITALY_DATA))
    if current_update_content_national_data == -1:
        log.info("Provider's server for National data is unresponsive, retrying later")
    elif current_update_content_national_data != last_update_content_national_data:
        log.info('National data update required')
        df_national_data = load_csv(constants.URL_CSV_ITALY_DATA, constants.DATE_PROPERTY_NAME_IT)
        df_national_data = add_variation_new_swabs_column_df_italy(df_national_data)
        df_national_data['ratio_n_pos_tamponi'] = round(((df_national_data['nuovi_positivi'] /
                                                          df_national_data['nuovi_tamponi']) * 100), 2)
        df_national_data['pressure_ICU'] = round(((df_national_data['terapia_intensiva'] /
                                                   constants.TOTAL_ICU_ITALY) * 100), 2)
        date_last_update_italy = get_content_date_last_download_data(constants.URL_CSV_ITALY_DATA)
        log.info(f"Old Content-length: {last_update_content_national_data} bytes")
        log.info(f"New Content-length: {current_update_content_national_data} bytes")
        last_update_content_national_data = current_update_content_national_data
    else:
        log.info('No updates required for National data')


def load_country_world_data():
    global df_country_world_data, df_rate_country_world, last_update_content_country_world_data
    # Check if updates for World data is required
    current_update_content_country_world_data = int(get_content_length(constants.URL_CSV_WORLD_COUNTRIES_DATA))
    if current_update_content_country_world_data == -1:
        log.info("Provider's server for Country World data is unresponsive, retrying later")
    elif current_update_content_country_world_data != last_update_content_country_world_data:
        log.info('Country World data update required')
        df_country_world_data = load_csv(constants.URL_CSV_WORLD_COUNTRIES_DATA, constants.DATE_PROPERTY_NAME_EN)
        df_country_world_data['Active_cases'] = df_country_world_data['Confirmed'] - \
                                                (df_country_world_data['Recovered'] + df_country_world_data['Deaths'])
        df_country_world_data = adjust_df_world_to_geojson(df_country_world_data)
        df_country_world_data = add_excluded_country_world(df_country_world_data)
        df_country_world_data = add_variation_columns_for_world_countries(df_country_world_data)
        df_rate_country_world = load_country_world_rate_data_frame(df_country_world_data)
        date_last_update_world_countries_data = get_content_date_last_download_data(
            constants.URL_CSV_WORLD_COUNTRIES_DATA)
        log.info(f"Old Content-length: {last_update_content_country_world_data} bytes")
        log.info(f"New Content-length: {current_update_content_country_world_data} bytes")
        last_update_content_country_world_data = current_update_content_country_world_data
    else:
        log.info('No updates required for Country World data')


def load_worldwide_aggregate_data():
    global df_worldwide_aggregate_data, date_last_update_world_aggregate, last_update_content_worldwide_aggregate_data
    # Check if updates for Worldwide Aggregate data is required
    current_update_content_worldwide_aggregate_data = int(
        get_content_length(constants.URL_CSV_WORLDWIDE_AGGREGATE_DATA))
    if current_update_content_worldwide_aggregate_data == -1:
        log.info("Provider's server for Worldwide Aggregate data is unresponsive, retrying later")
    elif current_update_content_worldwide_aggregate_data != last_update_content_worldwide_aggregate_data:
        log.info('Worldwide Aggregate data update required')
        df_worldwide_aggregate_data = load_csv(constants.URL_CSV_WORLDWIDE_AGGREGATE_DATA,
                                               constants.DATE_PROPERTY_NAME_EN)
        df_worldwide_aggregate_data['Active_cases'] = df_worldwide_aggregate_data['Confirmed'] - \
                                                      (df_worldwide_aggregate_data['Recovered'] +
                                                       df_worldwide_aggregate_data['Deaths'])
        df_worldwide_aggregate_data = add_variation_columns_for_world_aggregate_data(df_worldwide_aggregate_data)
        date_last_update_world_aggregate = get_content_date_last_download_data(
            constants.URL_CSV_WORLDWIDE_AGGREGATE_DATA)
        log.info(f"Old Content-length: {last_update_content_worldwide_aggregate_data} bytes")
        log.info(f"New Content-length: {current_update_content_worldwide_aggregate_data} bytes")
        last_update_content_worldwide_aggregate_data = current_update_content_worldwide_aggregate_data
    else:
        log.info('No updates required for Worldwide Aggregate data')


def load_vaccines_italy_data():
    global df_vaccines_italy_summary_latest, date_last_update_vaccines_italy, last_update_content_vaccines_italy_data, \
        df_vaccines_italy_registry_summary_latest, df_vaccines_italy_admin_summary_latest, \
        df_vaccines_italy_administration_point, df_vaccines_italy_admin_summary_latest_grouped_by_ITA, \
        df_vaccines_italy_daily_summary_latest_grouped_by_ITA
    # Check if updates for National data is required
    current_update_content_vaccines_italy_data = int(get_content_length(constants.URL_VACCINES_ITA_SUMMARY_LATEST))
    if current_update_content_vaccines_italy_data == -1:
        log.info("Provider's server for Italian Vaccines data is unresponsive, retrying later")
    elif current_update_content_vaccines_italy_data != last_update_content_vaccines_italy_data:
        log.info('Italian Vaccines data update required')
        df_vaccines_italy_summary_latest = load_csv(constants.URL_VACCINES_ITA_SUMMARY_LATEST,
                                                    constants.DATE_PROPERTY_NAME_VACCINES_ITA_LAST_UPDATE)
        df_vaccines_italy_registry_summary_latest = load_csv(constants.URL_VACCINES_ITA_REGISTRY_SUMMARY_LATEST,
                                                             constants.DATE_PROPERTY_NAME_VACCINES_ITA_LAST_UPDATE)
        df_vaccines_italy_admin_summary_latest = \
            load_csv(constants.URL_VACCINES_ITA_ADMINISTRATIONS_SUMMARY_LATEST, "data_somministrazione")
        df_vaccines_italy_admin_summary_latest_grouped_by_ITA = \
            add_total_on_day_administrations_vaccines_italy(df_vaccines_italy_admin_summary_latest)
        df_vaccines_italy_daily_summary_latest_grouped_by_ITA = \
            add_daily_administrations_italy(df_vaccines_italy_admin_summary_latest)
        df_vaccines_italy_administration_point = load_csv(constants.URL_VACCINES_ITA_ADMINISTRATION_POINT)
        date_last_update_vaccines_italy = get_content_date_last_download_data(constants.URL_VACCINES_ITA_SUMMARY_LATEST)
        log.info(f"Old Content-length: {last_update_content_vaccines_italy_data} bytes")
        log.info(f"New Content-length: {current_update_content_vaccines_italy_data} bytes")
        last_update_content_vaccines_italy_data = current_update_content_vaccines_italy_data
    else:
        log.info('No updates required for Italian Vaccines data')


def app_layout():
    app.layout = html.Div(
        children=create_page_components(app, df_regional_data, df_country_world_data),
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )


schedule.every(30).minutes.do(load_data_from_web)
schedule.every().day.at("08:15").do(load_data_from_web)
schedule.every().day.at("18:05").do(load_data_from_web)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(10)


def initialize_thread():
    log.info('Starting schedule thread')
    schedule_thread = Thread(name="scheduled2-thread", target=run_schedule)
    schedule_thread.start()


initialize_thread()
load_data_from_web()
app.config.suppress_callback_exceptions = True
# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("regional_timeseries_linear", "figure")],
)
app.title = "SARS-CoV-2-Gellex"
app_layout()


def get_boot_time():
    return time.time() - app_start_time


def show_application_started_messages():
    log.info("----------------------------------------------------------------------")
    log.info(f"| *** Server started in {round(get_boot_time(), 2)} seconds \t\t\t\t\t\t\t *** |")
    log.info("| *** Running on http://127.0.0.1:5000/ - Enjoy the application! *** |")
    log.info("----------------------------------------------------------------------")


if __name__ == '__main__':
    show_application_started_messages()
    time.sleep(0.01)  # Sleep for few milliseconds otherwise log messages get messed up with the app running
    app.server.run(debug=False)  # debug=True active a button in the bottom right corner of the web page
