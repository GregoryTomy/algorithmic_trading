#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Exploring financial data gathering through yahoofinancials. 

@author: gregory
'''

from yahoofinancials import YahooFinancials
import pandas as pd
import datetime as dt

ticker = 'MSFT'
yahoo_fin = YahooFinancials(ticker)

data = yahoo_fin.get_historical_price_data('2018-04-24', '2020-04-24', 'daily')
# provides data in JSON (think nested dictionaries)

# extracting stock data and parsing JSON
tickers = ['AAPL','MSFT','CSCO','AMZN','INTC']

close_prices = pd.DataFrame()
end_date = (dt.date.today()).strftime('%Y-%m-%d')  # convert datetime object to string
start_date = (dt.date.today()-dt.timedelta(1825)).strftime('%Y-%m-%d')

for ticker in tickers:
    yahoo_fin = YahooFinancials(ticker)
    json_obj = yahoo_fin.get_historical_price_data(start_date,end_date,'daily')
    ohlv = json_obj[ticker]['prices']  # store prices dictionary
    temp = pd.DataFrame(ohlv)[['formatted_date','adjclose']]  # create temp dataframe with relevant columns
    temp.set_index('formatted_date',inplace=True)
    temp.dropna(inplace=True)
    close_prices[ticker] = temp['adjclose']  # append series to close prices data frame
    

# this method is a bit more invovled than yfinance but is good to have in the backpocket
