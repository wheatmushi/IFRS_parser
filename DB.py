import sqlite3
import pandas as pd
import macrotrends_data


class DB:
    def __init__(self):
        self.connection = sqlite3.connect('metrics.db')
        self.cursor = self.connection.cursor()

    def update(self, tickers, metrics):
        if type(tickers) is str:
            tickers = (tickers,)
        for ticker in tickers:
            table = macrotrends_data.get_combined_quarterly_data(ticker, metrics)
            table.to_sql(ticker, con=self.connection, if_exists='replace', index=True)
        print('DB updated')

    def read(self, ticker, metric='*'):
        return pd.read_sql("SELECT {} FROM {}".format(metric, ticker), self.connection)
