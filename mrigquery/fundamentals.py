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


def getResults(symbol, period_start=None, period_end=None, period_type='Quarterly'):
    export_dir = os.path.join('downloads')
    end_date = datetime.date.today()
    if period_end is not None:
        end_date = datetime.datetime.strptime(period_end, '%Y-%m-%d')
    if period_start is not None:
        start_date = datetime.datetime.strptime(period_start, '%Y-%m-%d')
    else:
        start_date = end_date - datetime.timedelta(days=368)

    sql = "select results from financial_results where symbol='{}' and " \
          "period_ended >= '{}' and period_ended <= '{}' and period='{}' and " \
          "timestamp = (select max(timestamp) from financial_results where symbol= '{}') "
    results = pd.read_sql(
        sql.format(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), period_type, symbol), mu.engine)
    result = pd.DataFrame()
    for inx in results.index:
        finres = pd.DataFrame.from_dict(json.loads(results.loc[inx]['results']), orient='index')
        finres.rename(columns={0: finres.loc['DateOfEndOfReportingPeriod'][0]}, inplace=True)
        result = pd.concat([result, finres], axis=1)

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    export_file = os.path.join(export_dir, symbol + "_" + start_date.strftime('%Y%m%d') + "_" + end_date.strftime(
        '%Y%m%d') + "_" + period_type + "_" + timestamp + ".csv")
    print(result)
    result.to_csv(export_file)
    return result
