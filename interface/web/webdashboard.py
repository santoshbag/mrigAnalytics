# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:46:14 2018

@author: Santosh Bag
"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import xlwings as xw
import pandas as pd
import numpy as np
from dateutil import relativedelta
import datetime
import mrigutilities as mu
import strategies.stocks as stocks
import io,base64
import stockScreener as ss
import media.news as n
import nsepy
import instruments.options as options
import instruments.termstructure as ts
import instruments.qlMaps as qlMaps

from fuzzywuzzy import fuzz
import mrigplots as mp
from matplotlib import colors as mcolors


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)


def mrigweb_db_fx(location,sheet='None'):
    
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


def mrigweb_db_crude(location,sheet='None'):
    
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


def mrigweb_db_nifty(location,sheet='None'):
    
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

    

def mrigweb_db_gold(location,sheet='None'):
    
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



def mrigweb_db_rates(location,sheet='None'):
    
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


def mrigweb_top_mf_holdings(location,tenor='6M',sheet='None'):
    
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
        

def mrigweb_nifty_sectors(location,tenor='6M',sheet='None'):
    
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
        
def mrigweb_bigmoneyzacks(tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.big_money_zack() #mu.get_stored_stock_strategies('bigm')
    

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

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    bigM_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
                            
    symlist = list(top_holdings.index)
    symlist.insert(0,"Big M Holdings")
    list24W = list(top_holdings.ret24W)
    list24W.insert(0,"24 Week Return")
    list12W = list(top_holdings.ret12W)
    list12W.insert(0,"12 Week Return")
    list4W = list(top_holdings.ret4W)
    list4W.insert(0,"4 Week Return")
    ret_lis = [symlist,list24W,list12W,list4W]
    return [top_holdings,bigM_graph]
    

def mrigweb_sector_returns(location,num_companies_per_sector=10,tenor='6M',sheet='None'):
    
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
    


def mrigweb_smallcapgrowth(tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.small_cap_growth() #mu.get_stored_stock_strategies('scg')
    
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

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    scg_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
                            
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"SCG Holdings")
    eps = list(top_holdings.eps_growth)
    eps.insert(0,"EPS Growth")
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    ps = list(top_holdings.ps)
    ps.insert(0,"P/Sales")
    ret_lis = [symlist,cum_returns,eps,pe,ps]
    return [top_holdings,scg_graph]


def mrigweb_tafa(tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.ta_fa() #mu.get_stored_stock_strategies('tafa')
    
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
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    tafa_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
                        
                        
    symlist = list(top_holdings.index)
    symlist.insert(0,"TAFA Holdings")
    eps = list(top_holdings.eps_growth)
    eps.insert(0,"EPS Growth")  
    pe = list(top_holdings.pe)
    pe.insert(0,"P/E")
    ps = list(top_holdings.ps)
    ps.insert(0,"P/Sales")
    ret_lis = [symlist,cum_returns,eps,pe,ps]
    return [top_holdings,tafa_graph]
        

def mrigweb_newhighs(tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

    top_holdings = ss.newhighs()#mu.get_stored_stock_strategies('nh')
        
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
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    nh_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
                        
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
    return [top_holdings,nh_graph]


def mrigweb_growthincome(tenor='6M'):
    
    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

#    top_holdings = mu.get_stored_stock_strategies('gi')
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
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    gi_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
                        
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
    return [top_holdings,gi_graph]

def mrigweb_custom_screener(criteria):

    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

#    top_holdings = mu.get_stored_stock_strategies('gi')
    top_holdings = ss.custom_stock_screener(criteria)
    
    return top_holdings
    
def mrigweb_news():
    
    n.get_MCNews()
    sql = "select distinct type, date, title, description from media \
           where date > ((select max(date) from media) - interval '2 days') \
           order by type ,date desc"
           
    
    engine =  mu.sql_engine()
    
    news = pd.read_sql(sql,engine)
    
    newstype = list(news.type)
    newsdate = list(news.date)
    newstitle = list(news.title)
    newsdesc = list(news.description)
    
    news = {}
    for t in newstype:
        news[t] = []
    
    i = 0
    for t in newstype:
        news[t].append([newsdate[i],newstitle[i],newsdesc[i]])
        i = i + 1
        
    return news


@xw.ret(expand='table', transpose=False)
def mrigweb_quote(symbol):
    
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


@xw.ret(expand='table', transpose=True)
def mrigweb_stocklist():
    sql = "select distinct symbol from security_master"
           
    
    engine =  mu.sql_engine()
    
    stocklist = pd.read_sql(sql,engine)
    
    stocklist = list(stocklist.symbol)
    return stocklist

def mrigweb_index(symbol='NIFTY 50',tenor='1Y'):
    
#    sheet='Stock'
#    sht = xw.Book.caller().sheets[sheet]
#    symbol = sht.range('B2').value
#    tenor = sht.range('M2').value
    index = stocks.Index(symbol)
    stock_desc = 'NIFTY 50 Index' #index.quote['companyName'] + " | "+index.industry+" | ISIN: "+ index.quote['isinCode']
    nifty = stocks.Index('NIFTY 50')
    price_labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
    quotes = [index.quote['lastPrice'],
              index.quote['open'],
              index.quote['previousClose'],
              index.quote['dayHigh'],
              index.quote['dayLow'],
              index.quote['high52'],
              index.quote['low52']]
    price_list = [price_labels,quotes]
#    sht.range('D3:J3').clear_contents()
#    sht.range('D2').value = price_list
    
    cum_returns = []
    return_labels = ['1W','4W','12W','24W', '1Y','3Y']
    for i in range(0,len(return_labels)):
        index.get_returns(return_labels[i])
        cum_returns.append('NA')
#        dates = list(stk.daily_logreturns.index)
#        cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
        try:
            period = (index.daily_logreturns.index[-1] - index.daily_logreturns.index[0]).days/360
            if period <= 1: period = 1
            cum_returns[i] = (float(index.daily_logreturns.sum()/period))
        except:
            pass
    return_list = [return_labels,cum_returns]
#    sht.range('D9:J9').clear_contents()
#    sht.range('D8').value = return_list
             
    index.get_price_vol(tenor)
    
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Price')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates = list(index.pricevol_data.index)
    
    primary.plot(dates,list(index.pricevol_data.close_adj),"C1",label='Close')
    primary.plot(dates,list(index.pricevol_data['20_day_SMA']),"C2",label='20 Day SMA')
    primary.plot(dates,list(index.pricevol_data['60_day_SMA']),"C3",label='60 Day SMA')
    primary.plot(dates,list(index.pricevol_data['100_day_SMA']),"C4",label='100 Day SMA')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
#    sht.pictures.add(fig, 
#                     name='Price', 
#                     update=True,
#                     left=sht.range('L3').left,
#                     top=sht.range('L3').top)
    
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Bands')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(dates,list(index.pricevol_data.close_adj),"C1",label='Close')
    primary.plot(dates,list(index.pricevol_data['Bollinger_Band']),"C2",label='Bollinger')
    primary.plot(dates,list(index.pricevol_data['Bollinger_UBand']),"C3",label='Boll Upper')
    primary.plot(dates,list(index.pricevol_data['Bollinger_LBand']),"C4",label='Boll Lower')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    boll_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
#    sht.pictures.add(fig, 
#                     name='Bands', 
#                     update=True,
#                     left=sht.range('L35').left,
#                     top=sht.range('L35').top)

    labels = ['Dates','Price','MACD']
    plt = mp.singleScaleLine_plots(labels,'MACD')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates = list(index.pricevol_data.index)
    
    primary.plot(dates,list(index.pricevol_data.close_adj),"C1",label='Close')
    secondary.plot(dates,list(index.pricevol_data['MACD']),"C2",label='MACD')
    secondary.plot(dates,list(index.pricevol_data['MACDS']),"C3",label='MACD Signal')
    primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
    secondary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    macd_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
#    sht.pictures.add(fig, 
#                     name='MACD', 
#                     update=True,
#                     left=sht.range('L52').left,
#                     top=sht.range('L52').top)

    labels = ['Dates','Returns']
    plt = mp.singleScaleLine_plots(labels,'Returns')
    fig,primary,secondary = plt[0],plt[1],plt[2]
    index.get_returns(tenor)
    nifty.get_returns(tenor)
    dates = list(index.daily_logreturns.index)
    cum_return_series = list(index.daily_logreturns.daily_log_returns.cumsum())
    nifty_dates = list(nifty.daily_logreturns.index)
    nifty_cum_return_series = list(nifty.daily_logreturns.daily_log_returns.cumsum())
    primary.plot(dates,cum_return_series,"C3",label=symbol)
    primary.plot(nifty_dates,nifty_cum_return_series,"C4",label='NIFTY')
#    if(index.industry != ""):
#        industry_ret = ss.sector_returns("10",tenor)
#        industry_ret_dates = list(industry_ret[industry_ret['industry'] == index.industry].index)
#        industry_ret_cum_return_series = list(industry_ret[industry_ret['industry'] == index.industry].daily_log_returns.cumsum())
#        primary.plot(industry_ret_dates,industry_ret_cum_return_series,"C2",label=index.industry)
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    return_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()

#    sht.pictures.add(fig, 
#                     name='Returns', 
#                     update=True,
#                     left=sht.range('L17').left,
#                     top=sht.range('L17').top)
    
#    sht.range('D14:J16').clear_contents()
#    risk = index.get_risk()
#    risklabels,risknumbers = [],[]
#    for key in risk.keys():
#        risklabels.append(key)
#        risknumbers.append(risk[key])
#    
#    risk_list = [risklabels,risknumbers]
##    sht.range('D14').value = [risklabels,risknumbers]
#             
#             
#    index.get_ratios()
##    ratios = [list(index.ratio_data.columns),index.ratio_data.values.tolist()[0]]
#    
##    sht.range('D18:J500').clear_contents()
#    if not index.ratio_data.empty:
##        ratios = [['Ratio Date',index.ratio_data.index[0]],[" "," "]]
##        ratioheads = list(index.ratio_data.columns)
##        ratiovals = index.ratio_data.values.tolist()[0]
##        for i in range(2,len(index.ratio_data.columns)):
##            if ratiovals[i] != '':
##                if abs(float(ratiovals[i])) > 100000.00:
##                    ratios.append([ratioheads[i].replace('_',' ').upper()+' (lacs)',float(ratiovals[i])/100000])
##                else:
##                    ratios.append([ratioheads[i].replace('_',' ').upper(),ratiovals[i]])
#        rd = index.ratio_data.transpose()
#        to_drop = ['symbol','download_date','rank','business_per_branch','business_per_employ', 'interest_income_per_branch','interest_income_per_employee', 'net_profit_per_branch','net_profit_per_employee']
#        rd.drop(to_drop,axis=0,inplace=True)
#        rd.rename(index=lambda x: x.upper().replace('_'," "),inplace=True)
##        rd.rename(columns=lambda x: x.upper().replace('_'," "),inplace=True)
#        rd.replace('',np.nan,inplace=True)
#        rd.dropna(how='all',axis=0,inplace=True)
##        sht.range('D19').value = rd
#    
    sql = "select distinct date, title, description from media \
           where date > ((select max(date) from media) - interval '2 days') \
           order by date desc"
           
    
    engine =  mu.sql_engine()
    
    news = engine.execute(sql).fetchall()
    
    news = [item for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
              
    optionchain = index.optionChain()
#    sht.range('W3:AR500').clear_contents()
#    sht.range('W3').value = optionchain
    return [price_list,return_list,None,pd.DataFrame(),optionchain,price_graph,return_graph,macd_graph,boll_graph,stock_desc,news]

    
def mrigweb_stock(symbol,tenor='1Y'):
    
#    sheet='Stock'
#    sht = xw.Book.caller().sheets[sheet]
#    symbol = sht.range('B2').value
#    tenor = sht.range('M2').value
    stk = stocks.Stock(symbol)
    stock_desc = stk.quote['companyName'] + " | "+stk.industry+" | ISIN: "+ stk.quote['isinCode']
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
#    sht.range('D3:J3').clear_contents()
#    sht.range('D2').value = price_list
    
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
#    sht.range('D9:J9').clear_contents()
#    sht.range('D8').value = return_list
             
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
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
#    sht.pictures.add(fig, 
#                     name='Price', 
#                     update=True,
#                     left=sht.range('L3').left,
#                     top=sht.range('L3').top)
    
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Bands')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_Band']),"C2",label='Bollinger')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_UBand']),"C3",label='Boll Upper')
    primary.plot(dates,list(stk.pricevol_data['Bollinger_LBand']),"C4",label='Boll Lower')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    boll_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
#    sht.pictures.add(fig, 
#                     name='Bands', 
#                     update=True,
#                     left=sht.range('L35').left,
#                     top=sht.range('L35').top)

    labels = ['Dates','Price','MACD']
    plt = mp.singleScaleLine_plots(labels,'MACD')
    
    fig,primary,secondary = plt[0],plt[1],plt[2]
    dates = list(stk.pricevol_data.index)
    
    primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    secondary.plot(dates,list(stk.pricevol_data['MACD']),"C2",label='MACD')
    secondary.plot(dates,list(stk.pricevol_data['MACDS']),"C3",label='MACD Signal')
    primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
    secondary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    macd_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
#    sht.pictures.add(fig, 
#                     name='MACD', 
#                     update=True,
#                     left=sht.range('L52').left,
#                     top=sht.range('L52').top)

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

    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    return_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()

#    sht.pictures.add(fig, 
#                     name='Returns', 
#                     update=True,
#                     left=sht.range('L17').left,
#                     top=sht.range('L17').top)
    
#    sht.range('D14:J16').clear_contents()
    risk = stk.get_risk()
    risklabels,risknumbers = [],[]
    for key in risk.keys():
        risklabels.append(key)
        risknumbers.append(risk[key])
    
    risk_list = [risklabels,risknumbers]
#    sht.range('D14').value = [risklabels,risknumbers]
             
             
    stk.get_ratios()
#    ratios = [list(stk.ratio_data.columns),stk.ratio_data.values.tolist()[0]]
    
#    sht.range('D18:J500').clear_contents()
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
#        sht.range('D19').value = rd
    
    sql = "select distinct date, title, description from media \
           where date > ((select max(date) from media) - interval '2 days') \
           order by date desc"
           
    
    engine =  mu.sql_engine()
    
    news = engine.execute(sql).fetchall()
    
    news = [item for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
              
    optionchain = stk.optionChain()
#    sht.range('W3:AR500').clear_contents()
#    sht.range('W3').value = optionchain
    return [price_list,return_list,risk_list,rd,optionchain,price_graph,return_graph,macd_graph,boll_graph,stock_desc,news]


def mrigweb_max_drawdown(symbol,window_days=29, period_months=12):

    drawdown = mu.max_stock_drawdown(symbol,window_days,period_months)
    return drawdown


def mrigweb_avg_drawdown(symbol,window_days=29, period_months=12):

    drawdown = mu.avg_stock_drawdown(symbol,window_days,period_months)
    return drawdown



def mrigweb_stored_strategies(name=None):

    strategy = mu.get_stored_option_strategies(name)
    return strategy


def mrigweb_stockquote(symbol):
    stk = stocks.Stock(symbol)
    quote = stk.quote['lastPrice']
    return quote

def mrigweb_covered_call():
#    sheet='Covered Calls'
#    sht = xw.Book.caller().sheets[sheet]
#    sht.range('B3:L500').clear_contents()
    oc = ss.covered_call()
    oc = oc[0]
#    oc_analytic = pd.DataFrame()
    if not oc.empty:

        oc['Initial_Yield'] = oc['CALL_LTP']/oc['Underlying']
        oc['Outlay'] = oc['Underlying']*oc['Lot']
        oc['Max_Profit'] = (oc['CALL_LTP'] + oc['Strike_Price'] - oc['Underlying'])*oc['Lot'] 
        oc['Max_Risk'] = oc['CALL_LTP']*oc['Lot'] - oc['Outlay']
        oc['Max_Yield'] = abs(oc['Max_Profit']/oc['Max_Risk'])

    return oc


def mrigweb_bull_put_spread():
    oc = ss.bull_put_spread()
    oc = oc[0]
#    oc_analytic = pd.DataFrame()

    if not oc.empty:
        oc['Initial_Yield'] = (oc['Higher_Strike_LTP']-oc['PUT_LTP'])/(oc['Higher_Strike']-oc['Strike_Price'])
        oc['Net_Credit'] = (oc['Higher_Strike_LTP']-oc['PUT_LTP'])*oc['Lot']
        oc['Max_Risk'] = (oc['Higher_Strike']-oc['Strike_Price'])*oc['Lot'] - oc['Net_Credit']
        oc['Max_Yield'] = abs(oc['Net_Credit']/oc['Max_Risk'])
        
    return oc

def mrigweb_bear_call_spread():
    oc = ss.bear_call_spread()
    oc = oc[0]
#    oc_analytic = pd.DataFrame()
    
    if not oc.empty:
        
        oc['Initial_Yield'] = (oc['Lower_Strike_LTP']-oc['CALL_LTP'])/(oc['Strike_Price']-oc['Lower_Strike'])
        oc['Net_Credit'] = (oc['Lower_Strike_LTP']-oc['CALL_LTP'])*oc['Lot']
        oc['Max_Risk'] = (oc['Strike_Price']-oc['Lower_Strike'])*oc['Lot'] - oc['Net_Credit']
        oc['Max_Yield'] = abs(oc['Net_Credit']/oc['Max_Risk'])

    return oc

def mrigweb_options(opid):
    
    enddate = datetime.date.today()
    startdate = enddate - datetime.timedelta(days=30)
    
    """
    Contract Specifications------------------------------------------------------------
    """
    option_type_map = {'PE':'Put European',
                       'CE':'Call European',
                       'PA':'Put American',
                       'CA':'Call American'}
    
    symbol = opid['symbol']
    expiry = opid['expiry']
    strike = opid['strike']
    option_type = opid['option_type']
    
    quote = mu.getStockOptionQuote(symbol,expiry,strike,option_type)
    moneyness = "ATM"
    if option_type[0] == 'C':
        if (strike - quote['underlyingValue']) < 0:
            moneyness = "ITM"
        if (strike - quote['underlyingValue']) > 0:
            moneyness = "OTM"
    if option_type[0] == 'P':
        if (strike - quote['underlyingValue']) > 0:
            moneyness = "ITM"
        if (strike - quote['underlyingValue']) < 0:
            moneyness = "OTM"
        
    contract_specs = [['Underlying','Option Type','Strike','Expiry',
                       'Lot','LTP','Open Interest','Underlying','Moneyness'],
                      [symbol,option_type_map[option_type],strike,expiry,
                       quote['marketLot'],quote['lastPrice'],quote['openInterest'],
                       quote['underlyingValue'],moneyness]]
    
    """
    Option History----------------------------------------------------------------------
    """
    
    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
    dates = list(oh.index)
    close = list(oh['Close'])
    OI = list(oh['Open Interest'])
    oh = oh.loc[[d for d in list(oh.index) if (enddate-d)% datetime.timedelta(days=3) == datetime.timedelta(0) ]]
    oh = oh.sort_index(ascending=0)
    
    """
    Price and OI Graph-------------------------------------------------------------------
    """
    labels = ['Dates','Price']
    plt = mp.singleScaleLine_plots(labels,'Price')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(dates,close,"C1",label='Close')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()

    labels = ['Dates','Open Interest']
    plt = mp.singleScaleLine_plots(labels,'Open Interest')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(dates,OI,"C1",label='Open Interest')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    oi_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    """
    Option Greeks and Graphs--------------------------------------------------------------
    """
    args = {'option_name':symbol+"_"+expiry.strftime('%d%b')+"_"+str(strike)+"_"+option_type,
            'underlying_name':symbol,
            'maturity_date':expiry,
            'option_type':option_type_map[option_type].split(' ')[0],
            'strike': strike,                               
            'exercise_type':option_type_map[option_type].split(' ')[1],
            'day_count':'30-360',
            'calendar':'India'}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        option = options.VanillaEuropeanOption(args)

    """
    Set Interest Rate Curve
    """    

    args = {'day_count':'30-360',
            'calendar': 'India',
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear',
            'shiftparameter' : None}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    today = datetime.date.today()
    
    engine = mu.sql_engine()
    try:
        today = engine.execute("select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1").fetchall()[0][0]
    except:
        pass
    discount_curve = ts.SpotZeroYieldCurve('INR',today)
    discount_curve.setupCurve(args)

    """
    Set Flat Volatility Curve
    """    
    spotVol = 0.10
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    volatility_curve = ts.FlatVolatilityCurve(today,spotVol)
    volatility_curve.setupCurve(args)
    
    """
    Set Flat Dividend Curve
    """    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'flat_rate':0.01,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    dividend_curve = ts.FlatDividendYieldCurve(today,args['flat_rate'])
    dividend_curve.setupCurve(args)
    
    """
    Set Option Valuation and get Results
    """    
    valuation_method = 'Black Scholes'
    underlying_spot = quote['underlyingValue']  
    
    option.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)
    
    if str(quote['lastPrice']).lstrip('-').replace('.','',1).isdigit():
        price = float(str(quote['lastPrice']))
        spotVol = option.getImpliedVol(price)
    elif str(close[0]).lstrip('-').replace('.','',1).isdigit():
        price = float(str(close[0]))
        spotVol = option.getImpliedVol(price)

        
        
        
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
    
    volatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    volatility_curve.setupCurve(args)

    option.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)

    results = option.getAnalytics()
    
    """
    Risk Profile and Greeks
    """
    
    underlying_spot_range = [max(underlying_spot/100,0.5)*i for i in range(1,200)]
    
    NPV = []
    delta = []
    gamma = []
    theta = []
    
    for spot in underlying_spot_range:
        option.valuation(spot,discount_curve,
                     volatility_curve,dividend_curve,
                     valuation_method)
        
        result = option.getAnalytics()
        NPV.append(result['NPV']- price)
        delta.append(result['delta'])
        gamma.append(result['gamma'])
        theta.append(result['theta'])
        
    labels = ['Underlying','NPV']
    plt = mp.singleScaleLine_plots(labels,'NPV')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,NPV,"C1",label='NPV')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    NPV_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Delta']
    plt = mp.singleScaleLine_plots(labels,'Delta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,delta,"C1",label='Delta')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    delta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Gamma']
    plt = mp.singleScaleLine_plots(labels,'Gamma')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,gamma,"C1",label='Gamma')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    gamma_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Theta']
    plt = mp.singleScaleLine_plots(labels,'Theta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,theta,"C1",label='Theta')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    theta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
    
    """
    Return list of analytics
    """
    
    return [contract_specs,oh,price_graph, results,NPV_graph,delta_graph,gamma_graph,theta_graph,oi_graph]
    
def covered_call_analysis(strategy):
    today = datetime.date.today()
    calloption = lambda spot, strike: max(spot - strike,0)
    putoption = lambda spot, strike: max(strike - spot,0)
    """
    Get Strategy Details--------------------------------------------------------------
    """

    symbol = strategy['Symbol']
    expiry = datetime.datetime.strptime(strategy['Expiry'],'%d%m%Y').date()
    time_to_maturity = (expiry - today).total_seconds()/datetime.timedelta(days=1).total_seconds()
    strike = float(strategy['Strike_Price'])
    lot = float(strategy['Lot'])
    underlying = float(strategy['Underlying'])
#    higher_strike,lower_strike = -1,-1
#    price,higher_strike_price, lower_strike_price = -1.-1.-1
    if 'Higher_Strike' in strategy.keys():
        higher_strike = strategy['Higher_Strike']
        higher_strike_price = strategy['Higher_Strike_LTP']
    if 'Lower_Strike' in strategy.keys():
        lower_strike = strategy['Lower_Strike']
        lower_strike_price = strategy['Lower_Strike_LTP']
    
    strategy_desc = [symbol,expiry,strike]
    strategy_specs = []
    strategy_risk = []

    price = float(strategy['CALL_LTP'])
    head = ['Legs','Asset','Direction','Lot','Strike','Expiry','Price','Outlay']
    longleg = ['Long Leg','Stock','Long',lot,'-','-',underlying,-underlying*lot]
    shortleg = ['Short Leg','Call Option','Short',lot,strike,expiry.strftime('%d-%b-%Y'),price,price*lot]
    total = ['','','','','','','',price*lot-underlying*lot]
    strategy_specs = [head,longleg,shortleg,total]
    
    head = ['Intial Yield','Intial Yield/Day','Max Profit','Max Yield','Max Risk']
    risk = ['{0:.2f}%'.format(float(strategy['Initial_Yield'])*100),'{0:.2f}%'.format(float(strategy['Initial_Yield'])/time_to_maturity*100),
            float(strategy['Max_Profit']),'{0:.2f}%'.format(float(strategy['Max_Yield'])*100),
            float(strategy['Max_Risk'])]
    strategy_risk = [head,risk]
#    """
#    Contract Specifications------------------------------------------------------------
#    """
#    option_type_map = {'PE':'Put European',
#                       'CE':'Call European',
#                       'PA':'Put American',
#                       'CA':'Call American'}
#    
#    symbol = opid['symbol']
#    expiry = opid['expiry']
#    strike = opid['strike']
#    option_type = opid['option_type']
#    
#    quote = mu.getStockOptionQuote(symbol,expiry,strike,option_type)
#    moneyness = "ATM"
#    if option_type[0] == 'C':
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "OTM"
#    if option_type[0] == 'P':
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "OTM"
#        
#    contract_specs = [['Underlying','Option Type','Strike','Expiry',
#                       'Lot','LTP','Open Interest','Underlying','Moneyness'],
#                      [symbol,option_type_map[option_type],strike,expiry,
#                       quote['marketLot'],quote['lastPrice'],quote['openInterest'],
#                       quote['underlyingValue'],moneyness]]
#    
#    """
#    Option History----------------------------------------------------------------------
#    """
#    
#    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
#    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
#    dates = list(oh.index)
#    close = list(oh['Close'])
#    OI = list(oh['Open Interest'])
#    oh = oh.loc[[d for d in list(oh.index) if (enddate-d)% datetime.timedelta(days=3) == datetime.timedelta(0) ]]
#    oh = oh.sort_index(ascending=0)
#    
#    """
#    Price and OI Graph-------------------------------------------------------------------
#    """
#    labels = ['Dates','Price']
#    plt = mp.singleScaleLine_plots(labels,'Price')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,close,"C1",label='Close')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#
#    labels = ['Dates','Open Interest']
#    plt = mp.singleScaleLine_plots(labels,'Open Interest')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,OI,"C1",label='Open Interest')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    oi_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#    
    """
    Option Greeks and Graphs--------------------------------------------------------------
    """
    args = {'option_name':symbol+"_"+expiry.strftime('%d%b')+"_"+str(strike)+"_CE",
            'underlying_name':symbol,
            'maturity_date':expiry,
            'option_type':'Call',
            'strike': strike,                               
            'exercise_type':'European',
            'day_count':'30-360',
            'calendar':'India'}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        option = options.VanillaEuropeanOption(args)

    """
    Set Interest Rate Curve
    """    

    args = {'day_count':'30-360',
            'calendar': 'India',
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear',
            'shiftparameter' : None}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    today = datetime.date.today()
    
    engine = mu.sql_engine()
    try:
        today = engine.execute("select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1").fetchall()[0][0]
    except:
        pass
    discount_curve = ts.SpotZeroYieldCurve('INR',today)
    discount_curve.setupCurve(args)

    """
    Set Flat Volatility Curve
    """    
    spotVol = 0.10
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    volatility_curve = ts.FlatVolatilityCurve(today,spotVol)
    volatility_curve.setupCurve(args)
    
    """
    Set Flat Dividend Curve
    """    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'flat_rate':0.01,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    dividend_curve = ts.FlatDividendYieldCurve(today,args['flat_rate'])
    dividend_curve.setupCurve(args)
    
    """
    Set Option Valuation and get Results
    """    
    valuation_method = 'Black Scholes'
    underlying_spot = underlying  
    
    option.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)
    
    spotVol = option.getImpliedVol(price)
        
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
    
    volatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    volatility_curve.setupCurve(args)

    option.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)

    results = option.getAnalytics()
    results.pop('NPV',None)
    
    greeks = {}
    greeks['PV'] = lot*(underlying - price)
    for key in results.keys():
        greeks[str(key).capitalize()] = - results[key]
    greeks['Delta'] = 1 + results['delta']
    
    
    """
    Risk Profile and Greeks
    """
    
    underlying_spot_range = [max(0,max(abs(strike - underlying_spot),0.5)*i + underlying_spot) for i in range(-20,20)]
    


    longlegNPV = []
    longlegdelta = []
    longleggamma = []
    longlegtheta = []
    shortlegNPV = []
    shortlegdelta = []
    shortleggamma = []
    shortlegtheta = []
    NPV = []
    delta = []
    gamma = []
    theta = []
    
    for spot in underlying_spot_range:
        option.valuation(spot,discount_curve,
                     volatility_curve,dividend_curve,
                     valuation_method)
        
        result = option.getAnalytics()
        longlegNPV.append((spot - underlying)*lot)
        shortlegNPV.append((price - result['NPV'])*lot)
        NPV.append(((spot - underlying) + (price - result['NPV']))*lot)
        longlegdelta.append(1)
        shortlegdelta.append(-result['delta'])
        delta.append(-result['delta']+1)
        longleggamma.append(0)
        shortleggamma.append(-result['gamma'])
        gamma.append(-result['gamma'])
        longlegtheta.append(0)
        shortlegtheta.append(-result['theta'])
        theta.append(-result['theta'])
        
    labels = ['Underlying','NPV']
    plt = mp.singleScaleLine_plots(labels,'NPV')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegNPV,"C2",linestyle='--',label=symbol)
    primary.plot(underlying_spot_range,shortlegNPV,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,NPV,"C1",label='NPV')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    NPV_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Delta']
    plt = mp.singleScaleLine_plots(labels,'Delta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegdelta,"C2",linestyle='--',label=symbol)
    primary.plot(underlying_spot_range,shortlegdelta,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,delta,"C1",label='Delta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    delta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Gamma']
    plt = mp.singleScaleLine_plots(labels,'Gamma')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longleggamma,"C2",linestyle='--',label=symbol)
    primary.plot(underlying_spot_range,shortleggamma,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,gamma,"C1",label='Gamma')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    gamma_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Theta']
    plt = mp.singleScaleLine_plots(labels,'Theta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegtheta,"C2",linestyle='--',label=symbol)
    primary.plot(underlying_spot_range,shortlegtheta,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,theta,"C1",label='Theta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    theta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
    
    """
    Return list of analytics
    """
    
    return [strategy_desc,strategy_specs,strategy_risk,NPV_graph,delta_graph,gamma_graph,theta_graph,greeks]


def bull_put_spread_analysis(strategy):
    today = datetime.date.today()
    
    """
    Get Strategy Details--------------------------------------------------------------
    """

    symbol = strategy['Symbol']
    expiry = datetime.datetime.strptime(strategy['Expiry'],'%d%m%Y').date()
    time_to_maturity = (expiry - today).total_seconds()/datetime.timedelta(days=1).total_seconds()
    strike = float(strategy['Strike_Price'])
    lot = float(strategy['Lot'])
    underlying = float(strategy['Underlying'])
    higher_strike = float(strategy['Higher_Strike'])
    higher_strike_price = float(strategy['Higher_Strike_LTP'])
    
    strategy_desc = [symbol,expiry,strike,higher_strike]
    strategy_specs = []
    strategy_risk = []

    price = float(strategy['PUT_LTP'])
    head = ['Legs','Asset','Direction','Lot','Strike','Expiry','Price','Underlying','Outlay']
    longleg = ['Long Leg','Put Option','Long',lot,strike,expiry.strftime('%d-%b-%Y'),price,underlying,-price*lot]
    shortleg = ['Short Leg','Put Option','Short',lot,higher_strike,expiry.strftime('%d-%b-%Y'),higher_strike_price,underlying,higher_strike_price*lot]
    total = ['','','','','','','','',higher_strike_price*lot-price*lot]
    strategy_specs = [head,longleg,shortleg,total]
    
    head = ['Intial Yield','Intial Yield/Day','Max Profit','Max Yield','Max Risk']
    risk = ['{0:.2f}%'.format(float(strategy['Initial_Yield'])*100),'{0:.2f}%'.format(float(strategy['Initial_Yield'])/time_to_maturity*100),
            float(strategy['Net_Credit']),'{0:.2f}%'.format(float(strategy['Max_Yield'])*100),
            float(strategy['Max_Risk'])]
    strategy_risk = [head,risk]
#    """
#    Contract Specifications------------------------------------------------------------
#    """
#    option_type_map = {'PE':'Put European',
#                       'CE':'Call European',
#                       'PA':'Put American',
#                       'CA':'Call American'}
#    
#    symbol = opid['symbol']
#    expiry = opid['expiry']
#    strike = opid['strike']
#    option_type = opid['option_type']
#    
#    quote = mu.getStockOptionQuote(symbol,expiry,strike,option_type)
#    moneyness = "ATM"
#    if option_type[0] == 'C':
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "OTM"
#    if option_type[0] == 'P':
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "OTM"
#        
#    contract_specs = [['Underlying','Option Type','Strike','Expiry',
#                       'Lot','LTP','Open Interest','Underlying','Moneyness'],
#                      [symbol,option_type_map[option_type],strike,expiry,
#                       quote['marketLot'],quote['lastPrice'],quote['openInterest'],
#                       quote['underlyingValue'],moneyness]]
#    
#    """
#    Option History----------------------------------------------------------------------
#    """
#    
#    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
#    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
#    dates = list(oh.index)
#    close = list(oh['Close'])
#    OI = list(oh['Open Interest'])
#    oh = oh.loc[[d for d in list(oh.index) if (enddate-d)% datetime.timedelta(days=3) == datetime.timedelta(0) ]]
#    oh = oh.sort_index(ascending=0)
#    
#    """
#    Price and OI Graph-------------------------------------------------------------------
#    """
#    labels = ['Dates','Price']
#    plt = mp.singleScaleLine_plots(labels,'Price')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,close,"C1",label='Close')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#
#    labels = ['Dates','Open Interest']
#    plt = mp.singleScaleLine_plots(labels,'Open Interest')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,OI,"C1",label='Open Interest')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    oi_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#    
    """
    Option Greeks and Graphs--------------------------------------------------------------
    """
    args = {'option_name':symbol+"_"+expiry.strftime('%d%b')+"_"+str(strike)+"_CE",
            'underlying_name':symbol,
            'maturity_date':expiry,
            'option_type':'Put',
            'strike': strike,                               
            'exercise_type':'European',
            'day_count':'30-360',
            'calendar':'India'}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        longoption = options.VanillaEuropeanOption(args)
        args['strike'] = higher_strike
        shortoption = options.VanillaEuropeanOption(args)

    """
    Set Interest Rate Curve
    """    

    args = {'day_count':'30-360',
            'calendar': 'India',
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear',
            'shiftparameter' : None}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    today = datetime.date.today()
    
    engine = mu.sql_engine()
    try:
        today = engine.execute("select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1").fetchall()[0][0]
    except:
        pass
    discount_curve = ts.SpotZeroYieldCurve('INR',today)
    discount_curve.setupCurve(args)

    """
    Set Flat Volatility Curve
    """    
    spotVol = 0.10
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    volatility_curve = ts.FlatVolatilityCurve(today,spotVol)
    volatility_curve.setupCurve(args)
    
    """
    Set Flat Dividend Curve
    """    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'flat_rate':0.01,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    dividend_curve = ts.FlatDividendYieldCurve(today,args['flat_rate'])
    dividend_curve.setupCurve(args)
    
    """
    Set Option Valuation and get Results
    """    
    valuation_method = 'Black Scholes'
    underlying_spot = underlying  
    
    longoption.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)

    shortoption.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)
    
    spotlongVol = longoption.getImpliedVol(price)
    spotshortVol = shortoption.getImpliedVol(higher_strike_price)
    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotlongVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
    
    longvolatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    longvolatility_curve.setupCurve(args)

    longoption.valuation(underlying_spot,
                     discount_curve,
                     longvolatility_curve,
                     dividend_curve,
                     valuation_method)
    
    args['spot_vols'] = spotshortVol
    shortvolatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    shortvolatility_curve.setupCurve(args)

    shortoption.valuation(underlying_spot,
                     discount_curve,
                     shortvolatility_curve,
                     dividend_curve,
                     valuation_method)

    longresults = longoption.getAnalytics()
    longresults.pop('NPV',None)
    shortresults = shortoption.getAnalytics()
    print(shortresults)
    shortresults.pop('NPV',None)

    longgreeks = {}
    shortgreeks = {}
    greeks = {}
    greeks['PV'] = float(strategy['Net_Credit'])

    for key in longresults.keys():
        longgreeks[str(key).capitalize()] = longresults[key]
        shortgreeks[str(key).capitalize()] = - shortresults[key]
        greeks[str(key).capitalize()] = longresults[key] - shortresults[key]                
    
    
    
    """
    Risk Profile and Greeks
    """
    
    underlying_spot_range = [max(0.10,max(abs(strike - higher_strike),0.5)*i + underlying_spot) for i in range(-5,5)]
    


    longlegNPV = []
    longlegdelta = []
    longleggamma = []
    longlegtheta = []
    shortlegNPV = []
    shortlegdelta = []
    shortleggamma = []
    shortlegtheta = []
    NPV = []
    delta = []
    gamma = []
    theta = []
    
    for spot in underlying_spot_range:
        longoption.valuation(spot,discount_curve,
                     longvolatility_curve,dividend_curve,
                     valuation_method)
        shortoption.valuation(spot,discount_curve,
                     shortvolatility_curve,dividend_curve,
                     valuation_method)
#        print(spot)
        longresult = longoption.getAnalytics()
        shortresult = shortoption.getAnalytics()
        longlegNPV.append((longresult['NPV'] - price)*lot)
        shortlegNPV.append((higher_strike_price - shortresult['NPV'])*lot)
        NPV.append((longresult['NPV']-shortresult['NPV'] + higher_strike_price - price)*lot)
        longlegdelta.append(longresult['delta'])
        shortlegdelta.append(-shortresult['delta'])
        delta.append(longresult['delta']-shortresult['delta'])
        longleggamma.append(longresult['gamma']-shortresult['gamma'])
        shortleggamma.append(-shortresult['gamma'])
        gamma.append(longresult['gamma']-shortresult['gamma'])
        longlegtheta.append(longresult['theta']-shortresult['theta'])
        shortlegtheta.append(-shortresult['theta'])
        theta.append(longresult['theta']-shortresult['theta'])
        
    labels = ['Underlying','NPV']
    plt = mp.singleScaleLine_plots(labels,'NPV')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegNPV,"C2",linestyle='--',label="Long Put")
    primary.plot(underlying_spot_range,shortlegNPV,"C3",linestyle='--',label="Short Put")
    primary.plot(underlying_spot_range,NPV,"C1",label='NPV')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    NPV_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Delta']
    plt = mp.singleScaleLine_plots(labels,'Delta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegdelta,"C2",linestyle='--',label="Long Put")
    primary.plot(underlying_spot_range,shortlegdelta,"C3",linestyle='--',label="Short Put")
    primary.plot(underlying_spot_range,delta,"C1",label='Delta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    delta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Gamma']
    plt = mp.singleScaleLine_plots(labels,'Gamma')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longleggamma,"C2",linestyle='--',label="Long Put")
    primary.plot(underlying_spot_range,shortleggamma,"C3",linestyle='--',label="Short Put")
    primary.plot(underlying_spot_range,gamma,"C1",label='Gamma')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    gamma_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Theta']
    plt = mp.singleScaleLine_plots(labels,'Theta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegtheta,"C2",linestyle='--',label="Long Put")
    primary.plot(underlying_spot_range,shortlegtheta,"C3",linestyle='--',label="Short Put")
    primary.plot(underlying_spot_range,theta,"C1",label='Theta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    theta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
    
    """
    Return list of analytics
    """
    
    return [strategy_desc,strategy_specs,strategy_risk,NPV_graph,delta_graph,gamma_graph,theta_graph,greeks]

def bear_call_spread_analysis(strategy):
    today = datetime.date.today()
    
    """
    Get Strategy Details--------------------------------------------------------------
    """

    symbol = strategy['Symbol']
    expiry = datetime.datetime.strptime(strategy['Expiry'],'%d%m%Y').date()
    time_to_maturity = (expiry - today).total_seconds()/datetime.timedelta(days=1).total_seconds()
    strike = float(strategy['Strike_Price'])
    lot = float(strategy['Lot'])
    underlying = float(strategy['Underlying'])
    lower_strike = float(strategy['Lower_Strike'])
    lower_strike_price = float(strategy['Lower_Strike_LTP'])
    
    strategy_desc = [symbol,expiry,strike,lower_strike]
    strategy_specs = []
    strategy_risk = []

    price = float(strategy['CALL_LTP'])
    head = ['Legs','Asset','Direction','Lot','Strike','Expiry','Price','Underlying','Outlay']
    longleg = ['Long Leg','Call Option','Long',lot,strike,expiry.strftime('%d-%b-%Y'),price,underlying,-price*lot]
    shortleg = ['Short Leg','Call Option','Short',lot,lower_strike,expiry.strftime('%d-%b-%Y'),lower_strike_price,underlying,lower_strike_price*lot]
    total = ['','','','','','','','',lower_strike_price*lot-price*lot]
    strategy_specs = [head,longleg,shortleg,total]
    
    head = ['Intial Yield','Intial Yield/Day','Max Profit','Max Yield','Max Risk']
    risk = ['{0:.2f}%'.format(float(strategy['Initial_Yield'])*100),'{0:.2f}%'.format(float(strategy['Initial_Yield'])/time_to_maturity*100),
            float(strategy['Net_Credit']),'{0:.2f}%'.format(float(strategy['Max_Yield'])*100),
            float(strategy['Max_Risk'])]
    strategy_risk = [head,risk]
#    """
#    Contract Specifications------------------------------------------------------------
#    """
#    option_type_map = {'PE':'Put European',
#                       'CE':'Call European',
#                       'PA':'Put American',
#                       'CA':'Call American'}
#    
#    symbol = opid['symbol']
#    expiry = opid['expiry']
#    strike = opid['strike']
#    option_type = opid['option_type']
#    
#    quote = mu.getStockOptionQuote(symbol,expiry,strike,option_type)
#    moneyness = "ATM"
#    if option_type[0] == 'C':
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "OTM"
#    if option_type[0] == 'P':
#        if (strike - quote['underlyingValue']) > 0:
#            moneyness = "ITM"
#        if (strike - quote['underlyingValue']) < 0:
#            moneyness = "OTM"
#        
#    contract_specs = [['Underlying','Option Type','Strike','Expiry',
#                       'Lot','LTP','Open Interest','Underlying','Moneyness'],
#                      [symbol,option_type_map[option_type],strike,expiry,
#                       quote['marketLot'],quote['lastPrice'],quote['openInterest'],
#                       quote['underlyingValue'],moneyness]]
#    
#    """
#    Option History----------------------------------------------------------------------
#    """
#    
#    oh = nsepy.get_history(symbol,startdate,enddate,option_type=option_type,strike_price=strike,expiry_date=expiry)
#    oh = oh[['Close','Open','High','Low','Open Interest','Underlying']]
#    dates = list(oh.index)
#    close = list(oh['Close'])
#    OI = list(oh['Open Interest'])
#    oh = oh.loc[[d for d in list(oh.index) if (enddate-d)% datetime.timedelta(days=3) == datetime.timedelta(0) ]]
#    oh = oh.sort_index(ascending=0)
#    
#    """
#    Price and OI Graph-------------------------------------------------------------------
#    """
#    labels = ['Dates','Price']
#    plt = mp.singleScaleLine_plots(labels,'Price')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,close,"C1",label='Close')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#
#    labels = ['Dates','Open Interest']
#    plt = mp.singleScaleLine_plots(labels,'Open Interest')
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    primary.plot(dates,OI,"C1",label='Open Interest')
##    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    oi_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
#    
    """
    Option Greeks and Graphs--------------------------------------------------------------
    """
    args = {'option_name':symbol+"_"+expiry.strftime('%d%b')+"_"+str(strike)+"_CE",
            'underlying_name':symbol,
            'maturity_date':expiry,
            'option_type':'Call',
            'strike': strike,                               
            'exercise_type':'European',
            'day_count':'30-360',
            'calendar':'India'}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        longoption = options.VanillaEuropeanOption(args)
        args['strike'] = lower_strike
        shortoption = options.VanillaEuropeanOption(args)

    """
    Set Interest Rate Curve
    """    

    args = {'day_count':'30-360',
            'calendar': 'India',
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear',
            'shiftparameter' : None}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    today = datetime.date.today()
    
    engine = mu.sql_engine()
    try:
        today = engine.execute("select curvedate from yieldcurve where curve='INR' order by curvedate desc limit 1").fetchall()[0][0]
    except:
        pass
    discount_curve = ts.SpotZeroYieldCurve('INR',today)
    discount_curve.setupCurve(args)

    """
    Set Flat Volatility Curve
    """    
    spotVol = 0.10
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    volatility_curve = ts.FlatVolatilityCurve(today,spotVol)
    volatility_curve.setupCurve(args)
    
    """
    Set Flat Dividend Curve
    """    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'flat_rate':0.01,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass

    
    dividend_curve = ts.FlatDividendYieldCurve(today,args['flat_rate'])
    dividend_curve.setupCurve(args)
    
    """
    Set Option Valuation and get Results
    """    
    valuation_method = 'Black Scholes'
    underlying_spot = underlying  
    
    longoption.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)

    shortoption.valuation(underlying_spot,
                     discount_curve,
                     volatility_curve,
                     dividend_curve,
                     valuation_method)
    
    spotlongVol = longoption.getImpliedVol(price)
    spotshortVol = shortoption.getImpliedVol(lower_strike_price)
    
    args = {'day_count':'30-360',
            'calendar': 'India',
            'spot_vols':spotlongVol,
            'compounding' : 'Compounded',
            'compounding_frequency' :'Annual',
            'interpolation' : 'Linear'}

    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
    
    longvolatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    longvolatility_curve.setupCurve(args)

    longoption.valuation(underlying_spot,
                     discount_curve,
                     longvolatility_curve,
                     dividend_curve,
                     valuation_method)
    
    args['spot_vols'] = spotshortVol
    shortvolatility_curve = ts.FlatVolatilityCurve(today,args['spot_vols'])
    shortvolatility_curve.setupCurve(args)

    shortoption.valuation(underlying_spot,
                     discount_curve,
                     shortvolatility_curve,
                     dividend_curve,
                     valuation_method)

    longresults = longoption.getAnalytics()
    longresults.pop('NPV',None)
    shortresults = shortoption.getAnalytics()
    shortresults.pop('NPV',None)

    longgreeks = {}
    shortgreeks = {}
    greeks = {}
    greeks['PV'] = float(strategy['Net_Credit'])

    for key in longresults.keys():
        longgreeks[str(key).capitalize()] = longresults[key]
        shortgreeks[str(key).capitalize()] = - shortresults[key]
        greeks[str(key).capitalize()] = longresults[key] - shortresults[key]                
    
    
    
    """
    Risk Profile and Greeks
    """
    
    underlying_spot_range = [max(0.10,max(abs(strike - lower_strike),0.5)*i + underlying_spot) for i in range(-5,5)]
    


    longlegNPV = []
    longlegdelta = []
    longleggamma = []
    longlegtheta = []
    shortlegNPV = []
    shortlegdelta = []
    shortleggamma = []
    shortlegtheta = []
    NPV = []
    delta = []
    gamma = []
    theta = []
    
    for spot in underlying_spot_range:
        longoption.valuation(spot,discount_curve,
                     longvolatility_curve,dividend_curve,
                     valuation_method)
        shortoption.valuation(spot,discount_curve,
                     shortvolatility_curve,dividend_curve,
                     valuation_method)
#        print(spot)
        longresult = longoption.getAnalytics()
        shortresult = shortoption.getAnalytics()
        longlegNPV.append((longresult['NPV'] - price)*lot)
        shortlegNPV.append((lower_strike_price - shortresult['NPV'])*lot)
        NPV.append((longresult['NPV']-shortresult['NPV'] + lower_strike_price - price)*lot)
        longlegdelta.append(longresult['delta'])
        shortlegdelta.append(-shortresult['delta'])
        delta.append(longresult['delta']-shortresult['delta'])
        longleggamma.append(longresult['gamma']-shortresult['gamma'])
        shortleggamma.append(-shortresult['gamma'])
        gamma.append(longresult['gamma']-shortresult['gamma'])
        longlegtheta.append(longresult['theta']-shortresult['theta'])
        shortlegtheta.append(-shortresult['theta'])
        theta.append(longresult['theta']-shortresult['theta'])
        
    labels = ['Underlying','NPV']
    plt = mp.singleScaleLine_plots(labels,'NPV')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegNPV,"C2",linestyle='--',label="Long Call")
    primary.plot(underlying_spot_range,shortlegNPV,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,NPV,"C1",label='NPV')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    NPV_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Delta']
    plt = mp.singleScaleLine_plots(labels,'Delta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegdelta,"C2",linestyle='--',label="Long Call")
    primary.plot(underlying_spot_range,shortlegdelta,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,delta,"C1",label='Delta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    delta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Gamma']
    plt = mp.singleScaleLine_plots(labels,'Gamma')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longleggamma,"C2",linestyle='--',label="Long Call")
    primary.plot(underlying_spot_range,shortleggamma,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,gamma,"C1",label='Gamma')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    gamma_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    labels = ['Underlying','Theta']
    plt = mp.singleScaleLine_plots(labels,'Theta')

    fig,primary,secondary = plt[0],plt[1],plt[2]
    
    primary.plot(underlying_spot_range,longlegtheta,"C2",linestyle='--',label="Long Call")
    primary.plot(underlying_spot_range,shortlegtheta,"C3",linestyle='--',label="Short Call")
    primary.plot(underlying_spot_range,theta,"C1",label='Theta')
    primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    
    buffer = io.BytesIO()
    fig.savefig(buffer,format="PNG")
    theta_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    buffer.close()
    
    
    
    """
    Return list of analytics
    """
    
    return [strategy_desc,strategy_specs,strategy_risk,NPV_graph,delta_graph,gamma_graph,theta_graph,greeks]
