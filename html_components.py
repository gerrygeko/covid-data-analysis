import base64
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
from pytz import timezone

import logger
from resources import language_list, load_resource, locale_language
from utils import get_options_from_list, get_options, new_positive_regions, get_version

SECONDS = 1000
PAGE_TITLE = "Coronavirus (SARS-CoV-2)"

# API Requests for news
news_requests = requests.get(
    "http://newsapi.org/v2/top-headlines?country=it&category=science&apiKey=b20640c581554761baab24317b8331e7")

encoded_image_gerardo = base64.b64encode(open('assets/gerardo.png', 'rb').read()).decode('ascii')
encoded_image_nicola = base64.b64encode(open('assets/nicola.png', 'rb').read()).decode('ascii')

log = logger.get_logger()

field_list_complete = ['ricoverati_con_sintomi', 'terapia_intensiva',
                       'totale_ospedalizzati', 'isolamento_domiciliare',
                       'totale_positivi', 'variazione_totale_positivi',
                       'nuovi_positivi', 'dimessi_guariti',
                       'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening', 'totale_casi',
                       'tamponi', 'casi_testati']


def create_news():
    json_data = news_requests.json()["articles"]
    df_news = pd.DataFrame(json_data)
    df_news = pd.DataFrame(df_news[["urlToImage", "title", "url"]])
    max_rows = 6
    news_title = load_resource('label_news')
    return html.Div(
        children=[
            html.H5(className="p-news title", children=news_title),
            html.P(
                className="p-news title",
                children=load_resource('label_last_update')
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


def create_contacts(app):
    return html.Div(
        children=[
            html.H5(className="p-news title", children=load_resource('label_contact_us')),
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


def create_page_components(app, df_regional_data):
    log.info("Loading all the components")
    global PAGE_TITLE
    return [  # START OF SUPREME INCAPSULATION ############################################
        dcc.Store(id="aggregate_data"),
        # Interval component for updating news list
        dcc.Interval(id="i_news", interval=900 * SECONDS, n_intervals=0),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(  # START OF 1ST INCAPSULATION - (LOGO - HEADING - BUTTON)
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "120px",
                                "width": "auto",
                                "margin-bottom": "0px",
                                "display": "block",
                                "margin-left": "auto",
                                "margin-right": "auto"
                            }
                        ),

                    ],
                    id="href-logos",
                    className="four columns",
                ),  # END OF LOGO
                html.Div(  # START OF HEADING
                    [
                        html.Div(
                            [
                                html.H3(
                                    PAGE_TITLE
                                ),
                                html.H5(id="subHeader", children='')
                            ]
                        )
                    ],
                    className="four columns",
                    id="title",
                ),  # END OF HEADING
                html.Div(  # START OF GITHUB LOGOS
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="dropdown_language_selected",
                                            options=language_list,
                                            value=locale_language.language,
                                            searchable=False
                                        )
                                    ]
                                )
                            ]
                        )
                    ],
                    className="four columns",
                    id="logos"
                ),  # END OF GITHUB LOGOS
            ],
            id="header",
            className="row flex-display"
        ),
        # =========================================================================================================
        dcc.Tabs(id='tabs_master', value='tab_master_1', children=[
            dcc.Tab(label=load_resource('label_tab_master_1'), value='tab_master_1',
                    children=[
                        html.Div(
                            [html.H5(id='card_header-1', children=load_resource('label_titolo'), className='title')]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [html.H6(id="total_positive_text", children=''),
                                                     html.H6(id="total_positive_variation", children=''),
                                                     html.P(load_resource('totale_positivi'))],
                                                    id="total_positive",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(id="total_cases_text", children=''),
                                                     html.H6(id="total_cases_variation", children=''),
                                                     html.P(load_resource('totale_casi'))],
                                                    id="total_cases",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(id="total_recovered_text", children=''),
                                                     html.H6(id="total_recovered_variation", children=''),
                                                     html.P(load_resource('dimessi_guariti'))],
                                                    id="total_recovered",
                                                    className="mini_container",
                                                )
                                            ],
                                            id="info-container",
                                            className="row container-display",
                                        ),
                                    ],
                                    className="ghosty_container six columns",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [html.H6(id="total_deaths_text", children=''),
                                                     html.H6(id="total_deaths_variation", children=''),
                                                     html.P(load_resource('deceduti'))],
                                                    id="total_deaths",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(id="total_icu_text", children=''),
                                                     html.H6(id="total_icu_variation", children=''),
                                                     html.P(load_resource('terapia_intensiva'))],
                                                    id="total_icu",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(id="total_swabs_text", children=''),
                                                     html.H6(id="total_swabs_variation", children=''),
                                                     html.P(load_resource('tamponi'))],
                                                    id="total_swabs",
                                                    className="mini_container",
                                                )
                                            ],
                                            id="info-container-2",
                                            className="row container-display",
                                        ),
                                    ],
                                    className="ghosty_container six columns",
                                ),
                            ],
                            className="row flex-display",
                        ),
                        dcc.Tabs(id='tabs', value='tab_national', children=[  # START OF TABS COMPONENT CREATOR
                            dcc.Tab(label=load_resource('label_tab_1'), value='tab_national',
                                    children=[  # START FIRST TAB
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Graph(id="italian_active_cases_bar_graph")
                                                    ],
                                                    className="pretty_container twelve columns",
                                                ),
                                            ],
                                            className="row flex-display",
                                        ),
                                        html.Div(
                                            # START OF 2ND INCAPSULATION  ############################################
                                            [
                                                html.Div(  # START OF 2ND BLOCK
                                                    [
                                                        html.Div(
                                                            [
                                                                html.P(load_resource('label_select_data'),
                                                                       className="control_label"),
                                                                dcc.Dropdown(
                                                                    id='dropdown_data_selected',
                                                                    options=get_options_from_list(field_list_complete),
                                                                    multi=False,
                                                                    value='nuovi_positivi',
                                                                    className='dcc_control'
                                                                ),
                                                                html.P(load_resource('label_select_multiregion'),
                                                                       className="control_label"),
                                                                dcc.Dropdown(id='dropdown_region_list_selected',
                                                                             options=get_options(
                                                                                 df_regional_data[
                                                                                     'denominazione_regione'].unique()),
                                                                             multi=True,
                                                                             value=new_positive_regions(
                                                                                 df_regional_data),
                                                                             className='dcc_control'
                                                                             ),
                                                                dcc.Graph(id='regional_timeseries_linear'),
                                                                dcc.Graph(id="pie_graph")
                                                            ],
                                                            className="pretty_container",
                                                        ),
                                                    ],
                                                    id="right-column",
                                                    className="eight columns",
                                                ),  # END OF 2ND BLOCK
                                                html.Div(
                                                    # START OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                                                    [
                                                        html.Div(
                                                            [
                                                                dcc.Graph(id="table_tab1")
                                                            ],
                                                            className="pretty_container twelve columns",
                                                        ),
                                                        html.Div(
                                                            [html.H5(id='bar_header',
                                                                     children=load_resource('label_top_ten'),
                                                                     className='title'),
                                                             dcc.Graph(id="bar_graph")],
                                                            className="pretty_container twelve columns",
                                                        ),

                                                    ],
                                                    className="pretty_container four columns",
                                                    id="cross-filter-options-tab1",
                                                ),  # END OF 1ST BLOCK (INCLUDE DROPDOWN, CHECK , RADIO CONTROLS)
                                            ],
                                            className="row flex-display",
                                        ),  # END OF 2ND INCAPSULATION  ############################################
                                        html.Div(  # START OF 3RD INCAPSULATION THAT INCLUDE BLOCK - 2 GRAPH component
                                            [
                                                html.Div(
                                                    [html.H5(id='map_header', children=load_resource('label_map'),
                                                             className='title'),
                                                     dcc.Graph(id="map_graph")],
                                                    className="pretty_container twelve columns",
                                                ),
                                            ],
                                            className="row flex-display",
                                        ),  # END OF 3RD INCAPSULATION THAT INCLUDE 2 GRAPH component

                                    ]),  # END OF FIRST TAB
                            dcc.Tab(label=load_resource('label_tab_2'), value='tab_regional',
                                    children=[  # START OF SECOND TAB
                                        html.Div(
                                            # START OF 2ND INCAPSULATION  ############################################
                                            [
                                                html.Div(
                                                    ##########################################################################
                                                    [
                                                        html.P(load_resource('label_select_region'),
                                                               className="control_label"),
                                                        dcc.Dropdown(
                                                            id='dropdown_region_selected',
                                                            options=get_options(
                                                                df_regional_data['denominazione_regione'].unique()),
                                                            multi=False,
                                                            value=
                                                            df_regional_data['denominazione_regione'].sort_values()[0],
                                                            className='dcc_control'
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [html.H5(id="string_max_date_new_positives"),
                                                                     html.P(load_resource('label_data_picco_max'))],
                                                                    className="mini_container_mean_max",
                                                                ),
                                                                html.Div(
                                                                    [html.H5(id="string_max_value_new_positives"),
                                                                     html.P(load_resource('label_valore_picco_max'))],
                                                                    className="mini_container_mean_max",
                                                                ),
                                                                html.Div(
                                                                    [html.H5(id="mean_total_cases"),
                                                                     html.P(load_resource('label_media_contagi'))],
                                                                    className="mini_container_mean_max",
                                                                ),
                                                            ],
                                                            id="info-container_max_mean_tab2",
                                                            className="row container-display",
                                                        ),
                                                    ],
                                                    className="pretty_container four columns",
                                                ),
                                                ################################################################################
                                                html.Div(  # START OF 2ND BLOCK
                                                    [
                                                        html.Div(  # START OF CARDS #
                                                            [
                                                                html.Div(
                                                                    [html.H6(id="total_cases_text_tab2", children=''),
                                                                     html.H6(id="total_cases_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('totale_casi'))],
                                                                    id="total_cases_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_positive_text_tab2",
                                                                             children=''),
                                                                     html.H6(id="total_positive_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('totale_positivi'))],
                                                                    id="total_positive_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_recovered_text_tab2",
                                                                             children=''),
                                                                     html.H6(id="total_recovered_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('dimessi_guariti'))],
                                                                    id="total_recovered_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_deaths_text_tab2", children=''),
                                                                     html.H6(id="total_deaths_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('deceduti'))],
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
                                                                    [html.H6(
                                                                        id="total_hospitalized_w_symptoms_text_tab2",
                                                                        children=''),
                                                                        html.H6(
                                                                            id="total_hospitalized_w_symptoms_variation_tab2",
                                                                            children=''),
                                                                        html.P(load_resource('totale_ospedalizzati'))],
                                                                    id="total_hospitalized_w_symptoms_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_icu_text_tab2", children=''),
                                                                     html.H6(id="total_icu_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('terapia_intensiva'))],
                                                                    id="total_icu_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_isolation_text_tab2",
                                                                             children=''),
                                                                     html.H6(id="total_isolation_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('isolamento_domiciliare'))],
                                                                    id="total_isolation_tab2",
                                                                    className="mini_container",
                                                                ),
                                                                html.Div(
                                                                    [html.H6(id="total_swabs_text_tab2", children=''),
                                                                     html.H6(id="total_swabs_variation_tab2",
                                                                             children=''),
                                                                     html.P(load_resource('tamponi'))],
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
                                                    [
                                                        dcc.Graph(id="bar_graph_tab2")
                                                    ],
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
                                    children=[
                                        html.Div(id="contacts", children=create_contacts(app)),
                                        html.Div(
                                            [
                                                html.H5(className='p-news title',
                                                        children=load_resource('label_credits')),
                                                html.A(
                                                    children=html.Img(
                                                        src=app.get_asset_url("github_gellex.png"),
                                                        className='credits_icon',
                                                        id="github-image",
                                                    ),
                                                    href="https://github.com/gerrygeko/covid-data-analysis",
                                                ),
                                                html.A(
                                                    children=html.Img(
                                                        src=app.get_asset_url("protezione_civile.png"),
                                                        className='credits_icon',
                                                        id="protezione-civile-image",
                                                    ),
                                                    href="https://github.com/pcm-dpc",
                                                ),
                                                html.A(
                                                    children=html.Img(
                                                        src=app.get_asset_url("istat.png"),
                                                        className='credits_icon',
                                                        id="istat-image",
                                                    ),
                                                    href="http://dati.istat.it/",
                                                )
                                            ]
                                        )
                                    ],
                                    className="pretty_container six columns",
                                ),
                            ],
                            className="row flex-display",
                        )  # END OF 4TH INCAPSULATION
                    ]),
            #==========================================================================================
            dcc.Tab(label=load_resource('label_tab_master_2'), value='tab_world_data',
                    children=[

                    ])
        ]),
        # ==========================================================================================
        html.A(
            html.P(
                id="version_text",
                className="p-version changelog",
                children=[get_version()]
            ),
            href="https://github.com/gerrygeko/covid-data-analysis/blob/master/CHANGELOG.md"
        )
    ]
