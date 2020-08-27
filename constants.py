import logger

DEFAULT_LANGUAGE = "IT"


class LocaleLanguage:

    def __init__(self, language):
        self.language = language


RESOURCES = dict(
    denominazione_regione=dict(IT='Regione', EN='Region'),
    ricoverati_con_sintomi=dict(IT='Ricoverati con sintomi', EN='Hospitalized with sympthoms'),
    terapia_intensiva=dict(IT='Terapia intensiva', EN='Intensive care'),
    totale_ospedalizzati=dict(IT='Totale ospedalizzati', EN='Total hospitalized'),
    isolamento_domiciliare='Isolamento domiciliare',
    totale_positivi=dict(IT='Casi attivi', EN='Active cases'),
    variazione_totale_positivi=dict(IT='Variazione totale positivi', EN='Variation total positives'),
    nuovi_positivi=dict(IT='Nuovi positivi', EN='New positives'),
    dimessi_guariti=dict(IT='Dimessi/Guariti', EN='Discharged/Cured'),
    deceduti=dict(IT='Decessi', EN='Deaths'),
    casi_da_sospetto_diagnostico='Casi Positivi identificati dal Sospetto Diagnostico',
    casi_da_screening='Casi Positivi accertati da Screening',
    totale_casi=dict(IT='Totale casi', EN='Total cases'),
    tamponi=dict(IT='Tamponi effettuati', EN='Tests done'),
    casi_testati=dict(IT='Casi Testati', EN='Tested Cases'),
    header_last_update=dict(IT='Dati Aggiornati al: %d/%m/%Y %H:%M', EN='Last Update at: %d/%m/%Y %H:%M')
)

log = logger.get_logger()
locale_language = LocaleLanguage(DEFAULT_LANGUAGE)


def load_resource(name):
    if name not in RESOURCES.keys():
        raise KeyError(f"The resource you are trying to load is not present. Resource: {name}")
    value = RESOURCES[name]
    # Temporary check to not fail when loading a resource without any translation ()
    if isinstance(value, dict):
        return value[locale_language.language]
    return value
