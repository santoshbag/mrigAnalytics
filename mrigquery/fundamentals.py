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

engine = mu.sql_engine()
def getResults(symbol, period_start=None, period_end=None, period_type='Quarterly',result_type='all',export=False):
    '''

    :param symbol:
    :param period_start:
    :param period_end:
    :param period_type: "Quarterly", "Annual"
    :param result_type: 'all','income_statement','ratios'
    :param export: True, False : Export to excelfile
    :return: DF of results with columns as Date and Rows as result items
    '''

    export_dir = os.path.join('downloads')
    end_date = datetime.date.today()

    xbrl_map = json.load(open(os.path.join(os.path.dirname(__file__), 'xbrl_map.json')))

    if period_end is not None:
        end_date = datetime.datetime.strptime(period_end, '%Y-%m-%d')
    if period_start is not None:
        start_date = datetime.datetime.strptime(period_start, '%Y-%m-%d')
    else:
        if period_type == 'Annual':
            start_date = end_date - datetime.timedelta(days=368*4)
        else:
            start_date = end_date - datetime.timedelta(days=368)

    sql = "select results from financial_results where symbol='{}' and " \
          "period_ended >= '{}' and period_ended <= '{}' and period='{}' order by period_ended desc"
    results = pd.read_sql(
        sql.format(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), period_type, symbol),engine )
    result = pd.DataFrame()
    for inx in results.index:
        finres = pd.DataFrame.from_dict(json.loads(results.loc[inx]['results']), orient='index')
        finres.rename(columns={0: finres.loc['DateOfEndOfReportingPeriod'][0]}, inplace=True)
        result = pd.concat([result, finres], axis=1)
    # print(result)

    if export:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        export_file = os.path.join(export_dir, symbol + "_" + start_date.strftime('%Y%m%d') + "_" + end_date.strftime(
            '%Y%m%d') + "_" + period_type + "_" + timestamp + ".csv")
        # print(result)
        result.to_csv(export_file)

    if result_type == 'income_statement':
        df = pd.DataFrame()
        # for i in range(1,10):
        for k in xbrl_map['income_statement'].keys():
            # if str(i) in xbrl_map['income_statement'].keys():
            # print(xbrl_map['income_statement'][str(i)])
            for inx in result.index:
                val = list(xbrl_map['income_statement'][k].values())[0]
                keys = list(xbrl_map['income_statement'][k].keys())[0]
                # print(inx,val)
                if inx in val:
                    # print(inx, val)
                    df = pd.concat([df, result.loc[inx].rename(index=keys)], axis=1)
        result = df.transpose()

    if result_type == 'assets':
        df = pd.DataFrame()
        # for i in range(1,10):
        for k in xbrl_map['bs_assets'].keys():
            # if str(i) in xbrl_map['income_statement'].keys():
            # print(xbrl_map['income_statement'][str(i)])
            for inx in result.index:
                val = list(xbrl_map['bs_assets'][k].values())[0]
                keys = list(xbrl_map['bs_assets'][k].keys())[0]
                # print(inx,val)
                if inx in val:
                    # print(inx, val)
                    df = pd.concat([df, result.loc[inx].rename(index=keys)], axis=1)
        result = df.transpose()

    if result_type == 'liabilities':
        df = pd.DataFrame()
        # for i in range(1,10):
        for k in xbrl_map['bs_liabilities'].keys():
            # if str(i) in xbrl_map['income_statement'].keys():
            # print(xbrl_map['income_statement'][str(i)])
            for inx in result.index:
                val = list(xbrl_map['bs_liabilities'][k].values())[0]
                keys = list(xbrl_map['bs_liabilities'][k].keys())[0]
                # print(inx,val)
                if inx in val:
                    # print(inx, val)
                    df = pd.concat([df, result.loc[inx].rename(index=keys)], axis=1)
        result = df.transpose()

    if result_type == 'ratios':
        df = pd.DataFrame()
        # for i in range(1,10):
        for k in xbrl_map['ratios']:
            # if str(i) in xbrl_map['income_statement'].keys():
            # print(xbrl_map['income_statement'][str(i)])
            for inx in result.index:
                val = list(k.values())[0]
                keys = list(k.keys())[0]
                # print(inx,val)
                if inx in val:
                    df = pd.concat([df, result.loc[inx].rename(index=keys)], axis=1)
        result = df.transpose()

    return result

def getIncomeStatement(symbol):
    res = getResults(symbol)
    xbrl_map = json.load(open('xbrl_map.json'))
    # print(xbrl_map['income_statement'])
    df = pd.DataFrame()
    # for i in range(1,10):
    for k in xbrl_map['income_statement'].keys():
        # if str(i) in xbrl_map['income_statement'].keys():
            # print(xbrl_map['income_statement'][str(i)])
        for inx in res.index:
            val = list(xbrl_map['income_statement'][k].values())[0]
            keys = list(xbrl_map['income_statement'][k].keys())[0]
            # print(inx,val)
            if inx in val:
                df = pd.concat([df,res.loc[inx].rename(index=keys)],axis=1)
    # print(df.transpose())
    return(df.transpose())




if __name__ == '__main__':
    sym = 'HDFCBANK'
    # print(getResults(sym,result_type='income_statement'))
    print(getResults(sym,result_type='assets',period_type='Annual'))
    print(getResults(sym,result_type='liabilities',period_type='Annual'))

    # print(getResults(sym,result_type='ratios'))

    # print(getIncomeStatement('ICICIBANK'))

