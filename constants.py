INHABITANT_RATE = 100000
NUMBER_OF_WORLD_COUNTRIES = 188
SECONDS_FOR_NEWS_UPDATE = 1000
TOTAL_ICU_ITALY = 6458

DATE_PROPERTY_NAME_IT = 'data'
DATE_PROPERTY_NAME_EN = 'Date'
DATE_PROPERTY_NAME_VACCINES_ITA_LAST_UPDATE = 'ultimo_aggiornamento'
PAGE_TITLE = "Coronavirus (SARS-CoV-2)"
REPO_NAME = "covid-data-analysis"
DEFAULT_LANGUAGE = "IT"

DEBUG_MODE_ENV_VAR = "DEBUG_MODE"
GITHUB_ACCESS_TOKEN_ENV_VAR = "GITHUB_ACCESS_TOKEN"
GITHUB_USER_ENV_VAR = "GITHUB_USER"

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
URL_NEWS_UPDATE = "http://newsapi.org/v2/top-headlines?country=it&category=science&apiKey=b20640c581554761baab24317b8331e7"

URL_VACCINES_ITA_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/vaccini-summary-latest.csv"
URL_VACCINES_ITA_REGISTRY_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/anagrafica-vaccini-summary-latest.csv"
URL_VACCINES_ITA_ADMINISTRATIONS_SUMMARY_LATEST = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv"
URL_VACCINES_ITA_ADMINISTRATIONS = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv"
URL_VACCINES_ITA_DELIVERIES = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv"
URL_VACCINES_ITA_ADMINISTRATION_POINT = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/punti-somministrazione-latest.csv"

LIST_OF_WORLD_COUNTRIES_WITHOUT_DATA = ('Turkmenistan', 'Myanmar', 'North Korea', 'Greenland')
LIST_OF_WORLD_FIELDS = ('Confirmed', 'Recovered', 'Deaths', 'New Confirmed', 'New Recovered', 'New Deaths', 'Active_cases')
LIST_OF_WORLD_FIELDS_TO_RATE = ('Confirmed', 'Recovered', 'Deaths', 'Active_cases', 'New Confirmed', 'New Recovered', 'New Deaths')
LIST_OF_NOT_LOCATED_COUNTRIES_ON_MAP = ('Diamond Princess', 'MS Zaandam', 'Holy See')
