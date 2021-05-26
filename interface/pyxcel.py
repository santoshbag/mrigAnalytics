# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:46:14 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import xlwings as xw
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import datetime
import QuantLib as ql
import mrigutilities as mu
from pywintypes import Time
import matplotlib.pyplot as plt
import matplotlib
import scipy.optimize
from datetime import date


@xw.func
@xw.arg('isinlist', ndim=1, transpose=True)
@xw.ret(expand='table', transpose=False)
def mrigxl_getMFNAV(reference_date, isinlist=None,db='localhost',justnav=0):
    
    nav_df = mu.getMFNAV(reference_date,isinlist,db=db)
    nav_df.drop(['Fund House','Scheme Type','Repurchase Price','Sale Price'],axis=1,inplace=True)
    nav_df.reset_index(level=0, inplace=True)
#    nav_df.sort_index(ascending=False, inplace=True)
    nav_df['Net Asset Value'] = nav_df['Net Asset Value'].apply(pd.to_numeric,errors='coerce')
    
    nav_df['Return'] = np.log(nav_df.groupby('Scheme Name')['Net Asset Value'].pct_change().add(1))
    nav_df['Cum Return'] = nav_df.groupby('Scheme Name')['Return'].cumsum().fillna(0).map("{:.2%}".format)
    nav_df['Return'] = nav_df['Return'].fillna(0).map("{:.2%}".format)

    nav_df.sort_values(by=['Scheme Name','Date'],ascending=[True,False],inplace=True)
    #nav_df.drop('Scheme Type',axis=1)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    nav_df.set_index('Date', inplace=True)
    nav_df.index = pd.DatetimeIndex(nav_df.index)
    if (justnav==1):
#        nav_df = reference_date.strftime('%Y-%d-%d')
        try:
            nav_df = nav_df.loc[reference_date]['Net Asset Value']#.head(1).values)
        except:
            pass
    return nav_df

@xw.func
@xw.arg('isinlist', ndim=1, transpose=True)
def mrigxl_getMFNAV1(reference_date, isinlist=None,db='localhost'):
    
    nav_df = mu.getMFNAV(reference_date,isinlist,db=db)
    nav_df.reset_index(level=0, inplace=True)
#    nav_df.sort_index(ascending=False, inplace=True)
    nav_df['Net Asset Value'] = nav_df['Net Asset Value'].apply(pd.to_numeric,errors='coerce')
    
    nav_df.sort_values(by=['Scheme Name','Date'],ascending=[True,False],inplace=True)
    #nav_df.drop('Scheme Type',axis=1)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    nav_df.set_index('Date', inplace=True)
    nav_df.index = pd.DatetimeIndex(nav_df.index)

    try:
        nav_df = nav_df.loc[reference_date]['Net Asset Value']#.head(1).values)
    except:
        pass
    return nav_df
    
@xw.func
#@xw.ret(expand='table', transpose=False)
def mrigxl_getStockData(symbol,start_date,end_date=None,last=True,db='localhost'):
    
    stock_df = mu.getStockData(symbol,start_date,end_date,last,db=db)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    if not stock_df.empty:
        stock_df = stock_df['close']
        if end_date is None:
            stock_df = list(stock_df.head(1).values)
        return stock_df
    else:
        return 0
@xw.func
#@xw.ret(expand='table', transpose=False)
@xw.arg('investments', pd.DataFrame, index=False, header=True)
def mrigxl_IRR(symbol,investments=None,startDate=None,endDate=None):
    df = investments[investments.Date.notnull()]
    if startDate != None:
        df = df[df['Date'] >= startDate]
    if endDate != None:
        df = df[df['Date'] <= endDate]

    if symbol!="ALL":
        df = investments[investments['Scheme Name']==symbol]
    dates = [dt.date() for dt in list(df['Date'])] +[datetime.date.today()]
#    dates = [dt.date() for dt in dates]
    values = list(df['Investment'])
    curr_investment_val = df['Market Value'].sum()  #df['Units'].sum() * df['Price'].iloc[0]
    values = values + [curr_investment_val]
    
    try:
        irr = scipy.optimize.newton(lambda r: xnpv(r, values, dates), 0.0)
    except RuntimeError:    # Failed to converge?
        irr =  scipy.optimize.brentq(lambda r: xnpv(r, values, dates), -1.0, 1e10)
    if (max(dates) - min(dates)).days < 365:
        irr = (1+ irr)**((max(dates) - min(dates)).days / 365.0) -1
    return irr
#    return dates

def xnpv(rate, values, dates):
    '''Equivalent of Excel's XNPV function.

    >>> from datetime import date
    >>> dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    >>> values = [-10000, 20, 10100]
    >>> xnpv(0.1, values, dates)
    -966.4345...
    '''
    if rate <= -1.0:
        return float('inf')
    d0 = dates[0]    # or min(dates)
#    if (max(dates) - min(dates)).days < 365:
#        return sum([ vi / (1.0 + rate)**(di - d0).days for vi, di in zip(values, dates)])
#    else:    
    return sum([ vi / (1.0 + rate)**((di - d0).days / 365.0) for vi, di in zip(values, dates)])

@xw.func
def mrigxl_zerodha(tran_type='EQ_D',qty=0,buy=0,sell=0,mode='oc'):
    
    charges = mu.getZerodhaChgs(tran_type,qty,buy,sell)
    if mode=='oc':
        return charges[0]
    else:
        return charges
    
if __name__ == '__main__':
    dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    values = [-10000, 20, 10100]
    print(xnpv(0.1, values, dates))
    
    
    