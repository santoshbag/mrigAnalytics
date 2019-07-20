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

import matplotlib.pyplot as plt
import statsmodels.api as sm
import research.math as rm
import strategies.stocks as st
from concurrent.futures import ThreadPoolExecutor as Executor
import nsepy
import numpy as np
from time import sleep

today = datetime.date.today()
engine = mu.sql_engine()

def big_money_zack():
    """
    BIG MONEY ZACK screener
    
    Min 20-day trading volume > 50,000
    Log return of 24 weeks : top 20
    Log return of 12 weeks : top 10
    Log return of 4 weeks : top 3
    P/S < 0.5
    """
    startdate = today - dateutil.relativedelta.relativedelta(weeks=27)
    
    volumedate = today - datetime.timedelta(days=20)
    sql = "select symbol from (select symbol, min(volume) as minvol from stock_history where series='EQ' and date > '"+volumedate.strftime('%Y-%m-%d') +"' group by symbol) as foo where minvol > 50000 "
    sql = "select  date, symbol, price, daily_log_returns from daily_returns where date > '"+startdate.strftime('%Y-%m-%d') + "' and symbol in ("+sql+") and price > 10  \
           and symbol in (select symbol from (select symbol,close,close/sales_per_share as ps from (select * , rank() over (partition by symbol order by ratio_date desc) \
           from industry_symbol_ratios()) tb1 where rank=1) tb2 where tb2.ps <= 0.5)"
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
#    print(stockreturns)
    stockreturns = stockreturns.sort_values(by='ret12W',ascending=0).head(10)
    stockreturns = stockreturns.sort_values(by='ret4W',ascending=0)
    
    bigmoneyzack_stocks = list(stockreturns.index)
#    print(bigmoneyzack_stocks)
    for i in bigmoneyzack_stocks:
        stock_df.xs(i,level='symbol')['price'].plot()
    
    return stockreturns        
    

def top_mf_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           convert_to_numeric(mfs.rating)=5 and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) and\
           mfp.download_date = mfs.download_date \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    #print(holdings)
    return holdings

def top_mf_smallcap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-SC' and \
           convert_to_numeric(mfs.rating) in (4,5) and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    print(holdings)

def top_mf_midcap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund), (select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-MC' and \
           convert_to_numeric(mfs.rating) in (4,5) and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
#    print(holdings)

def top_mf_largecap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund), (select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-LC' and \
           convert_to_numeric(mfs.rating) in (4,5) and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
#    print(holdings)

def top_mf_multicap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-MLC' and \
           convert_to_numeric(mfs.rating) in (4,5) and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
#    print(holdings)

def top_mf_value_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-VAL' and \
           convert_to_numeric(mfs.rating) in (4,5) and \
           convert_to_numeric(mfp.holding_current)>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
#    print(holdings)

def sector_returns(num_companies_per_sector='10',period='1Y'):
          
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
    
#    sql = "select r.date, sm.industry, avg(r.daily_log_returns) as daily_log_returns \
#          from daily_returns r inner join security_master sm on r.symbol=sm.symbol \
#          where sm.industry is not null and r.date >='"+startdate.strftime('%Y-%m-%d')+"' \
#          group by r.date, sm.industry"

    sql = "select * from industry_returns("+num_companies_per_sector+" ,'" + startdate.strftime('%Y-%m-%d')+"')"
    
    engine = mu.sql_engine()
    daily_logreturns = pd.read_sql(sql,engine)
    if not daily_logreturns.empty:
        daily_logreturns.set_index('retdate',inplace=True)

    return daily_logreturns    


def small_cap_growth():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
    """
    (1) MktCap of below 5000 cr (2) price > 10 (3)ADTV > 25 M 
    (4) EPSGROWTH > 1.2 * MEDIAN(industry EPS growth) < 50% 
    (5) PE < MEDIAN(INDUSTRY PE) (6)PS < MEDIAN (INDUSTRY PS)
    (7) Strong Buy
    """
    startdate = today - dateutil.relativedelta.relativedelta(months=3)    
    sql = " select foo.*, indmedsagg.* from (select * , rank() over ( partition by symbol order by ratio_date desc) from industry_symbol_ratios() where symbol in \
          (select sm.symbol from security_master sm where convert_to_numeric(sm.outstanding_shares)* \
          (select sh.close from stock_history sh where sh.symbol=sm.symbol order by sh.date  desc limit 1) \
          <= 50000000000 and \
          sm.symbol in (select distinct symbol from stock_history where close > 10) and \
          sm.symbol in (select symbol from (select symbol, avg(close*volume) as adtv from stock_history where series='EQ' and date > \
          '" + startdate.strftime('%Y-%m-%d')+"' group by symbol) foo1 where adtv > 25000000))) foo inner join \
          (select industry as inds, median(eps_growth) as eps_growth_median, median(close/basic_eps) as pemedian, median(close/sales_per_share) as psmedian from \
          (select * , rank() over (partition by symbol order by ratio_date desc ) \
          from industry_symbol_ratios()) indmeds \
          where rank=1 group by industry) indmedsagg on indmedsagg.inds = foo.industry"
          
    engine = mu.sql_engine()
    small_caps = pd.read_sql(sql,engine)
    if not small_caps.empty:
        small_caps.set_index('symbol',inplace=True)
    small_caps['pe'] = small_caps['close']/small_caps['basic_eps']
    small_caps['ps'] = small_caps['close']/small_caps['sales_per_share']
    small_caps = small_caps.loc[small_caps['rank'] == 1]
    small_caps = small_caps.loc[small_caps['eps_growth'] > 0]
    EPSGrowth = small_caps.loc[small_caps['eps_growth'] >= 1.2*small_caps['eps_growth_median']]
    EPSGrowth = EPSGrowth.loc[EPSGrowth['eps_growth'] <= 0.5]
    PELow = EPSGrowth.loc[EPSGrowth['pe'] <= EPSGrowth['pemedian']]
    PSLow = PELow.loc[PELow['ps'] <= PELow['psmedian']]
    PSLow = PSLow.sort_values(by='ps',ascending=1).head(7)
#    print(PSLow[['industry','close','basic_eps','eps_growth','pe','ps','pemedian','psmedian','eps_growth_median']])
    return(PSLow)

def roe_growth():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore

    """
    (1) PS <= 1 (2) ROE > 10 (3)Price > 5 
    (7) Strong Buy
    """

    
#    startdate = today - dateutil.relativedelta.relativedelta(months=3)    
    sql = " select * , rank() over ( partition by symbol order by ratio_date desc) from industry_symbol_ratios()"
          
    engine = mu.sql_engine()
    roe = pd.read_sql(sql,engine)
    if not roe.empty:
        roe.set_index('symbol',inplace=True)
#    roe['pe'] = roe['close']/roe['basic_eps']
    roe['ps'] = roe['close']/roe['sales_per_share']
    roe = roe.loc[roe['rank'] == 1]
    
    ROEGrowth = roe.loc[roe['return_on_equity'] >= 10]
    PSLow = ROEGrowth.loc[ROEGrowth['ps'] <= 1]
    PRICE5 = PSLow.loc[PSLow['close'] >= 5]
#    print(PRICE5[['industry','close','basic_eps','eps_growth','ps','return_on_equity']])
    return(PRICE5)

def ta_fa():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
    """
    TECHNICAL ANALYSIS AND FUNDAMENTAL ANALYSIS
    (1) Strong Buy (2) price > 10 (3) ADTV > 75 M 
    (4) EPSGROWTH > MEDIAN(industry EPS growth) 
    (5) Volume > Volume 1 wk ago > Volume 2 Wk ago > Volume 3 wk ago
    (6)PS < MEDIAN (INDUSTRY PS)
    (7) 24W return (Top 30) (8) 12W return (Top 20) (9) 4W return (Top 7)
    """
    
    
    startdate = today - dateutil.relativedelta.relativedelta(weeks=27)
    threeweekago = today - dateutil.relativedelta.relativedelta(weeks=3)
    twoweekago = today - dateutil.relativedelta.relativedelta(weeks=2)
    oneweekago = today - dateutil.relativedelta.relativedelta(weeks=1)
    
    sql = "select foo.*, indmedsagg.* ,dr.date,dr.daily_log_returns from (select * , rank() over \
          ( partition by symbol order by ratio_date desc) from industry_symbol_ratios() where symbol in \
          (select symbol from stock_history where series='EQ' and close*volume >= 75000000) \
          and symbol in (select sh.symbol from \
            stock_history sh inner join stock_history sh1 on sh.symbol=sh1.symbol \
            inner join stock_history sh2 on sh2.symbol=sh1.symbol \
            inner join stock_history sh3 on sh3.symbol=sh2.symbol \
            where sh.date = (select date from stock_history order by date desc limit 1) \
            and sh1.date = sh.date - interval '1 week' \
            and sh2.date = sh1.date - interval '1 week' \
            and sh3.date = sh2.date - interval '1 week' \
            and sh.volume > sh1.volume \
            and sh1.volume > sh2.volume \
            and sh2.volume > sh3.volume)) foo inner join \
            (select industry as inds, median(eps_growth) as eps_growth_median, median(close/basic_eps) as pemedian, median(close/sales_per_share) as psmedian from \
            (select * , rank() over (partition by symbol order by ratio_date desc ) \
            from industry_symbol_ratios()) indmeds \
            where rank=1 group by industry) indmedsagg on indmedsagg.inds = foo.industry \
            inner join daily_returns dr \
            on foo.symbol = dr.symbol where dr.date > '"+startdate.strftime('%Y-%m-%d')+"'"
          
    engine = mu.sql_engine()
    ta_fa = pd.read_sql(sql,engine)
#    print(set(ta_fa.index))    

    if not ta_fa.empty:
        ta_fa.set_index('symbol',inplace=True)
    ta_fa['pe'] = ta_fa['close']/ta_fa['basic_eps']
    ta_fa['ps'] = ta_fa['close']/ta_fa['sales_per_share']
    ta_fa = ta_fa.loc[ta_fa['rank'] == 1]
    ta_fa = ta_fa.loc[ta_fa['eps_growth'] > 0]
    EPSGrowth = ta_fa.loc[ta_fa['eps_growth'] >= ta_fa['eps_growth_median']]
    PSLow = EPSGrowth.loc[EPSGrowth['ps'] <= EPSGrowth['psmedian']]
    start24 = today -dateutil.relativedelta.relativedelta(weeks=24)
    start12 = today -dateutil.relativedelta.relativedelta(weeks=12)
    start4 = today -dateutil.relativedelta.relativedelta(weeks=4)
#    print(set(PSLow.index))
    PSLow['ret24W'] = "NA"
    PSLow['ret12W'] = "NA"
    PSLow['ret4W'] = "NA"
    for sym in set(PSLow.index):
#        print(sym)
        PSLow.loc[sym,'ret24W'] = PSLow.loc[PSLow['date'] >= start24].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret12W'] = PSLow.loc[PSLow['date'] >= start12].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret4W'] = PSLow.loc[PSLow['date'] >= start4].loc[sym]['daily_log_returns'].sum()
    PSLow = PSLow[['industry','eps_growth','ps','ret24W','ret12W','ret4W','eps_growth_median','psmedian','pe']].drop_duplicates()
#    print(PSLow)
    PSLow = PSLow.sort_values(by='ret24W',ascending=0).head(30)
#    print(stockreturns)
    PSLow = PSLow.sort_values(by='ret12W',ascending=0).head(20)
    PSLow = PSLow.sort_values(by='ret4W',ascending=0).head(7)

    return(PSLow)

def newhighs():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
    """
    NEW HIGHS
    (1) Current Price / 52 W High >=80% (2) 12W return > 0 (3) 4W return > 0 
    (4) EPSGROWTH > MEDIAN(industry EPS growth) 
    (5) 20D Avg Volume > 20D Avg Volume 1 wk ago > 100000
    (6)PS <= MEDIAN (INDUSTRY PS) (7) PE <= MEDIAN (INDUSTRY PE)
    (8) 12W return + 4W return (Top 5)
    """
    
    startdate = today - dateutil.relativedelta.relativedelta(weeks=13)
    threeweekago = today - dateutil.relativedelta.relativedelta(weeks=3)
    twoweekago = today - dateutil.relativedelta.relativedelta(weeks=2)
    oneweekago = today - dateutil.relativedelta.relativedelta(weeks=1)
    
    sql = "select foo.*, indmedsagg.* ,dr.date,dr.daily_log_returns from (select * , rank() over \
          ( partition by symbol order by ratio_date desc) from industry_symbol_ratios() where symbol in \
          (select symbol from (select sh.symbol , sh.close_adj , (select max(sh1.close_adj) as high52week from stock_history sh1  \
          where sh1.date > now() - interval '52 weeks' and sh1.symbol=sh.symbol) \
          from stock_history sh where sh.date = (select max(date) from stock_history)) highs where close_adj/high52week >= 0.80) \
          and symbol in ( \
          select symbol from (select sh.symbol, (select avg(sh1.volume) as avg20dvol1 from stock_history sh1 where \
          sh1.date > (now() - interval '20 days') \
          and sh1.symbol = sh.symbol group by sh.symbol), \
          (select avg(sh2.volume) as avg20dvol2 from stock_history sh2 where sh2.date > (now() - interval '40 days') \
          and sh2.date <= (now() - interval '20 days') and sh2.symbol = sh.symbol group by sh2.symbol) \
          from stock_history sh \
          where sh.date = (select max(date) from stock_history)) volavg \
          where avg20dvol1 > avg20dvol2 and avg20dvol1 > 100000)) foo inner join \
          (select industry as inds, median(eps_growth) as eps_growth_median, median(close/basic_eps) as pemedian, median(close/sales_per_share) as psmedian from \
          (select * , rank() over (partition by symbol order by ratio_date desc ) \
          from industry_symbol_ratios()) indmeds \
          where rank=1 group by industry) indmedsagg on indmedsagg.inds = foo.industry \
          inner join daily_returns dr \
          on foo.symbol = dr.symbol where dr.date > '"+startdate.strftime('%Y-%m-%d')+"'"
          
    engine = mu.sql_engine()
    newhighs = pd.read_sql(sql,engine)
    if not newhighs.empty:
        newhighs.set_index('symbol',inplace=True)
    newhighs['pe'] = newhighs['close']/newhighs['basic_eps']
    newhighs['ps'] = newhighs['close']/newhighs['sales_per_share']
    newhighs = newhighs.loc[newhighs['rank'] == 1]
    newhighs = newhighs.loc[newhighs['eps_growth'] > 0]
#    print(set(newhighs.index))    
    EPSGrowth = newhighs.loc[newhighs['eps_growth'] >= newhighs['eps_growth_median']]
    PELow = EPSGrowth.loc[EPSGrowth['pe'] <= EPSGrowth['pemedian']]
    PSLow = PELow.loc[PELow['ps'] <= PELow['psmedian']]
    start24 = today -dateutil.relativedelta.relativedelta(weeks=24)
    start12 = today -dateutil.relativedelta.relativedelta(weeks=12)
    start4 = today -dateutil.relativedelta.relativedelta(weeks=4)
#    print(set(PSLow.index))
    PSLow['ret12W'] = np.NaN
    PSLow['ret4W'] = np.NaN
    for sym in set(PSLow.index):
        PSLow.loc[sym,'ret12W'] = PSLow.loc[PSLow['date'] >= start12].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret4W'] = PSLow.loc[PSLow['date'] >= start4].loc[sym]['daily_log_returns'].sum()
#    print(PSLow)
    PSLow = PSLow.loc[PSLow['ret12W'] > 0]
    PSLow = PSLow.loc[PSLow['ret4W'] > 0]
    PSLow['ret'] = PSLow['ret12W'] + PSLow['ret4W']
    PSLow.sort_values(by='ret',ascending=0)
    PSLow = PSLow[['industry','eps_growth','ps','pe','ret12W','ret4W','eps_growth_median','psmedian','pemedian']].drop_duplicates()
#    print(PSLow)
    return(PSLow)

def growth_income():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
    """
    GROWTH AND INCOME
    (1) ROE >= MEDIAN(Nifty ROE) (2) PE <= MEDIAN(Nifty PE) (3) D/E <= 1 
    (4) Beta <= 1 
    (5) Div Yld >= MEDIAN (NIFTY Div Yld)
    (6) Div Yld (Top 2 of each sector) (7) Div Yld (Top 7)
    12 Weeks balancing period
    """
    
    startdate = today - dateutil.relativedelta.relativedelta(weeks=13)
    
    sql = "select ra.*,mds.* from (select * , rank() over \
          ( partition by symbol order by ratio_date desc) from industry_symbol_ratios()) ra  \
          , (select median(pe) as niftype,median(pb) as niftypb , median(100*pb/pe) as niftyroe , median(div_yield) as niftydivyld from stock_history \
          where symbol='NIFTY 50' and series='IN' \
          and date > (now() - interval '12 weeks')) mds \
          where rank = 1 and dividend_per_share is not null and dividend_per_share <> 0 and debt_to_equity <> 0"
    
    return_sql = "select * from daily_returns dr where dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
    engine = mu.sql_engine()
    growth_income = pd.read_sql(sql,engine)
    returns = pd.read_sql(return_sql,engine)
    if not growth_income.empty:
        growth_income.set_index('symbol',inplace=True)
    if not returns.empty:
        returns.set_index('symbol',inplace=True)
    growth_income['pe'] = growth_income['close']/growth_income['basic_eps']
    growth_income['divyld'] = 100*growth_income['dividend_per_share']/growth_income['close']
    growth_income = growth_income.loc[growth_income['rank'] == 1]
    PELow = growth_income.loc[growth_income['pe'] <= growth_income['niftype']]
#    print(PELow[['pe','return_on_equity','debt_to_equity','divyld']])
    ROEHigh = PELow.loc[PELow['return_on_equity'] >= PELow['niftyroe']]
#    print(ROEHigh[['pe','return_on_equity','debt_to_equity','divyld']])
    DELow = ROEHigh.loc[ROEHigh['debt_to_equity'] <= 1]
#    print(DELow[['pe','return_on_equity','debt_to_equity','divyld']])
    DIVHigh = DELow.loc[DELow['divyld'].astype(float) >= DELow['niftydivyld']]
    for sym in set(DIVHigh.index):
        A = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc['NIFTY 50'])
        B = list(returns[returns['date'].isin(set(returns['date'].loc['NIFTY 50']) & set(returns['date'].loc[sym]))]['daily_log_returns'].loc[sym])
        beta = np.cov(A,B)[0][1]/np.var(A)
        DIVHigh.loc[sym,'beta'] = beta # np.cov(A,B)[0][1]/np.var(A)
#    print(set(PEGLow.index))
    DIVHigh = DIVHigh.loc[DIVHigh['beta']<= 1]
    DIVHigh = DIVHigh.sort_values(by='divyld', ascending=0)
#    print(DIVHigh.head(7))
    return(DIVHigh.head(7))


def custom_stock_screener(criteria):
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
    """
    GROWTH AND INCOME
    (1) ROE >= MEDIAN(Nifty ROE) (2) PE <= MEDIAN(Nifty PE) (3) D/E <= 1 
    (4) Beta <= 1 
    (5) Div Yld >= MEDIAN (NIFTY Div Yld)
    (6) Div Yld (Top 2 of each sector) (7) Div Yld (Top 7)
    12 Weeks balancing period
    """
    
    operator = {'equals':'=',
                'greater than':'>',
                'greater than or equals':'>=',
                'less than':'<',
                'less than or equals':'<=',
                }
    aggregator = {'Average':'avg',
                'Median':'median',
                'High':'max',
                'Low':'min',
                }
    period = {'D':'days',
                'W':'weeks',
                'M':'months',
                'Y':'years',
                }
    
    resultdf = pd.DataFrame()
    sql = "select distinct symbol from stock_history"
    engine = mu.sql_engine()
    resultdf = pd.read_sql(sql,engine)
    resultdf.set_index('symbol',inplace=True)

    symbollist = ""
    startdate = today - dateutil.relativedelta.relativedelta(weeks=13)
    """
    Market/Technical Parameter filters
    Market Capitalization	
    Price
    Daily Volume
    Price Volume
    Price Returns
    """    
    marketcap_op = criteria['marketcap_op']
    marketcap_abs_filter = criteria['marketcap_abs_filter']

    if marketcap_abs_filter.strip() != "-":
        sql = "select sm.symbol, convert_to_numeric(sm.outstanding_shares)*\
              (select sh.close from stock_history sh where sh.symbol=sm.symbol order by sh.date  desc limit 1) as marketcap \
              from security_master sm where convert_to_numeric(sm.outstanding_shares)*\
              (select sh.close from stock_history sh where sh.symbol=sm.symbol order by sh.date  desc limit 1)\
              "+ operator[marketcap_op] +" "+marketcap_abs_filter
    
        engine = mu.sql_engine()
        marketcap = pd.read_sql(sql,engine)
        symbollist = ""
        if not marketcap.empty:
            marketcap.set_index('symbol',inplace=True)
            symbollist = "where st.symbol in "+str(tuple(marketcap.index))
            resultdf = marketcap
        
    price_aggf = criteria['price_aggf']
    price_aggp = criteria['price_aggp']
    price_aggpnum = criteria['price_aggpnum']    
    price_op = criteria['price_op']
    price_abs_filter = criteria['price_abs_filter']
    
    if price_abs_filter.strip() != "-":
        if price_aggf != '-999' and price_aggp != '-999':
            sql = "select * from (select sh.symbol, "+aggregator[price_aggf]+"(sh.close) as close from stock_history sh \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   sh.date >= (now() - interval '"+price_aggpnum+" "+period[price_aggp]+"') group by sh.symbol) tab1 where  tab1.close\
                   "+operator[price_op] +" "+price_abs_filter
        elif price_abs_filter != '0':
            sql = "select sh.symbol, sh.close from stock_history sh inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   sh.close "+operator[price_op] +" "+price_abs_filter        
        else:
            sql = ""
    
        engine = mu.sql_engine()
        if sql != "":
            price = pd.read_sql(sql,engine)
            symbollist = ""
            if not price.empty:
                price.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(price.index))
                resultdf = resultdf.merge(price,how='inner',left_index=True,right_index=True)
    
# Volume Filter
    volume_aggf = criteria['volume_aggf']
    volume_aggp = criteria['volume_aggp']
    volume_aggpnum = criteria['volume_aggpnum']    
    volume_op = criteria['volume_op']
    volume_abs_filter = criteria['volume_abs_filter']

    if volume_abs_filter.strip() != "-":    
        if volume_aggf != '-999' and volume_aggp != '-999':
            sql = "select * from (select sh.symbol, "+aggregator[volume_aggf]+"(sh.volume) as volume from stock_history sh \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   sh.date >= (now() - interval '"+volume_aggpnum+" "+period[volume_aggp]+"') group by sh.symbol) tab1 where  tab1.volume\
                   "+operator[volume_op] +" "+volume_abs_filter
        elif volume_abs_filter != '0':
            sql = "select sh.symbol, sh.volume from stock_history sh inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   sh.volume "+operator[volume_op] +" "+volume_abs_filter        
        else:
            sql = ""
    
        engine = mu.sql_engine()
        if sql != "":
            volume = pd.read_sql(sql,engine)
            symbollist = ""
            if not volume.empty:
                volume.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(volume.index))
                resultdf = resultdf.merge(volume,how='inner',left_index=True,right_index=True)

# PriceVolume Filter
    pricevolume_aggf = criteria['pricevolume_aggf']
    pricevolume_aggp = criteria['pricevolume_aggp']
    pricevolume_aggpnum = criteria['pricevolume_aggpnum']    
    pricevolume_op = criteria['pricevolume_op']
    pricevolume_abs_filter = criteria['pricevolume_abs_filter']
    
    if pricevolume_abs_filter.strip() != "-":
        if pricevolume_aggf != '-999' and pricevolume_aggp != '-999':
            sql = "select * from (select sh.symbol, "+aggregator[pricevolume_aggf]+"(sh.close*sh.volume) as pricevolume from stock_history sh \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   sh.date >= (now() - interval '"+pricevolume_aggpnum+" "+period[pricevolume_aggp]+"') group by sh.symbol) tab1 where  tab1.pricevolume\
                   "+operator[pricevolume_op] +" "+pricevolume_abs_filter
        elif pricevolume_abs_filter != '0':
            sql = "select sh.symbol, (sh.close*sh.volume) as pricevolume from stock_history sh inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=sh.symbol where \
                   (sh.close*sh.volume) "+operator[pricevolume_op] +" "+pricevolume_abs_filter        
        else:
            sql = ""
    
        engine = mu.sql_engine()
        if sql != "":
            pricevolume = pd.read_sql(sql,engine)
            symbollist = ""
            if not pricevolume.empty:
                pricevolume.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(pricevolume.index))
                resultdf = resultdf.merge(pricevolume,how='inner',left_index=True,right_index=True)
        
# PriceReturn Filter
    pricereturn_aggp = criteria['pricereturn_aggp']
    pricereturn_aggpnum = criteria['pricereturn_aggpnum']    
    pricereturn_op = criteria['pricereturn_op']
    pricereturn_abs_filter = criteria['pricereturn_abs_filter']
    pricereturn_bm_f = criteria['pricereturn_bm_f']

    if pricereturn_abs_filter.strip() != "-" and pricereturn_bm_f != -999:
        if pricereturn_bm_f == 'Nifty' and pricereturn_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[pricereturn_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"'))"
        elif pricereturn_bm_f == 'Industry Median' and pricereturn_aggp != '-999':
            sql = "select distinct tab3.symbol, tab3.ret, tab3.industry,tab4.medret from  (select tab1.symbol, tab1.ret , industry from \
                  (select dr.symbol,sum(dr.daily_log_returns) as ret from daily_returns  dr \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol \
                  where dr.date > (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 \
                  inner join security_master sm on tab1.symbol=sm.symbol where industry is not null) tab3 inner join (select tab2.industry, median(tab2.ret) \
                  as medret from (select tab1.symbol, tab1.ret , industry from \
                  (select dr.symbol,sum(dr.daily_log_returns) as ret from daily_returns  dr \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol \
                  where dr.date > (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 \
                  inner join security_master sm on tab1.symbol=sm.symbol where industry is not null) tab2 group by tab2.industry) tab4 on tab3.industry=tab4.industry \
                  where tab3.ret "+operator[pricereturn_op] +"tab4.medret"
        elif pricereturn_bm_f == 'Industry Average' and pricereturn_aggp != '-999':
            sql = "select distinct tab3.symbol, tab3.ret, tab3.industry,tab4.medret from  (select tab1.symbol, tab1.ret , industry from \
                  (select dr.symbol,sum(dr.daily_log_returns) as ret from daily_returns  dr \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol \
                  where dr.date > (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 \
                  inner join security_master sm on tab1.symbol=sm.symbol where industry is not null) tab3 inner join (select tab2.industry, avg(tab2.ret) \
                  as medret from (select tab1.symbol, tab1.ret , industry from \
                  (select dr.symbol,sum(dr.daily_log_returns) as ret from daily_returns  dr \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol \
                  where dr.date > (now() - interval'"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 \
                  inner join security_master sm on tab1.symbol=sm.symbol where industry is not null) tab2 group by tab2.industry) tab4 on tab3.industry=tab4.industry \
                  where tab3.ret "+operator[pricereturn_op] +"tab4.medret"
        else:
            sql = "select distinct * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+pricereturn_aggpnum+" "+period[pricereturn_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[pricereturn_op] +" "+pricereturn_abs_filter
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            pricereturn = pd.read_sql(sql,engine)
            symbollist = ""
            if not pricereturn.empty:
                pricereturn.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(pricereturn.index))
                resultdf = resultdf.merge(pricereturn,how='inner',left_index=True,right_index=True)

#EPS Growth
    basiceps_aggf = criteria['basiceps_aggf']
    basiceps_aggp = criteria['basiceps_aggp']
    basiceps_aggpnum = criteria['basiceps_aggpnum']    
    basiceps_op = criteria['basiceps_op']
    basiceps_abs_filter = criteria['basiceps_abs_filter']
    basiceps_bm_f = criteria['basiceps_bm_f']

    if basiceps_abs_filter.strip() != "-" and basiceps_bm_f != -999:
        if basiceps_bm_f == 'Nifty' and basiceps_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+basiceps_aggpnum+" "+period[basiceps_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[basiceps_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+basiceps_aggpnum+" "+period[basiceps_aggp]+"'))"
        elif basiceps_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.eps_growth, isr2.medianeps from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(eps_growth) as medianeps from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.eps_growth \
                  "+operator[basiceps_op] +" isr2.medianeps order by isr1.industry"
        elif basiceps_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.eps_growth, isr2.avgeps from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(eps_growth) as avgeps from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.eps_growth \
                  "+operator[basiceps_op] +" isr2.avgeps order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.eps_growth from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.eps_growth"+operator[basiceps_op] +" "+basiceps_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            basiceps = pd.read_sql(sql,engine)
            symbollist = ""
            if not basiceps.empty:
                basiceps.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(basiceps.index))
                resultdf = resultdf.merge(basiceps,how='inner',left_index=True,right_index=True)

#Dividend Yield

    dividendyield_aggf = criteria['dividendyield_aggf']
    dividendyield_aggp = criteria['dividendyield_aggp']
    dividendyield_aggpnum = criteria['dividendyield_aggpnum']    
    dividendyield_op = criteria['dividendyield_op']
    dividendyield_abs_filter = criteria['dividendyield_abs_filter']
    dividendyield_bm_f = criteria['dividendyield_bm_f']

    if dividendyield_abs_filter.strip() != "-" and dividendyield_bm_f != -999:
        if dividendyield_bm_f == 'Nifty' and dividendyield_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+dividendyield_aggpnum+" "+period[dividendyield_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[dividendyield_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+dividendyield_aggpnum+" "+period[dividendyield_aggp]+"'))"
        elif dividendyield_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.dividend_yield, isr2.median_dividend_yield from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(dividend_yield) as median_dividend_yield from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.dividend_yield \
                  "+operator[dividendyield_op] +" isr2.median_dividend_yield order by isr1.industry"
        elif dividendyield_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.dividend_yield, isr2.avg_dividend_yield from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(dividend_yield) as avg_dividend_yield from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.dividend_yield \
                  "+operator[dividendyield_op] +" isr2.avg_dividend_yield order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.dividend_yield from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.dividend_yield"+operator[dividendyield_op] +" "+dividendyield_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            dividendyield = pd.read_sql(sql,engine)
            symbollist = ""
            if not dividendyield.empty:
                dividendyield.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(dividendyield.index))
                resultdf = resultdf.merge(dividendyield,how='inner',left_index=True,right_index=True)

#Price Earnings

    pe_aggf = criteria['pe_aggf']
    pe_aggp = criteria['pe_aggp']
    pe_aggpnum = criteria['pe_aggpnum']    
    pe_op = criteria['pe_op']
    pe_abs_filter = criteria['pe_abs_filter']
    pe_bm_f = criteria['pe_bm_f']

    if pe_abs_filter.strip() != "-" and pe_bm_f != -999:
        if pe_bm_f == 'Nifty' and pe_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+pe_aggpnum+" "+period[pe_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[pe_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+pe_aggpnum+" "+period[pe_aggp]+"'))"
        elif pe_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earnings, isr2.median_price_to_earnings from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(price_to_earnings) as median_price_to_earnings from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_earnings \
                  "+operator[pe_op] +" isr2.median_price_to_earnings order by isr1.industry"
        elif pe_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earnings, isr2.avg_price_to_earnings from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(price_to_earnings) as avg_price_to_earnings from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_earnings \
                  "+operator[pe_op] +" isr2.avg_price_to_earnings order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earnings from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.price_to_earnings"+operator[pe_op] +" "+pe_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            pe = pd.read_sql(sql,engine)
            symbollist = ""
            if not pe.empty:
                pe.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(pe.index))
                resultdf = resultdf.merge(pe,how='inner',left_index=True,right_index=True)

#Price to BV

    pb_aggf = criteria['pb_aggf']
    pb_aggp = criteria['pb_aggp']
    pb_aggpnum = criteria['pb_aggpnum']    
    pb_op = criteria['pb_op']
    pb_abs_filter = criteria['pb_abs_filter']
    pb_bm_f = criteria['pb_bm_f']

    if pb_abs_filter.strip() != "-" and pb_bm_f != -999:
        if pb_bm_f == 'Nifty' and pb_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+pb_aggpnum+" "+period[pb_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[pb_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+pb_aggpnum+" "+period[pb_aggp]+"'))"
        elif pb_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_bv, isr2.medianeps from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(price_to_bv) as medianeps from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_bv \
                  "+operator[pb_op] +" isr2.medianeps order by isr1.industry"
        elif pb_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_bv, isr2.avgeps from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(price_to_bv) as avgeps from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_bv \
                  "+operator[pb_op] +" isr2.avgeps order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_bv from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.price_to_bv"+operator[pb_op] +" "+pb_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            pb = pd.read_sql(sql,engine)
            symbollist = ""
            if not pb.empty:
                pb.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(pb.index))
                resultdf = resultdf.merge(pb,how='inner',left_index=True,right_index=True)
                

#Price to Sales

    ps_aggf = criteria['ps_aggf']
    ps_aggp = criteria['ps_aggp']
    ps_aggpnum = criteria['ps_aggpnum']    
    ps_op = criteria['ps_op']
    ps_abs_filter = criteria['ps_abs_filter']
    ps_bm_f = criteria['ps_bm_f']

    if ps_abs_filter.strip() != "-" and ps_bm_f != -999:
        if ps_bm_f == 'Nifty' and ps_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+ps_aggpnum+" "+period[ps_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[ps_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+ps_aggpnum+" "+period[ps_aggp]+"'))"
        elif ps_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_sales, isr2.median_price_to_sales from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(price_to_sales) as median_price_to_sales from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_sales \
                  "+operator[ps_op] +" isr2.median_price_to_sales order by isr1.industry"
        elif ps_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_sales, isr2.avg_price_to_sales from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(price_to_sales) as avg_price_to_sales from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_sales \
                  "+operator[ps_op] +" isr2.avg_price_to_sales order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_sales from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.price_to_sales"+operator[ps_op] +" "+ps_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            ps = pd.read_sql(sql,engine)
            symbollist = ""
            if not ps.empty:
                ps.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(ps.index))
                resultdf = resultdf.merge(ps,how='inner',left_index=True,right_index=True)
        

#Price Earning Ratio

    peg_aggf = criteria['peg_aggf']
    peg_aggp = criteria['peg_aggp']
    peg_aggpnum = criteria['peg_aggpnum']    
    peg_op = criteria['peg_op']
    peg_abs_filter = criteria['peg_abs_filter']
    peg_bm_f = criteria['peg_bm_f']

    if peg_abs_filter.strip() != "-" and peg_bm_f != -999:
        if peg_bm_f == 'Nifty' and peg_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+peg_aggpnum+" "+period[peg_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[peg_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+peg_aggpnum+" "+period[peg_aggp]+"'))"
        elif peg_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earningsgrowth, isr2.median_price_to_earningsgrowth from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(price_to_earningsgrowth) as median_price_to_earningsgrowth from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_earningsgrowth \
                  "+operator[peg_op] +" isr2.median_price_to_earningsgrowth order by isr1.industry"
        elif peg_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earningsgrowth, isr2.avg_price_to_earningsgrowth from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(price_to_earningsgrowth) as avg_price_to_earningsgrowth from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.price_to_earningsgrowth \
                  "+operator[peg_op] +" isr2.avg_price_to_earningsgrowth order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.price_to_earningsgrowth from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.price_to_earningsgrowth"+operator[peg_op] +" "+peg_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            peg = pd.read_sql(sql,engine)
            symbollist = ""
            if not peg.empty:
                peg.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(peg.index))
                resultdf = resultdf.merge(peg,how='inner',left_index=True,right_index=True)
        

#Return on Equity

    roe_aggf = criteria['roe_aggf']
    roe_aggp = criteria['roe_aggp']
    roe_aggpnum = criteria['roe_aggpnum']    
    roe_op = criteria['roe_op']
    roe_abs_filter = criteria['roe_abs_filter']
    roe_bm_f = criteria['roe_bm_f']

    if roe_abs_filter.strip() != "-" and roe_bm_f != -999:
        if roe_bm_f == 'Nifty' and roe_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+roe_aggpnum+" "+period[roe_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[roe_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+roe_aggpnum+" "+period[roe_aggp]+"'))"
        elif roe_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_equity, isr2.median_return_on_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(return_on_equity) as median_return_on_assets from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.return_on_equity \
                  "+operator[roe_op] +" isr2.median_return_on_equity order by isr1.industry"
        elif roe_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_equity, isr2.avg_return_on_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(return_on_equity) as avg_return_on_equity from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.return_on_equity \
                  "+operator[roe_op] +" isr2.avg_return_on_equity order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.return_on_equity"+operator[roe_op] +" "+roe_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            roe = pd.read_sql(sql,engine)
            symbollist = ""
            if not roe.empty:
                roe.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(roe.index))
                resultdf = resultdf.merge(roe,how='inner',left_index=True,right_index=True)
        

#Return on Assets

    roa_aggf = criteria['roa_aggf']
    roa_aggp = criteria['roa_aggp']
    roa_aggpnum = criteria['roa_aggpnum']    
    roa_op = criteria['roa_op']
    roa_abs_filter = criteria['roa_abs_filter']
    roa_bm_f = criteria['roa_bm_f']

    if roa_abs_filter.strip() != "-" and roa_bm_f != -999:
        if roa_bm_f == 'Nifty' and roa_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+roa_aggpnum+" "+period[roa_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[roa_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+roa_aggpnum+" "+period[roa_aggp]+"'))"
        elif roa_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_assets, isr2.median_return_on_assets from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(return_on_assets) as median_return_on_assets from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.return_on_assets \
                  "+operator[roa_op] +" isr2.median_return_on_assets order by isr1.industry"
        elif roa_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_assets, isr2.avg_return_on_assets from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(return_on_assets) as avg_return_on_assets from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.return_on_assets \
                  "+operator[roa_op] +" isr2.avg_return_on_assets order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.return_on_assets from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.return_on_assets"+operator[roa_op] +" "+roa_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            roa = pd.read_sql(sql,engine)
            symbollist = ""
            if not roa.empty:
                roa.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(roa.index))
                resultdf = resultdf.merge(roa,how='inner',left_index=True,right_index=True)
        
#Net Profit Margin

    netprofitmargin_aggf = criteria['netprofitmargin_aggf']
    netprofitmargin_aggp = criteria['netprofitmargin_aggp']
    netprofitmargin_aggpnum = criteria['netprofitmargin_aggpnum']    
    netprofitmargin_op = criteria['netprofitmargin_op']
    netprofitmargin_abs_filter = criteria['netprofitmargin_abs_filter']
    netprofitmargin_bm_f = criteria['netprofitmargin_bm_f']

    if netprofitmargin_abs_filter.strip() != "-" and netprofitmargin_bm_f != -999:
        if netprofitmargin_bm_f == 'Nifty' and netprofitmargin_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+netprofitmargin_aggpnum+" "+period[netprofitmargin_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[netprofitmargin_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+netprofitmargin_aggpnum+" "+period[netprofitmargin_aggp]+"'))"
        elif netprofitmargin_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.net_profit_margin, isr2.median_net_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(net_profit_margin) as median_net_profit_margin from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.net_profit_margin \
                  "+operator[netprofitmargin_op] +" isr2.median_net_profit_margin order by isr1.industry"
        elif netprofitmargin_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.net_profit_margin, isr2.avg_net_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(net_profit_margin) as avg_net_profit_margin from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.net_profit_margin \
                  "+operator[netprofitmargin_op] +" isr2.avg_net_profit_margin order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.net_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.net_profit_margin"+operator[netprofitmargin_op] +" "+netprofitmargin_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            netprofitmargin = pd.read_sql(sql,engine)
            symbollist = ""
            if not netprofitmargin.empty:
                netprofitmargin.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(netprofitmargin.index))
                resultdf = resultdf.merge(netprofitmargin,how='inner',left_index=True,right_index=True)
        
#Operating Profit Margin

    operatingprofitmargin_aggf = criteria['operatingprofitmargin_aggf']
    operatingprofitmargin_aggp = criteria['operatingprofitmargin_aggp']
    operatingprofitmargin_aggpnum = criteria['operatingprofitmargin_aggpnum']    
    operatingprofitmargin_op = criteria['operatingprofitmargin_op']
    operatingprofitmargin_abs_filter = criteria['operatingprofitmargin_abs_filter']
    operatingprofitmargin_bm_f = criteria['operatingprofitmargin_bm_f']

    if operatingprofitmargin_abs_filter.strip() != "-" and operatingprofitmargin_bm_f != -999:
        if operatingprofitmargin_bm_f == 'Nifty' and operatingprofitmargin_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+operatingprofitmargin_aggpnum+" "+period[operatingprofitmargin_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[operatingprofitmargin_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+operatingprofitmargin_aggpnum+" "+period[operatingprofitmargin_aggp]+"'))"
        elif operatingprofitmargin_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.operating_profit_margin, isr2.median_operating_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(operating_profit_margin) as median_operating_profit_margin from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.operating_profit_margin \
                  "+operator[operatingprofitmargin_op] +" isr2.median_operating_profit_margin order by isr1.industry"
        elif operatingprofitmargin_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.operating_profit_margin, isr2.avg_operating_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(operating_profit_margin) as avg_operating_profit_margin from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.operating_profit_margin \
                  "+operator[operatingprofitmargin_op] +" isr2.avg_operating_profit_margin order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.operating_profit_margin from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.operating_profit_margin"+operator[operatingprofitmargin_op] +" "+operatingprofitmargin_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            operatingprofitmargin = pd.read_sql(sql,engine)
            symbollist = ""
            if not operatingprofitmargin.empty:
                operatingprofitmargin.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(operatingprofitmargin.index))
                resultdf = resultdf.merge(operatingprofitmargin,how='inner',left_index=True,right_index=True)
        
#Current Ratio

    currentratio_aggf = criteria['currentratio_aggf']
    currentratio_aggp = criteria['currentratio_aggp']
    currentratio_aggpnum = criteria['currentratio_aggpnum']    
    currentratio_op = criteria['currentratio_op']
    currentratio_abs_filter = criteria['currentratio_abs_filter']
    currentratio_bm_f = criteria['currentratio_bm_f']

    if currentratio_abs_filter.strip() != "-" and currentratio_bm_f != -999:
        if currentratio_bm_f == 'Nifty' and currentratio_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+currentratio_aggpnum+" "+period[currentratio_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[currentratio_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+currentratio_aggpnum+" "+period[currentratio_aggp]+"'))"
        elif currentratio_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.current_ratio, isr2.median_current_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(current_ratio) as median_current_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.current_ratio \
                  "+operator[currentratio_op] +" isr2.median_current_ratio order by isr1.industry"
        elif currentratio_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.current_ratio, isr2.avg_current_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(current_ratio) as avg_current_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.current_ratio \
                  "+operator[currentratio_op] +" isr2.avg_current_ratio order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.current_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.current_ratio"+operator[currentratio_op] +" "+currentratio_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            currentratio = pd.read_sql(sql,engine)
            symbollist = ""
            if not currentratio.empty:
                currentratio.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(currentratio.index))
                resultdf = resultdf.merge(currentratio,how='inner',left_index=True,right_index=True)
        
#Quick Ratio

    quickratio_aggf = criteria['quickratio_aggf']
    quickratio_aggp = criteria['quickratio_aggp']
    quickratio_aggpnum = criteria['quickratio_aggpnum']    
    quickratio_op = criteria['quickratio_op']
    quickratio_abs_filter = criteria['quickratio_abs_filter']
    quickratio_bm_f = criteria['quickratio_bm_f']

    if quickratio_abs_filter.strip() != "-" and quickratio_bm_f != -999:
        if quickratio_bm_f == 'Nifty' and quickratio_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+quickratio_aggpnum+" "+period[quickratio_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[quickratio_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+quickratio_aggpnum+" "+period[quickratio_aggp]+"'))"
        elif quickratio_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.quick_ratio, isr2.median_quick_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(quick_ratio) as median_quick_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.quick_ratio \
                  "+operator[quickratio_op] +" isr2.median_quick_ratio order by isr1.industry"
        elif quickratio_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.quick_ratio, isr2.avg_quick_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(quick_ratio) as avg_quick_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.quick_ratio \
                  "+operator[quickratio_op] +" isr2.avg_quick_ratio order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.quick_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.quick_ratio"+operator[quickratio_op] +" "+quickratio_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            quickratio = pd.read_sql(sql,engine)
            symbollist = ""
            if not quickratio.empty:
                quickratio.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(quickratio.index))
                resultdf = resultdf.merge(quickratio,how='inner',left_index=True,right_index=True)
        
#Debt Equity Ratio

    debtequity_aggf = criteria['debtequity_aggf']
    debtequity_aggp = criteria['debtequity_aggp']
    debtequity_aggpnum = criteria['debtequity_aggpnum']    
    debtequity_op = criteria['debtequity_op']
    debtequity_abs_filter = criteria['debtequity_abs_filter']
    debtequity_bm_f = criteria['debtequity_bm_f']

    if debtequity_abs_filter.strip() != "-" and debtequity_bm_f != -999:
        if debtequity_bm_f == 'Nifty' and debtequity_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+debtequity_aggpnum+" "+period[debtequity_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[debtequity_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+debtequity_aggpnum+" "+period[debtequity_aggp]+"'))"
        elif debtequity_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.debt_to_equity, isr2.median_debt_to_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(debt_to_equity) as median_debt_to_equity from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.debt_to_equity \
                  "+operator[debtequity_op] +" isr2.median_debt_to_equity order by isr1.industry"
        elif debtequity_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.debt_to_equity, isr2.avg_debt_to_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(debt_to_equity) as avg_debt_to_equity from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.debt_to_equity \
                  "+operator[debtequity_op] +" isr2.avg_debt_to_equity order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.debt_to_equity from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.debt_to_equity"+operator[debtequity_op] +" "+debtequity_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            debtequity = pd.read_sql(sql,engine)
            symbollist = ""
            if not debtequity.empty:
                debtequity.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(debtequity.index))
                resultdf = resultdf.merge(debtequity,how='inner',left_index=True,right_index=True)
        
#Asset Turnover

    assetturnover_aggf = criteria['assetturnover_aggf']
    assetturnover_aggp = criteria['assetturnover_aggp']
    assetturnover_aggpnum = criteria['assetturnover_aggpnum']    
    assetturnover_op = criteria['assetturnover_op']
    assetturnover_abs_filter = criteria['assetturnover_abs_filter']
    assetturnover_bm_f = criteria['assetturnover_bm_f']

    if assetturnover_abs_filter.strip() != "-" and assetturnover_bm_f != -999:
        if assetturnover_bm_f == 'Nifty' and assetturnover_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+assetturnover_aggpnum+" "+period[assetturnover_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[assetturnover_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+assetturnover_aggpnum+" "+period[assetturnover_aggp]+"'))"
        elif assetturnover_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.asset_turnover_ratio, isr2.median_asset_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(asset_turnover_ratio) as median_asset_turnover_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.asset_turnover_ratio \
                  "+operator[assetturnover_op] +" isr2.median_asset_turnover_ratio order by isr1.industry"
        elif assetturnover_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.asset_turnover_ratio, isr2.avg_asset_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(asset_turnover_ratio) as avg_asset_turnover_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.asset_turnover_ratio \
                  "+operator[assetturnover_op] +" isr2.avg_asset_turnover_ratio order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.asset_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.asset_turnover_ratio "+operator[assetturnover_op] +" "+assetturnover_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            assetturnover = pd.read_sql(sql,engine)
            symbollist = ""
            if not assetturnover.empty:
                assetturnover.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(assetturnover.index))
                resultdf = resultdf.merge(assetturnover,how='inner',left_index=True,right_index=True)
        
#Return on Assets

    inventoryturnover_aggf = criteria['inventoryturnover_aggf']
    inventoryturnover_aggp = criteria['inventoryturnover_aggp']
    inventoryturnover_aggpnum = criteria['inventoryturnover_aggpnum']    
    inventoryturnover_op = criteria['inventoryturnover_op']
    inventoryturnover_abs_filter = criteria['inventoryturnover_abs_filter']
    inventoryturnover_bm_f = criteria['inventoryturnover_bm_f']

    if inventoryturnover_abs_filter.strip() != "-" and inventoryturnover_bm_f != -999:
        if inventoryturnover_bm_f == 'Nifty' and inventoryturnover_aggp != '-999':
            sql = "select * from (select dr.symbol, sum(dr.daily_log_returns) as returns from daily_returns dr \
                   inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=dr.symbol where \
                   dr.date >= (now() - interval '"+inventoryturnover_aggpnum+" "+period[inventoryturnover_aggp]+"') group by dr.symbol) tab1 where  tab1.returns\
                   "+operator[inventoryturnover_op] +" (select sum(daily_log_returns) from daily_returns where symbol='NIFTY 50' where \
                   date >= (now() - interval '"+inventoryturnover_aggpnum+" "+period[inventoryturnover_aggp]+"'))"
        elif inventoryturnover_bm_f == 'Industry Median':
            sql = "select isr1.symbol, isr1.industry, isr1.inventory_turnover_ratio, isr2.median_inventory_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, median(inventory_turnover_ratio) as median_inventory_turnover_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.inventory_turnover_ratio \
                  "+operator[inventoryturnover_op] +" isr2.median_inventory_turnover_ratio order by isr1.industry"
        elif inventoryturnover_bm_f == 'Industry Average':
            sql = "select isr1.symbol, isr1.industry, isr1.inventory_turnover_ratio, isr2.avg_inventory_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  inner join (select industry, avg(inventory_turnover_ratio) as avg_inventory_turnover_ratio from industry_symbol_ratios() where ratiorank = 1 \
                  group by industry) isr2 on isr1.industry = isr2.industry where isr1.ratiorank = 1 and isr1.inventory_turnover_ratio \
                  "+operator[inventoryturnover_op] +" isr2.avg_inventory_turnover_ratio order by isr1.industry"
        else:
            sql = "select isr1.symbol, isr1.industry, isr1.inventory_turnover_ratio from industry_symbol_ratios() isr1 \
                  inner join (select distinct st.symbol from stock_history st "+symbollist+") stock on stock.symbol=isr1.symbol \
                  where isr1.ratiorank = 1 and isr1.inventory_turnover_ratio"+operator[inventoryturnover_op] +" "+inventoryturnover_abs_filter+" order by isr1.industry"
        
#        print(sql)
        engine = mu.sql_engine()
        if sql != "":
            inventoryturnover = pd.read_sql(sql,engine)
            symbollist = ""
            if not inventoryturnover.empty:
                inventoryturnover.set_index('symbol',inplace=True)
                symbollist = "where st.symbol in "+str(tuple(inventoryturnover.index))
                resultdf = resultdf.merge(inventoryturnover,how='inner',left_index=True,right_index=True)
        
    if len(resultdf.columns) == 0: 
        resultdf = pd.DataFrame()
#    print(resultdf)
    return(resultdf)


    
def covered_call(budget=1000000,live=False):
    minexpiry = today + dateutil.relativedelta.relativedelta(weeks=2)
    
    #Stock Filter Criteria
    #1. Return for past 8 weeks is positive
    #2. Average Daily Volume >= 500000
    #3. Remove Penny stocks
    
    
    sql = "select symbol from (select sh.symbol, avg(sh.volume) as adtv, \
           sum(dr.daily_log_returns) as pr from stock_history sh inner join daily_returns dr \
           on sh.symbol = dr.symbol where sh.series = 'EQ' and sh.date = dr.date and sh.close > 10 and \
           sh.date > (now() - interval '8 weeks') group by sh.symbol) CR1 \
           where adtv >= 500000 and pr > 0 "
           
#    return_sql = "select * from daily_returns dr where dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
    engine = mu.sql_engine()
    symbols = pd.read_sql(sql,engine)
    symbols = list(symbols.symbol)
    OC_COLS = ['Symbol','Underlying','Lot','Strike_Price','CALL_LTP','CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty']#,'MaxDrawdown']
#    symbols = ['ICICIBANK','HDFCBANK','AMBUJACEM']
    calls = []
    errormsg = ""
    for symbol in symbols:
        errormsg = errormsg + " "+symbol+"|"
        try:
            stock = st.Stock(symbol)
            stockquote = stock.quote['lastPrice']
#            drawdown = stock.avg_drawdown()
            if live:
                stock_oc = stock.optionChain()
            else:
                stock_oc = mu.get_stored_option_chain(symbol)
            if not stock_oc.empty:
    #            stock_oc = stock_oc[OC_COLS[3:]]
                errormsg = errormsg + "OC Downloaded | "
                stock_oc = stock_oc.apply(pd.to_numeric,errors='coerce')
                # PCR OI test
                PCR,IVSKEW = 1,1
                if stock_oc['CALL_OI'].sum() != 0:
                    PCR = stock_oc['PUT_OI'].sum()/stock_oc['CALL_OI'].sum()
                # IV SKEW TEST
                if stock_oc['PUT_IV'].sum() != 0:
                    IVSKEW = stock_oc['CALL_IV'].sum()/stock_oc['PUT_IV'].sum()
                
    #            if (PCR > 0.7 and IVSKEW > 0.8): 
                if (PCR > 0 and IVSKEW > 0): 
                    errormsg = errormsg + "PCR and IVSKEW test passed | "
                    strikes = sorted(set(list(stock_oc['Strike_Price'])))
                    strike_pts = abs(strikes[2]-strikes[3])
                    atmstrike = mu.closestmatch(stockquote,
                                                strikes,
                                                strike_pts)
                    strike1,strike2,strike3 = atmstrike,atmstrike,atmstrike
                    strike2,strike3 = strike2 + strike_pts,strike3 + strike_pts
                    stock_oc = stock_oc.dropna()
                    valid_expiries = sorted(set(stock_oc.index))
#                    print(valid_expiries)
                    for d in valid_expiries:
                        if d < minexpiry:
#                            print("removing -> "+str(d))
                            valid_expiries.remove(d)
                    #STRIKES FILTER
#                    print(valid_expiries)
                    if len(valid_expiries) > 0:
                        errormsg = errormsg + " valid expiry of "+ str(valid_expiries) + "|"
#                        print(valid_expiries[0])
                        optionquote = mu.getStockOptionQuote(symbol,valid_expiries[0],atmstrike)
        #                print(optionquote)
                        marketLot = optionquote['marketLot']
                        if (float(marketLot)*stockquote) <= budget:
                            try:
                                stock_oc = stock_oc[(stock_oc['Strike_Price'] == strike1) |
                                                    (stock_oc['Strike_Price'] == strike2) |
                                                    (stock_oc['Strike_Price'] == strike3)]
                                
                                #EXPIRY FILTER
                                
                                stock_oc = stock_oc.loc[valid_expiries]
                                
                                # OPEN INTEREST FILTER
                                
                                stock_oc = stock_oc[stock_oc['CALL_OI'] >= 500]
                                
                                # YIELD FILTER
                                
                                stock_oc = stock_oc[stock_oc['CALL_LTP']/stockquote >= 0.03]
                                stock_oc = stock_oc[OC_COLS[3:]]
                                stock_oc['Symbol'] = symbol
                                stock_oc['Lot'] = marketLot
                                stock_oc['Underlying'] = stockquote
        #                        stock_oc['MaxDrawdown'] = drawdown
                                stock_oc = stock_oc.reindex(columns=OC_COLS)
                                calls.append(stock_oc)
                                errormsg = errormsg + " Final OC Accepted \n"
        #                        print(stock_oc)
                            except:
                                pass
        except:
            pass
    if len(calls) > 0:
        calls = pd.concat(calls)
        if (time.localtime().tm_hour > 17):
            timestamp = "CC_"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
            sql = "insert into strategies (name,type,date,strategy_df) values ('%s','covered_call','%s','%s')"
            oc = calls.reset_index()
            oc = oc.to_string()
            sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
            try:
                engine.execute(sql)
            except:
                pass
    else:
        calls = pd.DataFrame()

#    print(calls)
    return [calls,errormsg]


def bull_put_spread(budget=1000000,live=False):
    minexpiry = today + dateutil.relativedelta.relativedelta(weeks=2)
    
    #Stock Filter Criteria
    #1. Return for past 8 weeks is positive
    #2. Average Daily Volume >= 500000
    #3. Remove Penny stocks
    
    
    sql = "select symbol from (select sh.symbol, avg(sh.volume) as adtv, \
           sum(dr.daily_log_returns) as pr from stock_history sh inner join daily_returns dr \
           on sh.symbol = dr.symbol where sh.series = 'EQ' and sh.date = dr.date and sh.close > 10 and \
           sh.date > (now() - interval '8 weeks') group by sh.symbol) CR1 \
           where adtv >= 500000 and pr > 0 "
           
#    return_sql = "select * from daily_returns dr where dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
    engine = mu.sql_engine()
    symbols = pd.read_sql(sql,engine)
    symbols = list(symbols.symbol)
    OC_COLS = ['Symbol','Underlying','Lot','Higher_Strike','Higher_Strike_LTP','Strike_Price','PUT_LTP','PUT_OI','PUT_BidQty','PUT_BidPrice','PUT_AskPrice','PUT_AskQty']#,'MaxDrawdown']
#    symbols = ['BANKINDIA']#,'HDFCBANK','AMBUJACEM']
    calls = []
    errormsg = ""
    for symbol in symbols:
#        print(symbol)
        errormsg = errormsg + " "+symbol+"|"
        try:
            stock = st.Stock(symbol)
            stockquote = stock.quote['lastPrice']
            errormsg = errormsg + " "+str(stockquote)+"|"
#            drawdown = stock.avg_drawdown()
            if live:
                stock_oc = stock.optionChain()
            else:
                stock_oc = mu.get_stored_option_chain(symbol)
#            print(stock_oc[OC_COLS[3:]])
            if not stock_oc.empty:
                bps_oc = pd.DataFrame()
                stock_oc = stock_oc[OC_COLS[5:]]
                errormsg = errormsg + "OC Downloaded | "
                stock_oc = stock_oc.apply(pd.to_numeric,errors='coerce')
                # PCR OI test
                PCR,IVSKEW = 1,1
#                if stock_oc['CALL_OI'].sum() != 0:
#                    PCR = stock_oc['PUT_OI'].sum()/stock_oc['CALL_OI'].sum()
#                # IV SKEW TEST
#                if stock_oc['PUT_IV'].sum() != 0:
#                    IVSKEW = stock_oc['CALL_IV'].sum()/stock_oc['PUT_IV'].sum()
                
    #            if (PCR > 0.7 and IVSKEW > 0.8): 
                if (PCR > 0 and IVSKEW > 0): 
                    errormsg = errormsg + "PCR and IVSKEW test passed | "
                    strikes = sorted(set(list(stock_oc['Strike_Price'])))
                    strike_pts = abs(strikes[2]-strikes[3])
                    h_strike = stockquote-int(stockquote*0.1/strike_pts)*strike_pts
                    h_strike = mu.closestmatch(h_strike,
                                                strikes,
                                                strike_pts)
#                    print(h_strike)
                    h_strike1,h_strike2,h_strike3 = h_strike,h_strike,h_strike
                    h_strike2,h_strike3 = h_strike2 - strike_pts,h_strike3 - strike_pts
                    stock_oc = stock_oc.dropna()
                    valid_expiries = sorted(set(stock_oc.index))
#                    print(valid_expiries)
                    for d in valid_expiries:
                        if d < minexpiry:
#                            print("removing -> "+str(d))
                            valid_expiries.remove(d)
                    #STRIKES FILTER
                    #print(valid_expiries)
                    if len(valid_expiries) > 0:
                        errormsg = errormsg + " valid expiry of "+ str(valid_expiries) + "|"
#                        print(valid_expiries[0])
                        optionquote = mu.getStockOptionQuote(symbol,valid_expiries[0],h_strike1,'PE')
        #                print(optionquote)
                        marketLot = optionquote['marketLot']
#                        h_ltp = optionquote['lastPrice']
                        h_ltp = stock_oc[stock_oc['Strike_Price'] == h_strike1].loc[valid_expiries[0]]['PUT_LTP']
                        if (float(marketLot)*stockquote) <= budget:
                            try:
#                                print(stock_oc[OC_COLS[3:]])
#                                stock_oc = stock_oc[(stock_oc['Strike_Price'] == h_strike1) |
#                                                    ((h_ltp - stock_oc['PUT_LTP'])/abs(h_strike1 - stock_oc['Strike_Price']) >=0.10)] 
                                stock_oc = stock_oc[((h_ltp - stock_oc['PUT_LTP'])/abs(h_strike1 - stock_oc['Strike_Price']) >=0.10)] 
                                if not stock_oc.empty:
                                    errormsg = errormsg + "10% yield test passed | "

#                                stock_oc = stock_oc[(stock_oc['Strike_Price'] == h_strike1) |
#                                                    (stock_oc['Strike_Price'] == h_strike2) |
#                                                    (stock_oc['Strike_Price'] == h_strike3)]
                                
                                #EXPIRY FILTER
                                
                                stock_oc = stock_oc.loc[valid_expiries]
                                if not stock_oc.empty:
                                    errormsg = errormsg + "yield and expiry test passed | "

                                # OPEN INTEREST FILTER
                                
                                stock_oc = stock_oc[stock_oc['PUT_OI'] >= 500]
                                if not stock_oc.empty:
                                    errormsg = errormsg + "OI of 500 test passed | "

                                bps_oc = stock_oc
                                bps_oc['Higher_Strike'] = h_strike1
                                bps_oc['Higher_Strike_LTP'] = h_ltp
                                # YIELD FILTER
                                
#                                stock_oc = stock_oc[stock_oc['CALL_LTP']/stockquote >= 0.03]
#                                stock_oc = stock_oc[OC_COLS[3:]]
#                                stock_oc['Symbol'] = symbol
#                                stock_oc['Lot'] = marketLot
#                                stock_oc['Underlying'] = stockquote
                                bps_oc['Symbol'] = symbol
                                bps_oc['Lot'] = marketLot
                                bps_oc['Underlying'] = stockquote
                                        
        #                        stock_oc['MaxDrawdown'] = drawdown
                                bps_oc = bps_oc.reindex(columns=OC_COLS)
#                                stock_oc.sort_values(by='Strike_Price',ascending=0)
                                if(len(bps_oc) > 0):
                                    calls.append(bps_oc)
                                    errormsg = errormsg + " Final OC Accepted \n"
        #                        print(stock_oc)
                            except:
                                pass
        except:
            pass
    if len(calls) > 0:
        calls = pd.concat(calls)
        if (time.localtime().tm_hour > 17):
            timestamp = "BPS_"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
            sql = "insert into strategies (name,type,date,strategy_df) values ('%s','bull_put_spread','%s','%s')"
            oc = calls.reset_index()
            oc = oc.to_string()
            sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
            try:
                engine.execute(sql)
            except:
                pass
    else:
        calls = pd.DataFrame()
#    print(calls)
    return [calls,errormsg]

def bear_call_spread(budget=1000000,live=False):
    minexpiry = today + dateutil.relativedelta.relativedelta(weeks=2)
    
    #Stock Filter Criteria
    #1. Return for past 8 weeks is negative
    #2. Average Daily Volume >= 500000
    #3. Remove Penny stocks
    
    
    sql = "select symbol from (select sh.symbol, avg(sh.volume) as adtv, \
           sum(dr.daily_log_returns) as pr from stock_history sh inner join daily_returns dr \
           on sh.symbol = dr.symbol where sh.series = 'EQ' and sh.date = dr.date and sh.close > 10 and \
           sh.date > (now() - interval '8 weeks') group by sh.symbol) CR1 \
           where adtv >= 500000 and pr < 0 "
           
#    return_sql = "select * from daily_returns dr where dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
    engine = mu.sql_engine()
    symbols = pd.read_sql(sql,engine)
    symbols = list(symbols.symbol)
    OC_COLS = ['Symbol','Underlying','Lot','Lower_Strike','Lower_Strike_LTP','Strike_Price','CALL_LTP','CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty']#,'MaxDrawdown']
#    symbols = ['ADANIENT']#,'HDFCBANK','AMBUJACEM']
    calls = []
    errormsg = ""
    for symbol in symbols:
#        print(symbol)
        errormsg = errormsg + " "+symbol+"|"
        try:
            stock = st.Stock(symbol)
            stockquote = stock.quote['lastPrice']
#            drawdown = stock.avg_drawdown()
            if live:
                stock_oc = stock.optionChain()
            else:
                stock_oc = mu.get_stored_option_chain(symbol)
#            print(stock_oc[OC_COLS[3:]])
            if not stock_oc.empty:
                bcs_oc = pd.DataFrame()
                stock_oc = stock_oc[OC_COLS[5:]]
#                print(stock_oc)
                errormsg = errormsg + "OC Downloaded | "
                stock_oc = stock_oc.apply(pd.to_numeric,errors='coerce')
                stock_oc = stock_oc.dropna()
                # PCR OI test
#                print(stock_oc)
                PCR,IVSKEW = 1,1
#                if stock_oc['CALL_OI'].sum() != 0:
#                    PCR = stock_oc['PUT_OI'].sum()/stock_oc['CALL_OI'].sum()
#                # IV SKEW TEST
#                if stock_oc['PUT_IV'].sum() != 0:
#                    IVSKEW = stock_oc['CALL_IV'].sum()/stock_oc['PUT_IV'].sum()
                
    #            if (PCR > 0.7 and IVSKEW > 0.8): 
                if (PCR > 0 and IVSKEW > 0): 
                    errormsg = errormsg + "PCR and IVSKEW test passed | "
                    strikes = sorted(set(list(stock_oc['Strike_Price'])))
                    strike_pts = abs(strikes[2]-strikes[3])
                    l_strike = stockquote+int(stockquote*0.1/strike_pts)*strike_pts
                    l_strike = mu.closestmatch(l_strike,
                                                strikes,
                                                strike_pts)
                    #print(l_strike)
                    l_strike1,h_strike2,h_strike3 = l_strike,l_strike,l_strike
                    h_strike2,h_strike3 = h_strike2 + strike_pts,h_strike3 + strike_pts
                    valid_expiries = sorted(set(stock_oc.index))
                    #print(valid_expiries)
                    for d in valid_expiries:
                        if d < minexpiry:
#                            print("removing -> "+str(d))
                            valid_expiries.remove(d)
                    #STRIKES FILTER
#                    print(valid_expiries)
                    if len(valid_expiries) > 0:
                        errormsg = errormsg + " valid expiry of "+ str(valid_expiries) + "|"
#                        print(valid_expiries[0])
                        optionquote = mu.getStockOptionQuote(symbol,valid_expiries[0],l_strike1)
        #                print(optionquote)
                        marketLot = optionquote['marketLot']
#                        l_ltp = optionquote['lastPrice']
                        l_ltp = stock_oc[stock_oc['Strike_Price'] == l_strike1].loc[valid_expiries[0]]['CALL_LTP']
                        if (float(marketLot)*stockquote) <= budget:
                            try:
                                #print(stock_oc)
                                stock_oc = stock_oc[((l_ltp -stock_oc['CALL_LTP'])/abs(l_strike1 - stock_oc['Strike_Price']) >=0.10)] 

#                                stock_oc = stock_oc[(stock_oc['Strike_Price'] == h_strike1) |
#                                                    (stock_oc['Strike_Price'] == h_strike2) |
#                                                    (stock_oc['Strike_Price'] == h_strike3)]
                                
                                #EXPIRY FILTER
#                                print(stock_oc)
                                stock_oc = stock_oc.loc[valid_expiries]
                                
                                # OPEN INTEREST FILTER
                                
                                stock_oc = stock_oc[stock_oc['CALL_OI'] >= 500]
                                
                                # YIELD FILTER
                                
                                bcs_oc = stock_oc
                                bcs_oc['Lower_Strike'] = l_strike1
                                bcs_oc['Lower_Strike_LTP'] = l_ltp

#                                stock_oc = stock_oc[stock_oc['CALL_LTP']/stockquote >= 0.03]
#                                stock_oc = stock_oc[OC_COLS[3:]]
                                bcs_oc['Symbol'] = symbol
                                bcs_oc['Lot'] = marketLot
                                bcs_oc['Underlying'] = stockquote
                                        
        #                        stock_oc['MaxDrawdown'] = drawdown
                                bcs_oc = bcs_oc.reindex(columns=OC_COLS)
#                                stock_oc.sort_values(by='Strike_Price',ascending=0)
                                if(len(bcs_oc) > 0):
                                    calls.append(bcs_oc)
                                    errormsg = errormsg + " Final OC Accepted \n"
        #                        print(stock_oc)
                            except:
                                pass
        except:
            pass
    if len(calls) > 0:
        calls = pd.concat(calls)
        if (time.localtime().tm_hour > 17):
            timestamp = "BCS_"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
            sql = "insert into strategies (name,type,date,strategy_df) values ('%s','bull_put_spread','%s','%s')"
            oc = calls.reset_index()
            oc = oc.to_string()
            sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
            try:
                engine.execute(sql)
            except:
                pass
    else:
        calls = pd.DataFrame()

#    print(calls)
    return [calls,errormsg]



def intraday_performers():
    stocks = [key for key in nsepy.constants.symbol_list]
    df = []
    with Executor(max_workers=8) as exe:
        jobs = [exe.submit(mu.getStockQuote, stock) for stock in stocks]
        results = [job.result() for job in jobs]
        
    for result in results:
        if result != None:
            try:
                if result['open'] > 0:
                    df.append([result['symbol'],result['open'],result['lastPrice'],result['dayHigh'],result['dayLow'],result['lastPrice']/result['open']-1])
            except:
                pass
    df = pd.DataFrame(df,columns=['symbol','open','lastPrice','dayHigh','dayLow','change'])        
    df = df.set_index('symbol')
    df = df.sort_values(by='change',ascending=0)
    return df
if __name__ == '__main__':
#    big_money_zack()
#    top_mf_smallcap_holdings(3)
#    top_mf_largecap_holdings()
#    top_mf_midcap_holdings()
#    top_mf_multicap_holdings()
#    top_mf_value_holdings()    
#    small_cap_growth()
#     roe_growth()
#    ta_fa()
#     newhighs()
#      momentum()
#      growth_income()
#      top_mf_holdings()
#    covered_call()
#   bull_put_spread()
   bear_call_spread()