import sqlite3
import pandas as pd
import macrotrends_data
import time


class DB:
    def __init__(self):
        self.connection = sqlite3.connect('metrics.db')
        self.cursor = self.connection.cursor()

    def update(self, tickers=None, metrics=None):
        if not tickers:
            tickers = self.get_list_of_tables()
        if type(tickers) is str:
            tickers = (tickers,)
        if not metrics:
            t = self.read(tickers[0])
            metrics = t.columns.values
        for ticker in tickers:
            print('updating {} data...'.format(ticker.upper()))
            table = macrotrends_data.get_combined_quarterly_data(ticker, metrics)
            table.to_sql(ticker, con=self.connection, if_exists='replace', index=True)
            time.sleep(5)
        print('DB updated')

    def read(self, ticker, metric='*'):
        return pd.read_sql("SELECT {} FROM {}".format(metric, ticker), self.connection, index_col='date')

    def get_list_of_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = self.cursor.fetchall()
        return [i for t in res for i in t]

    def execute(self, request):
        return self.cursor.execute(request)
