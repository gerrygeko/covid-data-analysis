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


def get_options(list_value):
    dict_list = []
    for i in list_value:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def create_figure_plot(data_frame, x_axis_data, y_axis_data_mapping, y_is_log=False):
    y_axis_type = "log" if y_is_log else "linear"
    scatter_list = []
    for y_data_name, label in y_axis_data_mapping:
        scatter = go.Scatter(x=x_axis_data, y=data_frame[y_data_name], mode='lines+markers', opacity=0.7,
                             name=label, textposition='bottom center')
        scatter_list.append(scatter)

    figure = {'data': scatter_list,
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Linear Scale', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [x_axis_data.values.min(), x_axis_data.values.max()]},
                  yaxis_type=y_axis_type
              ),
              }
    return figure


def create_empty_figure_region_plot():
    df_sub = df_national_data
    time_set = list(set(df_sub['denominazione_regione'].index.to_series().values))
    scatter = go.Scatter(x=time_set, y=[], mode='lines', opacity=0.7, name="No selection", textposition='bottom center')

    figure = {'data': [scatter],
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(224, 224, 224, 0)',
                  plot_bgcolor='rgba(224, 224, 224, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'New Positive', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_linear', 'figure'), [Input('regionselector', 'value')])
def update_graph(selected_dropdown_value):
    regions_list = []
    df_sub = df_regional_data

    # if no region selected, create empty figure
    if len(selected_dropdown_value) == 0:
        figure = create_empty_figure_region_plot()
        return figure

    for region in selected_dropdown_value:
        regions_list.append(go.Scatter(x=df_sub[df_sub['denominazione_regione'] == region].index,
                                 # https://plotly.com/python/line-charts/#line-plot-with-goscatter
                                 y=df_sub[df_sub['denominazione_regione'] == region]['nuovi_positivi'],
                                 mode='lines+markers',
                                 opacity=1,
                                 name=region,
                                 textposition='bottom center'))

    figure = {'data': regions_list,
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  # ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(224, 224, 224, 0)',
                  plot_bgcolor='rgba(224, 224, 224, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'New Positives (linear scale)', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_log', 'figure'), [Input('regionselector', 'value')])
def update_graph_log(selected_dropdown_value):
    trace1 = []
    df_sub = df_regional_data

    if len(selected_dropdown_value) == 0:
        figure = create_empty_figure_region_plot()
        return figure

    for region in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['denominazione_regione'] == region].index,
                                 # https://plotly.com/python/line-charts/#line-plot-with-goscatter
                                 y=df_sub[df_sub['denominazione_regione'] == region]['totale_positivi'],
                                 mode='lines',
                                 opacity=1,
                                 name=region,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  # ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(224, 224, 224, 0)',
                  plot_bgcolor='rgba(224, 224, 224, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Total Positives (log scale)', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
                  yaxis_type="log"
              ),
              }
    return figure


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
                                                  dcc.Graph(figure=create_figure_plot(df_national_data,
                                                                                      df_national_data.index,
                                                                                      national_data_mapping,
                                                                                      y_is_log=False),
                                                            config={'displayModeBar': False},
                                                            animate=True),
                                                  dcc.Graph(figure=create_figure_plot(df_national_data,
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
    app_layout()
    app.run_server(debug=True)  # debug=True active a button in the bottom right corner of the web page
