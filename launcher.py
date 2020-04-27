import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import numpy as np

""" Column names for National Data
['data' 'stato' 'ricoverati_con_sintomi' 'terapia_intensiva'
 'totale_ospedalizzati' 'isolamento_domiciliare' 'totale_positivi'
 'variazione_totale_positivi' 'nuovi_positivi' 'dimessi_guariti'
 'deceduti' 'totale_casi' 'tamponi' 'casi_testati' 'note_it' 'note_en']
"""

url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/" \
                        "dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"

x_data = []
y_data = []


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


def create_time_plot_relative_numbers(df, axis, figure):
    df_formatted = pd.to_datetime(df['data'])
    line, = axis.plot(df_formatted, df['nuovi_positivi'], label='Nuovi Positivi')
    axis.plot(df_formatted, df['dimessi_giornalieri'], label='Dimessi Giornalieri')
    set_labels_and_title_for_axis(axis, y_name='N° of People')

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

    return line


def create_bar_graph_latest_number(df, axis):
    df_last_days = df.tail(7)
    df_formatted = pd.to_datetime(df_last_days['data'])
    # Convert the date to numbers so you can use floats to move around the bars and group them one next to the other
    date2num = mdates.date2num(df_formatted)

    width = 0.2  # size of the bar
    rects1 = axis.bar(date2num + 0.2, df_last_days['nuovi_positivi'], width, color='b', label='Positive Tests')
    rects2 = axis.bar(date2num + 0.4, df_last_days['tamponi_giornalieri'], width, color='r', label='Tests per day')

    autolabel_bars(rects1, axis)
    autolabel_bars(rects2, axis)

    set_labels_and_title_for_axis(axis, y_name='N° of People')

    dates = mdates.num2date(date2num)
    axis.set_xticklabels(dates)

    axis.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    # Customize the major grid
    axis.grid(which='major', linestyle='-', linewidth='0.5', color='grey')

    axis.legend(loc=2, prop={'size': 9})


def autolabel_bars(rects, axis):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        axis.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, -2),  # -2 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def set_labels_and_title_for_axis(axis, x_name=None, y_name=None, title=None):
    if x_name is not None: axis.set_xlabel(x_name)
    if y_name is not None: axis.set_ylabel(y_name)
    if title is not None: axis.set_title(title)


def configure_mainplot_with_subplots():
    figure, axis = plt.subplots(2, 2)
    # Set distance of the subplots using margin distance with main plot area
    figure.subplots_adjust(left=0.08, right=0.96, bottom=0.1, top=0.9)
    figure.suptitle('COVID-19')
    # Set size of the window
    figure.set_figheight(8)
    figure.set_figwidth(15)
    # Set position of the window in the screen
    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry('+250+40')
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


# def init(axis):
#     axis.set_data([], [])


def func(i, national_data, axis):
    value_x = datetime.datetime.strptime(national_data.iloc[i]['data'], '%Y-%m-%dT%H:%M:%S')
    x_data.append(mdates.date2num(value_x))
    y_data.append(national_data.iloc[i]['nuovi_positivi'])
    axis.set_xdata(x_data)
    axis.set_ydata(y_data)
    return axis


def run_application():
    national_data = load_csv(url_csv_national_data)
    calculate_and_add_daily_variance_of_dimessi(national_data)
    calculate_and_add_daily_variance_of_tamponi(national_data)
    figure, ((axis_1, axis_2), (axis_3, axis_4)) = configure_mainplot_with_subplots()

    create_time_plot_total_numbers(national_data, axis_1)
    axis = create_time_plot_relative_numbers(national_data, axis_3, figure)
    create_bar_graph_latest_number(national_data, axis_2)
    create_bar_graph_latest_number(national_data, axis_4)
    animation = FuncAnimation(figure,
                              func=func,
                              fargs=(national_data, axis),
                              frames=len(national_data.index.tolist()) - 1,
                              interval=1)
    # Show the plot figure
    plt.show()


if __name__ == '__main__':
    run_application()
