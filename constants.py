import logger

DEFAULT_LANGUAGE = "IT"


class LocaleLanguage:

    def __init__(self, language):
        self.language = language


RESOURCES = dict(
    denominazione_regione=dict(IT='Regione', EN='Region'),
    ricoverati_con_sintomi='Ricoverati con sintomi',
    terapia_intensiva='Terapia intensiva',
    totale_ospedalizzati='Totale ospedalizzati',
    isolamento_domiciliare='Isolamento domiciliare',
    totale_positivi='Casi attivi',
    variazione_totale_positivi='Variazione totale positivi',
    nuovi_positivi=dict(IT='Nuovi positivi', EN='New positives'),
    dimessi_guariti='Dimessi/Guariti',
    deceduti='Decessi',
    casi_da_sospetto_diagnostico='Casi Positivi identificati dal Sospetto Diagnostico',
    casi_da_screening='Casi Positivi accertati da Screening',
    totale_casi='Totale casi',
    tamponi='Tamponi effettuati',
    casi_testati='Casi Testati',
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
