import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

url_csv_regional_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
url_csv_italy_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"


def load_csv(url):
    data_loaded = pd.read_csv(url, parse_dates=True)
    return data_loaded


df_italy_region = load_csv(url_csv_regional_data)
df_italy_region.index = pd.to_datetime(df_italy_region['data'])

df_italy = load_csv(url_csv_italy_data)
df_italy.index = pd.to_datetime(df_italy['data'])

# Initialise the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


# When we generate dynamic components from callbacks (as in your case),
# Dash has no way of knowing which IDs you are generating.
# After all, the IDs could be totally dynamic!
# Dash assumes that you are making a typo by assigning a callback to an ID that doesn’t exist at app start but
# allows you to manually correct this assumption by setting app.config['suppress_callback_exceptions']=True.
# This forces you to acknowledge that Dash will not protect you against ID exceptions.


def get_options(list_value):
    dict_list = []
    for i in list_value:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def create_figure_national_plot_linear():
    df_sub = df_italy
    time_set = df_sub['data']
    tot_cases = df_sub['totale_casi']
    tot_positive = df_sub['totale_positivi']
    symptomatics_patients = df_sub['ricoverati_con_sintomi']
    intensive_care = df_sub['terapia_intensiva']
    scatter1 = go.Scatter(x=time_set, y=tot_cases, mode='lines+markers', opacity=0.7, name="Total cases",
                         textposition='bottom center')
    scatter2 = go.Scatter(x=time_set, y=tot_positive, mode='lines+markers', opacity=0.7, name="Currently positive",
                          textposition='bottom center')
    scatter3 = go.Scatter(x=time_set, y=symptomatics_patients, mode='lines+markers', opacity=0.7, name="Symptomatics patients",
                         textposition='bottom center')
    scatter4 = go.Scatter(x=time_set, y=intensive_care, mode='lines+markers', opacity=0.7, name="Intensive care",
                          textposition='bottom center')

    figure = {'data': [scatter1, scatter2, scatter3, scatter4],
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Linear Scale', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }
    return figure


def create_figure_national_plot_log():
    df_sub = df_italy
    time_set = df_sub['data']
    tot_cases = df_sub['totale_casi']
    tot_positive = df_sub['totale_positivi']
    symptomatics_patients = df_sub['ricoverati_con_sintomi']
    intensive_care = df_sub['terapia_intensiva']
    scatter1 = go.Scatter(x=time_set, y=tot_cases, mode='lines+markers', opacity=0.7, name="Total cases",
                          textposition='bottom center')
    scatter2 = go.Scatter(x=time_set, y=tot_positive, mode='lines+markers', opacity=0.7, name="Currently positive",
                          textposition='bottom center')
    scatter3 = go.Scatter(x=time_set, y=symptomatics_patients, mode='lines+markers', opacity=0.7,
                          name="Symptomatics patients",
                          textposition='bottom center')
    scatter4 = go.Scatter(x=time_set, y=intensive_care, mode='lines+markers', opacity=0.7, name="Intensive care",
                          textposition='bottom center')
    figure = {'data': [scatter1, scatter2, scatter3, scatter4],
              'layout': go.Layout(
                  colorway=["#ffff00", '#ff0000', '#adff2f', '#f0ffff', '#00bfff', '#ffa500'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Logarithmic Scale', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
                  yaxis_type="log"
              ),
              }
    return figure


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
                                                           df_italy_region['denominazione_regione'].unique()),
                                                       multi=True,
                                                       value=[
                                                           df_italy_region['denominazione_regione'].sort_values()[0]],
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
                                              dcc.Graph(id='regional_timeseries_log', config={'displayModeBar': False},
                                                        animate=True)

                                          ]),
                                          dcc.Tab(label='National Area', children=[
                                              dcc.Graph(figure=create_figure_national_plot_linear(),
                                                        config={'displayModeBar': False},
                                                        animate=True),
                                              dcc.Graph(figure=create_figure_national_plot_log(),
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


def create_empty_figure_region_plot():
    df_sub = df_italy_region
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
    trace1 = []
    df_sub = df_italy_region

    if len(selected_dropdown_value) == 0:
        figure = create_empty_figure_region_plot()
        return figure

    for region in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['denominazione_regione'] == region].index,
                                 # https://plotly.com/python/line-charts/#line-plot-with-goscatter
                                 y=df_sub[df_sub['denominazione_regione'] == region]['nuovi_positivi'],
                                 mode='lines+markers',
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
                  title={'text': 'New Positives (linear scale)', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }
    return figure


# Callback for timeseries/region
@app.callback(Output('regional_timeseries_log', 'figure'), [Input('regionselector', 'value')])
def update_graph_log(selected_dropdown_value):
    trace1 = []
    df_sub = df_italy_region

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
                  # xaxis_type="log",
                  yaxis_type="log"
              ),
              }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)  # debug=True active a button in the bottom right corner of the web page
