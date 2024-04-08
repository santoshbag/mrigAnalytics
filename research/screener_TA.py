# -*- coding: utf-8 -*-
"""
Created on Tue May  2 13:13:44 2023

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tkinter as tk
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mrigstatics as ms
import mrigutilities as mu

engine = mu.sql_engine()

# define a function to display the analytics for the selected stock
def display_analytics(stocks='NIFTY 50'):
    # get the stock name from the entry box
    df = pd.DataFrame()
    cnt = 1
    
    print('<<<<<<<<<<'+stocks+'>>>>>>>>>>')
    if stocks == 'NIFTY 50':
        slist = ms.NIFTY_50
        nifty_50 = engine.execute("select index_members from stock_history where symbol='NIFTY 50' and index_members is not NULL order by date desc limit 1").fetchall()[0][0]
        nifty_50 = nifty_50.strip('][').split(', ')
        slist = [x[1:-1] for x in nifty_50]
    else:
        slist = ms.NIFTY_100
        nifty_100 = engine.execute("select index_members from stock_history where symbol='NIFTY 100' and index_members is not NULL order by date desc limit 1").fetchall()[0][0]
        nifty_100 = nifty_100.strip('][').split(', ')
        slist = [x[1:-1] for x in nifty_100]
    for stock in slist: #['SBIN','TATAMOTORS']: #ms.NIFTY_50:
    # for stock in ['SBIN','TATAPOWER']:
    # get the stock data from Yahoo Finance using pandas_datareader
    # data = pdr.get_data_yahoo(stock_name)
        columnmap = {'MACD_12_26_9':'MACD',
                     'MACDh_12_26_9':'MACD_H',
                     'MACDs_12_26_9':'MACD_S',
                     'SUPERT_7_3.0':'SuperTrend',
                     'BBL_20_2.0':'BollingB_L',
                     'BBM_20_2.0':'BollingB_M',
                     'BBU_20_2.0':'BollingB_U',
                     'STOCHRSIk_14_14_3_3':'STOCH_RSI_k',
                     'STOCHRSId_14_14_3_3':'STOCH_RSI_d'
            }
        
        data = yf.download(stock+'.NS',period='6mo')
        data = data[['High', 'Low', 'Close']]
        data['stock'] = stock
        macd = ta.macd(data['Close'])
        supertrend = ta.supertrend(data['High'], data['Low'], data['Close'], period=7, multiplier=3)
        bb = ta.bbands(data['Close'],length=20,std=2)
        stocRSI = ta.stochrsi(data['Close'])
        # print(macd.columns)
        # print(supertrend.columns)
        # print(bb.columns)
        # print(stocRSI.columns)
        data = pd.merge(data,supertrend['SUPERT_7_3.0'],left_index=True,right_index=True)
        data = pd.merge(data,macd,left_index=True,right_index=True)
        data = pd.merge(data,bb[['BBL_20_2.0','BBM_20_2.0','BBU_20_2.0']],left_index=True,right_index=True)
        data = pd.merge(data,stocRSI[['STOCHRSIk_14_14_3_3' ,'STOCHRSId_14_14_3_3']],left_index=True,right_index=True)
        
        data.drop(columns=['High', 'Low'],inplace=True)
        data.rename(columnmap,axis=1,inplace=True)
        if cnt == 1:
            df = data.tail(1)
        else:
            df = pd.concat([df,data.tail(1)])
        cnt = cnt + 1
    stock_col = df.pop('stock')
    df.insert(0,'Security',stock_col)
    return df.round(2)  
if __name__ == '__main__':
    display_analytics()