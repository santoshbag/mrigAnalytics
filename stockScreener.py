# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime, dateutil.relativedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import research.math as rm

today = datetime.date.today()
engine = mu.sql_engine()

"""
BIG MONEY ZACK screener

Min 20-day trading volume > 50,000
Log return of 24 weeks : top 20
Log return of 12 weeks : top 10
Log return of 4 weeks : top 3
"""
startdate = today - dateutil.relativedelta.relativedelta(weeks=27)

volumedate = today - datetime.timedelta(days=20)
sql = "select symbol from (select symbol, min(volume) as minvol from stock_history where series='EQ' and date > '"+volumedate.strftime('%Y-%m-%d') +"' group by symbol) as foo where minvol > 50000"
sql = "select  date, symbol, close_adj, volume_adj, daily_log_returns from stock_returns_adj where date > '"+startdate.strftime('%Y-%m-%d') + "' and symbol in ("+sql+")"
stock_df = pd.read_sql(sql,engine)
if not stock_df.empty:
    #for i in range(0,len(stock_df['date'])-1):
    #    stock_df.iloc[i]['date'] = datetime.datetime.combine(stock_df.iloc[i]['date'],datetime.time())
    #stock_df.date = pd.DatetimeIndex(stock_df.date)
    stock_df.set_index(['date','symbol'],inplace=True)
start = today -dateutil.relativedelta.relativedelta(weeks=24)
returns = stock_df.reset_index().pivot('date','symbol','daily_log_returns')
ret24W = returns[start:].sum()
ret24W.name = 'ret24W'

start = today -dateutil.relativedelta.relativedelta(weeks=12)
returns = stock_df.reset_index().pivot('date','symbol','daily_log_returns')
ret12W = returns[start:].sum()
ret12W.name = 'ret12W'

start = today -dateutil.relativedelta.relativedelta(weeks=4)
returns = stock_df.reset_index().pivot('date','symbol','daily_log_returns')
ret4W = returns[start:].sum()
ret4W.name = 'ret4W'

stockreturns = pd.concat([ret24W,ret12W,ret4W],axis=1)

stockreturns = stockreturns.sort_values(by='ret24W',ascending=0).head(20)
#print(stockreturns)
stockreturns = stockreturns.sort_values(by='ret12W',ascending=0).head(10)
stockreturns = stockreturns.sort_values(by='ret4W',ascending=0).head(3)

bigmoneyzack_stocks = list(stockreturns.index)
print(bigmoneyzack_stocks)
for i in bigmoneyzack_stocks:
    stock_df.xs(i,level='symbol')['close_adj'].plot()
    

