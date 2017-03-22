import requests
import re
import pandas as pd
from datetime import datetime


# TODO: get opening, min and max prices from STOCK_URL

GLOBAL_URL = 'http://pregao-online.bmfbovespa.com.br/Cotacoes.aspx'
STOCK_URL = ('http://pregao-online.bmfbovespa.com.br/'
             'Noticias.aspx?Papel={stock_code}')


def get_stock_listing(url=GLOBAL_URL):
    "fetches stock listings and returns a pandas.Dataframe"

    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()

    stock_listing_dataframes = pd.read_html(
        response.text,
        attrs={'id': (lambda x: 'GrdCarteiraIndice' in x)},
        header=0,
        index_col=0,
        converters={
            # stock name
            1: (lambda x: re.sub(' +', ' ', x)),

            # price
            2: (lambda x: int(x)/100),

            # oscilation
            3: (lambda x: int(x)/100),

            # datetime
            4: parse_date,
        }
    )

    result_df, = stock_listing_dataframes  # unpack dataframe
    return result_df.iloc[:, :-1]  # selects all but the last column


def parse_date(value):
    "helper function for parsing dates"
    # value contains no info about current year
    bad_date = datetime.strptime(value, '%d/%m - %H:%M')

    day = bad_date.day
    month = bad_date.month
    hour = bad_date.hour
    minute = bad_date.minute

    good_date = datetime(
        year=datetime.now().year,
        month=month,
        day=day,
        hour=hour,
        minute=minute
    )

    return good_date


if __name__ == '__main__':
    "writes a timestamped csv with stock data"
    df = get_stock_listing()
    filename = datetime.now().isoformat() + '.csv'
    df.to_csv(filename)
