import logger
from googletrans import Translator

DEFAULT_LANGUAGE = "IT"
temp = []
key_to_list = []
value_to_list = []


class LocaleLanguage:

    def __init__(self, language):
        self.language = language


RESOURCES_ITA = dict(
    denominazione_regione='Regione',
    ricoverati_con_sintomi='Ricoverati con sintomi',
    terapia_intensiva='Terapia intensiva',
    totale_ospedalizzati='Totale ospedalizzati',
    isolamento_domiciliare='Isolamento domiciliare',
    totale_positivi='Casi attivi',
    variazione_totale_positivi='Variazione totale positivi',
    nuovi_positivi='Nuovi positivi',
    dimessi_guariti='Dimessi/Guariti',
    deceduti='Decessi',
    casi_da_sospetto_diagnostico='Casi Positivi identificati dal Sospetto Diagnostico',
    casi_da_screening='Casi Positivi accertati da Screening',
    totale_casi='Totale casi',
    tamponi='Tamponi effettuati',
    casi_testati='Casi Testati',
    nazione='Italia',
    header_last_update='Dati Aggiornati al: %d/%m/%Y %H:%M',
    label_titolo='Totale Dati Nazionali',
    label_tab_1='Analisi dei dati nazionali',
    label_tab_2='Analisi dei dati regionali',
    label_select_data='Seleziona il dato da analizzare:',
    label_select_multiregion='Seleziona una o più regioni italiane da confrontare:',
    label_select_region='Seleziona la regione italiana da analizzare:',
    label_data_picco_max='Data Picco massimo',
    label_valore_picco_max='Picco massimo',
    label_media_contagi='Media contagi',
    label_casi_attivi='Casi Attivi per giorno:',
    label_news='News Scienza - Italia',
    label_contact_us='Contattaci',
    label_last_update='Ultimo Aggiornamento:',
    label_map='N° casi ogni 100K abitanti',
    label_top_ten='Top 10 Regioni:',
    label_hover_map='per regione (ogni 100K abitanti)',
    label_table_details='Dati di dettaglio',
    label_persone='Persone',

)


log = logger.get_logger()
locale_language = LocaleLanguage(DEFAULT_LANGUAGE)


def translate_my_dict(my_dict):
    translator = Translator()
    for key, value in my_dict.items():
        value_translated = translator.translate(value, src=DEFAULT_LANGUAGE, dest=locale_language.language).text
        #temp = [key, value_translated]
        key_to_list.append(key)
        value_to_list.append(value_translated)
    dict_translated = dict(zip(key_to_list, value_to_list))
    return dict_translated


def load_resource(name):
    if name not in RESOURCES_ITA.keys():
        raise KeyError(f"The resource you are trying to load is not present. Resource: {name}")
    value = translate_my_dict(RESOURCES_ITA)[name]
    # Temporary check to not fail when loading a resource without any translation ()
    if isinstance(value, dict):
        return value[locale_language.language]
    return value
