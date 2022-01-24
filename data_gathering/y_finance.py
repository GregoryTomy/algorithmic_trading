# -*- coding: utf-8 -*-
"""
Exploring financial data gathering through yfinance.
@author: gregory
"""

import datetime as dt
import yfinance as yf
import pandas as pd

# basics
data = yf.download('MSFT', period='1mo', interval='5m')


# data for multiple tickers
stocks = ['AMZN', 'MSFT', 'INTC', 'GOOG', 'INFY.NS', '3988.HK']

# start date
start = dt.datetime.today() - dt.timedelta(30)  # date 30 days ago
end = dt.datetime.today()  # today's date

closing_price = pd.DataFrame()  # empty dataframe to be filled with closing prices

# looping over tickers and filling the dataframe with close prices
for ticker in stocks:
    closing_price[ticker] = yf.download(ticker, start, end)['Adj Close']
    
# store OHLCV in dictionary 
ohlcv_data = {}

for ticker in stocks:
    ohlcv_data[ticker] = yf.download(ticker, start, end)