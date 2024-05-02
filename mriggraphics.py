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
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.subplots as subplt
import mrigutilities as mu

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


def plotly_candlestick(ticker, data_ohlcv,smas=[10],levelFlag=True):
    if 'date' in data_ohlcv.columns:
        data_ohlcv['timestamp'] = data_ohlcv['date']
    data_ohlcv.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close','volume':'Volume'},
                     inplace=True)
    data_ohlcv['colors_vol'] = data_ohlcv.Close - data_ohlcv.Close.shift(1)
    data_ohlcv['colors_vol'] = data_ohlcv['colors_vol'].apply(lambda x: 'green' if x > 0 else 'red')

    startDate = min(data_ohlcv['Date'])
    endDate = max(data_ohlcv['Date'])

    levels = []
    if levelFlag:
        levels = mu.getLevels(ticker, startDate, endDate)
        levels = [x[1] for x in levels[0]]
        print(levels)

    for sma in smas:
        data_ohlcv['MA_' + str(sma)] = data_ohlcv['Close'].rolling(window=sma).mean()

    sma_colors = ['purple', 'blue', 'darkcyan', 'teal']

    # Make Subplot of 2 rows to plot 2 graphs sharing the x axis

    sma_colors = ['purple', 'blue','darkcyan','teal']
    fig = subplt.make_subplots(rows=2,
                           cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.02)

    fig.add_trace(go.Candlestick(x=data_ohlcv['Date'],
                                         open=data_ohlcv['Open'],
                                         high=data_ohlcv['High'],
                                         low=data_ohlcv['Low'],
                                         close=data_ohlcv['Close'],
                                         increasing_line_color='green',
                                         decreasing_line_color='red',
                                         name='Price'), row=1,col=1)

    for sma,lcolor in list(zip(smas,sma_colors)):
        fig.add_trace(go.Scatter(x=data_ohlcv['Date'],
                                 y=data_ohlcv['MA_'+str(sma)],
                              line=dict(color=lcolor,
                                           width=1,
                                           shape='spline'), # smooth the line
                                 name='MA_'+str(sma)), row=1,col=1)


    for l in levels:
        fig.add_trace( go.Scatter(x=data_ohlcv['Date'],
                                 y= pd.Series(l, index=np.arange(len(data_ohlcv['Date']))),
                              line=dict(color='grey',
                                           width=1,
                                           shape='spline'),showlegend=False),
                                  row=1,col=1)


    # Add Volume Chart to Row 2 of subplot
    fig.add_trace(go.Bar(x=data_ohlcv['Date'],
                         y=data_ohlcv['Volume'],
                         marker_color=list(data_ohlcv['colors_vol'].values)
                         ,name='Volume'), row = 2, col = 1)

    # Update Price Figure layout
    fig.update_layout(title= ticker,
    yaxis1_title = 'Price',
    yaxis2_title = 'Volume',
    # xaxis2_title = ‘Time’,
    xaxis1_rangeslider_visible = False,
    xaxis2_rangeslider_visible = False)

    # plt_div = plot(fig, output_type='div')
    return fig

def plotly_tech_indicators(ticker, data_ohlcv,indicators=['MACD']):
    if 'date' in data_ohlcv.columns:
        data_ohlcv['timestamp'] = data_ohlcv['date']
    data_ohlcv.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close','volume':'Volume'},
                     inplace=True)
    data_ohlcv['colors_vol'] = data_ohlcv.Close - data_ohlcv.Close.shift(1)
    data_ohlcv['colors_vol'] = data_ohlcv['colors_vol'].apply(lambda x: 'green' if x > 0 else 'red')

    # for indicator in indicators:
    #     data_ohlcv['MA_' + str(sma)] = data_ohlcv['Close'].rolling(window=sma).mean()

    sma_colors = ['purple', 'blue', 'darkcyan', 'teal']

    # Make Subplot of 2 rows to plot 2 graphs sharing the x axis

    sma_colors = ['purple', 'blue','darkcyan','teal']
    fig = subplt.make_subplots(rows=1,
                           cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.02)

    fig.add_trace(go.Candlestick(x=data_ohlcv['Date'],
                                         open=data_ohlcv['Open'],
                                         high=data_ohlcv['High'],
                                         low=data_ohlcv['Low'],
                                         close=data_ohlcv['Close'],
                                         increasing_line_color='green',
                                         decreasing_line_color='red',
                                         name='Price'), row=1,col=1)

    for indicator,lcolor in list(zip(indicators,sma_colors)):
        fig.add_trace(go.Scatter(x=data_ohlcv['Date'],
                                 y=data_ohlcv[indicator],
                              line=dict(color=lcolor,
                                           width=1,
                                           shape='spline'), # smooth the line
                                 name=indicator), row=1,col=1)


    # Add Volume Chart to Row 2 of subplot
    # fig.add_trace(go.Bar(x=data_ohlcv['Date'],
    #                      y=data_ohlcv['Volume'],
    #                      marker_color=list(data_ohlcv['colors_vol'].values)
    #                      ,name='Volume'), row = 2, col = 1)

    # Update Price Figure layout
    fig.update_layout(title= ticker,
    yaxis1_title = 'Price',
    # xaxis2_title = ‘Time’,
    xaxis1_rangeslider_visible = False)

    # plt_div = plot(fig, output_type='div')
    return fig




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


'''
CSS color:
                aliceblue, antiquewhite, aqua, aquamarine, azure,
                beige, bisque, black, blanchedalmond, blue,
                blueviolet, brown, burlywood, cadetblue,
                chartreuse, chocolate, coral, cornflowerblue,
                cornsilk, crimson, cyan, darkblue, darkcyan,
                darkgoldenrod, darkgray, darkgrey, darkgreen,
                darkkhaki, darkmagenta, darkolivegreen, darkorange,
                darkorchid, darkred, darksalmon, darkseagreen,
                darkslateblue, darkslategray, darkslategrey,
                darkturquoise, darkviolet, deeppink, deepskyblue,
                dimgray, dimgrey, dodgerblue, firebrick,
                floralwhite, forestgreen, fuchsia, gainsboro,
                ghostwhite, gold, goldenrod, gray, grey, green,
                greenyellow, honeydew, hotpink, indianred, indigo,
                ivory, khaki, lavender, lavenderblush, lawngreen,
                lemonchiffon, lightblue, lightcoral, lightcyan,
                lightgoldenrodyellow, lightgray, lightgrey,
                lightgreen, lightpink, lightsalmon, lightseagreen,
                lightskyblue, lightslategray, lightslategrey,
                lightsteelblue, lightyellow, lime, limegreen,
                linen, magenta, maroon, mediumaquamarine,
                mediumblue, mediumorchid, mediumpurple,
                mediumseagreen, mediumslateblue, mediumspringgreen,
                mediumturquoise, mediumvioletred, midnightblue,
                mintcream, mistyrose, moccasin, navajowhite, navy,
                oldlace, olive, olivedrab, orange, orangered,
                orchid, palegoldenrod, palegreen, paleturquoise,
                palevioletred, papayawhip, peachpuff, peru, pink,
                plum, powderblue, purple, red, rosybrown,
                royalblue, saddlebrown, salmon, sandybrown,
                seagreen, seashell, sienna, silver, skyblue,
                slateblue, slategray, slategrey, snow, springgreen,
                steelblue, tan, teal, thistle, tomato, turquoise,
                violet, wheat, white, whitesmoke, yellow,
                yellowgreen
'''