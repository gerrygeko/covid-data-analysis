import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

url_csv_regional_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"


def load_csv(url):
    data_loaded = pd.read_csv(url)
    return data_loaded


df_italy_region = load_csv(url_csv_regional_data)
df_italy_region.index = pd.to_datetime(df_italy_region['data'])

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


# Define the web app
app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('COVID-19'),
                                 html.P('by Gellex (Geko + Killex)'),
                                 html.P('Visualising time series with Plotly - Dash.'),
                                 html.P('Select one or more regions from the dropdown:'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='regionselector',
                                                      options=get_options(df_italy_region['denominazione_regione'].unique()),
                                                      multi=True,
                                                      value=[df_italy_region['denominazione_regione'].sort_values()[0]],
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      ),
                                     ],
                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
                             ])
                              ])
        ]

)


def create_empty_figure():
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
@app.callback(Output('timeseries', 'figure'), [Input('regionselector', 'value')])
def update_graph(selected_dropdown_value):
    trace1 = []
    df_sub = df_italy_region

    if len(selected_dropdown_value) is 0:
        figure = create_empty_figure()
        return figure

    for region in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['denominazione_regione'] == region].index,           #https://plotly.com/python/line-charts/#line-plot-with-goscatter
                                 y=df_sub[df_sub['denominazione_regione'] == region]['nuovi_positivi'],
                                 mode='lines+markers',
                                 opacity=1,
                                 name=region,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
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


if __name__ == '__main__':
    app.run_server(debug=True)
