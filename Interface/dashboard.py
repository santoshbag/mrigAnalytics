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
from dateutil import relativedelta
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import datetime
import QuantLib as ql
import mrigutilities as mu
import strategies.stocks as stocks
import stockScreener as ss
from pywintypes import Time

import mrigplots as mp
from matplotlib import colors as mcolors


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_fx(location):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select value_date, to_number(rate,'99999.9999') as rate from exchange_rates where currency='INR' and value_date >='"+lastmonth.strftime('%Y-%m-%d')+"' order by value_date desc"
    engine =  mu.sql_engine()
    
    fxrates = engine.execute(sql).fetchall()

    dates = [item[0] for item in fxrates]
    fxrates = [item[1] for item in fxrates]
    
    todayfx = fxrates[0]
    yesterdayfx = fxrates[1]
    lastmonthfx = fxrates[-1]
    lastweekfx = fxrates[6]

    dailyfxchange = float(todayfx/yesterdayfx -1)
    weeklyfxchange = float(todayfx/lastweekfx -1)
    monthlyfxchange = float(todayfx/lastmonthfx -1)
     
    fxdb = [[dates[0],dates[6],dates[-1]],[todayfx,lastweekfx,lastmonthfx],[dailyfxchange,weeklyfxchange,monthlyfxchange]]
    
    labels = ['dates','fxrate']
    plt = mp.singleScaleLine_plots(labels,'INRUSD')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    primary.plot(dates,fxrates,"orange",label="SpotFX")
    
    sht.pictures.add(fig, 
                     name='INRUSD', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return fxdb

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_crude(location):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select value_date, to_number(price,'99999.99') as price from crudeoil_prices where crude_benchmark='BRENT' and value_date >='"+lastmonth.strftime('%Y-%m-%d')+"' order by value_date desc"
    engine =  mu.sql_engine()
    
    oilrates = engine.execute(sql).fetchall()

    dates = [item[0] for item in oilrates]
    oilrates = [item[1] for item in oilrates]
    
    todayoil = oilrates[0]
    yesterdayoil = oilrates[1]
    lastmonthoil = oilrates[-1]
    lastweekoil = oilrates[6]

    dailyoilchange = float(todayoil/yesterdayoil -1)
    weeklyoilchange = float(todayoil/lastweekoil -1)
    monthlyoilchange = float(todayoil/lastmonthoil -1)
     
    oildb = [[dates[0],dates[6],dates[-1]],[todayoil,lastweekoil,lastmonthoil],[dailyoilchange,weeklyoilchange,monthlyoilchange]]
    
    labels = ['Dates','Brent Price']
    plt = mp.singleScaleLine_plots(labels,'Brent')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    primary.plot(dates,oilrates,"orange",label="SpotFX")
    
    sht.pictures.add(fig, 
                     name='Brent', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return oildb

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_nifty(location):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select date, close from stock_history where symbol='NIFTY 50' and series='IN' and date >='"+lastmonth.strftime('%Y-%m-%d')+"' order by date desc"
    engine =  mu.sql_engine()
    
    niftyrates = engine.execute(sql).fetchall()
    
    dates = [item[0] for item in niftyrates]
    niftyrates = [item[1] for item in niftyrates]
    
    todaynifty = niftyrates[0]
    yesterdaynifty = niftyrates[1]
    lastmonthnifty = niftyrates[-1]
    lastweeknifty = niftyrates[6]

    dailyniftychange = float(todaynifty/yesterdaynifty -1)
    weeklyniftychange = float(todaynifty/lastweeknifty -1)
    monthlyniftychange = float(todaynifty/lastmonthnifty -1)
     
    niftydb = [[dates[0],dates[6],dates[-1]],[todaynifty,lastweeknifty,lastmonthnifty],[dailyniftychange,weeklyniftychange,monthlyniftychange]]
    
    labels = ['Dates','Nifty']
    plt = mp.singleScaleLine_plots(labels,'Nifty')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    primary.plot(dates,niftyrates,"orange",label="Nifty")
    
    sht.pictures.add(fig, 
                     name='Nifty', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return niftydb

    
@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_gold(location):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select value_date, to_number(price,'99999.99') as price from gold_prices where value_date >='"+lastmonth.strftime('%Y-%m-%d')+"' order by value_date desc"
    engine =  mu.sql_engine()
    
    goldrates = engine.execute(sql).fetchall()
    
    dates = [item[0] for item in goldrates]
    goldrates = [item[1] for item in goldrates]
    
    todaygold = goldrates[0]
    yesterdaygold = goldrates[1]
    lastmonthgold = goldrates[-1]
    lastweekgold = goldrates[6]

    dailygoldchange = float(todaygold/yesterdaygold -1)
    weeklygoldchange = float(todaygold/lastweekgold -1)
    monthlygoldchange = float(todaygold/lastmonthgold -1)
     
    golddb = [[dates[0],dates[6],dates[-1]],[todaygold,lastweekgold,lastmonthgold],[dailygoldchange,weeklygoldchange,monthlygoldchange]]
    
    labels = ['Dates','Gold Price']
    plt = mp.singleScaleLine_plots(labels,'Gold')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    primary.plot(dates,goldrates,"orange",label="Gold")
    
    sht.pictures.add(fig, 
                     name='Gold', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return golddb


@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_rates(location):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select curvedate, curve, tenor, yield/100 as yield from yieldcurve where curvedate >='"+lastmonth.strftime('%Y-%m-%d')+"' and curve in ('INR','USD') and tenor in ('3 months','1 year') order by curvedate desc, curve asc"
    engine =  mu.sql_engine()
    
    rates = engine.execute(sql).fetchall()
    
    INRdates = []
    INRyield3m = []
    INRyield1y = []
    USDdates = []
    USDyield3m = []
    USDyield1y = []

    for item in rates:
        if item[1] == "INR": 
            if item[2] == "3 months":
                INRdates.append(item[0])
                INRyield3m.append(float(item[3]))
            if item[2] == "1 year":
                INRyield1y.append(float(item[3]))
        if item[1] == "USD": 
            if item[2] == "3 months":
                USDdates.append(item[0])
                USDyield3m.append(float(item[3]))
            if item[2] == "1 year":
                USDyield1y.append(float(item[3]))
            
    todayINRyield3m = INRyield3m[0]
    yesterdayINRyield3m = INRyield3m[1]
    lastmonthINRyield3m = INRyield3m[-1]
    lastweekINRyield3m = INRyield3m[6]

    todayINRyield1y = INRyield1y[0]
    yesterdayINRyield1y = INRyield1y[1]
    lastmonthINRyield1y = INRyield1y[-1]
    lastweekINRyield1y = INRyield1y[6]

    todayUSDyield3m = USDyield3m[0]
    yesterdayUSDyield3m = USDyield3m[1]
    lastmonthUSDyield3m = USDyield3m[-1]
    lastweekUSDyield3m = USDyield3m[6]

    todayUSDyield1y = USDyield1y[0]
    yesterdayUSDyield1y = USDyield1y[1]
    lastmonthUSDyield1y = USDyield1y[-1]
    lastweekUSDyield1y = USDyield1y[6]
     
    rates = [[INRdates[0],INRdates[6],INRdates[-1]],
             [todayINRyield3m,lastweekINRyield3m,lastmonthINRyield3m],
             [todayINRyield1y,lastweekINRyield1y,lastmonthINRyield1y],
             [USDdates[0],USDdates[6],USDdates[-1]],
             [todayUSDyield3m,lastweekUSDyield3m,lastmonthUSDyield3m],
             [todayUSDyield1y,lastweekUSDyield1y,lastmonthUSDyield1y]]
    
    labels = ['Dates','Interest Rates']
    plt = mp.singleScaleLine_plots(labels,'Rates')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    primary.plot(INRdates,INRyield3m,"orange",label="INR 3M")
    primary.plot(INRdates,INRyield1y,"pink",label="INR 1Y")
    primary.plot(USDdates,USDyield3m,"cyan",label="USD 3M")
    primary.plot(USDdates,USDyield1y,"yellow",label="USD 1Y")
    
    sht.pictures.add(fig, 
                     name='Rates', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return rates

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_top_mf_holdings(location,tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.top_mf_holdings()
    

    top_holdings = top_holdings.head(10)
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    
    cum_returns = ["Returns(An)"]
    color = 0
    for sym in top_holdings['symbol']:
        stk = stocks.Stock(sym)
        stk.get_returns(tenor)
        dates = list(stk.daily_logreturns.index)
        cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
        period = (stk.daily_logreturns.index[-1] - stk.daily_logreturns.index[0]).days/360
        if period <= 1: period = 1
        cum_returns.append(float(stk.daily_logreturns.sum()/period))
        primary.plot(dates,cum_return_series,"C"+str(color),label=sym)
        primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
        color = color + 1
        
    sht.pictures.add(fig, 
                     name='Returns', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
                        
                        
    lis = list(top_holdings['company'])
    lis.insert(0,"Top MF Holdings")
    ret_lis = [lis,cum_returns]
    return ret_lis
        
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_nifty_sectors(location,tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    sectors = ['NIFTY BANK',
               'NIFTY IT',
               'NIFTY FMCG',
               'NIFTY PHARMA',
               'NIFTY AUTO',
               'NIFTY ENERGY',
               'NIFTY INFRASTRUCTURE',
               'NIFTY METAL']
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Sector Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    
    sector = ["Sectors"]
    cum_returns = ["Returns(An)"]
    color = 0
    for sym in sectors:
        try:
            stk = stocks.Stock(sym)
            stk.get_returns(tenor)
            dates = list(stk.daily_logreturns.index)
            cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
            period = (stk.daily_logreturns.index[-1] - stk.daily_logreturns.index[0]).days/360
            if period <= 1: period = 1
            cum_returns.append(float(stk.daily_logreturns.sum()/period))
            sector.append(sym)
            primary.plot(dates,cum_return_series,"C"+str(color),label=sym)
            primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
            color = color + 1
        except:
            pass
    sht.pictures.add(fig, 
                     name='Sector Returns', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
                        
    ret_lis = [sector,cum_returns]
    return ret_lis
        
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_bigmoneyzacks(location,tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.big_money_zack()
    

    top_holdings = top_holdings.head(10)
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'BM Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    
    cum_returns = ["Returns(An)"]
    color = 0
    for sym in top_holdings.index:
        stk = stocks.Stock(sym)
        stk.get_returns(tenor)
        dates = list(stk.daily_logreturns.index)
        cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
        period = (stk.daily_logreturns.index[-1] - stk.daily_logreturns.index[0]).days/360
        if period <= 1: period = 1
        cum_returns.append(float(stk.daily_logreturns.sum()/period))
        primary.plot(dates,cum_return_series,"C"+str(color),label=sym)
        primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
        color = color + 1
        
    sht.pictures.add(fig, 
                     name='BM Returns', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"Big M Holdings")
    list24W = list(top_holdings.ret24W)
    list24W.insert(0,"24 Week Return")
    list12W = list(top_holdings.ret12W)
    list12W.insert(0,"12 Week Return")
    list4W = list(top_holdings.ret4W)
    list4W.insert(0,"4 Week Return")
    ret_lis = [symlist,list24W,list12W,list4W]
    return ret_lis
    
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_sector_returns(location,num_companies_per_sector=10,tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    industry = ss.sector_returns(num_companies_per_sector,tenor)
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Industry')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    sht = xw.Book.caller().sheets.active
    
    ind_list = ["Industry"]                    
    cum_returns = ["Returns(An)"]
    color = 1
    for sym in set(industry['industry']):
        dates = list(industry[industry['industry'] == sym].index)
        cum_return_series = list(industry[industry['industry'] == sym].daily_log_returns.cumsum())
        period = (industry[industry['industry'] == sym].index[-1] - industry[industry['industry'] == sym].index[0]).days/360
        if period <= 1: period = 1
        cum_returns.append(float(industry[industry['industry'] == sym].daily_log_returns.sum()/period))
        ind_list.append(sym)
        primary.plot(dates,cum_return_series,list(colors.keys())[color*2],label=sym)
        primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=4)
        color = color + 1
        
    sht.pictures.add(fig, 
                     name='Industry', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
                        
    return [ind_list,cum_returns]
    
        