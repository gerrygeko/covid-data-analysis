import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from pandas import DataFrame

url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"

def load_csv():
    data = pd.read_csv(url_csv_national_data)
    print(data.head())
    df = DataFrame(data, columns=['data', 'nuovi_positivi', 'deceduti', 'dimessi_guariti'])
    # figure variable can be used later to save the image of the plot
    figure, axis = plt.subplots(figsize=(11, 5))
    df_formatted = pd.to_datetime(df['data'])
    axis.plot(df_formatted, df['nuovi_positivi'], label='Nuovi Positivi')
    # axis.plot(df_formatted, df['deceduti'], label='Deceduti')
    # axis.plot(df_formatted, df['dimessi_guariti'], label='Dimessi/Guariti')
    axis.set_xlabel('Time')
    axis.set_ylabel('N° of People')
    axis.set_title('COVID-19')
    axis.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    # axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    # axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d-%b"))
    axis.minorticks_on()
    # Customize the major grid
    axis.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    # Customize the minor grid
    axis.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
    axis.legend()
    axis.grid(True)

    figure, axis2 = plt.subplots(figsize=(11, 5))
    df_formatted = pd.to_datetime(df['data'])
    axis2.plot(df_formatted, df['deceduti'], label='Deceduti')
    axis2.plot(df_formatted, df['dimessi_guariti'], label='Dimessi/Guariti')
    axis2.set_xlabel('Time')
    axis2.set_ylabel('N° of People')
    axis2.set_title('COVID-19')
    axis2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    axis2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    axis2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    # axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    # axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d-%b"))
    axis2.minorticks_on()
    # Customize the major grid
    axis2.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    # Customize the minor grid
    axis2.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
    axis2.grid(True)
    axis2.legend()
    plt.show()

if __name__ == '__main__':
    print("Hello world!")
    load_csv()
