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
    app_layout()
    app.run_server(debug=True)  # debug=True active a button in the bottom right corner of the web page
