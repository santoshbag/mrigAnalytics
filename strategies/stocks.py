# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:37:47 2018

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

class Stock():
    def __init__(self,name):
        self.symbol = name
        
    
    def get(self,period='1Y'):
        today = datetime.date.today()
        years=0
        months=0
        weeks=0
        days=0
        
        if period[-1] == 'Y':
            years = int(period[:-1])
        if period[-1] == 'M':
            months = int(period[:-1])
        if period[-1] == 'W':
            weeks = int(period[:-1])
        if period[-1] == 'D':
            days = int(period[:-1])

        startdate = today - dateutil.relativedelta.relativedelta(years=years,
                                                                 months=months,
                                                                 weeks=weeks,
                                                                 days=days)
        print(startdate)
        self.pricevol_data = mu.getStockData(self.symbol,
                                           startdate,
                                           today)
        self.pricevol_data['daily_logreturns'] = np.log(self.pricevol_data['close']/self.pricevol_data['close'].shift(1))
        sql = "select * from ratios where symbol='" + self.symbol + "'"
        
        engine = mu.sql_engine()
        self.ratio_data = pd.read_sql(sql,engine)
        if not self.ratio_data.empty:
            self.ratio_data.set_index('ratio_date',inplace=True)

def stock_adjust():
    
    #List of Stocks to adjust
    today = datetime.date.today()
    engine = mu.sql_engine()
    
    sql = "select symbol, ex_date, factor from corp_action_view"
    updates = engine.execute(sql).fetchall()
    
    sql = ""
    for update in updates:
        stock = update[0]
        exdate = update[1]
        factor = update[2]
        
        sql = sql + " UPDATE stock_history set "\
            + " close_adj = close * "+str(factor)+", "\
            +" volume_adj = volume /"+str(factor)+" "\
            +" where symbol = '"+stock+"' "\
            +" and date < '"+exdate.strftime('%Y-%m-%d')+"'; "
    
    
    #print(sql)
    engine.execute(sql)

if __name__ == '__main__':
    stock_adjust()