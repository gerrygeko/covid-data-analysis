import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pandas import DataFrame



df = DataFrame
url_csv_national_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"


def load_csv():
    #data_from_requests = requests.get(url_csv_national_data).content
    data = pd.read_csv(url_csv_national_data)
    print(data.head())
    df = DataFrame(data, columns=['data', 'nuovi_positivi', 'deceduti', 'dimessi_guariti'])
    #df['data'] = pd.to_datetime(df['data'])
    #df['data'] = df['data'].dt.strftime('%d-%m')
    fig, ax = plt.subplots(figsize=(11, 5))
    t = pd.to_datetime(df['data'])
    ax.plot(t, df['nuovi_positivi'], label='Nuovi Positivi')
    ax.plot(t, df['deceduti'], label='Deceduti')
    ax.plot(t, df['dimessi_guariti'], label='Dimessi/Guariti')
    ax.set_xlabel('Data')
    ax.set_ylabel('N° of People')
    ax.set_title('COVID-19')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d-%b"))
    ax.grid(True)
    ax.legend()
    plt.show()
    #ax.tick_params(labelsize=10)

if __name__ == '__main__':
    print("Hello world!")
    load_csv()
