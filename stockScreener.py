# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

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

today = datetime.date.today()
engine = mu.sql_engine()

def big_money_zack():
    """
    BIG MONEY ZACK screener
    
    Min 20-day trading volume > 50,000
    Log return of 24 weeks : top 20
    Log return of 12 weeks : top 10
    Log return of 4 weeks : top 3
    """
    startdate = today - dateutil.relativedelta.relativedelta(weeks=27)
    
    volumedate = today - datetime.timedelta(days=20)
    sql = "select symbol from (select symbol, min(volume) as minvol from stock_history where series='EQ' and date > '"+volumedate.strftime('%Y-%m-%d') +"' group by symbol) as foo where minvol > 50000"
    sql = "select  date, symbol, price, daily_log_returns from daily_returns where date > '"+startdate.strftime('%Y-%m-%d') + "' and symbol in ("+sql+")"
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
           to_number(mfs.rating,'9')=5 and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
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
           to_number(mfs.rating,'9') in (4,5) and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
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
           to_number(mfs.rating,'9') in (4,5) and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    print(holdings)

def top_mf_largecap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund), (select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-LC' and \
           to_number(mfs.rating,'9') in (4,5) and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    print(holdings)

def top_mf_multicap_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-MLC' and \
           to_number(mfs.rating,'9') in (4,5) and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    print(holdings)

def top_mf_value_holdings(holding_percent=5):
    """
    Gets the top holding stocks for 4-5 rated mutual funds.
    """
    
    sql = "select  mfp.company, count(mfp.fund),(select symbol from security_master where value_research_name = mfp.company ) as symbol\
           from mf_portfolios as mfp inner join mf_snapshot as mfs \
           on  mfp.fund = mfs.fund \
           where \
           mfs.category='EQ-VAL' and \
           to_number(mfs.rating,'9') in (4,5) and \
           to_number(mfp.holding_current,'99.99')>=" + str(holding_percent)+ "and \
           mfs.download_date = (select download_date from mf_snapshot order by download_date desc limit 1) \
           group by mfp.company \
           order by count desc"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
        
    print(holdings)

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
    
    startdate = today - dateutil.relativedelta.relativedelta(months=3)    
    sql = " select foo.*, indmedsagg.* from (select * , rank() over ( partition by symbol order by ratio_date desc) from industry_symbol_ratios() where symbol in \
          (select sm.symbol from security_master sm where to_number(sm.outstanding_shares,'9999999999999999.99')* \
          (select sh.close from stock_history sh where sh.symbol=sm.symbol order by sh.date  desc limit 1) \
          <= 50000000000 and \
          sm.symbol in (select distinct symbol from stock_history where close > 1) and \
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
    print(PSLow[['industry','close','basic_eps','eps_growth','pe','ps','pemedian','psmedian','eps_growth_median']])
    return(PSLow)

def roe_growth():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    
#    startdate = today - dateutil.relativedelta.relativedelta(months=3)    
    sql = " select * , rank() over ( partition by symbol order by ratio_date desc) from industry_symbol_ratios()"
          
    engine = mu.sql_engine()
    roe = pd.read_sql(sql,engine)
    if not roe.empty:
        roe.set_index('symbol',inplace=True)
#    roe['pe'] = roe['close']/roe['basic_eps']
    roe['ps'] = roe['close']/roe['sales_per_share']
    roe = roe.loc[roe['rank'] == 1]
    
    ROEGrowth = roe.loc[roe['return_on_equity'].astype(float) >= 10]
    PSLow = ROEGrowth.loc[ROEGrowth['ps'] <= 1]
    PRICE5 = PSLow.loc[PSLow['close'] >= 5]
    print(PRICE5[['industry','close','basic_eps','eps_growth','ps','return_on_equity']])
    return(PRICE5)

def ta_fa():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
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
    print(set(ta_fa.index))    

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
    print(set(PSLow.index))
    PSLow['ret24W'] = "NA"
    PSLow['ret12W'] = "NA"
    PSLow['ret4W'] = "NA"
    for sym in set(PSLow.index):
        print(sym)
        PSLow.loc[sym,'ret24W'] = PSLow.loc[PSLow['date'] >= start24].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret12W'] = PSLow.loc[PSLow['date'] >= start12].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret4W'] = PSLow.loc[PSLow['date'] >= start4].loc[sym]['daily_log_returns'].sum()
    #PSLow = PSLow[['industry','eps_growth','ps','ret24W','ret12W','ret4W','eps_growth_median','psmedian']].drop_duplicates()
    print(PSLow)
    return(PSLow)

def newhighs():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
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
    print(set(newhighs.index))    
    EPSGrowth = newhighs.loc[newhighs['eps_growth'] >= newhighs['eps_growth_median']]
    PELow = EPSGrowth.loc[EPSGrowth['pe'] <= EPSGrowth['pemedian']]
    PSLow = PELow.loc[PELow['ps'] <= PELow['psmedian']]
    start24 = today -dateutil.relativedelta.relativedelta(weeks=24)
    start12 = today -dateutil.relativedelta.relativedelta(weeks=12)
    start4 = today -dateutil.relativedelta.relativedelta(weeks=4)
    #print(set(PSLow.index))
    for sym in set(PSLow.index):
        PSLow.loc[sym,'ret12W'] = PSLow.loc[PSLow['date'] >= start12].loc[sym]['daily_log_returns'].sum()
        PSLow.loc[sym,'ret4W'] = PSLow.loc[PSLow['date'] >= start4].loc[sym]['daily_log_returns'].sum()
    PSLow = PSLow.loc[PSLow['ret12W'] > 0]
    PSLow = PSLow.loc[PSLow['ret4W'] > 0]
    PSLow['ret'] = PSLow['ret12W'] + PSLow['ret4W']
    PSLow.sort_values(by='ret',ascending=0)
    PSLow = PSLow[['industry','eps_growth','ps','pe','ret12W','ret4W','eps_growth_median','psmedian','pemedian']].drop_duplicates()
    print(PSLow)
    return(PSLow)

def growth_income():
    
    # Market Cap of company
    #Large Cap is >= 20000 crore
    # Mdcap >= 5000 crore < 20000 crore    
    # smallcap < 5000 crore
    startdate = today - dateutil.relativedelta.relativedelta(weeks=13)
    
    sql = "select ra.*,mds.* from (select * , rank() over \
          ( partition by symbol order by ratio_date desc) from industry_symbol_ratios()) ra  \
          , (select median(pe) as niftype,median(pb) as niftypb , median(100*pb/pe) as niftyroe , median(div_yield) as niftydivyld from stock_history \
          where symbol='NIFTY 50' and series='IN' \
          and date > (now() - interval '12 weeks')) mds \
          where rank = 1 and dividend_per_share is not null and dividend_per_share <> '' and debt_to_equity <> ''"
    
    return_sql = "select * from daily_returns dr where dr.date > (now() - interval '1 year')" #in ( select date from daily_returns where symbol = 'NIFTY 50' and price is not null and date > (now() - interval '1 year'))"      
    engine = mu.sql_engine()
    growth_income = pd.read_sql(sql,engine)
    returns = pd.read_sql(return_sql,engine)
    if not growth_income.empty:
        growth_income.set_index('symbol',inplace=True)
    if not returns.empty:
        returns.set_index('symbol',inplace=True)
    growth_income['pe'] = growth_income['close']/growth_income['basic_eps']
    growth_income['divyld'] = 100*growth_income['dividend_per_share'].astype(float)/growth_income['close']
    growth_income = growth_income.loc[growth_income['rank'] == 1]
    PELow = growth_income.loc[growth_income['pe'] <= growth_income['niftype']]
#    print(PELow[['pe','return_on_equity','debt_to_equity','divyld']])
    ROEHigh = PELow.loc[PELow['return_on_equity'].astype(float) >= PELow['niftyroe']]
#    print(ROEHigh[['pe','return_on_equity','debt_to_equity','divyld']])
    DELow = ROEHigh.loc[ROEHigh['debt_to_equity'].astype(float) <= 1]
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
    print(DIVHigh.head(7))
    return(DIVHigh.head(7))

    
    
    
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
      growth_income()
#      top_mf_holdings()