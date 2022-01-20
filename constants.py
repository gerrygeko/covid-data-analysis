INHABITANT_RATE = 100000
NUMBER_OF_WORLD_COUNTRIES = 188
SECONDS_FOR_NEWS_UPDATE = 1000
TOTAL_ICU_ITALY = 6458
VACCINABLE_ITALIAN_POPULATION = 54000000 #Vaccinable population
#Italian population on 1st Jan 2021 (ISTAT source) 59257566


DATE_PROPERTY_NAME_IT = 'data'
DATE_PROPERTY_NAME_EN = 'Date'
DATE_PROPERTY_NAME_VACCINES_ITA_LAST_UPDATE = 'ultimo_aggiornamento'
PAGE_TITLE = "Coronavirus Data (SARS-CoV-2)"
COPYRIGHT = "Copyright (C) 2020 | Coronavirus Data by Gellex"
REPO_NAME = "covid-data-analysis"
DEFAULT_LANGUAGE = "it"

DEBUG_MODE_ENV_VAR = "DEBUG_MODE"
CURRENT_LOCALE_ENV_VAR = "CURRENT_LOCALE"
GITHUB_ACCESS_TOKEN_ENV_VAR = "GITHUB_ACCESS_TOKEN"
GITHUB_USER_ENV_VAR = "GITHUB_USER"
ONE_SIGNAL_TEST_API_KEY_ENV_VAR = "ONE_SIGNAL_TEST_API_KEY"
ONE_SIGNAL_PROD_API_KEY_ENV_VAR = "ONE_SIGNAL_PROD_API_KEY"

URL_CSV_REGIONAL_DATA = \
    "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
URL_CSV_ITALY_DATA = \
    "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale" \
    "/dpc-covid19-ita-andamento-nazionale.csv"
URL_CSV_WORLD_COUNTRIES_DATA = \
    "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv"
URL_CSV_WORLDWIDE_AGGREGATE_DATA = \
    "https://raw.githubusercontent.com/datasets/covid-19/main/data/worldwide-aggregate.csv"
URL_GEOJSON_REGIONS = \
    "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
URL_GEOJSON_WORLD_COUNTRIES = \
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

URL_VACCINES_ITA_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/vaccini-summary-latest.csv"
URL_VACCINES_ITA_REGISTRY_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/anagrafica-vaccini-summary-latest.csv"
URL_VACCINES_ITA_ADMINISTRATIONS_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv"
URL_VACCINES_ITA_ADMINISTRATIONS = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
URL_VACCINES_ITA_DELIVERIES = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv"
URL_VACCINES_ITA_ADMINISTRATION_POINT = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/punti-somministrazione-latest.csv"
URL_VACCINES_WORLD = "https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations"


LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA = ('Turkmenistan', 'Myanmar', 'North Korea', 'Greenland')
LIST_OF_WORLD_FIELDS = ('Confirmed', 'Deaths', 'New Confirmed', 'New Deaths', 'Active_cases')
LIST_OF_WORLD_FIELDS_TO_RATE = ('Confirmed', 'Deaths', 'Active_cases', 'New Confirmed', 'New Deaths')
LIST_OF_NOT_LOCATED_COUNTRIES_ON_MAP = ('Diamond Princess', 'MS Zaandam', 'Holy See')
