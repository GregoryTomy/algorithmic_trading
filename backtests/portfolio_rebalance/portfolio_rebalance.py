#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 11:24:00 2022

@author: gregory
"""

import matplotlib.pyplot as plt
from technical_indicators import kpi
import yfinance as yf
import datetime as dt
import copy
import pandas as pd
import pickle

# # Download historical data (monthly) for DJI constituent stocks
# tickers = ['MMM','AXP', 'AAPL','BA','CAT','CVX','CSCO','KO', 'DOW', 'XOM','GS',
#            'HD','IBM','INTC','JNJ','JPM','MCD','MRK','MSFT','NKE','PFE','PG',
#            'TRV','UTX','UNH','VZ','V','WMT','DIS', 'WBA']

# # dictionary with ohlc monthly value for each stock  
# ohlc_mon = {} 
# start = dt.datetime.today()-dt.timedelta(3650)
# end = dt.datetime.today()

# # loop over tickers and get OHLC data
# for ticker in tickers:
#     ohlc_mon[ticker] = yf.download(ticker,start,end,interval='1mo')
#     ohlc_mon[ticker].dropna(inplace=True,how="all")
    

# # remove incomplete/corrupted data 
# ohlc_mon.pop('UTX', None)
# ohlc_mon.pop('DOW', None)

# # save data as pickle file
# f = open('dji_ohlc_20220125.pkl', 'wb')
# pickle.dump(ohlc_mon, f)
# f.close()

# load data dictionary from pickle
infile = open('dji_ohlc_20220125.pkl', 'rb')
ohlc_mon = pickle.load(infile)
infile.close()

# update ticker list
tickers = ohlc_mon.keys()

################ buy and holding DJI index tracking ETF ################

# data for past 5 years
# dia = yf.download("DIA",dt.date.today()-dt.timedelta(1900),dt.date.today(),interval='1mo')
# dia.dropna(inplace=True)
# dia.to_csv('dia_ohlc_20220125.csv')

dia = pd.read_csv('dia_ohlc_20220125.csv')

prices_dia = dia['Adj Close']
returns_dia = prices_dia.pct_change()

################ portfolio rebalance strategy ################

# deep copy to avoid tampering with the orig data dictionary 
ohlc_dict = copy.deepcopy(ohlc_mon)

# get dataframe with stock returns
return_df = pd.DataFrame()

for ticker in tickers:
    print(f'Calculating monthly return for {ticker}')
    return_df[ticker] = ohlc_dict[ticker]['Adj Close'].pct_change()

# drop last row
return_df.drop(return_df.tail(1).index, inplace=True)
return_df.to_csv('test.csv')


def portfolio_rebalance(df, m, n):
    """Backtests a portfolio rebalance strategy. Long only.
    :param df: dataframe with returns for stocks in the rebalance pool
    :param m: number of stocks to select for the portfolio
    :param n: number of underperforming stocks removed every rebalance period
    :return: portfolio dataframe with returns
    """

    # set portfolio and monthly return lists
    portfolio = []  # per rebalance period portfolio
    portfolios = []  # list of portfolio lists
    new = []    # list of new stocks selected each rebalance period
    relegated = [0]  # list of underperforming stocks removed each rebalance period
    monthly_ret = [0]  # monthly returns of portfolio

    for i in range(1,len(df)):
        # select n underperforming stocks if portfolio is initalized
        if len(portfolio) > 0:
            # record average monthly return for portfolio
            monthly_ret.append(df[portfolio].iloc[i,:].mean())
            # select n underperforming stocks from the portfolio
            bad_stocks = df[portfolio].iloc[i, :].sort_values(ascending=True)[:n].index.values.tolist()
            relegated.append(bad_stocks)
            # remove underperforming stocks from portfolio
            portfolio = [s for s in portfolio if s not in bad_stocks]
    
        # stocks to fill in portfolio
        fill = m - len(portfolio)
        # get the top performing stocks to fill
        new_picks = df.iloc[i, :].sort_values(ascending=False)[:fill].index.values.tolist()
        new.append(new_picks)
        portfolio = portfolio + new_picks
        # record portfolio composition at each month
        portfolios.append(portfolio)
    
    port_rebal_df = pd.DataFrame({'portfolio': portfolios, 'new_picks': new,
                                  'relegated': relegated, 
                                  'monthly_performance': monthly_ret},
                                  index=df.index.delete(0))
    
    return port_rebal_df

results = portfolio_rebalance(return_df, 10, 3)

# saves results
results.to_csv('portfolio_rebal_df.csv')



################ Performance metrics and Comparison ################

# key performance indicators for benchmark
kpi.cagr(returns_dia,12) 
# rf has 10 year treasury yield
kpi.sharpe(returns_dia, 0.0175, 12, 12)
kpi.max_drawdown(returns_dia)

# key performance indicators for strategy
returns_strat = results['monthly_performance']

kpi.cagr(returns_strat,12) 
# rf has 10 year treasury yield
kpi.sharpe(returns_strat, 0.0175, 12, 12)
kpi.max_drawdown(returns_strat)


# Summary: For this particular stratergy, our returns are slightly lower than
# the buy and hold, but the sharpe is higher due to reduced volatility. Max drawdown 
# is considerably less. Please note that we have not modeled any trade slippage so our
# results are overestimating.
