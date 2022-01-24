#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Exploring Alpha Vantage API and python wrapper 

@author: gregory
'''

from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time 

key_path = '/home/gregory/Spyder Projects/data_gathering/av_key.txt'

# single ticker extraction
ts = TimeSeries(key=open(key_path, 'r').read(), output_format='pandas')
data = ts.get_daily(symbol='EURUSD', outputsize='full')[0]  # grab OHLCV data and ignore metadata
data.columns = data.columns = ['open','high','low','close','volume']  # rename columns
data = data.iloc[::-1]  # reverse dataframe since with AV, the data populates from the most recent and backwards



# multiple ticker extraction
all_tickers = ["AAPL","MSFT","CSCO","AMZN","GOOG","FB"]
close_prices = pd.DataFrame()
api_call_count = 0  # to handle API frequency limit   
# initiate timeseries with key
ts = TimeSeries(key=open(key_path,'r').read(), output_format='pandas')

start_time = time.time()  # to time the loop
for ticker in all_tickers:
    data = ts.get_intraday(symbol=ticker,interval='1min', outputsize='compact')[0]
    api_call_count+=1  # increase api call count by 1
    data.columns = ["open","high","low","close","volume"]
    data = data.iloc[::-1]
    close_prices[ticker] = data["close"]  # append to dataframe
    if api_call_count == 5:
        api_call_count = 0
        time.sleep(60 - ((time.time() - start_time) % 60.0))  # take present time and subtract from start time to get elapsed time


# extracting stock data (historical close price) for multiple stocks
all_tickers = ["AAPL","MSFT","CSCO","AMZN","GOOG",
               "FB","BA","MMM","XOM","NKE","INTC"]
close_prices_2 = pd.DataFrame()
api_call_count = 1
ts = TimeSeries(key=open(key_path,'r').read(), output_format='pandas')
start_time = time.time()
for ticker in all_tickers:
    data = ts.get_intraday(symbol=ticker,interval='1min', outputsize='compact')[0]
    api_call_count+=1
    data.columns = ["open","high","low","close","volume"]
    data = data.iloc[::-1]
    close_prices_2[ticker] = data["close"]
    if api_call_count==5:
        api_call_count = 1
        time.sleep(60 - ((time.time() - start_time) % 60.0))
        
time.time()
