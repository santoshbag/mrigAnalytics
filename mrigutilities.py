# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
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
# from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import yfinance as yf

# import kite.kite_trade as zkite
import kite.mrigkite as zkite

import scipy.stats as si
from scipy import optimize
from sqlalchemy.dialects.postgresql import insert

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



def get_last_row(csv_filename, lines=1):
    with open(csv_filename, 'r') as f:
        try:
            lastrow = deque(csv.reader(f), lines)
        except IndexError:  # empty file
            lastrow = None
        return lastrow


def clean_df_db_dups(df, tablename, engine, dup_cols=[],
                     filter_continuous_col=None,
                     filter_categorical_col=None,
                     date_handling=None,
                     leftIdx=False):
    """
    Remove rows from a dataframe that already exist in a database
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
        dup_cols: list or tuple of column names to check for duplicate row values
    Optional:
        filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                               can be either a datetime, int, or float data type
                               useful for restricting the database table size to check
        filter_categorical_col : the name of the categorical data column for Where = value check
                                 Creates an "IN ()" check on the unique values in this column
    Returns
        Unique list of values from dataframe compared to database table
    """
    args = 'SELECT %s FROM %s' % (', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
    if date_handling is not None:
        args = args.replace("\"Date\"", date_handling)
    # print(args)
    args_contin_filter, args_cat_filter = None, None
    # print("santosh -->"+ args)
    existing_security = ""
    if filter_continuous_col is not None:
        if df[filter_continuous_col].dtype == 'datetime64[ns]':
            args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s')
                                          AND Convert(datetime, '%s')""" % (filter_continuous_col,
                                                                            df[filter_continuous_col].min(),
                                                                            df[filter_continuous_col].max())

    if filter_categorical_col is not None:
        args_cat_filter = ' "%s" in(%s)' % (filter_categorical_col,
                                            ', '.join(["'{0}'".format(value) for value in
                                                       df[filter_categorical_col].unique()]))

    if args_contin_filter and args_cat_filter:
        args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
    elif args_contin_filter:
        args += ' Where ' + args_contin_filter
    elif args_cat_filter:
        args += ' Where ' + args_cat_filter

    try:
        df.drop_duplicates(dup_cols, keep='last', inplace=True)
    except:
        pass
    # print(pd.read_sql(args, engine))
    # print(df)
    df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, left_index=leftIdx, indicator=True,
                  suffixes=['', '_in_db'])
    # print(df)
    existing_security = str(df[df['_merge'] == 'both'])
    df = df[df['_merge'] == 'left_only']
    # print(df)
    df.drop(['_merge'], axis=1, inplace=True)
    # print(df)
    return [df, existing_security]


def sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT], dbhost="localhost"):
    DB_TYPE = 'postgresql'
    DB_DRIVER = 'psycopg2'
    DB_USER = 'postgres'
    DB_PASS = 'xanto007'
    DB_HOST = mrigstatics.DBHOST[dbhost]
    DB_PORT = '5432'
    DB_NAME = dbname
    if dbhost == "SIRIUS":
        DB_NAME = mrigstatics.RB_WAREHOUSE['production']
    POOL_SIZE = 50

    SQLALCHEMY_DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER,
                                                          DB_PASS, DB_HOST, DB_PORT, DB_NAME)
    ENGINE = create_engine(
        SQLALCHEMY_DATABASE_URI, pool_size=POOL_SIZE, max_overflow=0, client_encoding='utf8')

    return ENGINE


def last_thursday_of_month(date):
    date = date + relativedelta.relativedelta(day=31, weekday=relativedelta.TH(-1))
    return date


def get_futures_expiry(startdate, enddate):
    expiryDateList = []
    if startdate > enddate:
        expiryDateList = None
    enddate = enddate + relativedelta.relativedelta(months=3)
    for yr in range(startdate.year, enddate.year + 1):
        for mon in range(1, 13):
            dt = datetime.date(yr, mon, 20)
            dt = last_thursday_of_month(dt)
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
    enddate = last_thursday_of_month(today + relativedelta.relativedelta(months=2))

    # 3 consecutive months 
    dt = today + datetime.timedelta(3 - today.weekday())
    while dt <= enddate:
        expiryDateList.append(dt)
        dt = dt + datetime.timedelta(7)

    # 3 Quarterly months expiry.
    anchordate = expiryDateList[-1]
    while anchordate.month not in [3, 6, 9, 12]:
        anchordate = anchordate + relativedelta.relativedelta(months=1)
        anchordate = last_thursday_of_month(anchordate)
    expiryDateList.append(anchordate)
    expiryDateList.append(last_thursday_of_month(anchordate + relativedelta.relativedelta(months=3)))
    expiryDateList.append(last_thursday_of_month(anchordate + relativedelta.relativedelta(months=6)))

    # 3 Quarterly months expiry.
    anchordate = expiryDateList[-1]
    while anchordate.month not in [6, 12]:
        anchordate = anchordate + relativedelta.relativedelta(months=1)
        anchordate = last_thursday_of_month(anchordate)

    expiryDateList.append(anchordate)
    for i in [1, 2, 3, 4, 5]:
        expiryDateList.append(last_thursday_of_month(anchordate + relativedelta.relativedelta(months=6 * i)))

    return sorted(set(expiryDateList))


def test_df():
    nifty_fut = nsepy.get_history(symbol="NIFTY",
                                  start=datetime.date(2015, 1, 1),
                                  end=datetime.date(2015, 1, 10),
                                  index=True,
                                  futures=True,
                                  expiry_date=datetime.date(2015, 1, 29))
    return nifty_fut


def get_Quandl():
    QUANDL_API_KEY = 'C33qTjnTYtCkx7UZ6H3R'

    return QUANDL_API_KEY


def get_AV():
    ALPHAVANTAGE_API_KEY = 'Q9CXTLUR0A69B3D9'

    return ALPHAVANTAGE_API_KEY


def get_finalColumns(cols=None):
    if cols is not None:
        for i in range(0, len(cols)):
            if cols[i] in mrigstatics.COLUMN_MAPPINGS.keys():
                cols[i] = mrigstatics.COLUMN_MAPPINGS[cols[i]]
    return cols


def get_date_vector(date_from_db):
    dateList = []
    """
    Takes a list [[curvedate(s)][tenor(s)]] and returns a 
    date vector [curvedate + tenor]
    
    """
    for i in range(0, len(date_from_db[0])):
        if date_from_db[1][i].split(" ")[1] == 'months':
            dateList.append(
                date_from_db[0][i] + relativedelta.relativedelta(months=int(date_from_db[1][i].split(" ")[0])))
        if date_from_db[1][i].split(" ")[1] in ('years', 'year'):
            dateList.append(
                date_from_db[0][i] + relativedelta.relativedelta(years=int(date_from_db[1][i].split(" ")[0])))
    dateList = [ql.Date(dt.day, dt.month, dt.year) for dt in dateList]
    return dateList


def args_inspector(args):
    """
    Does checks if the arguments are valid.
    """
    check = True
    wrong_arg = ""
    for arg_name in args:
        if args[arg_name] == "":
            check = False
            wrong_arg = wrong_arg + "|" + arg_name + "-" + args[arg_name]
    return [check, wrong_arg]


def python_dates(qldates):
    return datetime.date(qldates.year(), qldates.month(), qldates.dayOfMonth())


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

    engine = sql_engine(dbhost=db)
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

    engine = sql_engine(dbhost=db)
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
            
    engine = sql_engine(dbhost=db)
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
    engine = sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
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
    engine = sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
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
    engine = sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
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
    engine = sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
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
    engine = sql_engine(mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
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

def closestmatch(x, arr, diff,accuracy=50):
    pivot = int(len(arr) / 2)
    if (abs(arr[pivot] - x) <= diff or accuracy == 0):
        return arr[pivot]
    if x < arr[pivot]:
        return closestmatch(x, arr[:pivot], diff,accuracy -1)
    if x > arr[pivot]:
        return closestmatch(x, arr[pivot:], diff,accuracy -1)


def max_stock_drawdown(symbol, window_days=29, period_months=12):
    sql = "select min(period_log_returns) from (select sh.date as date, \
               sum(sh.daily_log_returns) over (partition by sh.symbol order by sh.date rows between " + str(
        window_days) + " preceding and current row ) as period_log_returns  \
               from daily_returns sh where sh.symbol='" + symbol + "' and sh.date > now() - interval '" + str(
        period_months) + " months' \
               order by sh.symbol, sh.date desc) as dat"

    engine = sql_engine()
    drawdown = engine.execute(sql).fetchall()
    if len(drawdown) > 0:
        drawdown = float(drawdown[0][0])
    return drawdown


def avg_stock_drawdown(symbol, window_days=29, period_months=12):
    sql = "select avg(period_log_returns) from (select sh.date as date, \
               sum(sh.daily_log_returns) over (partition by sh.symbol order by sh.date rows between " + str(
        window_days) + " preceding and current row ) as period_log_returns  \
               from daily_returns sh where sh.symbol='" + symbol + "' and sh.date > now() - interval '" + str(
        period_months) + " months' \
               order by sh.symbol, sh.date desc) as dat where period_log_returns < 0"

    engine = sql_engine()
    drawdown = engine.execute(sql).fetchall()
    if len(drawdown) > 0:
        drawdown = float(drawdown[0][0])
    return drawdown


def get_stored_option_strategies(name=None,strategy_type=None):
    if name != None:
        sql = "select strategy_df from strategies where name='" + name + "'"
    elif strategy_type != None:
        sql = "select strategy_df from strategies where type='" + strategy_type + "' order by date desc limit 1"
    else:
        sql = "select strategy_df from strategies order by date desc limit 1"

    engine = sql_engine()
    df = engine.execute(sql).fetchall()
    if len(df) > 0:
        df = df[0][0]
        df = pd.read_csv(StringIO(df), sep='\s+')
#        df['Expiry'] = pd.to_datetime(df['Expiry'], format='%Y-%m-%d').apply(lambda x: x.date())
#        df = df.set_index('Expiry')
    else:
        df = pd.DataFrame()
    return df


def optionChainLive(symbol_list,expiry_list):

    urlheader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "authority": "www.nseindia.com",
        "scheme":"https",
        "cookie":'_ga=GA1.2.1900743387.1621872644; _gid=GA1.2.1565546829.1622526748; ak_bmsc=40EF2CB9128814B1A8BDF1B556226C7A312C73C7604200003466B8603C50C750~plt/6T92/vy04BjFxlaztkE8el9qsKY7nTN+u/AkhLL3Mm3v+/LFvjGWZQPnMKtmjUzRccCMZljEOeblAS1nh5V8M0ltXbtcl3+xYId/JAJhoGoHnWO4Ll61W8y38XF7J3Mk32oZZtuITMc7l+RbuJA+XncOZOHX7UNN6g1Z6gf7dycLgX1MJbY4/0vQH06pvswqnjeaf9WyGq7fiN7DrQhqSjPNucoWL5tVV9b6lvyh4=; RT="z=1&dm=nseindia.com&si=b78ffdeb-2ce3-4c9d-866c-11e26f51a29c&ss=kpgdhaiz&sl=0&tt=0&bcn=//684fc539.akstat.io/"; nsit=ihm6P54k5EFoZGRvb47nKVw9; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTYyMjcwMDc2MiwiZXhwIjoxNjIyNzA0MzYyfQ.0reIEoJ4qYfgIpt292SU-bS5Sph9gqhB4HGTlA0wuII; bm_mi=A0CE0C54A067C9DCF1CA57561E785F00~PtJqH3aENglUdv0juAQCaX1wewrplnM3GNZUJmvuRk78Y4PYlV5Y4nMsBPgw0cPCCtqTH6hg+kFMNL5AYfJ4gPR3kWHiZ8drZ4NoqL5VN/94uabv0ZzDIh9BS+AT6pBB6qNd/0pPTGUUhJXs/NtwCDIaJB+DQHeGbyhmHMxog8a9k5NusQOfoMTSKt91ZvI1OMol9/0O0sGoFyI25ng19ZmKPx4XuLsiWuqngAIz1kM=; bm_sv=86BDFB03E8E046ECA9EE6CFDC9D205A4~tJ2iWqTMmwKX6C4ANaQbvPduQw+jhfcHlG8HKGksgOtFU25iowQkpRhmdgzRdfPpgrr2KiWi7X9msRt4aL4rxhF/j/PzUHNDIB+oCThnWpN9iAb/w9yuzFVe5cS0ALim8eJB4C7R4/DSiPzPOeIhHX+/hYEss24X7E9pHxogBD0='}
    
    option_chain = []
    for (symbol,sec_type) in symbol_list:
#        for expiry in expiry_list:
#            expiry_dt = expiry.strftime('%d')+'-'+expiry.strftime('%b')+'-'+str(expiry.year)
        if sec_type == 'I':
            url = 'https://www.nseindia.com/api/option-chain-indices?symbol='+symbol
        if sec_type == 'E':
            url = 'https://www.nseindia.com/api/option-chain-equities?symbol='+symbol            
        data = requests.get(url, headers=urlheader).content
#        print(data)                               
        data2 = data.decode('utf-8')
        df = json.loads(data2)
#        for expiry in expiry_list:
        expiry_dt = [expiry.strftime('%d')+'-'+expiry.strftime('%b')+'-'+str(expiry.year) for expiry in expiry_list]
#        print(expiry_dt)
        json_ce = eval("[data['CE'] for data in df['records']['data'] if 'CE' in data and data['expiryDate'] in " + str(expiry_dt) + "]")
        df_ce = json_normalize(json_ce)
#            print('*** NIFTY Call Options Data with Expiry Date: '+ expiry_dt + ' *** \n', df_ce)
        json_pe = eval("[data['PE'] for data in df['records']['data'] if 'PE' in data and data['expiryDate'] in " + str(expiry_dt) + "]")
        df_pe = json_normalize(json_pe)
#            print('*** NIFTY Put Options Data with Expiry Date: '+ expiry_dt + ' *** \n', df_pe)
        df = pd.merge(df_ce,df_pe,on=['strikePrice'],suffixes=['_Call','_Put'])
        df['expiryDate'] = df['expiryDate_Call']
        df.drop(['expiryDate_Call','expiryDate_Put'],axis=1,inplace=True)
#        df.sort_values(by=['expiryDate','strikePrice'],axis=1,inplace=True)            
        df.set_index('expiryDate',inplace=True)
        option_chain.append(df)
    if len(option_chain) > 0:
        option_chain = pd.concat(option_chain)
    else:
        option_chain = pd.DataFrame()
    return option_chain

def get_stored_stock_strategies(strategy_type=None):
    if strategy_type == None:
        sql = "select strategy_df from strategies order by date asc limit 1"
    else:
        sql = "select strategy_df from strategies where type='" + strategy_type + "' order by date desc limit 1"

    engine = sql_engine()
    df = engine.execute(sql).fetchall()
    if len(df) > 0:
        df = df[0][0]
        df = pd.read_csv(StringIO(df), sep='\s+')
        #        df['Expiry'] = pd.to_datetime(df['Expiry'],format='%Y-%m-%d').apply(lambda x: x.date())
        df = df.set_index('symbol')
    else:
        df = pd.DataFrame()
    return df


def get_stored_option_chain(name=None):
    if name == None:
        sql = "select oc from option_chain_history order by date desc limit 1"
    else:
        sql = "select oc from option_chain_history where symbol='" + name + "' order by date desc limit 1"

    engine = sql_engine()
    df = engine.execute(sql).fetchall()
    if len(df) > 0:
        df = df[0][0]
        df = pd.read_csv(StringIO(df), sep='\s+')
        df['Expiry'] = pd.to_datetime(df['Expiry'], format='%Y-%m-%d').apply(lambda x: x.date())
        df = df.set_index('Expiry')
    else:
        df = pd.DataFrame()
    return df


def getIndexQuote(symbol):
    nse = nsetools.Nse()
    indexQuote = nse.get_index_quote(symbol)['lastPrice']

    return float(indexQuote)


def getIndustry(symbol):
    sql = "select distinct industry from security_master where symbol = '" + symbol + "'"
    engine = sql_engine()
    industry = engine.execute(sql).fetchall()

    if (len(industry) > 0):
        return industry[0][0]
    else:
        return ""


def getSecMasterData(symbol):
    sql = "select distinct * from security_master where symbol = '" + symbol + "'"
    engine = sql_engine()
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
    engine = sql_engine(dbhost=db)
    for isin in isinlist:
        if isin != None:
            sql = sql + "'" + isin + "',"
    sql = sql[:-1] + ")"
    nav_df = pd.read_sql(sql, engine)
    nav_df.set_index('Date', inplace=True)
    return nav_df


def getTransactionCosts():
    cost = mrigstatics.TR_CHARGES['BROK'] \
           + mrigstatics.TR_CHARGES['STT/CTT'] \
           + mrigstatics.TR_CHARGES['EXCH'] \
           + mrigstatics.TR_CHARGES['GST'] * (mrigstatics.TR_CHARGES['BROK'] + mrigstatics.TR_CHARGES['EXCH'])

    return cost


def is_connected(url="www.google.com"):
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((url, 80))
        return True
    except OSError:
        pass
    return False


def generatekey(length=20):
    return ''.join([choice(string.ascii_letters + string.digits) for i in range(length)]) + str(
        datetime.datetime.timestamp(datetime.datetime.now())).replace('.', '_')


def mrigsession_write(to_write):
    now_tstamp = datetime.datetime.timestamp(datetime.datetime.now())
    prior_tstamp = datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(days=2))
    engine = sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])

    flushsql = "delete from  mrigsession where sessionexpiry <= " + str(prior_tstamp)

    engine.execute(flushsql)

    to_write = json.dumps(to_write)
    sessionid = generatekey(20)
    writesql = "insert into mrigsession values ('%s','%s',%s)"

    engine.execute(writesql % (sessionid, to_write, str(now_tstamp)))

    return sessionid


def mrigsession_get(to_get):
    engine = sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])

    getsql = "select sessionobj from  mrigsession where sessionid = '" + to_get + "'"

    sessionobj = engine.execute(getsql).fetchall()[0][0]
    sessionobj = json.loads(sessionobj)

    return sessionobj


def getStrikes(symbol):
    oc = get_stored_option_chain(symbol)

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

def getZerodhaChgs(tran_type='EQ_D',qty=0,buy=0,sell=0):
    charges = 0
    
    brokerage_flat = mrigstatics.ZERODHA_CHARGES[tran_type]['BROK_FLAT']
    brokerage_per = mrigstatics.ZERODHA_CHARGES[tran_type]['BROK_PER']
    stt_ctt = mrigstatics.ZERODHA_CHARGES[tran_type]['STT/CTT']
    exch = mrigstatics.ZERODHA_CHARGES[tran_type]['EXCH']
    gst = mrigstatics.ZERODHA_CHARGES[tran_type]['GST']
    sebi = mrigstatics.ZERODHA_CHARGES[tran_type]['SEBI']
    sell_val = sell*qty
    buy_val = buy*qty
    tran_val = buy_val + sell_val
    
    if tran_type == 'EQ_D':
        brokerage = min(brokerage_flat,brokerage_per*(buy_val + sell_val))
#        print(brokerage)
        stt_ctt_chgs = stt_ctt * (buy_val + sell_val)
#        print(stt_ctt_chgs)
        exch_chgs = exch * tran_val
#        print(exch_chgs)
        gst_chgs = gst * (brokerage + exch_chgs)
#        print(gst_chgs)
        sebi_chgs = sebi*(buy_val+sell_val)/10000000
#        print(sebi_chgs)
        charges = brokerage + stt_ctt_chgs + exch_chgs + gst_chgs + sebi_chgs
    if tran_type == 'EQ_I':
        brokerage = min(brokerage_flat,brokerage_per*buy_val) + min(brokerage_flat,brokerage_per*sell_val)
        stt_ctt_chgs = stt_ctt * sell_val
        exch_chgs = exch * (buy_val + sell_val)
        gst_chgs = gst * (brokerage + exch_chgs)
        sebi_chgs = sebi*(buy_val+sell_val)/10000000
        charges = brokerage + stt_ctt_chgs + exch_chgs + gst_chgs + sebi_chgs
    if tran_type == 'EQ_F':
        brokerage = min(brokerage_flat,brokerage_per*buy_val) + min(brokerage_flat,brokerage_per*sell_val)
        stt_ctt_chgs = stt_ctt * sell_val
        exch_chgs = exch * (buy_val + sell_val)
        gst_chgs = gst * (brokerage + exch_chgs)
        sebi_chgs = sebi*(buy_val+sell_val)/10000000
        charges = brokerage + stt_ctt_chgs + exch_chgs + gst_chgs + sebi_chgs
    if tran_type == 'EQ_O':
        brokerage = min(brokerage_flat,brokerage_per*buy_val) + min(brokerage_flat,brokerage_per*sell_val)
        stt_ctt_chgs = stt_ctt * sell_val
        exch_chgs = exch * (buy_val + sell_val)
        gst_chgs = gst * (brokerage + exch_chgs)
        sebi_chgs = sebi*(buy_val+sell_val)/10000000
        charges = brokerage + stt_ctt_chgs + exch_chgs + gst_chgs + sebi_chgs
    
    return [charges,brokerage,stt_ctt_chgs,exch_chgs,gst_chgs,sebi_chgs]

def optionChainHistorical(symbol_list,expiry_list=None,db='localhost'):
    option_chain = []
    """
    
Index(['askPrice_Call', 'askQty_Call', 'bidQty_Call', 'bidprice_Call',
       'change_Call', 'changeinOpenInterest_Call', 'identifier_Call',
       'impliedVolatility_Call', 'lastPrice_Call', 'openInterest_Call',
       'pChange_Call', 'pchangeinOpenInterest_Call', 'strikePrice',
       'totalBuyQuantity_Call', 'totalSellQuantity_Call',
       'totalTradedVolume_Call', 'underlying_Call', 'underlyingValue_Call',
       'askPrice_Put', 'askQty_Put', 'bidQty_Put', 'bidprice_Put',
       'change_Put', 'changeinOpenInterest_Put', 'identifier_Put',
       'impliedVolatility_Put', 'lastPrice_Put', 'openInterest_Put',
       'pChange_Put', 'pchangeinOpenInterest_Put', 'totalBuyQuantity_Put',
       'totalSellQuantity_Put', 'totalTradedVolume_Put', 'underlying_Put',
       'underlyingValue_Put'],
      dtype='object')
    """
    sql = "select * from futures_options_history where date >= (select date from futures_options_history order by date desc limit 1) \
           and option_type in ('CE','PE')"

    column_map = {'close':'lastPrice',
                  'oi':'openInterest',
                  'oi_change':'changeinOpenInterest',
                  'expiry':'expiryDate',
                  'strike':'strikePrice'}
    
    engine = sql_engine(dbhost=db)
    op_df = pd.read_sql(sql, engine)
    if not op_df.empty:
        op_df.drop(['open','high','low'],axis=1,inplace=True)
        op_df.rename(columns=column_map,inplace=True)
        op_df = op_df[op_df.symbol.isin (symbol_list)]
        if expiry_list != None:
            op_df = op_df[op_df.expiryDate.isin (expiry_list)]
        op_df_ce = op_df[op_df['option_type'] == 'CE']
        op_df_pe = op_df[op_df['option_type'] == 'PE']
        op_df = pd.merge(op_df_ce,op_df_pe,on=['strikePrice'],suffixes=['_Call','_Put'])
        op_df = op_df[(op_df['symbol_Call'] == op_df['symbol_Put'])] 
        op_df = op_df[(op_df['expiryDate_Call'] == op_df['expiryDate_Put'])]
        op_df['expiryDate'] = op_df['expiryDate_Call']
        op_df['valDate'] = op_df['date_Call']
        op_df['symbol'] = op_df['symbol_Call']
        op_df.drop(['expiryDate_Call','expiryDate_Put','instrument_Call','instrument_Put','symbol_Call','symbol_Put','date_Call','date_Put'],axis=1,inplace=True)
        op_df.sort_values(by=['symbol','expiryDate','strikePrice'], inplace=True)
        op_df.set_index('expiryDate',inplace=True)
        option_chain = op_df
        
        ## Populate with latest prices
        
        # op_df.reset_index(inplace=True)
        
        # for i in op_df.index:
        #     expiry = op_df.loc[i]['expiryDate']
        #     scrip = op_df.loc[i]['symbol']
        #     strikeP = op_df.loc[i]['strikePrice']
        #     call_ltp = getStockOptionQuote(scrip,expiry,strikeP,'CE')
        #     # print(call_ltp)
        #     put_ltp = getStockOptionQuote(scrip,expiry,strikeP,'PE')
        #     # print(put_ltp)
        #     try:
        #         op_df.loc[i,'lastPrice_Call'] = call_ltp['lastPrice']
        #     except:
        #         pass
        #     try:
        #         op_df.loc[i,'lastPrice_Put'] = put_ltp['lastPrice']
        #     except:
        #         pass
        # op_df.set_index('expiryDate',inplace=True)
        # option_chain = op_df
        
        # for i in range(0,len(stock_df.index)-1):
        #   stock_df.index[i] = datetime.datetime.combine(stock_df.index[i], datetime.time())

    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    
    return option_chain

def marketLot(symbol):
        engine = sql_engine()
        lot = engine.execute("select lot from futures_option_lots where symbol='"+symbol+"' limit 1").fetchall()[0][0]
        
        return int(lot)

'''
------Fractals
A fractal is a candlestick pattern made by 5 candles. The third candle has the lowest low price, 
the previous candles have decreasing lows and the next candles have increasing lows. 
By this pattern, the low of the third candle is the support level. The same concept
 applies to resistance levels, where the third candle has the highest high of the five ones.

------Windows Shifting Method 
we take a window of 9 candles (illustrated by the yellow box) and find the maximum of the 
candles within the window. Then, shift the window up a candle (the green box) and find
the maximum of the candles within the window. Do the same until you have shifted 5 times.
If the candle with the highest value remains the same throughout the steps, we have 
a pivot point.
 
Result - Each level is a tuple whose first element is the index of the signal candle and the
second element is the price value. 
 
'''

def getLevels(name,startdate=(datetime.date.today() - datetime.timedelta(days=365)),
              enddate=datetime.date.today(),
              method='fractal'):
    yahoomap = {'NIFTY': '^NSEI',
                'NIFTY 50': '^NSEI',
                'BANKNIFTY': '^NSEBANK',
                'NIFTY BANK': '^NSEBANK',}

    if name in ['NIFTY', 'BANKNIFTY','NIFTY 50','NIFTY BANK']:
        yahooscrip = yahoomap[name]
    else:
        yahooscrip = name + '.NS'
    ticker = yf.Ticker(yahooscrip)
    start, end = startdate.strftime('%Y-%m-%d') , enddate.strftime('%Y-%m-%d')
    df = ticker.history(interval="1d",start=start, end=end)
    df['Date'] = pd.to_datetime(df.index)
    df['Date'] = df['Date'].apply(mpl_dates.date2num)
    df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]
    
    s =  np.mean(df['High'] - df['Low'])
    
    def isFarFromLevel(l):
       return np.sum([abs(l-x) < s  for x in levels]) == 0
   
    def isSupport(df,i):
      support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
      return support

    def isResistance(df,i):
      resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
      return resistance

    if method == 'fractal':
    
        levels = []
        for i in range(2,df.shape[0]-2):
          if isSupport(df,i):
            l = df['Low'][i]
            if isFarFromLevel(l):
              levels.append((i,round(l)))
          elif isResistance(df,i):
            l = df['High'][i]
            if isFarFromLevel(l):
              levels.append((i,round(l)))
    else:
        levels = []
        max_list = []
        min_list = []
            # to make sure the new level area does not exist already
        def is_far_from_level(value, levels, df):    
          ave =  np.mean(df['High'] - df['Low'])    
          return np.sum([abs(value-level)<ave for _,level in levels])==0
        for i in range(5, len(df)-5):
          # taking a window of 9 candles
          high_range = df['High'][i-5:i+4]
          current_max = high_range.max()
          # if we find a new maximum value, empty the max_list 
          if current_max not in max_list:
            max_list = []
          max_list.append(current_max)
          # if the maximum value remains the same after shifting 5 times
          if len(max_list)==5 and is_far_from_level(current_max,levels,df):
              # levels.append((high_range.idxmax(), current_max))
              levels.append((i, round(current_max)))

          low_range = df['Low'][i-5:i+5]
          current_min = low_range.min()
          if current_min not in min_list:
            min_list = []
          min_list.append(current_min)
          if len(min_list)==5 and is_far_from_level(current_min,levels,df):
            # levels.append((low_range.idxmin(), current_min))
            levels.append((i, round(current_min)))
            
    return [levels,df]
    

def bs_price(S,K,T,sigma,r=0.05,opt='CE'):
    # print( 'S  ---> '+str(S)+'   K  ---> '+str(K)+'   T  ---> '+str(T))
    if (opt == 'FUT'):
        return 0
    else:
        d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
        d2=d1-(sigma*np.sqrt(T))
        if opt == 'CE':
            BSprice = S*si.norm.cdf(d1,0,1)-K*np.exp(-r*T)*si.norm.cdf(d2,0,1)
        else:
            BSprice = K*np.exp(-r*T)*si.norm.cdf(-d2,0,1) - S*si.norm.cdf(-d1,0,1)
    return BSprice

def bs_delta(S,K,T,sigma,r=0.05,opt='CE'):
    # print( 'S  ---> '+str(S)+'   K  ---> '+str(K)+'   T  ---> '+str(T))
    if (opt == 'FUT'):
        return 1
    else:
        d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
        d2=d1-(sigma*np.sqrt(T))
        if opt == 'CE':
            delta = si.norm.cdf(d1,0,1)
        else:
            delta = si.norm.cdf(d1,0,1) - 1
    return delta

def bs_theta(S,K,T,sigma,r=0.05,opt='CE'):
    # print( 'S  ---> '+str(S)+'   K  ---> '+str(K)+'   T  ---> '+str(T))
    if (opt == 'FUT'):
        return 0
    else:
        d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
        d2=d1-(sigma*np.sqrt(T))
        N_d1 = np.exp(-(d1**2)/2)/np.sqrt(2*math.pi)
        # print(N_d1)
        if opt == 'CE':
            theta = (-(S * sigma * N_d1) / (2 * np.sqrt(T)) 
             - r * K * np.exp(-r * T) * si.norm.cdf(d2,0,1)) / 365
        else:
            theta = (-(S * sigma * N_d1) / (2 * np.sqrt(T)) 
             + r * K * np.exp(-r * T) * si.norm.cdf(-d2,0,1)) / 365
    return theta


def impVol(S,K,T,option_price,r=0.05,opt='CE'):
    def diff(sigma):
        return bs_price(S, K, T, sigma,r,opt) - option_price
    if (opt == 'FUT'):
        return 0
    else:
        vol = -1
        try:
            vol = optimize.brentq(diff,0.0001,100,maxiter=1000)
            # print('Vol -->'+str(vol))
        except:
            pass
    return vol

def insert_on_conflict_nothing(table, conn, keys, data_iter):
    # "a" is the primary key in "conflict_table"
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=table.index)
    # stmt = insert(table.table).values(data).on_conflict_do_nothing()
    result = conn.execute(stmt)
    return result.rowcount

def find_atm(spot,strike_diff):
    # diff = 2.5
    divisor = strike_diff
    cnt = 1
    while divisor%5 != 0:
        divisor *= cnt
        cnt += 1

    a1 = int(round(spot/divisor)*divisor/divisor)*divisor
    atm = a1
    if abs(spot-atm-strike_diff) < strike_diff/2:
        atm += strike_diff
    return atm

def getKiteSession():
    # datadir = os.path.dirname(__file__)
    # settings_files_path = os.path.join(datadir,"kite_settings.json")
    # file = open(settings_files_path)
    # enctoken = json.load(file)
    # token = enctoken["encauth"]

    engine = sql_engine()
    auth = pd.read_sql("select token from auth where vendor='zerodha'",engine)
    token = auth['token'].values[0]
    kite_object = zkite.mrigkite()
    session = kite_object.kite
    # print(token)
    # session = zkite.KiteApp(enctoken=token)
    quote = session.quote('NSE:NIFTY 50')
    if quote is not None:
        print('connection active')
    else:
        print('no connection')
        session = None
    # if session is not None:
    #     print(token)
    return session


def getExpiry(**kwargs):
    engine = sql_engine()
    scrip_list = []
    instrument_list = []
    args = kwargs
    print(args)
    if 'scrip' in kwargs.keys():
        scrip_list.append(kwargs['scrip'])
    if 'scriplist' in kwargs.keys():
        scrip_list = scrip_list + kwargs['scriplist']
    if 'instrument' in kwargs.keys():
        instrument_list.append(kwargs['instrument'])
    if 'instrumentlist' in kwargs.keys():
        instrument_list = instrument_list + kwargs['instrumentlist']

    scrip_list = scrip_list if len(scrip_list) > 0 else ['-99']
    instrument_list = instrument_list if len(instrument_list) > 0 else ['-99']

    scrip_list = str(scrip_list).replace('[', '(').replace(']', ')')
    instrument_list = str(instrument_list).replace('[', '(').replace(']', ')')

    sql = "select instrument_token,tradingsymbol,name,expiry from market_instruments \
    where (name in {} or tradingsymbol in {}) \
    and instrument_date = (select max(instrument_date) from market_instruments)".format(scrip_list, instrument_list)

    expiry_df = pd.read_sql(sql, engine)

    return expiry_df
    # print(expiry_df)


getExpiry(scrip='NIFTY', instrumentlist=['BANKNIFTY24JUNFUT'])


def kite_OC(scrips=['NIFTY'],expiry=None):
    session = getKiteSession()
    ins = session.instruments(exchange='NFO')
    if expiry is None:
        expiry = [last_thursday_of_month(datetime.date.today())]
    inspd = pd.DataFrame(ins)
    # inspd = inspd[(inspd['name'] == scrip) & (inspd['expiry'] == expiry) & (inspd['strike'] >= 18000) & (inspd['strike'] <= 20500) ][['tradingsymbol','strike']]
    # inspd = inspd[inspd['name'].isin(scrip)]
    # # print(inspd)
    # inspd = inspd[inspd['expiry'].isin(expiry)]
    # print(inspd)
    # inspd = inspd[(inspd['strike'] > 0)][['tradingsymbol', 'strike','expiry']]


    inspd = inspd[(inspd['name'].isin(scrips)) & (inspd['expiry'].isin(expiry)) & (inspd['strike'] > 0)][['name','tradingsymbol', 'strike','expiry']]
    inspd['tradingsymbol'] = 'NFO:' + inspd['tradingsymbol']
    inspd.set_index('tradingsymbol', inplace=True)
    inslist= []
    for scrip in scrips:
        for exp in expiry:
            inslist_i = list(inspd[(inspd['name'] == scrip) & (inspd['expiry'] == exp)].index)
            inslist.append(inslist_i[int(len(inslist_i) / 2 - len(inslist_i) / 4):int(len(inslist_i) / 2 + len(inslist_i) / 4)])
    qt = None
    try:
        qt = session.quote(inslist)
    except:
        pass
    if qt is not None:
        oc = pd.DataFrame(qt).T
        oc.index.name = 'tradingsymbol'
        oc1 = oc.merge(inspd, on='tradingsymbol')[['name','strike', 'oi', 'volume', 'last_price','expiry']]
        return oc1
    else:
        return None


def kite_OC_new(scrips=['NIFTY']):
    session = getKiteSession()
    # ins = session.instruments(exchange='NFO')

    inspd = getExpiry(scriplist=scrips)
    inspd.set_index('instrument_token', inplace=True)
    inspd.index = inspd.index.map(str)

    qt = {}
    for scrip in scrips:
        print(scrip)
        for exp in sorted(set(inspd['expiry'])):
            qt = qt | session.quote(inspd[(inspd['name'] == scrip) & (inspd['expiry'] == exp)]['instrument_token'])

    if qt is not None:
        oc = pd.DataFrame(qt).T
        oc.set_index('instrument_token', inplace=True)
        oc.index = oc.index.map(str)
        oc1 = pd.merge(inspd, oc, left_index=True, right_index=True)
        return oc1
    else:
        return None


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
    engine = sql_engine()
    members = []
    try:
        members = engine.execute("select index_members from stock_history where symbol=%s order by date desc limit 1",(index)).fetchall()[0][0]
    except:
        pass
    return members
if __name__ == '__main__':
#    print(getZerodhaChgs('EQ_D',8,0,310.35))
    # expiries_i = [datetime.date(2021,9,30),datetime.date(2021,6,10)]
    # expiries_e = [datetime.date(2021,6,24),datetime.date(2021,7,29)]
#    oc = optionChainLive([('NIFTY','I')],expiries_i)
#    oc = optionChainHistorical(['BANKNIFTY'])#,expiries_i+expiries_e)
#    oc.sort_values(['expiryDate'],axis=0,inplace=True)
#    oc.to_csv('oc_live.csv')        
#    print(oc.columns)
#    print(oc.tail(10))
#     expiry1 = last_thursday_of_month(datetime.date.today())
#     expiry2 = last_thursday_of_month(expiry1 + datetime.timedelta(days=30))
#     expiry3 = last_thursday_of_month(expiry2 + datetime.timedelta(days=30))
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

    # print(getStockQuote('TATAPOWER'))
    print(getIndexMembers('NIFTY BANK'))
