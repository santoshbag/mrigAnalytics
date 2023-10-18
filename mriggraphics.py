# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
import io
import os
import sys

import pandas as pd
import numpy as np
#from pandas.compat import StringIO
from io import StringIO
from collections import deque
from sqlalchemy import create_engine
from dateutil import relativedelta
import datetime, nsepy, nsetools
import mrigstatics
import QuantLib as ql
from urllib.parse import quote
import requests, socket, time
from bs4 import BeautifulSoup
from random import choice
import string
import json
from pandas.io.json import json_normalize
import math
import yfinance
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

import kite.kite_trade as zkite

import scipy.stats as si
from scipy import optimize

# from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def candlestick_plot(ticker,data_ohlc, studies=False):
    # Calc moving average
    # data_ohlc.rename(columns=lambda x: str(x).capitalize(),inplace=True)
    if 'date' in data_ohlc.columns:
        data_ohlc['timestamp'] = data_ohlc['date']
    data_ohlc.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'},
                     inplace=True)
    data_ohlc['MA10'] = data_ohlc['Close'].rolling(window=10).mean()

    # data_ohlc.reset_index(inplace=True)

    data_ohlc['Date'] = mdates.datestr2num(data_ohlc['timestamp'].astype(str))  # datestr2num
    data_ohlc.tail(60)
    # print(data_ohlc)
    # Plot candlestick chart
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    # ax3 = fig.add_subplot(111)
    ax1.xaxis_date()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax2.plot(data_ohlc.Date, data_ohlc['MA10'], label='MA_10')
    if studies:
        # data_ohlc['MA10'] = data_ohlc['close'].rolling(window=10).mean()
        data_ohlc['MA60'] = data_ohlc['Close'].rolling(window=60).mean()
        ax3 = ax1.twinx()
        ax3.plot(data_ohlc.Date, data_ohlc['MA60'], label='MA_60')
    plt.ylabel("Price")
    plt.title(ticker)
    ax1.grid(True)
    plt.legend(loc='best')
    plt.xticks(rotation=45)
    candlestick_ohlc(ax1, data_ohlc.values, width=0.6, colorup='g', colordown='r')
    img_buf = io.BytesIO()
    plt.savefig(img_buf,format='png')
    return img_buf

# if __name__ == '__main__':
#    print(getZerodhaChgs('EQ_D',8,0,310.35))
    # expiries_i = [datetime.date(2021,9,30),datetime.date(2021,6,10)]
    # expiries_e = [datetime.date(2021,6,24),datetime.date(2021,7,29)]
#    oc = optionChainLive([('NIFTY','I')],expiries_i)
#    oc = optionChainHistorical(['BANKNIFTY'])#,expiries_i+expiries_e)
#    oc.sort_values(['expiryDate'],axis=0,inplace=True)
#    oc.to_csv('oc_live.csv')        
#    print(oc.columns)
#    print(oc.tail(10))
