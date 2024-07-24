# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
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
from pandas import json_normalize

import math
import yfinance
# from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import yfinance as yf

# import kite.kite_trade as zkite
import kite.mrigkite as zkite

import scipy.stats as si
from scipy import optimize
from sqlalchemy.dialects.postgresql import insert
import sympy as sp

def get_futures_expiry(startdate, enddate):
    expiryDateList = []
    if startdate > enddate:
        expiryDateList = None
    enddate = enddate + relativedelta.relativedelta(months=3)
    for yr in range(startdate.year, enddate.year + 1):
        for mon in range(1, 13):
            dt = datetime.date(yr, mon, 20)
            dt = mu.last_thursday_of_month(dt)
            if (startdate <= dt <= enddate):
                expiryDateList.append(dt)
    return expiryDateList


def get_indexoptions_expiry():
    """
    Trading cycle
    
    CNX Nifty options contracts have 3 consecutive monthly contracts,
     additionally 3 quarterly months of the cycle March / June / September / December 
     and 5 following semi-annual months of the cycle June / December would be available,
     so that at any point in time there would be options contracts with atleast 3 year
     tenure available. On expiry of the near month contract, new contracts (monthly/quarterly/ 
    half yearly contracts as applicable) are introduced at new strike prices for both call and
     put options, on the trading day following the expiry of the near month contract.    
    """

    today = datetime.date.today()
    expiryDateList = []
    enddate = mu.last_thursday_of_month(today + relativedelta.relativedelta(months=2))

    # 3 consecutive months 
    dt = today + datetime.timedelta(3 - today.weekday())
    while dt <= enddate:
        expiryDateList.append(dt)
        dt = dt + datetime.timedelta(7)

    # 3 Quarterly months expiry.
    anchordate = expiryDateList[-1]
    while anchordate.month not in [3, 6, 9, 12]:
        anchordate = anchordate + relativedelta.relativedelta(months=1)
        anchordate = mu.last_thursday_of_month(anchordate)
    expiryDateList.append(anchordate)
    expiryDateList.append(mu.last_thursday_of_month(anchordate + relativedelta.relativedelta(months=3)))
    expiryDateList.append(mu.last_thursday_of_month(anchordate + relativedelta.relativedelta(months=6)))

    # 3 Quarterly months expiry.
    anchordate = expiryDateList[-1]
    while anchordate.month not in [6, 12]:
        anchordate = anchordate + relativedelta.relativedelta(months=1)
        anchordate = mu.last_thursday_of_month(anchordate)

    expiryDateList.append(anchordate)
    for i in [1, 2, 3, 4, 5]:
        expiryDateList.append(mu.last_thursday_of_month(anchordate + relativedelta.relativedelta(months=6 * i)))

    return sorted(set(expiryDateList))
def getIndexData(symbol, start_date, end_date,db='localhost'):
    '''
    :param symbol:
    :param start_date:
    :param end_date:
    :param db:
    :return:
    '''
    sql = "select * from stock_history where series = 'IN' and date >='" + start_date.strftime('%Y-%m-%d') \
          + "' and date <'" + end_date.strftime('%Y-%m-%d') \
          + "' and symbol='" \
          + symbol + "'"

    engine = mu.sql_engine(dbhost=db)
    index_df = pd.read_sql(sql, engine)
    if not index_df.empty:
        for i in range(0, len(index_df['date']) - 1):
            index_df.iloc[i]['date'] = datetime.datetime.combine(index_df.iloc[i]['date'], datetime.time())
        index_df.date = pd.DatetimeIndex(index_df.date)
        index_df.set_index('date', inplace=True)
        # for i in range(0,len(stock_df.index)-1):
        #   stock_df.index[i] = datetime.datetime.combine(stock_df.index[i], datetime.time())

    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return index_df

def getOptionData(symbol, start_expirydate, end_expirydate,db='localhost'):
    sql = "select * from futures_options_history where option_type in ('PE','CE') and expiry >='" + start_expirydate.strftime('%Y-%m-%d') \
          + "' and expiry <'" + end_expirydate.strftime('%Y-%m-%d') \
          + "' and symbol='" \
          + symbol + "'"

    engine = mu.sql_engine(dbhost=db)
    option_df = pd.read_sql(sql, engine)
    if not option_df.empty:
        # for i in range(0, len(option_df['date']) - 1):
        #     option_df.iloc[i]['date'] = datetime.datetime.combine(option_df.iloc[i]['date'], datetime.time())
        # option_df.date = pd.DatetimeIndex(option_df.date)
        option_df.set_index('date', inplace=True)
        # for i in range(0,len(stock_df.index)-1):
        #   stock_df.index[i] = datetime.datetime.combine(stock_df.index[i], datetime.time())

    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return option_df

def getStockData(symbol, start_date, end_date=None, last=False,db='localhost'):
    
    if end_date:
        sql = "select * from stock_history where date >='" + start_date.strftime('%Y-%m-%d') \
              + "' and date <'" + end_date.strftime('%Y-%m-%d') \
              + "' and symbol='" \
              + symbol + "'"
    else:
        if not last:
            sql = "select * from stock_history where date >='" + start_date.strftime('%Y-%m-%d') \
                  + "' and symbol='" \
                  + symbol + "'"
        else:
            sql = "select * from stock_history where date >=(select MIN(date) from ((select date from " \
                  + "stock_history where symbol='"+symbol+"' order by date desc limit 1) union all (select "\
                  + "to_date('"+start_date.strftime('%Y-%m-%d')+"','YYYY-MM-DD') as date)) as T)" \
                  + " and symbol='" \
                  + symbol + "'"
            
    engine = mu.sql_engine(dbhost=db)
    stock_df = pd.read_sql(sql, engine)
    if not stock_df.empty:
        for i in range(0, len(stock_df['date']) - 1):
            stock_df.iloc[i]['date'] = datetime.datetime.combine(stock_df.iloc[i]['date'], datetime.time())
        stock_df.date = pd.DatetimeIndex(stock_df.date)
        stock_df.set_index('date', inplace=True)
        # for i in range(0,len(stock_df.index)-1):
        #   stock_df.index[i] = datetime.datetime.combine(stock_df.index[i], datetime.time())

    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return stock_df


def getStockQuote(symbol):
    stockQuote = {}
    try:
        # stockQuote = nsepy.get_quote(symbol)
        # if ('data' in stockQuote.keys()):
        #     stockQuote = stockQuote['data'][0]
        price = yf.download(symbol+'.NS',period='1d',interval='1m')
        stockQuote['lastPrice'] = price.tail(1)['Close'].values[0]
        stockQuote['high'] = max(price['High'].values)
        stockQuote['low'] = min(price['Low'].values)
        stockQuote['open'] = price.head(1)['Close'].values[0]
        stockQuote['time'] = str(price.head(1).index[0]).split('+')[0]
    except:
        pass
#    print(stockQuote)
#     if len(stockQuote) <= 0:
#        print("not live")
    sql = "select prev_close,(select max(close_adj)  as high52 from stock_history where symbol='%s' and date > (now() - interval '1 year')) ," \
          " (select min(close_adj)  as low52 from stock_history where symbol='%s' and date > (now() - interval '1 year'))" \
          " from stock_history where symbol='%s' order by date desc limit 1"
    engine = mu.sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    stockQuote1 = pd.read_sql(sql % (symbol,symbol,symbol), engine)
    if not stockQuote1.empty:
        # stockQuote1.drop('date', axis=1, inplace=True)
        stockQuote1.rename(columns={'close_adj' : 'lastPrice'}, inplace=True)
        stockQuote1 = stockQuote1.to_dict(orient='records')
        stockQuote1 = stockQuote1[0]
        stockQuote = stockQuote | stockQuote1
#            stockQuote = json.loads(stockQuote)
#            for key in stockQuote.keys():
#                stockQuote[key] = stockQuote[key][0]
#            stockQuote['lastPrice'] = stockQuote['quote']
#         else:
#             try:
#                 timecounter = 0
#                 while True:
#                     timecounter = timecounter + 1
#                     if is_connected():
#                         stockQuote = nsepy.get_quote(quote(symbol, safe=''))
#                         if ('data' in stockQuote.keys()):
#                             stockQuote = stockQuote['data'][0]
#                     if is_connected() or timecounter > 5:
#                         break
#                     else:
#                         time.sleep(60)
#             except:
#                 pass
#     momentum = 0
#     for i in range(1, 10):
#         try:
#             momentum = (stockQuote['buyPrice' + str(i)] * stockQuote['buyQuantity' + str(i)])
#             - (stockQuote['sellPrice' + str(i)] * stockQuote['sellQuantity' + str(i)])
#             stockQuote['momentum'] = momentum
#         except:
#             pass
#         # print(stockQuote['lastPrice'])
    return stockQuote


def getStockOptionQuote(symbol, expiry, strike, option_type='CE',instrument='OPTSTK'):
    stockOptionQuote = {}
    sql = "select * from live where symbol='%s' and expiry='%s' and strike='%s' and option_type='%s' order by date desc limit 1"
    engine = mu.sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    stockOptionQuote = pd.read_sql(sql % (symbol, expiry.strftime('%Y-%m-%d'), str(strike), option_type), engine)
    if not stockOptionQuote.empty:
        stockOptionQuote.set_index('symbol', inplace=True)
    else:
        stockOptionQuote = nsepy.get_quote(symbol=quote(symbol, safe=''),
                                           expiry=expiry, strike=strike,
                                           option_type=option_type,
                                           instrument=instrument)
#        print(stockOptionQuote)
        if ('data' in stockOptionQuote.keys()):
            stockOptionQuote = stockOptionQuote['data'][0]
        momentum = 0
        for i in range(1, 10):
            try:
                momentum = (stockOptionQuote['buyPrice' + str(i)] * stockOptionQuote['buyQuantity' + str(i)])
                - (stockOptionQuote['sellPrice' + str(i)] * stockOptionQuote['sellQuantity' + str(i)])
            except:
                pass
        stockOptionQuote['momentum'] = momentum
    return stockOptionQuote

def getStockFuturesQuote(symbol, expiry, instrument='FUTSTK'):
    stockOptionQuote = {}
    sql = "select * from live where symbol='%s' and expiry='%s' order by date desc limit 1"
    engine = mu.sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    stockOptionQuote = pd.read_sql(sql % (symbol, expiry.strftime('%Y-%m-%d')), engine)
    if not stockOptionQuote.empty:
        stockOptionQuote.set_index('symbol', inplace=True)
    else:
        stockOptionQuote = nsepy.get_quote(symbol=quote(symbol, safe=''),
                                           expiry=expiry,
                                           instrument=instrument)
#        print(stockOptionQuote)
        if ('data' in stockOptionQuote.keys()):
            stockOptionQuote = stockOptionQuote['data'][0]
        momentum = 0
        for i in range(1, 10):
            try:
                momentum = (stockOptionQuote['buyPrice' + str(i)] * stockOptionQuote['buyQuantity' + str(i)])
                - (stockOptionQuote['sellPrice' + str(i)] * stockOptionQuote['sellQuantity' + str(i)])
            except:
                pass
        stockOptionQuote['momentum'] = momentum
    return stockOptionQuote



def getIndexOptionQuote(symbol, expiry, strike, option_type='CE',instrument='OPTIDX'):
    stockOptionQuote = {}
    sql = "select * from live where symbol='%s' and expiry='%s' and strike='%s' and option_type='%s' order by date desc limit 1"
    engine = mu.sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    stockOptionQuote = pd.read_sql(sql % (symbol, expiry.strftime('%Y-%m-%d'), str(strike), option_type), engine)
    if not stockOptionQuote.empty:
        stockOptionQuote.set_index('symbol', inplace=True)
    else:
        stockOptionQuote = nsepy.get_quote(symbol=quote(symbol, safe=''),
                                           expiry=expiry, strike=strike,
                                           option_type=option_type,
                                           instrument=instrument)
#        print(stockOptionQuote)
        if ('data' in stockOptionQuote.keys()):
            stockOptionQuote = stockOptionQuote['data'][0]
        momentum = 0
        for i in range(1, 10):
            try:
                momentum = (stockOptionQuote['buyPrice' + str(i)] * stockOptionQuote['buyQuantity' + str(i)])
                - (stockOptionQuote['sellPrice' + str(i)] * stockOptionQuote['sellQuantity' + str(i)])
            except:
                pass
        stockOptionQuote['momentum'] = momentum
    return stockOptionQuote


def getIndexFuturesQuote(symbol, expiry, instrument='FUTIDX'):
    stockOptionQuote = {}
    sql = "select * from live where symbol='%s' and expiry='%s' order by date desc limit 1"
    engine = mu.sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    stockOptionQuote = pd.read_sql(sql % (symbol, expiry.strftime('%Y-%m-%d')), engine)
    if not stockOptionQuote.empty:
        stockOptionQuote.set_index('symbol', inplace=True)
    else:
        stockOptionQuote = nsepy.get_quote(symbol=quote(symbol, safe=''),
                                           expiry=expiry,
                                           instrument=instrument)
#        print(stockOptionQuote)
        if ('data' in stockOptionQuote.keys()):
            stockOptionQuote = stockOptionQuote['data'][0]
        momentum = 0
        for i in range(1, 10):
            try:
                momentum = (stockOptionQuote['buyPrice' + str(i)] * stockOptionQuote['buyQuantity' + str(i)])
                - (stockOptionQuote['sellPrice' + str(i)] * stockOptionQuote['sellQuantity' + str(i)])
            except:
                pass
        stockOptionQuote['momentum'] = momentum
    return stockOptionQuote

def getIndexQuote(symbol):
    nse = nsetools.Nse()
    indexQuote = nse.get_index_quote(symbol)['lastPrice']

    return float(indexQuote)


def getIndustry(symbol):
    sql = "select distinct industry from security_master where symbol = '" + symbol + "'"
    engine = mu.sql_engine()
    industry = engine.execute(sql).fetchall()

    if (len(industry) > 0):
        return industry[0][0]
    else:
        return ""


def getSecMasterData(symbol):
    sql = "select distinct * from security_master where symbol = '" + symbol + "'"
    engine = mu.sql_engine()
    metadata = pd.read_sql(sql, engine)

    if not metadata.empty:
        metadata = metadata.to_dict()
        for key in metadata.keys():
            if metadata[key][0]:
                #                print(key)
                #                print(metadata[key][0])
                metadata[key] = metadata[key][0]
            else:
                #                print("setting blank for "+key)
                metadata[key] = ""
        return metadata
    else:
        return {}


def getMFNAV(reference_date, isinlist=None,db='localhost'):
    sql = "select * from mf_nav_history where \"Date\">='" + reference_date.strftime(
        '%Y-%m-%d') + "' and \"ISIN Div Payout/ ISIN Growth\" in ("
    engine = mu.sql_engine(dbhost=db)
    for isin in isinlist:
        if isin != None:
            sql = sql + "'" + isin + "',"
    sql = sql[:-1] + ")"
    nav_df = pd.read_sql(sql, engine)
    nav_df.set_index('Date', inplace=True)
    return nav_df


def getStrikes(symbol):
    oc = mu.get_stored_option_chain(symbol)

    strikes = []
    if not oc.empty:
        strikes = sorted(set(list(oc['Strike_Price'])))

    return strikes


def getNifty200():
    nifty200 = []
    nifty200_url = "https://www.nseindia.com/content/indices/ind_nifty200list.csv"

    r = requests.get(nifty200_url)
    symbols = r.text.split("\r\n")
    for row in symbols:
        try:
            nifty200.append(row.split(',')[2])
        except:
            pass
    return nifty200


def getNifty50():
    nifty50 = []
    nifty50_url = "https://www.nseindia.com/content/indices/ind_nifty50list.csv"

    r = requests.get(nifty50_url)
    symbols = r.text.split("\r\n")
    for row in symbols:
        try:
            nifty50.append(row.split(',')[2])
        except:
            pass
    return nifty50


def price(scrip):
    price = None
    yahoo_map = {'NIFTY': '^NSEI','NIFTY 50': '^NSEI', 'BANKNIFTY': '^NSEBANK'}
    yahooid = scrip + '.NS'
    if (scrip == 'NIFTY' or scrip == 'BANKNIFTY'):
        yahooid = yahoo_map[scrip]
    if len(yahooid) > 0:
        if yahooid is not None:
            try:
                price = yf.download(yahooid, period='1d').Close.values[0]
            except:
                None

    return price

def price_steps(price):
    if price <=100:
        return 2
    elif price <= 500:
        return 5
    elif price <= 1000:
        return 10
    else:
        return 50

def getIndexMembers(index):
    engine = mu.sql_engine()
    members = []
    try:
        members = engine.execute("select index_members from stock_history where symbol=%s order by date desc limit 1",(index)).fetchall()[0][0]
    except:
        pass
    return members


if __name__ == '__main__':
    print(pd.__version__)
#    print(getZerodhaChgs('EQ_D',8,0,310.35))
    # expiries_i = [datetime.date(2021,9,30),datetime.date(2021,6,10)]
    # expiries_e = [datetime.date(2021,6,24),datetime.date(2021,7,29)]
#    oc = optionChainLive([('NIFTY','I')],expiries_i)
#    oc = optionChainHistorical(['BANKNIFTY'])#,expiries_i+expiries_e)
#    oc.sort_values(['expiryDate'],axis=0,inplace=True)
#    oc.to_csv('oc_live.csv')        
#    print(oc.columns)
#    print(oc.tail(10))
#     expiry1 = mu.last_thursday_of_month(datetime.date.today())
#     expiry2 = mu.last_thursday_of_month(expiry1 + datetime.timedelta(days=30))
#     expiry3 = mu.last_thursday_of_month(expiry2 + datetime.timedelta(days=30))
# # strk = 17500
#     # print(getIndexOptionQuote('NIFTY', exp, strk))
#     #print(getStockQuote('AXISBANK'))
#
#     # levels1 = getLevels('TATAMOTORS.NS', exp)
#     # levels2 = getLevels('TATAMOTORS.NS', exp,method='window')
#     # print(levels1)
#     # print(levels2)
#     #
#     scrip = ['ADANIENSOL']#,'TATAMOTORS']
#     oc = kite_OC(scrip,[expiry1,expiry2,expiry3])
#     oc.reset_index(inplace=True)
#     print(oc[oc['name'] == scrip[0]])
#     print(oc[oc['name'] == scrip[1]])
#     print(getExpiry(scrip = 'CIPLA'))
    # print(getStockQuote('TATAPOWER'))
    # print(getIndexMembers('NIFTY BANK'))
