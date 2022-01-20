from pygoogletranslation import Translator

import logger
import time
from constants import DEFAULT_LANGUAGE

language_list = [{'label': 'Italiano', 'value': 'it'},
                 {'label': 'English', 'value': 'en'},
                 {'label': 'Dutch', 'value': 'nl'},
                 {'label': 'German', 'value': 'de'},
                 {'label': 'French', 'value': 'fr'},
                 {'label': 'Spanish', 'value': 'es'},
                 {'label': 'Portuguese', 'value': 'pt'}
                 ]

standard_colors = dict(light_blue="rgb(123, 199, 255)",
                       dark_blue="rgb(4, 74, 152)",
                       pink="rgb(244, 0, 161)",
                       aqua="rgb(0, 204, 153)",
                       azure="rgb(51, 133, 255)",
                       red="rgb(204, 51, 0)")


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
    'dimessi_guariti': 'Guariti',
    'deceduti': 'Decessi',
    'casi_da_sospetto_diagnostico': 'Casi Positivi identificati dal Sospetto Diagnostico',
    'casi_da_screening': 'Casi Positivi accertati da Screening',
    'totale_casi': 'Totale casi',
    'tamponi': 'Tamponi effettuati',
    'casi_testati': 'Casi Testati',
    'ratio_n_pos_tamponi': 'Rapporto Positivi / Tamponi',
    'pressure_ICU': 'Pressione terapie intensive',
    'nazione': 'Italia',
    'label_dati_italia': 'Totale Dati - Italia',
    'label_dati_mondo': 'Totale Dati - Mondo',
    'label_tab_1': 'Analisi dei dati nazionali',
    'label_tab_2': 'Analisi dei dati regionali',
    'label_tab_master_worldwide': 'Mondo',
    'label_tab_master_ita': 'Italia',
    'label_tab_master_ita_regions': 'Regioni Italiane',
    'label_tab_vaccines_italy': 'Tassi di vaccinazione Italia',
    'label_select_data': 'Seleziona il dato da analizzare:',
    'label_select_multiregion': 'Seleziona una o più regioni italiane da confrontare:',
    'label_select_multicountry': 'Seleziona uno o più Paesi da confrontare:',
    'label_select_region': 'Seleziona la regione italiana da analizzare:',
    'label_select_country': 'Paese:',
    'label_data_picco_max': 'Data Picco massimo',
    'label_valore_picco_max': 'Picco massimo',
    'label_media_contagi': 'Media contagi',
    'label_casi_attivi': 'Casi Attivi',
    'label_news': 'News Scienza - Italia',
    'label_contact_us': 'Contattaci',
    'header_last_update_world': 'Ultimo rilascio dati DataHub:',
    'header_last_update_italy': 'Ultimo rilascio dati Protezione Civile Italiana:',
    'header_last_update_vaccines_italy': 'Ultimo rilascio dati Ministero della Salute:',
    'label_last_news_update': 'Ultimo aggiornamento: ',
    'label_last_check_update': 'Ultimo controllo dati:',
    'label_map': 'N° casi ogni 100K abitanti',
    'label_top_ten': 'Top 10 Regioni:',
    'label_hover_map': 'per regione (ogni cento mila abitanti)',
    'label_hover_world_map': 'per nazione (ogni cento mila abitanti)',
    'label_persone': 'Persone',
    'vaccine_phase_1': 'Fase 1',
    'vaccine_phase_2': 'Fase 2',
    'vaccine_phase_3': 'Fase 3',
    'vaccine_phase_4': 'Fase 4',
    'label_credits': 'Crediti',
    'confirmed_worldwide_aggregate': 'Totale Casi',
    'recovered_worldwide_aggregate': 'Guariti',
    'deaths_worldwide_aggregate': 'Decessi',
    'increase_rate_worldwide_aggregate': 'Tasso di Crescita',
    'Country': 'Paese',
    'Confirmed': 'Confermati',
    'Recovered': 'Guariti',
    'Deaths': 'Decessi',
    'New Confirmed': 'Nuovi Positivi',
    'New Recovered': 'Nuovi Guariti',
    'New Deaths': 'Nuovi Decessi',
    'Active_cases': 'Casi Attivi',
    'administered_doses': 'Dosi Somministrate',
    'delivered_doses': 'Dosi Consegnate',
    'total_people_vaccinated': 'Totale Persone Vaccinate (over 5)',
    'percentage_vaccinated_population': 'Percentuale Platea Vaccinati (over 5)',
    'administrations_by_age': 'Somministrazioni per fasce di età',
    'administrations_by_day': 'Somministrazioni giornaliere',
    'total_administrations': 'Somministrazioni totali',
    'percentage_administrations': 'Percentuale somministrazione',
    'filter_by': 'Filtra per:',
    'total_vaccines': 'Totale',
    'suppliers': 'Fornitori',
    'sex': 'Sesso',
    'doses': 'Dosi',
    'doses_first_second': 'Prima e seconda dose',
    'additional_doses': 'Dosi addizionali',
    'sex_male': 'Maschi',
    'sex_female': 'Femmine',
    'age_60_69': 'Età 60-69',
    'age_70_79': 'Età 70-79',
    'over_80': 'Over 80',
    'first_vaccine_dose': 'Prima dose',
    'second_vaccine_dose': 'Seconda dose',
    'previous_infection_vaccine_dose': 'Dose unica per pregressa infezione',
    'additional_vaccine_dose': 'Dose aggiuntiva',
    'booster_vaccine_dose': 'Dose richiamo',
    'daily_administrations': ' Somministrazioni',
    'rolling_average_7_days': 'Media mobile a 7 giorni',
    'string_italy_herd_immunity': 'Data raggiungimento 90% popolazione vaccinabile: ',
    'unique_visitors': 'Visitatori unici: ',
    'test_update': 'Test di notifica',
    'notification_text_repo_pandemic_data_ita_updated': '"Nuovi dati giornalieri dalla Protezione Civile Italiana, '
                                                        'controlla gli aggiornamenti!"',
    'notification_text_repo_pandemic_data_world_updated': 'Nuovi dati mondiali sui contagi Covid-19, controlla gli '
                                                          'aggiornamenti!',
    'notification_text_repo_vaccines_data_ita_updated': 'Nuovi dati sulla situazione vaccini in Italia, controlla gli '
                                                        'aggiornamenti! ',
    'notification_text_daily_italian_update': "Update! Oggi {} nuovi positivi in Italia!"
}
}

log = logger.get_logger()
locale_language = LocaleLanguage(DEFAULT_LANGUAGE)


def load_resource(name):
    try:
        resource = find_resource(name)
    except KeyError:
        resource = "Label not available"
    return resource


def find_resource(name):
    if locale_language.language not in resources.keys():
        raise KeyError(
            f"The language selected is not loaded: {locale_language.language}. Maybe you are running in debug mode ")
    if name not in resources[locale_language.language].keys():
        raise KeyError(f"The resource you are trying to load is not present. Resource: {name}")
    return resources[locale_language.language][name]


def create_resource_dict_for_languages(resource_key, is_debug, *args):
    if is_debug:
        # If in debug mode we pass the italian resource as an english resource,
        # because the OneSignal API require 'en' to be default, but in debug we have only 'IT' resources.
        return {"en": resources[DEFAULT_LANGUAGE][resource_key].format(*args)}
    else:
        languages = [language_dict['value'] for language_dict in language_list]
    resource_dict = {language.lower(): resources[language][resource_key].format(*args) for language in languages}
    return resource_dict


def add_translations_to_resource_dict(translations, language):
    resources_key_list = list(resources[DEFAULT_LANGUAGE].keys())
    language_dict = {language: {}}
    resources.update(language_dict)
    for key, translation in zip(resources_key_list, translations):
        resources[language][key] = translation.text


def start_translation():
    translator = Translator()
    languages_code_list = []
    log.info(f"Start of translation service")
    for language in language_list:
        languages_code_list.append(language["value"])

    default_language_string_list = list(resources[DEFAULT_LANGUAGE].values())

    for language in languages_code_list:
        if language != DEFAULT_LANGUAGE:
            start_time = time.time()
            translations = translator.translate(default_language_string_list, src=DEFAULT_LANGUAGE, dest=language)
            add_translations_to_resource_dict(translations, language)
            log.info(f"The {language} translation has taken {time.time() - start_time} seconds")
            log.info(f"End of loading for resources for: {language}")

    log.info(f"Translation for all languages is completed")
