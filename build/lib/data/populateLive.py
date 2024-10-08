# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 12:49:11 2019

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import nsepy
import pandas as pd
import datetime
import mrigutilities as mu
import mrigstatics
import json
import time
import moneycontrol as mc 

def populateStock():
    today = datetime.date.today()
    starttime = time.monotonic()
    engine = mu.sql_engine()
    stocklist = engine.execute("select distinct sm.symbol, sm.stock_name from security_master sm inner join stock_history sh on sm.symbol=sh.symbol where sh.series='EQ'").fetchall()
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
           
#    stocklist = [('ANDHRACEMT',),('NILKAMAL',),('ADORWELD',)]
    for stock in stocklist:
        symbol = str(stock[0]).strip()
        sql = "insert into live (date,symbol,quote,open,previousclose, dayhigh, daylow, high52, low52, metadata) values "
        try:
            quote = nsepy.get_quote(symbol)
            sql = sql + "('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')," %(today.strftime('%Y-%m-%d'),symbol,quote['lastPrice'],quote['open'],
                          quote['previousClose'],quote['dayHigh'],quote['dayLow'],
                          quote['high52'],quote['low52'],json.dumps(quote))
            sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT live_pkey DO UPDATE SET \
                         quote=EXCLUDED.quote, \
                         open=EXCLUDED.open, \
                         previousClose=EXCLUDED.previousClose, \
                         dayHigh=EXCLUDED.dayHigh, \
                         dayLow=EXCLUDED.dayLow, \
                         high52=EXCLUDED.high52, \
                         low52=EXCLUDED.low52, \
                         metadata=EXCLUDED.metadata"
        #    print(sql)
            engine.execute(sql)
        except:
            pass
    elapsed = time.monotonic() - starttime
    print("Time Taken for Stock load %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
    
def populateIndex():
    today = datetime.date.today()
    starttime = time.monotonic()
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    stocklist = ['NIFTY 50']
           
#    stocklist = [('ANDHRACEMT',),('NILKAMAL',),('ADORWELD',)]
    for stock in stocklist:
        symbol = str(stock).strip()
        sql = "insert into live (date,symbol,quote,open,previousclose, dayhigh, daylow, high52, low52, metadata) values "
        try:
            quote = mc.get_NSELive()
#            print(quote)
            sql = sql + "('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')," %(today.strftime('%Y-%m-%d'),symbol,quote['lastPrice'],quote['open'],
                          quote['previousclose'],quote['dayhigh'],quote['daylow'],
                          quote['high52'],quote['low52'],json.dumps(quote))
            sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT live_pkey DO UPDATE SET \
                         quote=EXCLUDED.quote, \
                         open=EXCLUDED.open, \
                         previousClose=EXCLUDED.previousClose, \
                         dayHigh=EXCLUDED.dayHigh, \
                         dayLow=EXCLUDED.dayLow, \
                         high52=EXCLUDED.high52, \
                         low52=EXCLUDED.low52, \
                         metadata=EXCLUDED.metadata"
        #    print(sql)
            engine.execute(sql)
        except:
            pass
    elapsed = time.monotonic() - starttime
    print("Time Taken for Index load %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
    
def populateStockOption():
    today = datetime.date.today()
    starttime = time.monotonic()
    engine = mu.sql_engine()
    sql = "select distinct symbol from stock_history"
    stocklist = engine.execute(sql).fetchall()
    
#    stocklist = [('ICICIBANK',),('BATAINDIA',)]
    sql = "insert into live (date,symbol,quote,open,previousclose, metadata) values "
    for stock in stocklist:
        symbol = str(stock[0]).strip()
        oc = mu.get_stored_option_chain(symbol)
        try:
            quote = nsepy.get_quote(symbol)
            sql = sql + "('%s','%s','%s','%s','%s','%s')," %(today.strftime('%Y-%m-%d'),symbol,quote['lastPrice'],quote['openPrice'],
                          quote['prevClose'],json.dumps(quote))
        except:
            pass
    sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT live_pkey DO UPDATE SET \
                 quote=EXCLUDED.quote, \
                 open=EXCLUDED.open, \
                 previousClose=EXCLUDED.previousClose, \
                 metadata=EXCLUDED.metadata"
#    print(sql)
    engine.execute(sql)
    elapsed = time.monotonic() - starttime
    print("Time Taken %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
    
if __name__ == '__main__':
    populateIndex()
    populateStock()
#    populateStockOption()
