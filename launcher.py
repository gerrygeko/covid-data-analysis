import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pandas import DataFrame

url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"


def load_csv(url):
    data_loaded = pd.read_csv(url)
    return data_loaded


def create_time_plot_total_numbers(data):
    df = DataFrame(data, columns=['data', 'deceduti', 'dimessi_guariti'])
    # figure variable can be used later to save the image of the plot
    figure, axis = plt.subplots(figsize=(11, 5))
    df_formatted = pd.to_datetime(df['data'])

    axis.plot(df_formatted, df['deceduti'], label='Deceduti')
    axis.plot(df_formatted, df['dimessi_guariti'], label='Dimessi/Guariti')

    set_labels_and_title_for_axis(axis, x_name='Time', y_name='N° of People', title='COVID-19')

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


def create_time_plot_relative_numbers(data):
    df = DataFrame(data, columns=['data', 'nuovi_positivi'])
    # figure variable can be used later to save the image of the plot
    figure, axis = plt.subplots(figsize=(11, 5))
    df_formatted = pd.to_datetime(df['data'])
    axis.plot(df_formatted, df['nuovi_positivi'], label='Nuovi Positivi')

    set_labels_and_title_for_axis(axis, x_name='Time', y_name='N° of People', title='COVID-19')

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


def set_labels_and_title_for_axis(axis, x_name="X axis", y_name="Y axis", title="Title"):
    axis.set_xlabel(x_name)
    axis.set_ylabel(y_name)
    axis.set_title(title)


if __name__ == '__main__':
    print("Hello world!")
    national_data = load_csv(url_csv_national_data)
    create_time_plot_relative_numbers(national_data)
    create_time_plot_total_numbers(national_data)
    plt.show()
