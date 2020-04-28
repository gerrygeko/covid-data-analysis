import datetime
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

""" Column names for National Data
['data' 'stato' 'ricoverati_con_sintomi' 'terapia_intensiva'
 'totale_ospedalizzati' 'isolamento_domiciliare' 'totale_positivi'
 'variazione_totale_positivi' 'nuovi_positivi' 'dimessi_guariti'
 'deceduti' 'totale_casi' 'tamponi' 'casi_testati' 'note_it' 'note_en']
"""

url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/" \
                        "dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"

FRAME_INTERVAL = 25

x_animation_data = defaultdict(list)
y_animation_data = defaultdict(list)


def load_csv(url):
    data_loaded = pd.read_csv(url)
    return data_loaded


def create_time_plot(df, axis, field_and_label_tuple_list: list):
    df_formatted = pd.to_datetime(df['data'])
    lines_list = []
    for field, label in field_and_label_tuple_list:
        line, = axis.plot(df_formatted, df[field], label=label)
        lines_list.append((line, field))
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

    return lines_list


def create_bar_graph_latest_number(df, axis):
    df_last_days = df.tail(7)
    df_formatted = pd.to_datetime(df_last_days['data'])
    # Convert the date to numbers so you can use floats to move around the bars and group them one next to the other
    date2num = mdates.date2num(df_formatted)

    width = 0.2  # size of the bar
    rects1 = axis.bar(date2num + 0.2, df_last_days['nuovi_positivi'], width, color='b', label='Positive Tests')
    rects2 = axis.bar(date2num + 0.4, df_last_days['tamponi_giornalieri'], width, color='r', label='Tests per day')

    auto_label_bars(rects1, axis)
    auto_label_bars(rects2, axis)

    set_labels_and_title_for_axis(axis, y_name='N° of People')

    dates = mdates.num2date(date2num)
    axis.set_xticklabels(dates)

    axis.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    # Customize the major grid
    axis.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    #

    axis.legend(loc=2, prop={'size': 9})


def auto_label_bars(rects, axis):
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


def animation_init(axis):
    axis.set_data([], [])
    return axis,


# TODO: Read this page to make animation for more lines:
# https://stackoverflow.com/questions/23049762/matplotlib-multiple-animate-multiple-lines
def animation_func(i, national_data, line_tuple):
    """
    :param i: Index of the frame for which the animation is iterating
    :param national_data: DataFrame that contain all the data
    :param line_tuple: Tuple that contain the Line2D and the name of the field in the DataFrame associated to the line
    :return: Line2D printed so far
    """
    line = line_tuple[0]
    field = line_tuple[1]
    value_x = datetime.datetime.strptime(national_data.iloc[i]['data'], '%Y-%m-%dT%H:%M:%S')
    x_animation_data[field].append(mdates.date2num(value_x))
    y_animation_data[field].append(national_data.iloc[i][field])
    line.set_xdata(x_animation_data[field])
    line.set_ydata(y_animation_data[field])
    return line,


def run_application():
    national_data = load_csv(url_csv_national_data)
    calculate_and_add_daily_variance_of_dimessi(national_data)
    calculate_and_add_daily_variance_of_tamponi(national_data)
    figure, ((axis_top_left, axis_top_right), (axis_bottom_left, axis_bottom_right)) = configure_mainplot_with_subplots()

    lines_list_top_left = create_time_plot(national_data, axis_top_left,
                                           [('deceduti', 'Decessi'), ('dimessi_guariti', 'Dimessi Guariti')])
    lines_list_bottom_left = create_time_plot(national_data, axis_bottom_left,
                                              [('nuovi_positivi', 'Nuovi Positivi'),
                                               ('dimessi_giornalieri', 'Dimessi Giornalieri')])
    create_bar_graph_latest_number(national_data, axis_top_right)
    create_bar_graph_latest_number(national_data, axis_bottom_right)
    animation = FuncAnimation(figure, func=animation_func, fargs=(national_data, lines_list_bottom_left[0]),
                              frames=len(national_data.index.tolist()),
                              interval=FRAME_INTERVAL, blit=True, repeat=False)
    animation = FuncAnimation(figure, func=animation_func, fargs=(national_data, lines_list_top_left[1]),
                              frames=len(national_data.index.tolist()),
                              interval=FRAME_INTERVAL, blit=True, repeat=False)

    # Show the plot figure
    plt.show()


if __name__ == '__main__':
    run_application()
