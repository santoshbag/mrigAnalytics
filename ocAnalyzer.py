# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime, dateutil.relativedelta, time
import pandas as pd
import mrigstatics
#import matplotlib.pyplot as plt
import statsmodels.api as sm
import research.math as rm
import strategies.stocks as st
from concurrent.futures import ThreadPoolExecutor as Executor
import nsepy
import numpy as np
from time import sleep

today = datetime.date.today()
engine = mu.sql_engine(dbhost='SIRIUS')

def short_trend():
    
    sql="select oi_date,client,instrument, ((sum(oi) filter (where long_short='long')) - \
    (sum(oi) filter (where long_short='short'))) as net_oi,(select close from stock_history\
    where date=fo.oi_date and symbol='NIFTY 50') as nifty,(select close from stock_history where\
    date=fo.oi_date and symbol='NIFTY BANK') as banknifty   from fo_oi_participants fo \
    group by oi_date,instrument,client order by oi_date desc, client,instrument;"
    
    startdate = today - dateutil.relativedelta.relativedelta(weeks=27)
    
    volumedate = today - datetime.timedelta(days=20)
    
    oc_df = []
    oc_df_cols = ['date','futures_DII','futures_FII','futures_Pro','option_FII','option_Pro','nifty','banknifty']
    stock_df = pd.read_sql(sql,engine)
    if not stock_df.empty:
        stock_df_piv= stock_df.pivot_table(index='oi_date',columns=['instrument','client'])#, values='net_oi')
        oc_df.append(list(stock_df_piv.index))
        oc_df.append(list(stock_df_piv['net_oi','futures','DII']))
        oc_df.append(list(stock_df_piv['net_oi','futures','FII']))
        oc_df.append(list(stock_df_piv['net_oi','futures','Pro']))
        oc_df.append(list(stock_df_piv['net_oi','option','FII']))
        oc_df.append(list(stock_df_piv['net_oi','option','Pro']))
        oc_df.append(list(stock_df_piv['nifty','futures','FII']))
        oc_df.append(list(stock_df_piv['banknifty','futures','Pro']))
        
        #Transpose the list
        oc_df = list(map(list, zip(*oc_df))) 
        oc_df = pd.DataFrame(oc_df,columns=oc_df_cols)
        oc_df.set_index('date',inplace=True)
        oc_df['futures_daily'] = oc_df['futures_DII'].diff(1) + oc_df['futures_FII'].diff(1) + oc_df['futures_Pro'].diff(1)
        oc_df['option_daily'] = oc_df['option_FII'].diff(1) + oc_df['option_Pro'].diff(1)
        oc_df['daily_trend'] = np.sign(oc_df['futures_daily']*oc_df['option_daily'])
        # Make the list a dataframe
        
        

        
#        stock_df= stock_df.pivot(index='oi_date', values='net_oi')

#        print(stock_df)
        print(oc_df.sort_index(ascending=False))
        oc_df.to_csv('ocdf.csv')
    return oc_df
   
if __name__ == '__main__':
    short_trend()       
   

