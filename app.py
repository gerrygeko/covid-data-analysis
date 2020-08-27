import base64
import copy
import csv
import json as js
import locale
import time
from threading import Thread
from urllib.request import urlopen

import dash
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import schedule
from dash.dependencies import Input, Output, ClientsideFunction
from dash.exceptions import PreventUpdate

import logger
from constants import RESOURCES, load_resource
from html_components import create_news, create_page_components, locale_language

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

field_list_to_rate = ['ricoverati_con_sintomi', 'terapia_intensiva',
                      'totale_ospedalizzati', 'isolamento_domiciliare',
                      'totale_positivi', 'nuovi_positivi', 'dimessi_guariti',
                      'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'totale_casi',
                      'tamponi', 'casi_testati']


def load_csv_from_file(path):
    reader = csv.reader(open(path, 'r'))
    d = {}
    for row in reader:
        k, v = row
        d[k] = v
    return d


def load_csv(url):
    data_loaded = pd.read_csv(url, parse_dates=['data'])
    return data_loaded


def load_geojson(url):
    with urlopen(url) as response:
        json = js.load(response)
    return json


region_population = load_csv_from_file('assets/region_population.csv')
geojson_province = load_geojson(url_geojson_regions)
last_update_content_regional_data = 0
last_update_content_national_data = 0
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
    layout_figure['hovermode'] = 'x unified'
    figure = dict(data=data, layout=layout_figure)
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                                               Input('dropdown_data_selected', 'value')])
def update_graph(region_list, data_selected):
    regions_list_mapping = []
    # if no region selected, create empty figure
    x_axis_data = df_regional_data[df_regional_data['denominazione_regione'] == "Abruzzo"]['data']
    if len(region_list) == 0 or data_selected is None:
        figure = create_scatter_plot(df_regional_data, '', x_axis_data, [])
        return figure
    for region in region_list:
        regions_list_mapping.append((data_selected, region))
    figure = create_scatter_plot_by_region(df_regional_data, load_resource(data_selected),
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
        value = df_regional_data[df_regional_data['denominazione_regione'] == region][data_selected].tail(1)
        value_list.append(int(value))
    data = [go.Pie(labels=region_list,
                   values=value_list,
                   hoverinfo='text+value+percent',
                   sort=False,
                   textinfo='label+percent',
                   hole=0.5)]
    layout_pie['legend'] = dict(font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)")
    figure = dict(data=data, layout=layout_pie)
    log.info('Updating pie graph')
    return figure


@app.callback(Output('map_graph', 'figure'), [Input('dropdown_data_selected', 'value')])
def update_map_graph(data_selected):
    df = df_rate_regional.tail(21)
    df['population'] = pd.to_numeric(df['population'], downcast='float')
    df['population'] = df['population'].apply(format_value_string_to_locale)
    date_string = df_national_data.iloc[-1]['data'].strftime('%d/%m/%Y')
    figure = px.choropleth_mapbox(df, geojson=url_geojson_regions, locations='codice_regione',
                                  featureidkey="properties.reg_istat_code_num",
                                  color=data_selected,
                                  color_continuous_scale="Blues",
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
            text='*Incidenza di {} <br>per regione (ogni 100K abitanti)<br>al {}'.format(RESOURCES[data_selected],
                                                                                         date_string),
            showarrow=False
        )]
    )
    log.info('Updating map graph')
    return figure


@app.callback(Output('bar_graph', 'figure'), [Input('dropdown_data_selected', 'value')])
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
                   hovertemplate='<i><b>Regione</b></i>: %{y}'+
                                '<br><b>N.</b>: %{x}<br>'+
                                '<extra></extra>',
                   insidetextanchor="start",
                   orientation='h'
                   )
            ]
    layout_bar = copy.deepcopy(layout)
    layout_bar['title'] = '{}'.format(RESOURCES[data_selected])
    layout_bar['yaxis'] = dict(zeroline=False, showline=False, showgrid=False, showticklabels=False)
    figure = dict(data=data, layout=layout_bar)
    log.info('Updating bar graph in Tab 1')
    return figure


@app.callback(Output('bar_graph_tab2', 'figure'), [Input('dropdown_region_selected', 'value')])
def update_bar_graph_active_cases(region_selected):
    df = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
    # Since we filter based on the region, our indexes are not sequential anymore
    # so we reindex to access to specific row easier later
    df.reset_index(inplace=True)
    y_list_1 = df['terapia_intensiva'].values.tolist()
    y_list_2 = df['ricoverati_con_sintomi'].values.tolist()
    y_list_3 = df['isolamento_domiciliare'].values.tolist()
    x_list = df['data']
    figure = go.Figure(
        go.Bar(x=x_list, y=y_list_1, name=RESOURCES['terapia_intensiva'], textposition='auto',
               insidetextanchor="start"))
    figure.add_trace(go.Bar(x=x_list, y=y_list_2, name=RESOURCES['ricoverati_con_sintomi']))
    figure.add_trace(go.Bar(x=x_list, y=y_list_3, name=RESOURCES['isolamento_domiciliare']))
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
               Output('total_icu_text', 'children'),
               Output('total_swabs_text', 'children'),
               Output('total_positive_variation', 'children'),
               Output('total_cases_variation', 'children'),
               Output('total_recovered_variation', 'children'),
               Output('total_deaths_variation', 'children'),
               Output('total_icu_variation', 'children'),
               Output('total_swabs_variation', 'children'),
               Output('subHeader', 'children')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_text(n):
    log.info('update cards')
    sub_header_text = (df_national_data['data'].iloc[-1]).strftime(load_resource('header_last_update'))
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
    return (*total_text_values), (*variation_text_values), sub_header_text


@app.callback([Output('total_positive_variation', 'style'),
               Output('total_cases_variation', 'style'),
               Output('total_recovered_variation', 'style'),
               Output('total_deaths_variation', 'style'),
               Output('total_icu_variation', 'style'),
               Output('total_swabs_variation', 'style')
               ], [Input("i_news", "n_intervals")])
def update_national_cards_color(n):
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


@app.callback(Output('table_tab1', 'figure'), [Input("dropdown_data_selected", "value")])
def update_data_table(data_selected):
    df = df_regional_data.tail(21)
    df = df.sort_values(by=[data_selected], ascending=False)
    df[data_selected] = pd.to_numeric(df[data_selected], downcast='float')
    df[data_selected] = df[data_selected].apply(format_value_string_to_locale)
    figure = go.Figure(data=[go.Table(
        header=dict(values=(load_resource('denominazione_regione'), load_resource(data_selected)),
                    fill_color='lightskyblue',
                    font_color='white',
                    font_size=16,
                    align='left'),
        cells=dict(values=[df['denominazione_regione'], df[data_selected]],
                   fill_color='aliceblue',
                   align='left',
                   font_size=14,
                   height=27))
    ])
    figure.update_layout(height=400, margin=dict(l=0, r=0, b=0, t=0))
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


@app.callback(Output('mainContainer', 'children'),
           [Input('dropdown_language_selected', 'value')])
def update_language(language):
    if language == locale_language.language:
        # Check required otherwise during startup the page is loaded twice
        log.info("Preventing language update since no language changes was detected")
        raise PreventUpdate
    locale_language.language = language
    log.info(f"Drawing components with language {language}")
    return create_page_components(app, df_regional_data)


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
    df_sb.reindex(list(range(0,21)))
    for field in field_list_to_rate:
        trento_value = trento_row.get(field)
        bolzano_value = bolzano_row.get(field)
        trentino_row.at[field] = trento_value + bolzano_value
    df_sb.drop([trento_row.name, bolzano_row.name], inplace=True)
    trentino_row.at['codice_regione'] = 4
    trentino_row.at['denominazione_regione'] = 'Trentino-Alto Adige'
    df_sb = df_sb.append(trentino_row)
    return df_sb


def load_region_rate_data_frame(df):
    # We create a copy of the original DataFrame to avoid working on the original DataFrame and to suppress warning
    df_sb = df.copy()
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


def get_content_length(url):
    resp = requests.head(url)
    if resp.status_code != 200:
        log.error(f"Request failed trying to contact URL: {url}")
        return -1
    size = resp.headers["Content-Length"]
    return size


def load_interactive_data():
    log.info('Start scheduled task to check data updates')
    global df_regional_data, df_national_data, df_rate_regional, \
        last_update_content_regional_data, last_update_content_national_data
    current_update_content_regional_data = int(get_content_length(url_csv_regional_data))
    current_update_content_national_data = int(get_content_length(url_csv_italy_data))

    # Check if updates for National data is required
    if current_update_content_national_data == -1:
        log.info("Provider's server for National data is unresponsive, retrying later")
    elif current_update_content_national_data != last_update_content_national_data:
        log.info('National data update required')
        df_national_data = load_csv(url_csv_italy_data)
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
        df_regional_data = load_csv(url_csv_regional_data)
        df_rate_regional = load_region_rate_data_frame(df_regional_data)
        log.info(f"Old Content-length: {last_update_content_regional_data} bytes")
        log.info(f"New Content-length: {current_update_content_regional_data} bytes")
        last_update_content_regional_data = current_update_content_regional_data
    else:
        log.info('No updates required for Regional data')

    log.info('Update task completed')


def app_layout():
    app.layout = html.Div(
        children=create_page_components(app, df_regional_data),
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

if __name__ == '__main__':
    app.server.run(debug=False)  # debug=True active a button in the bottom right corner of the web page

