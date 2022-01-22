#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script demonstrates the technical_indicators package

@author: gregory
"""
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
from technical_indicators import ta

# get data
data = yf.download('AAPL', period='1y', interval='1d')
prices = data['Adj Close']
high = data['High']
low = data['Low']
volume = data['Volume']

def main():
    
    # MACD implementation
    df_macd = data.copy()
    df_macd['MACD'], df_macd['signal'] = ta.macd_signal_line(prices)
    df_macd.dropna(inplace=True)
    print(df_macd)
    
    # ROC
    df_roc = data.copy()
    df_roc['ROC'] = ta.roc(prices, 14)
    df_roc.dropna(inplace=True)
    print(df_roc)
    
    # RSI
    df_rsi = data.copy()
    df_rsi['RS'], df_rsi['RSI'] = ta.rs_rsi(prices, 14)
    df_rsi.dropna(inplace=True)
    print(df_rsi)
    
    # Bollinger Bands
    df_bb = data.copy()
    df_bb['sma'],df_bb['upper'], df_bb['lower'] = ta.bollinger_band(prices)
    df_bb.dropna(inplace=True)
    print(df_bb)
    
    # Average true range
    df_atr = data.copy()
    df_atr['ATR'] = ta.atr(prices, high, low)
    df_atr.dropna(inplace=True)
    print(df_atr)
    
    # Average directional index
    df_adx = data.copy()
    df_adx['DI+'], df_adx['DI-'], df_adx['ADX'] = ta.adx(prices, high, low)
    df_adx.dropna(inplace=True)
    print(df_adx)
    
    # On balance volume
    df_obv = data.copy()
    df_obv['OBV'] = ta.obv(prices, volume)
    df_obv.dropna(inplace=True)
    print(df_obv)
    
    # Slope in a chart
    df_slope = data.copy()
    df_slope['slope'] = ta.slope(prices)
    df_slope.dropna(inplace=True)
    print(df_slope)
    
    # Renko
    df = data.copy()
    renko_df = ta.renko(data)
    print(renko_df)
    
    
if __name__ == '__main__':
    main()