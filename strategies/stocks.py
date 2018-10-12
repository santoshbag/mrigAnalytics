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
        
    
    def get_price_vol(self,period='1Y'):
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
        self.pricevol_data['daily_logreturns'] = np.log(self.pricevol_data['close_adj']/self.pricevol_data['close_adj'].shift(1))

    def get_returns(self,period='1Y'):
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

        sql = "select date, daily_log_returns from daily_returns where symbol='" + self.symbol + "' and date >='"+startdate.strftime('%Y-%m-%d')+"'"

        engine = mu.sql_engine()
        self.daily_logreturns = pd.read_sql(sql,engine)
        if not self.daily_logreturns.empty:
            self.daily_logreturns.set_index('date',inplace=True)

        
    def get_ratios(self):    
        sql = "select * from ratios where symbol='" + self.symbol + "' and download_date = "\
              + " ( select download_date from ratios where symbol='" + self.symbol + "' order by download_date desc limit 1)"
        
        engine = mu.sql_engine()
        self.ratio_data = pd.read_sql(sql,engine)
        if not self.ratio_data.empty:
            self.ratio_data.set_index('ratio_date',inplace=True)

def stock_adjust():
    
    #List of Stocks to adjust
    today = datetime.date.today()
    engine = mu.sql_engine()
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"

    sql = "select symbol, ex_date, factor from corp_action_view order by symbol desc, ex_date desc" #where download_date = (select download_date from corp_action_view order by download_date desc limit 1)"
    
    engine.execute(disable_sql)                                                                                     
    updates = engine.execute(sql).fetchall()
    
    sql = ""
    for update in updates:
        stock = update[0]
        exdate = update[1]
        factor = update[2]
        
        if exdate <=today:
            sql = sql + " UPDATE stock_history set "\
                + " close_adj = close * "+str(factor)+", "\
                +" volume_adj = volume /"+str(factor)+" "\
                +" where symbol = '"+stock+"' "\
                +" and date < '"+exdate.strftime('%Y-%m-%d')+"'; "
    

    #print(sql)
    engine.execute(sql)
    engine.execute(enable_sql)

if __name__ == '__main__':
    stock_adjust()