# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 13:31:31 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities as mu

arguments = sys.argv[1:]

startdate= datetime.date(2017,1,1)
enddate= datetime.date(2018,11,23)

try:
    startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
    enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
except:
    pass

disable_sql = "alter table stock_history disable trigger return_trigger"
enable_sql = "alter table stock_history enable trigger return_trigger"

#select stocks list
sql = "select distinct symbol from stock_history where series = 'EQ' and date >= '%s' and date <= '%s' "
#print(sql %(startdate.strftime('%Y-%m-%d'),enddate.strftime('%Y-%m-%d')))
engine = mu.sql_engine()
engine.execute(disable_sql)
codes = engine.execute(sql %(startdate.strftime('%Y-%m-%d'),enddate.strftime('%Y-%m-%d'))).fetchall()
codes = [code[0] for code in codes]
#print(codes)
stocksdata = DataFrame()
#codes=['TCS']
for symbol in codes:
    print(symbol)
    sql = " select weekday from (select a::date as weekday \
            from generate_series('%s'::date, '%s', '1 days') s(a) \
            where extract(dow from a) in (1,2,3,4,5)) weekdays\
            where weekday not in \
            (select distinct date from stock_history sh where symbol = '%s')"
    missingdates = engine.execute(sql %(startdate.strftime('%Y-%m-%d'),enddate.strftime('%Y-%m-%d'),symbol)).fetchall()
    missingdates = [missingdate[0] for missingdate in missingdates]
    for missingdate in missingdates:
#        print(missingdate)
        try:
            stockdata = nsepy.get_history(symbol=symbol,start=missingdate,end=missingdate)
            stocksdata = stocksdata.append(stockdata)
#            print(stockdata)
        except:
            pass
try:
    stocksdata.index.rename('date',inplace=True)
    stocksdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
    #   stocksdata = mu.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
    #    stocksdata = stocksdata[0]
    stocksdata['close_adj'] = stocksdata['close']
    stocksdata['volume_adj'] = stocksdata['volume']
    print(stocksdata)
    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
except:
    pass
#if __name__ == '__main__':
    
