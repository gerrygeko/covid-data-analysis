from googletrans import Translator

import logger

DEFAULT_LANGUAGE = "IT"

language_list = [{'label': 'Italiano', 'value': 'IT'},
                 {'label': 'English', 'value': 'EN'},
                 {'label': 'Dutch', 'value': 'NL'},
                 {'label': 'German', 'value': 'DE'},
                 {'label': 'French', 'value': 'FR'},
                 {'label': 'Spanish', 'value': 'ES'},
                 {'label': 'Portuguese', 'value': 'PT'}
                 ]


class LocaleLanguage:

    def __init__(self, language):
        self.language = language

    def __str__(self):
        return f"ID: {id(self)} and language {self.language}"


resources = {DEFAULT_LANGUAGE: {
    'denominazione_regione': 'Regione',
    'ricoverati_con_sintomi': 'Ricoverati con sintomi',
    'terapia_intensiva': 'Terapia intensiva',
    'totale_ospedalizzati': 'Totale ospedalizzati',
    'isolamento_domiciliare': 'Isolamento domiciliare',
    'totale_positivi': 'Casi attivi',
    'variazione_totale_positivi': 'Variazione totale positivi',
    'nuovi_positivi': 'Nuovi positivi',
    'dimessi_guariti': 'Dimessi/Guariti',
    'deceduti': 'Decessi',
    'casi_da_sospetto_diagnostico': 'Casi Positivi identificati dal Sospetto Diagnostico',
    'casi_da_screening': 'Casi Positivi accertati da Screening',
    'totale_casi': 'Totale casi',
    'tamponi': 'Tamponi effettuati',
    'casi_testati': 'Casi Testati',
    'nazione': 'Italia',
    'header_last_update': 'Dati Aggiornati al:',
    'label_titolo': 'Totale Dati - Italia',
    'label_tab_1': 'Analisi dei dati nazionali',
    'label_tab_2': 'Analisi dei dati regionali',
    'label_select_data': 'Seleziona il dato da analizzare:',
    'label_select_multiregion': 'Seleziona una o più regioni italiane da confrontare:',
    'label_select_region': 'Seleziona la regione italiana da analizzare:',
    'label_data_picco_max': 'Data Picco massimo',
    'label_valore_picco_max': 'Picco massimo',
    'label_media_contagi': 'Media contagi',
    'label_casi_attivi': 'Casi Attivi',
    'label_news': 'News Scienza - Italia',
    'label_contact_us': 'Contattaci',
    'label_last_update': 'Ultimo Aggiornamento:',
    'label_map': 'N° casi ogni 100K abitanti',
    'label_top_ten': 'Top 10 Regioni:',
    'label_hover_map': 'per regione (ogni cento mila abitanti)',
    'label_persone': 'Persone',
    'fase_1': 'Fase 1',
    'fase_2': 'Fase 2',
    'fase_3': 'Fase 3',
    'label_credits': 'Crediti'
    }
}

log = logger.get_logger()
locale_language = LocaleLanguage(DEFAULT_LANGUAGE)


def load_resource(name):
    log.info(locale_language)
    if name not in resources[locale_language.language].keys():
        raise KeyError(f"The resource you are trying to load is not present. Resource: {name}")
    return resources[locale_language.language][name]


def add_translations_to_resource_dict(translations, language):
    resources_key_list = list(resources[DEFAULT_LANGUAGE].keys())
    language_dict = {language: {}}
    resources.update(language_dict)
    for key, translation in zip(resources_key_list, translations):
        resources[language][key] = translation.text


def start_translation():
    translator = Translator()
    languages_code_list = []

    for language in language_list:
        languages_code_list.append(language["value"])

    default_language_string_list = list(resources[DEFAULT_LANGUAGE].values())

    for language in languages_code_list:
        if language != DEFAULT_LANGUAGE:
            log.info(f"Loading resources for: {language}")
            translations = translator.translate(default_language_string_list, src=DEFAULT_LANGUAGE, dest=language)
            add_translations_to_resource_dict(translations, language)

