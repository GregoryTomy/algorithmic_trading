#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains the technical indicators developed in conjunction with
learning technical analysis.
@author: gregory
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import numpy as np
from stocktrends import Renko


def macd_signal_line(prices, fast_win=12, slow_win=26, signal_win=9):
    """
    Get MACD and signal line
    :param prices: series with adjusted prices
    :param fast_win: fast window period
    :param slow_win: slow window period
    :param signal_win: signal window period
    :return: pandas Series with MACD and signal values
    """
    slow = prices.ewm(span=slow_win, adjust=False, min_periods=slow_win).mean()
    fast = prices.ewm(span=fast_win, adjust=False, min_periods=fast_win).mean()
    macd = fast - slow
    signal = macd.ewm(span=signal_win, adjust=False, min_periods=signal_win).mean()

    return macd, signal


def roc(prices, period):
    """
    Calculates Rate of Change signal
    :param prices: pandas series of adjusted close prices
    :param period: look-back period in days
    :return: ROC values
    """
    # computes the difference in prices between the current day’s price and the price “n” day’s ago
    period_diff = prices.diff(period)
    # fetch the previous “n” day’s price
    period_price = prices.shift(period)

    roc = period_diff / period_price

    return roc * 100


def rs_rsi(prices, window):
    """
    Calculate Relative Strength (RS) and Relative Strength Index (RSI) values for a given window.
    :param prices: pandas series of adjusted close prices
    :param window: look-back period in days
    :return: relative strength and relative strength index
    """
    changes = prices.diff()
    gains = changes.where(changes > 0, other=0)
    losses = abs(changes.where(changes < 0, other=0))
    avg_gain = gains.rolling(window=window, min_periods=window).mean()
    avg_loss = losses.rolling(window=window, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - 100 / (1 + rs)

    return rs, rsi


def bollinger_band(prices, window, num_std=1):
    """
    Calculates the simple moving average for a given window and
    upper and lower bands for given number of standard deviations
    :param prices: pandas series of adjusted close prices
    :param window: lookback period in days
    :param num_std: number of standard deviations from the mean.
    :return: simple moving average, upper band, and lower band
    """
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    return sma, upper_band, lower_band


def atr(prices, high, low, period=14):
    """
    Calculates the average price movement each day. Requires OHLCV data.
    Average True Range (ATR) is a volatilty indicator
    :param prices: pandas series of adjusted close prices
    :param high: pandas series of daily high prices
    :param low: pandas series of daily low prices
    :param period: lookback period
    :return: pandas series of average true range
    """
    # high price minus low price
    h_l = abs(high - low)
    # high price minus previous day close
    h_pc = abs(high - prices.shift(1))
    # low price minus previous day close
    l_pc = abs(low - prices.shift(1))
   # create temporary df to house data and find max
    true_range = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1, skipna=False)
    avg_true_range = true_range.rolling(period).mean()
    
    return avg_true_range

def adx(prices, high, low, period=14):
    """
    Calculates the average directional index.
    :param prices: pandas series of adjusted close prices
    :param high: pandas series of daily high prices
    :param low: pandas series of daily low prices
    :param period: lookback period
    :return: pandas series of adx
    """
    plus_dm = high.diff()
    minus_dm = low.diff()
    # replace negative and positive values for DM+ and DM- respectively
    plus_dm[plus_dm < 0] = 0
    minus_dm[plus_dm > 0] = 0
    # get average true range
    a_tr = atr(prices, high, low, period=period)
    # calculate DI+ and DI-
    plus_di = 100 * (plus_dm.ewm(alpha= 1/period).mean() / a_tr)
    minus_di = abs(100 * (minus_dm.ewm(alpha= 1/period).mean() / a_tr))
    
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    avg_dx = ((dx.shift(1) * (period - 1)) + dx) / period
    adx_smooth = avg_dx.ewm(alpha= 1/period).mean()
    
    return plus_di, minus_di, adx_smooth


def obv(prices, volume):
    """
    Calculates the On Balance Volume indicator
    :param prices: pandas series of adjusted close prices
    :param volume: pandas series of daily traded volume
    :return: pandas series on balance volume
    """
    
    ret = prices.pct_change()
    # mark direction of price change
    direction = np.where(ret >= 0, 1, -1)
    # change first direction calc to 0
    direction[0] = 0
    vol_adj = direction * volume
    on_bal_vol = vol_adj.cumsum()
    
    return on_bal_vol


def slope(prices, window):
    """
    Note: Not entirely sure if this works
    Calculates the slope of a window of consecutive prices. 
    :param prices: pandas series of adjusted close prices
    :param window: data points (days) to consider for the slope
    :return: series of slope in degrees
    """
    
    # standardize prices and x values
    std = (prices - prices.min()) / (princes.max() - prices.min())
    x = np.array(range(len(prices)))  # unclear with this step. why len prices?
    x = (x - x.min())/(x.max() - x.min())
    
    # create array to save slopes. first window - 1 values will be 0
    slopes = np.zeros(window -1)
    
    for i in range(window, len(prices) + 1):
        # get the std prices for window. empty if window hasn't reached
        y = std[i-window:i]
        x = x[:window]
        # add constants for y = mx + c line
        x = sm.add_constant(x)
        # insantiate model and fit line
        res = sm.OLS(y, x).fit()
        # append slopes from model to slope list
        slopes = np.append(slopes, res.params[-1])

    # convert slope to angle
    slope_angle = np.rad2deg(np.arctan(slopes))
    
    return slope_angle

def renko(data, n=120):
    """
    Calculates Renko dataframe for given data frame and ATR lookback period.
    We wrap stocktrends Renko function and use our ATR to set bricksize.
    To check out stocktrends:
    https://github.com/chillaranand/stocktrends
    :param data: pandas dataframe with columns [date, open, high, low, close]
    :param n: ATR lookback period
    :return: Boolean columns for uptrend
    """
    df = data.copy()
    df.reset_index(inplace=True)
    # drop unwanted columns
    df.drop(columns=['Close', 'Volume'], inplace=True)
    # change column names to stocktrends.Renko format
    df.rename(columns = {"Date" : "date", "High" : "high","Low" : "low", 
                         "Open" : "open","Adj Close" : "close"}, 
              inplace = True)
    # initialize Renko from stocktrends
    ren = Renko(df)
    # set brick size using ATR for last n days
    ren.brick_size= round(ta.atr(df['close'], df['high'], df['low'], n).iloc[-1], 0)
    renko_df = ren.get_ohlc_data()
    
    return renko_df

    
    
    