import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

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

    figure = create_figure(data_frame, scatter_list, title, y_axis_type)
    return figure


def create_scatter_plot_by_region(data_frame, title, x_axis_data, y_axis_data_mapping_region, y_is_log=False):
    y_axis_type = "log" if y_is_log else "linear"
    scatter_list = []
    # Draw empty figures if an empty list is passed
    if len(y_axis_data_mapping_region) == 0:
        scatter = go.Scatter(x=x_axis_data, y=[], mode='lines+markers', opacity=0.7, textposition='bottom center')
        scatter_list.append(scatter)
    else:
        for field, region in y_axis_data_mapping_region:
            scatter = go.Scatter(x=x_axis_data, y=data_frame[data_frame['denominazione_regione'] == region][field],
                                 mode='lines+markers',
                                 opacity=0.7,
                                 name=region,
                                 textposition='bottom center')
            scatter_list.append(scatter)

    figure = create_figure(data_frame, scatter_list, title, y_axis_type)
    return figure


def create_figure(data_frame, data, title, y_axis_type):
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': title, 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [data_frame.index.min(), data_frame.index.max()]},
                  yaxis_type=y_axis_type
              ),
              }
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('regionselector', 'value')])
def update_graph(selected_dropdown_value):
    df_sub = df_regional_data
    regions_list_mapping = []
    # if no region selected, create empty figure
    if len(selected_dropdown_value) == 0:
        figure = create_scatter_plot(df_sub, 'Linear region data', df_sub.index, [])
        return figure
    for region in selected_dropdown_value:
        regions_list_mapping.append(('nuovi_positivi', region))
    x_axis_data = df_sub.index.drop_duplicates()
    figure = create_scatter_plot_by_region(df_sub, 'Linear region data', x_axis_data, regions_list_mapping)
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_log', 'figure'), [Input('regionselector', 'value')])
def update_graph_log(selected_dropdown_value):
    df_sub = df_regional_data
    regions_list_mapping = []
    if len(selected_dropdown_value) == 0:
        figure = create_scatter_plot(df_sub, 'Logarithm region data', df_sub.index, [])
        return figure
    for region in selected_dropdown_value:
        regions_list_mapping.append(('totale_positivi', region))
    x_axis_data = df_sub.index.drop_duplicates()
    figure = create_scatter_plot_by_region(df_sub, 'Logarithm region data', x_axis_data, regions_list_mapping, y_is_log=True)
    return figure


def app_oil_layout():
    app.layout = html.Div(
        [# START OF SUPREME INCAPSULATION ############################################
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(# START OF 1ST INCAPSULATION - (LOGO - HEADING - BUTTON)
                [
                    html.Div( # START OF LOGO
                        [
                            html.Img(
                                src=app.get_asset_url("dash-logo.png"),
                                id="plotly-image",
                                style={
                                    "height": "60px",
                                    "width": "auto",
                                    "margin-bottom": "25px",
                                },
                            )
                        ],
                        className="one-third column",
                    ), # END OF LOGO
                    html.Div( # START OF HEADING
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Italian Covid-19",
                                        style={"margin-bottom": "0px"},
                                    ),
                                    html.H5(
                                        "by Gellex (Geko + Killex) - Visualising time series with Plotly - Dash",
                                        style={"margin-top": "0px"}
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ), # END OF HEADING
                    html.Div( #START OF BUTTON
                        [
                            html.A(
                                html.Button("Learn More", id="learn-more-button"),
                                href="https://plot.ly/dash/pricing/",
                            )
                        ],
                        className="one-third column",
                        id="button",
                    ), #END OF BUTTON
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),# END OF 1ST INCAPSULATION -END OF HEADING############################################

            html.Div(# START OF 2ND INCAPSULATION  ############################################
                [
                    html.Div( # START OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                        [
                            html.P(
                                "Filter by construction date (or select range in histogram):",
                                className="control_label",
                            ),
                            dcc.RangeSlider(
                                id="year_slider",
                                min=1960,
                                max=2017,
                                value=[1990, 2010],
                                className="dcc_control",
                            ),
                            html.P("Filter by well status:", className="control_label"),
                            dcc.RadioItems(
                                id="well_status_selector",
                                options=[
                                    {"label": "All ", "value": "all"},
                                    {"label": "Active only ", "value": "active"},
                                    {"label": "Customize ", "value": "custom"},
                                ],
                                value="active",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            dcc.Dropdown(id='regionselector',
                                         options=get_options(
                                             df_regional_data['denominazione_regione'].unique()),
                                         multi=True,
                                         value=[
                                             df_regional_data['denominazione_regione'].sort_values()[
                                                 0]],
                                         # style={'backgroundColor': '#1E1E1E'},
                                         className='dcc_control'
                                         ),
                            dcc.Checklist(
                                id="lock_selector",
                                options=[{"label": "Lock camera", "value": "locked"}],
                                className="dcc_control",
                                value=[],
                            ),
                            html.P("Filter by well type:", className="control_label"),
                            dcc.RadioItems(
                                id="well_type_selector",
                                options=[
                                    {"label": "All ", "value": "all"},
                                    {"label": "Productive only ", "value": "productive"},
                                    {"label": "Customize ", "value": "custom"},
                                ],
                                value="productive",
                                labelStyle={"display": "inline-block"},
                                className="dcc_control",
                            ),
                            dcc.Dropdown(
                                id="well_types",
                                #options=well_type_options,
                                multi=True,
                                #value=list(WELL_TYPES.keys()),
                                className="dcc_control",
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),# END OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)

                    html.Div( # START OF 2ND BLOCK
                        [
                            html.Div( # START OF CARDS #
                                [
                                    html.Div(
                                        [html.H6(id="well_text"), html.P("No. of Wells")],
                                        id="wells",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="gasText"), html.P("Gas")],
                                        id="gas",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="oilText"), html.P("Oil")],
                                        id="oil",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.H6(id="waterText"), html.P("Water")],
                                        id="water",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ), # END OF CARDS #
                            html.Div( # START OF THE GRAPH UNDER THE CARDS#
                                [dcc.Graph(id='regional_timeseries_linear')],
                                id="countGraphContainer",
                                className="pretty_container",
                            ),# END OF THE GRAPH #
                        ],
                        id="right-column",
                        className="eight columns",
                    ),# END OF 2ND BLOCK
                ],
            className = "row flex-display",
            ), # END OF 2ND INCAPSULATION  ############################################
            html.Div( # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
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
            ),# END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component
            html.Div(# START OF 4TH INCAPSULATION THAT INCLUDE 2 GRAPH component
                [
                    html.Div(
                        [dcc.Graph(id="pie_graph")],
                        className="pretty_container seven columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="aggregate_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),# END OF 4TH INCAPSULATION THAT INCLUDE 2 GRAPH component
        ],# END OF SUPEREME INCAPSULATION ############################################

        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )

def app_layout():
    # Define the web app
    app.layout = html.Div(
        children=[
            html.Div(className='row',
                     children=[
                         html.Div(className='four columns div-user-controls',
                                  children=[
                                      html.H2('COVID-19:ITALY'),
                                      html.P('by Gellex (Geko + Killex)'),
                                      html.P('Visualising time series with Plotly - Dash.'),
                                      html.P('Select one or more regions from the dropdown:'),
                                      html.Div(
                                          className='div-for-dropdown',
                                          children=[
                                              dcc.Dropdown(id='regionselector',
                                                           options=get_options(
                                                               df_regional_data['denominazione_regione'].unique()),
                                                           multi=True,
                                                           value=[
                                                               df_regional_data['denominazione_regione'].sort_values()[
                                                                   0]],
                                                           style={'backgroundColor': '#1E1E1E'},
                                                           className='regionselector'
                                                           ),
                                          ],

                                          style={'color': '#1E1E1E'})
                                  ]
                                  ),

                         html.Div(className='eight columns div-for-charts bg-grey',
                                  children=[
                                      html.Div([
                                          dcc.Tabs([
                                              dcc.Tab(label='Regional Area', children=[
                                                  dcc.Graph(id='regional_timeseries_linear',
                                                            config={'displayModeBar': False},
                                                            animate=True),
                                                  dcc.Graph(id='regional_timeseries_log',
                                                            config={'displayModeBar': False},
                                                            animate=True)

                                              ]),
                                              dcc.Tab(label='National Area', children=[
                                                  dcc.Graph(figure=create_scatter_plot(df_national_data,
                                                                                      'Linear national data',
                                                                                       df_national_data.index,
                                                                                       national_data_mapping,
                                                                                       y_is_log=False),
                                                            config={'displayModeBar': False},
                                                            animate=True),
                                                  dcc.Graph(figure=create_scatter_plot(df_national_data,
                                                                                      'Logarithm national data ',
                                                                                       df_national_data.index,
                                                                                       national_data_mapping,
                                                                                       y_is_log=True),
                                                            config={'displayModeBar': False},
                                                            animate=True)
                                              ])
                                          ], colors={
                                              "border": "grey",
                                              "primary": "gold",
                                              "background": "grey"
                                          })
                                      ])
                                  ])
                     ])
        ]

    )


if __name__ == '__main__':
    # Initialise the app
    app.config.suppress_callback_exceptions = True
    # app_layout()
    app_oil_layout()
    app.run_server(debug=True)  # debug=True active a button in the bottom right corner of the web page
