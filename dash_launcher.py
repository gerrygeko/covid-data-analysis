import copy
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go

from dash.dependencies import Input, Output
from constants import DATA_DICT

app = dash.Dash(__name__)
url_csv_regional_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
url_csv_italy_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"


def load_csv(url):
    data_loaded = pd.read_csv(url, index_col=[0], parse_dates=['data'])
    return data_loaded


df_regional_data = load_csv(url_csv_regional_data)
df_national_data = load_csv(url_csv_italy_data)

national_data_mapping = [('totale_casi', 'Total cases'),
                         ('totale_positivi', 'Currently positive'),
                         ('ricoverati_con_sintomi', 'Hospitalized patients'),
                         ('terapia_intensiva', 'ICU patients')]

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        # accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)


def get_options(list_value):
    dict_list = []
    for i in list_value:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def get_options_from_dict(data_dict):
    dict_list = []
    for data in data_dict:
        dict_list.append({'label': str(data_dict[data]), 'value': str(data)})

    return dict_list


def create_scatter_plot(data_frame, title, x_axis_data, y_axis_data_mapping, y_is_log=False):
    y_axis_type = "log" if y_is_log else "linear"
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

    figure = create_figure(scatter_list, title, y_axis_type)
    return figure


def create_scatter_plot_by_region(data_frame, title, x_axis_data, y_axis_data_mapping_region, y_is_log=False):
    y_axis_type = "log" if y_is_log else "linear"
    scatter_list = []
    for field, region in y_axis_data_mapping_region:
        scatter = go.Scatter(x=x_axis_data, y=data_frame[data_frame['denominazione_regione'] == region][field],
                             mode='lines+markers',
                             opacity=0.7,
                             name=region,
                             # line=dict(shape="spline", smoothing=1, width=1),
                             textposition='bottom center')
        scatter_list.append(scatter)
    figure = create_figure(scatter_list, title, y_axis_type)
    return figure


# TODO: re-implement logic for logarithm scale
def create_figure(data, title, y_axis_type):
    layout_figure = copy.deepcopy(layout)

    layout_figure['title'] = title
    figure = dict(data=data, layout=layout_figure)
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                                               Input('dropdown_data_selected', 'value'),
                                                               Input('dropdown_data_list_selected', 'value'),
                                                               Input('dropdown_region_selected', 'value'),
                                                               Input('tabs', 'value')])
def update_graph(region_list, data_selected, data_list, region_selected, tab_selected):
    if tab_selected == 'tab_region':
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
    elif tab_selected == 'tab_data':
        data_list_mapping = []
        # if no region selected, create empty figure
        if len(data_list) == 0 or region_selected is None:
            figure = create_scatter_plot(df_regional_data, '', df_regional_data.index, [])
            return figure
        df_sub = df_regional_data[df_regional_data['denominazione_regione'] == region_selected]
        for data in data_list:
            data_list_mapping.append((data, DATA_DICT[data]))
        x_axis_data = df_sub.index
        figure = create_scatter_plot(df_sub, region_selected, x_axis_data, data_list_mapping)
    return figure


@app.callback(Output('pie_graph', 'figure'), [Input('dropdown_region_list_selected', 'value'),
                                              Input('dropdown_data_selected', 'value')])
def update_pie_graph(region_list, data_selected):
    layout_pie = copy.deepcopy(layout)
    value_list = []
    if len(region_list) == 0 or data_selected is None:
        data = [go.Pie(labels=[],
                       values=value_list,
                       hoverinfo='text+value+percent',
                       textinfo='label+percent',
                       hole=0.5)]
        layout_pie['title'] = ""
        figure = dict(data=data, layout=layout_pie)
        return figure
    for region in region_list:
        value = df_regional_data[df_regional_data['denominazione_regione'] == region][data_selected][-1]
        value_list.append(value)
    data = [go.Pie(labels=[region for region in region_list],
                   values=value_list,
                   hoverinfo='text+value+percent',
                   textinfo='label+percent',
                   hole=0.5)]
    date = df_regional_data.index[-1].strftime('%d/%m/%Y')
    layout_pie['title'] = "Regional graph for {} at {}".format(DATA_DICT[data_selected], date)
    figure = dict(data=data, layout=layout_pie)
    return figure


def update_cards_text(field):
    if field == 'data':
        string_header_last_update = (df_national_data.index[-1]).strftime('Dati Aggiornati al: %d/%m/%Y %H:%M')
        return string_header_last_update
    else:
        card_value = df_national_data[field].iloc[-1]
        card_value_previous_day= df_national_data[field].iloc[-2]
        variation_previous_day = card_value - card_value_previous_day
        if variation_previous_day > 0:
            return card_value, " ( +", variation_previous_day, " )"
        else:
            return card_value, " ( ", variation_previous_day, " )"


def app_layout():
    app.layout = html.Div(
        [  # START OF SUPREME INCAPSULATION ############################################
            dcc.Store(id="aggregate_data"),
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
                                    "margin-bottom": "15px",
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
                                        "Covid-19 Italia by Gellex",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    html.H5(id="subHeader", children=update_cards_text('data'),
                                            style={"margin-top": "0px"}),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),  # END OF HEADING
                    html.Div(  # START OF BUTTON
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
                        #id="button",
                    ),  # END OF BUTTON
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),  # END OF 1ST INCAPSULATION -END OF HEADING############################################

            html.Div(  # START OF 2ND INCAPSULATION  ############################################
                [
                    html.Div(  # START OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                        [

                            dcc.Tabs(id='tabs', value='tab_region', children=[  # START OF TABS COMPONENT CREATOR
                                dcc.Tab(label='Compare Regions', value='tab_region', children=[  # START FIRST TAB
                                    html.P(
                                        "Filter by date (or select range in histogram):",
                                        className="control_label",
                                    ),
                                    dcc.RangeSlider(
                                        id="year_slider_tab_1",
                                        min=1960,
                                        max=2017,
                                        value=[1990, 2010],
                                        className="dcc_control",
                                    ),
                                    html.P("Multi-Select Regions:", className="control_label"),
                                    dcc.Dropdown(id='dropdown_region_list_selected',
                                                 options=get_options(
                                                     df_regional_data['denominazione_regione'].unique()),
                                                 multi=True,
                                                 value=['Abruzzo', 'Campania'],
                                                 className='dcc_control'
                                                 ),
                                    html.P("Select data to show:", className="control_label"),
                                    dcc.Dropdown(
                                        id='dropdown_data_selected',
                                        options=get_options_from_dict(DATA_DICT),
                                        multi=False,
                                        value='ricoverati_con_sintomi',
                                        className='dcc_control'
                                    ),
                                    dcc.Graph(id="pie_graph")
                                ]),  # END OF FIRST TAB
                                dcc.Tab(label='Compare Data', value='tab_data', children=[  # START OF SECOND TAB
                                    html.P(
                                        "Filter by date (or select range in histogram):",
                                        className="control_label",
                                    ),
                                    dcc.RangeSlider(
                                        id="year_slider_tab_2",
                                        min=1960,
                                        max=2017,
                                        value=[1990, 2010],
                                        className="dcc_control",
                                    ),
                                    html.P("Multi-Select Data:", className="control_label"),
                                    dcc.Dropdown(id='dropdown_data_list_selected',
                                                 options=get_options_from_dict(DATA_DICT),
                                                 multi=True,
                                                 value=['ricoverati_con_sintomi'],
                                                 className='dcc_control'
                                                 ),
                                    html.P("Select region to show:", className="control_label"),
                                    dcc.Dropdown(
                                        id='dropdown_region_selected',
                                        options=get_options(df_regional_data['denominazione_regione'].unique()),
                                        multi=False,
                                        value=df_regional_data['denominazione_regione'].sort_values()[0],
                                        className='dcc_control'
                                    ),
                                ]),  # END OF SECOND TAB

                            ])  # END OF TABS COMPONENT CREATOR

                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),  # END OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)

                    html.Div(  # START OF 2ND BLOCK
                        [
                            html.Div(  # START OF CARDS #
                                [
                                    html.Div(
                                        [html.H6(id="total_positive_text",
                                                 children=update_cards_text('totale_positivi')),
                                         html.P("Attualmente Positivi Italia")],
                                        id="total_positive",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_cases_text", children=update_cards_text('totale_casi')),
                                         html.P("Totale Casi Italia")],
                                        id="total_cases",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_recovered_text",
                                                 children=update_cards_text('dimessi_guariti')),
                                         html.P("Dimessi/Guariti Italia")],
                                        id="total_recovered",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="total_deaths_text", children=update_cards_text('deceduti')),
                                         html.P("Decessi Italia")],
                                        id="total_deaths",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ),  # END OF CARDS #
                            html.Div(  # START OF THE GRAPH UNDER THE CARDS#
                                [dcc.Graph(id='regional_timeseries_linear')],
                                id="countGraphContainer",
                                className="pretty_container",
                            ),  # END OF THE GRAPH #
                        ],
                        id="right-column",
                        className="eight columns",
                    ),  # END OF 2ND BLOCK
                ],
                className="row flex-display",
            ),  # END OF 2ND INCAPSULATION  ############################################
            html.Div(  # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
                [
                    html.Div(
                        [dcc.Graph(id="main_graph")],
                        className="pretty_container seven columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="individual_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),  # END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component
            html.Div(  # START OF 4TH INCAPSULATION THAT INCLUDE 2 GRAPH component
                [
                    html.Div(
                        [dcc.Graph(id="pie_graph_2")],
                        className="pretty_container seven columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="aggregate_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),  # END OF 4TH INCAPSULATION THAT INCLUDE 2 GRAPH component
        ],  # END OF SUPEREME INCAPSULATION ############################################

        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )


if __name__ == '__main__':
    # Initialise the app
    app.config.suppress_callback_exceptions = True
    app_layout()
    app.run_server(debug=True)  # debug=True active a button in the bottom right corner of the web page
