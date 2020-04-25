import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num

""" Column names for National Data
['data' 'stato' 'ricoverati_con_sintomi' 'terapia_intensiva'
 'totale_ospedalizzati' 'isolamento_domiciliare' 'totale_positivi'
 'variazione_totale_positivi' 'nuovi_positivi' 'dimessi_guariti'
 'deceduti' 'totale_casi' 'tamponi' 'casi_testati' 'note_it' 'note_en']
"""

url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/" \
                        "dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"

def load_csv(url):
    data_loaded = pd.read_csv(url)
    return data_loaded

def create_time_plot_total_numbers(df, axis):
    df_formatted = pd.to_datetime(df['data'])
    axis.plot(df_formatted, df['deceduti'], label='Deceduti')
    axis.plot(df_formatted, df['dimessi_guariti'], label='Dimessi/Guariti')

    set_labels_and_title_for_axis(axis, y_name='N° of People')

    axis.minorticks_on()
    axis.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    # Customize the major grid
    axis.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    # Customize the minor grid
    axis.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
    axis.grid(True)
    axis.legend()


def create_time_plot_relative_numbers(df, axis):
    df_formatted = pd.to_datetime(df['data'])
    axis.plot(df_formatted, df['nuovi_positivi'], label='Nuovi Positivi')
    axis.plot(df_formatted, df['dimessi_giornalieri'], label='Dimessi Giornalieri')

    set_labels_and_title_for_axis(axis, x_name='Time', y_name='N° of People')

    axis.minorticks_on()
    # Set intervals and format on the x axis
    axis.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    # Customize the major grid
    axis.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    # Customize the minor grid
    axis.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
    axis.grid(True)
    axis.legend()


def create_bar_graph_latest_number(df, axis):
    df_last_days = df.tail(7)
    df_formatted = pd.to_datetime(df_last_days['data'])
    x = date2num(df_formatted)
    width = 0.2  # size of the bar
    axis.bar(x, df_last_days['nuovi_positivi'], width, color='b', label='Positive Test per day')
    axis.bar(x + 0.2, df_last_days['tamponi_giornalieri'], width, color='r', label='Testing per day')
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    axis.xaxis_date()
    axis.autoscale(tight=True)
    axis.set_xticklabels(df_formatted)
    plt.legend(loc='upper left', fontsize=16)
    plt.show()

def set_labels_and_title_for_axis(axis, x_name=None, y_name=None, title=None):
    if x_name is not None: axis.set_xlabel(x_name)
    if y_name is not None: axis.set_ylabel(y_name)
    if title is not None: axis.set_title(title)


def configure_mainplot_with_subplots():
    figure, axis = plt.subplots(2, 2, sharex=True)
    figure.suptitle('COVID-19')
    # Set size of the window
    figure.set_figheight(7)
    figure.set_figwidth(11)
    # Set position of the window in the screen
    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry('+450+100')
    ########################################
    figure.subplots_adjust(bottom=0.3)
    figure.text(0.1, 0.10, 'Esempio stampa')
    ###########################################
    return figure, axis


def calculate_and_add_daily_variance_of_dimessi(national_data):
    list_dimessi = national_data['dimessi_guariti'].values.tolist()
    list_dimessi_giornalieri = []
    for i in range(len(list_dimessi)):
        if i == 0:
            list_dimessi_giornalieri.append(0)
        else:
            list_dimessi_giornalieri.append(list_dimessi[i] - list_dimessi[i - 1])
    national_data['dimessi_giornalieri'] = list_dimessi_giornalieri

def calculate_and_add_daily_variance_of_tamponi(national_data):
    list_tamponi = national_data['tamponi'].values.tolist()
    list_tamponi_giornalieri = []
    for i in range(len(list_tamponi)):
        if i == 0:
            list_tamponi_giornalieri.append(0)
        else:
            list_tamponi_giornalieri.append(list_tamponi[i] - list_tamponi[i - 1])
    national_data['tamponi_giornalieri'] = list_tamponi_giornalieri


def run_application():
    national_data = load_csv(url_csv_national_data)
    calculate_and_add_daily_variance_of_dimessi(national_data)
    calculate_and_add_daily_variance_of_tamponi(national_data)
    figure, ((axis_1, axis_2),(axis_2, axis_3)) = configure_mainplot_with_subplots()
    create_time_plot_total_numbers(national_data, axis_1)
    create_time_plot_relative_numbers(national_data, axis_2)
    create_bar_graph_latest_number(national_data, axis_3)
    plt.show()


if __name__ == '__main__':
    run_application()
