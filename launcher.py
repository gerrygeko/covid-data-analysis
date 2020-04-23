import pandas as pd
import requests
from pandas import DataFrame

df = DataFrame
url_csv_national_data = "https://github.com/pcm-dpc/COVID-19/blob/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"


def load_csv():
    #data_from_requests = requests.get(url_csv_national_data).content
    data = pd.read_csv(url_csv_national_data)
    #print(data)


if __name__ == '__main__':
    print("Hello world!")
    load_csv()
