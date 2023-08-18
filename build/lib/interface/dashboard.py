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

from pywintypes import Time
import stockScreener as ss

import mrigplots as mp
from matplotlib import colors as mcolors


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_fx(location,sheet='None'):
    
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
    
    primary.plot(dates,fxrates,"orange",label="SpotFX")

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet]     
        sht.pictures.add(fig, 
                         name='INRUSD', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return fxdb

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_crude(location,sheet='None'):
    
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
   
    primary.plot(dates,oilrates,"orange",label="SpotFX")

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet]  
        sht.pictures.add(fig, 
                     name='Brent', 
                     update=True,
                     left=sht.range(location).left,
                     top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return oildb

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_nifty(location,sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)
    
    sql = "select date, close from stock_history where symbol='NIFTY 50' and series='IN' and date >='"+lastmonth.strftime('%Y-%m-%d')+"' order by date desc"
    engine =  mu.sql_engine()
    
    niftyrates = engine.execute(sql).fetchall()
    
    dates = [item[0] for item in niftyrates]
    niftyrates = [item[1] for item in niftyrates]
    
    todaynifty = mu.getIndexQuote('NIFTY 50')   #niftyrates[0]
    yesterdaynifty = niftyrates[0]
    lastmonthnifty = niftyrates[-1]
    lastweeknifty = niftyrates[6]

    dailyniftychange = todaynifty/float(yesterdaynifty) -1
    weeklyniftychange = todaynifty/float(lastweeknifty) -1
    monthlyniftychange = todaynifty/float(lastmonthnifty) -1
     
    niftydb = [[today,dates[6],dates[-1]],[todaynifty,lastweeknifty,lastmonthnifty],[dailyniftychange,weeklyniftychange,monthlyniftychange]]
    
    labels = ['Dates','Nifty']
    plt = mp.singleScaleLine_plots(labels,'Nifty')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates.insert(0,today)
    niftyrates.insert(0,todaynifty)
    primary.plot(dates,niftyrates,"orange",label="Nifty")

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='Nifty', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return niftydb

    
@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_gold(location,sheet='None'):
    
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
    
    primary.plot(dates,goldrates,"orange",label="Gold")
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='Gold', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return golddb


@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_db_rates(location,sheet='None'):
    
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

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='Rates', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
    #    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return rates

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_top_mf_holdings(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.top_mf_holdings()
    

    top_holdings = top_holdings.head(10)
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
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

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet]     
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
def mrigxl_nifty_sectors(location,tenor='6M',sheet='None'):
    
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
    
    sector = ["Sectors"]
    cum_returns = ["Returns(An)"]
    color = 0
    for sym in sectors:
        try:
            stk = stocks.Index(sym)
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
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet]     
        sht.pictures.add(fig, 
                         name='Sector Returns', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                        
    ret_lis = [sector,cum_returns]
    return ret_lis
        
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_bigmoneyzacks(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.big_money_zack()
    

    top_holdings = top_holdings.head(10)
    #print(top_holdings)
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'BM Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    
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
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
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
@xw.ret(expand='table', transpose=False)
def mrigxl_sector_returns(location,num_companies_per_sector=10,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    industry = ss.sector_returns(num_companies_per_sector,tenor)
    industry1Y = ss.sector_returns(num_companies_per_sector,'18M')
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Industry')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    industry_returns = []
    ind_list = ["Industry"]                    
    cum_returns = ["Returns(An)"]
    color = 1
    for sym in set(industry['industry']):
        dates = list(industry[industry['industry'] == sym].index)
        cum_return_series = list(industry[industry['industry'] == sym].daily_log_returns.cumsum())
        period = (industry[industry['industry'] == sym].index[-1] - industry[industry['industry'] == sym].index[0]).days/360
        if period <= 1: period = 1
        industry_returns.append([sym,float(industry[industry['industry'] == sym].daily_log_returns.sum()/period)])
        cum_returns.append(float(industry[industry['industry'] == sym].daily_log_returns.sum()/period))
        ind_list.append(sym)
        primary.plot(dates,cum_return_series,list(colors.keys())[color*2],label=sym)
        primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=4)
        color = color + 1

    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet]       
        sht.pictures.add(fig, 
                         name='Industry', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                            
#    return [ind_list,cum_returns]
    if not industry1Y.empty:
        #for i in range(0,len(stock_df['date'])-1):
        #    stock_df.iloc[i]['date'] = datetime.datetime.combine(stock_df.iloc[i]['date'],datetime.time())
        #stock_df.date = pd.DatetimeIndex(stock_df.date)
        industry1Y.reset_index()
#        industry1Y.set_index(['retdate','industry'],inplace=True)
    start = today - relativedelta.relativedelta(months=12)
    returns = industry1Y.reset_index().pivot('retdate','industry','daily_log_returns')
    ret12M = returns[start:].sum()
    ret12M.name = 'Returns 12M'
    
    start = today -relativedelta.relativedelta(months=6)
    returns = industry1Y.reset_index().pivot('retdate','industry','daily_log_returns')
    ret6M = returns[start:].sum()
    ret6M.name = 'Returns 6M'
    
    start = today - relativedelta.relativedelta(months=3)
    returns = industry1Y.reset_index().pivot('retdate','industry','daily_log_returns')
    ret3M = returns[start:].sum()
    ret3M.name = 'Returns 3M'
    
    
    
#    stockreturns = stockreturns.sort_values(by='Returns 3M',ascending=0)
    industry_returns = pd.DataFrame(industry_returns,columns=["industry","Tenor(An)"])
    industry_returns = industry_returns.set_index('industry')
    industry_returns = pd.concat([ret3M,ret6M,ret12M,industry_returns],axis=1)
    industry_returns = industry_returns.sort_values(by='Returns 3M',ascending=0)
    return industry_returns
    
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_smallcapgrowth(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.small_cap_growth()
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'SCG Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    
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
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='SCG Returns', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"SCG Holdings")
    eps = list(top_holdings.eps_growth)
    eps.insert(0,"EPS Growth")
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    ps = list(top_holdings.ps)
    ps.insert(0,"P/Sales")
    ret_lis = [symlist,cum_returns,eps,pe,ps]
    return ret_lis

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_tafa(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.ta_fa()
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'TAFA Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    
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
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='TAFA Returns', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"TAFA Holdings")
    eps = list(top_holdings.eps_growth)
    eps.insert(0,"EPS Growth")  
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    ps = list(top_holdings.ps)
    ps.insert(0,"P/Sales")
    ret_lis = [symlist,cum_returns,eps,pe,ps]
    return ret_lis
        
@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_newhighs(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.newhighs()
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'NewHighs Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    
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
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='NewHighs Returns', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"New Highs")
    eps = list(top_holdings.eps_growth)
    eps.insert(0,"EPS Growth")
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    ps = list(top_holdings.ps)
    ps.insert(0,"P/Sales")
    list12W = list(top_holdings.ret12W)
    list12W.insert(0,"12 Week Return")
    list4W = list(top_holdings.ret4W)
    list4W.insert(0,"4 Week Return")
    
    ret_lis = [symlist,cum_returns,list12W,list4W,eps]
    return ret_lis

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_growthincome(location,tenor='6M',sheet='None'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.growth_income()
    
    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'GrowthIncome Returns')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    
    cum_returns = ["Returns(An)"]
    color = 0
    for sym in top_holdings.index:
        try:
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
        except:
            pass
    
    if sheet != 'None':
        sht = xw.Book.caller().sheets[sheet] 
        sht.pictures.add(fig, 
                         name='GrowthIncome Returns', 
                         update=True,
                         left=sht.range(location).left,
                         top=sht.range(location).top)
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"Growth Income")
    roe = list(top_holdings.return_on_equity)
    roe.insert(0,"Return on Equity")
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    beta = list(top_holdings.beta)
    beta.insert(0,"Beta")
#    list12W = list(top_holdings.ret12W)
#    list12W.insert(0,"12 Week Return")
#    list4W = list(top_holdings.ret4W)
#    list4W.insert(0,"4 Week Return")
    
    ret_lis = [symlist,cum_returns,roe,pe,beta]
    return ret_lis

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_news():
    sql = "select distinct type, date, title, description from media \
           where date > ((select max(date) from media) - interval '1 week') \
           order by type ,date desc"
           
    
    engine =  mu.sql_engine()
    
    news = pd.read_sql(sql,engine)
    
    newstype = list(news.type)
    newsdate = list(news.date)
    newstitle = list(news.title)
    newsdesc = list(news.description)
    
    news = [newstype,newsdate,newstitle,newsdesc]
    return news

@xw.func
@xw.ret(expand='table', transpose=False)
def mrigxl_quote(symbol):
    
#    symbol = symbol.replace('&','\&')
    stk = stocks.Stock(symbol)
    
    labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
    quotes = [stk.quote['lastPrice'],
              stk.quote['open'],
              stk.quote['previousClose'],
              stk.quote['dayHigh'],
              stk.quote['dayLow'],
              stk.quote['high52'],
              stk.quote['low52']]
    ret_lis = [labels,quotes]
    return ret_lis

@xw.func
@xw.ret(expand='table', transpose=True)
def mrigxl_stocklist():
    sql = "select distinct symbol from security_master"
           
    
    engine =  mu.sql_engine()
    
    stocklist = pd.read_sql(sql,engine)
    
    stocklist = list(stocklist.symbol)
    return stocklist
    
def mrigxl_stock():
    
    sheet='Stock'
    sht = xw.Book.caller().sheets[sheet]
    symbol = sht.range('B2').value
    tenor = sht.range('M2').value
    stk = stocks.Stock(symbol)
    nifty = stocks.Index('NIFTY 50')
    price_labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
    quotes = [stk.quote['lastPrice'],
              stk.quote['open'],
              stk.quote['previousClose'],
              stk.quote['dayHigh'],
              stk.quote['dayLow'],
              stk.quote['high52'],
              stk.quote['low52']]
    price_list = [price_labels,quotes]
    sht.range('D3:J3').clear_contents()
    sht.range('D2').value = price_list
    
    cum_returns = []
    return_labels = ['1W','4W','12W','24W', '1Y','3Y']
    for i in range(0,len(return_labels)):
        stk.get_returns(return_labels[i])
        cum_returns.append('NA')
#        dates = list(stk.daily_logreturns.index)
#        cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
        try:
            period = (stk.daily_logreturns.index[-1] - stk.daily_logreturns.index[0]).days/360
            if period <= 1: period = 1
            cum_returns[i] = (float(stk.daily_logreturns.sum()/period))
        except:
            pass
    return_list = [return_labels,cum_returns]
    sht.range('D9:J9').clear_contents()
    sht.range('D8').value = return_list
             
    stk.get_price_vol(tenor)
    
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Price')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates = list(stk.pricevol_data.index)
    
    primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    primary.plot(dates,list(stk.pricevol_data['20_day_SMA']),"C2",label='20 Day SMA')
    primary.plot(dates,list(stk.pricevol_data['60_day_SMA']),"C3",label='60 Day SMA')
    primary.plot(dates,list(stk.pricevol_data['100_day_SMA']),"C4",label='100 Day SMA')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    sht.pictures.add(fig, 
                     name='Price', 
                     update=True,
                     left=sht.range('L3').left,
                     top=sht.range('L3').top)
    
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Bands')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_Band']),"C2",label='Bollinger')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_UBand']),"C3",label='Boll Upper')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_LBand']),"C4",label='Boll Lower')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    sht.pictures.add(fig, 
                     name='Bands', 
                     update=True,
                     left=sht.range('L35').left,
                     top=sht.range('L35').top)

    labels = ['Dates','Price','MACD']
    plt = mp.singleScaleLine_plots(labels,'MACD')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates = list(stk.pricevol_data.index)
    
    primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    secondary.plot(dates,list(stk.pricevol_data['MACD']),"C2",label='MACD')
    secondary.plot(dates,list(stk.pricevol_data['MACDS']),"C3",label='MACD Signal')
    primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
    secondary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    sht.pictures.add(fig, 
                     name='MACD', 
                     update=True,
                     left=sht.range('L52').left,
                     top=sht.range('L52').top)

    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Returns')
    fig,primary,secondary = plt[0],plt[1],plt[2]
    stk.get_returns(tenor)
    nifty.get_returns(tenor)
    dates = list(stk.daily_logreturns.index)
    cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
    nifty_dates = list(nifty.daily_logreturns.index)
    nifty_cum_return_series = list(nifty.daily_logreturns.daily_log_returns.cumsum())
    primary.plot(dates,cum_return_series,"C3",label=symbol)
    primary.plot(nifty_dates,nifty_cum_return_series,"C4",label='NIFTY')
    if(stk.industry != ""):
        industry_ret = ss.sector_returns("10",tenor)
        industry_ret_dates = list(industry_ret[industry_ret['industry'] == stk.industry].index)
        industry_ret_cum_return_series = list(industry_ret[industry_ret['industry'] == stk.industry].daily_log_returns.cumsum())
        primary.plot(industry_ret_dates,industry_ret_cum_return_series,"C2",label=stk.industry)
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    sht.pictures.add(fig, 
                     name='Returns', 
                     update=True,
                     left=sht.range('L17').left,
                     top=sht.range('L17').top)
    
    sht.range('D14:J16').clear_contents()
    risk = stk.get_risk()
    risklabels,risknumbers = [],[]
    for key in risk.keys():
        risklabels.append(key)
        risknumbers.append(risk[key])
    
    sht.range('D14').value = [risklabels,risknumbers]
             
             
    stk.get_ratios()
#    ratios = [list(stk.ratio_data.columns),stk.ratio_data.values.tolist()[0]]
    
    sht.range('D18:J500').clear_contents()
    if not stk.ratio_data.empty:
#        ratios = [['Ratio Date',stk.ratio_data.index[0]],[" "," "]]
#        ratioheads = list(stk.ratio_data.columns)
#        ratiovals = stk.ratio_data.values.tolist()[0]
#        for i in range(2,len(stk.ratio_data.columns)):
#            if ratiovals[i] != '':
#                if abs(float(ratiovals[i])) > 100000.00:
#                    ratios.append([ratioheads[i].replace('_',' ').upper()+' (lacs)',float(ratiovals[i])/100000])
#                else:
#                    ratios.append([ratioheads[i].replace('_',' ').upper(),ratiovals[i]])
        rd = stk.ratio_data.transpose()
        to_drop = ['symbol','download_date','rank','business_per_branch','business_per_employ', 'interest_income_per_branch','interest_income_per_employee', 'net_profit_per_branch','net_profit_per_employee']
        rd.drop(to_drop,axis=0,inplace=True)
        rd.rename(index=lambda x: x.upper().replace('_'," "),inplace=True)
#        rd.rename(columns=lambda x: x.upper().replace('_'," "),inplace=True)
        rd.replace('',np.nan,inplace=True)
        rd.dropna(how='all',axis=0,inplace=True)
        sht.range('D19').value = rd
    optionchain = stk.optionChain()
    sht.range('W3:AR500').clear_contents()
    sht.range('W3').value = optionchain

@xw.func
def mrigxl_covered_call(live=False):
    sheet='Covered Calls'
    sht = xw.Book.caller().sheets[sheet]
    sht.range('B3:L500').clear_contents()
    oc = ss.covered_call(live=live)
    sht.range('B3').value = oc[0]
    sht.range('AC4').value = oc[1]

@xw.func
def mrigxl_max_drawdown(symbol,window_days=29, period_months=12):

    drawdown = mu.max_stock_drawdown(symbol,window_days,period_months)
    return drawdown

@xw.func
def mrigxl_avg_drawdown(symbol,window_days=29, period_months=12):

    drawdown = mu.avg_stock_drawdown(symbol,window_days,period_months)
    return drawdown

@xw.func
@xw.ret(expand='table')
def mrigxl_stored_strategies(name=None):

    strategy = mu.get_stored_option_strategies(name)
    return strategy

@xw.func
def mrigxl_stockquote(symbol):
    stk = stocks.Stock(symbol)
    quote = stk.quote['lastPrice']
    quote = float(quote.replace(',',''))
    return quote

@xw.func
def mrigxl_bull_put_spread(live=False,stored=False, dbhost='localhost'):
    sheet='Bull Put Spread'
#    ts = datetime.datetime.now()
#    output = open(os.path.join(os.path.dirname(__file__), 'bps'+str(ts).replace(":","")+'.csv'),"w+")
#    err_info = open('bps_err'+str(ts).replace(":","")+'.csv',"w+")
#    bps = pd.DataFrame()
    sht = xw.Book.caller().sheets[sheet]
    sht.range('B3:N500').clear_contents()
    oc = ss.bull_put_spread(live=live,stored=stored, dbhost=dbhost)
#    bps = oc[0]
#    bps.to_csv(output)
#    err_info.write(oc[1])
#    output.close()
#    err_info.close()
    sht.range('B3').value = oc[0]
    sht.range('AE4').value = oc[1]

@xw.func
def mrigxl_bear_call_spread(live=False,stored=False,dbhost='localhost'):
    sheet='Bear Call Spread'
    sht = xw.Book.caller().sheets[sheet]
    sht.range('B3:N500').clear_contents()
    oc = ss.bear_call_spread(live=live,stored=stored,dbhost=dbhost)
    sht.range('B3').value = oc[0]
    sht.range('AE4').value = oc[1]
