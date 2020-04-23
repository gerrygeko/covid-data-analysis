import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    axis.plot(df_formatted, df['deceduti'], label='Deceduti')
    axis.plot(df_formatted, df['dimessi_guariti'], label='Dimessi/Guariti')
    axis.set_xlabel('Time')
    axis.set_ylabel('N° of People')
    axis.set_title('COVID-19')
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    axis.xaxis.set_minor_formatter(mdates.DateFormatter("%d-%b"))
    axis.grid(True)
    axis.legend()
    plt.show()


if __name__ == '__main__':
    print("Hello world!")
    load_csv()
