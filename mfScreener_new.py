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
amc = 'Axis'

def mf_dashboard():
    sql = ''' select 
    '''


def top_aum_mfs():
    sql = ''' select * from mf_scheme_master 
    order by amc,scheme_name , aum::DECIMAL desc
    '''
    # print(sql.format(amc))
    data = pd.read_sql(sql.format(amc), engine)
    data['scheme'] = data['scheme_name'].apply(lambda x: x.split('-')[0])
    data['aum'] = data[['aum']].apply(pd.to_numeric, errors='coerce').fillna(-1)
    # for asset_type in ['Debt Scheme','Equity Scheme','Hybrid Scheme','Other Scheme']:
    #     print(data[(data['scheme_asset_type_1'] == asset_type)][data['aum'] > 1000000]
    #           .sort_values(by='aum',ascending=False).head(10)[['scheme_asset_type_1','scheme_name','aum']])
    aum_data = data[data['scheme_asset_type_1'].isin(['Debt Scheme', 'Equity Scheme', 'Hybrid Scheme', 'Other Scheme'])]
    aum_data = aum_data[aum_data['aum'] > 1000000].pivot_table(index=['scheme_asset_type_1', 'scheme'],
                                                               values=['aum'], aggfunc='mean')
    # aum_data.style.format('{:.0f}')
    aum_data['aum'] = aum_data['aum'] / 100
    aum_data = aum_data.sort_values(by=['scheme_asset_type_1', 'aum'], ascending=[True, False]).reset_index()
    # print(aum_data.sort_values(by=['scheme_asset_type_1', 'aum'], ascending=[True, False]))
    return aum_data

def top_performing_mfs():
    sql = '''select mr.scheme_name,mr.daily_log_return,mr.nav_date, msm.scheme_asset_type_1, msm.scheme_asset_type_2,msm.aum 
    from mf_returns mr inner join mf_scheme_master msm 
    on mr.isin = msm.isin 
    where msm.isin is not NULL and position('{}' in msm.amc) > 0 
    '''

    # print(sql.format(amc))
    data = pd.read_sql(sql.format(amc), engine)
    data['aum'] = data[['aum']].apply(pd.to_numeric, errors='coerce').fillna(-1)
    data['scheme'] = data['scheme_name'].apply(lambda x: x.split('-')[0])
    # data = data.pivot_table(index=['scheme_asset_type_1','scheme_asset_type_2','scheme','nav_date'],
    #                         values=['daily_log_return'], aggfunc='mean').stack()
    data = data[data['scheme_asset_type_1'].isin(['Equity Scheme', 'Debt Scheme', 'Hybrid Scheme', 'Other Scheme'])]
    data = data[data['aum'] > 100000]

    data = data.groupby(['scheme_asset_type_1', 'scheme_asset_type_2', 'scheme', 'nav_date']).mean().reset_index()

    # print(data.columns)
    today = datetime.date.today()
    week_dt = today - datetime.timedelta(days=7)
    month_dt = today - datetime.timedelta(days=30)
    month_6_dt = today - datetime.timedelta(days=30 * 6)
    year_dt = today - datetime.timedelta(days=365)
    year_3_dt = today - datetime.timedelta(days=365 * 3)
    year_5_dt = today - datetime.timedelta(days=365 * 5)

    monthly = data[data['nav_date'] > month_dt].pivot_table(index=['scheme_asset_type_1', 'scheme_asset_type_2', 'scheme'],
                                                            values=['daily_log_return'], aggfunc='sum')
    # monthly = monthly.pivot_table(index=['scheme'],values=['daily_log_return'], aggfunc='mean')
    # monthly.style.format({'daily_log_return': '{:.2%}'})

    monthly = monthly.sort_values(by=['scheme_asset_type_1', 'scheme_asset_type_2', 'daily_log_return', 'scheme'], axis=0,
                        ascending=[True, True, False, True]).reset_index()
    # print(monthly)
    return monthly
    

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

def top_mfs(min_rating=3,min_ranking=3):
    """
    Gets the top holding stocks for 5 rated mutual funds.
    """

    sql = "select mfs.*,mfc.mf_category_name, \
           case when (\"position\"(mfs.fund,'-') > 0) then \
           (select mnh.\"Net Asset Value\" from mf_nav_history mnh where \
           mnh.\"Scheme Name\" like ( '%%' || substr(mfs.fund,0, \"position\"(mfs.fund,'-')-1) || '%%') limit 1) \
           else \
           (select mnh.\"Net Asset Value\" from mf_nav_history mnh where \
           mnh.\"Scheme Name\" like ( '%%' || mfs.fund || '%%') limit 1) \
           end \
           from mf_snapshot mfs \
           inner join mf_categories mfc on \
           mfs.category = mfc.mf_category_code \
           where \
           convert_to_int(mfs.rating) > "+str(min_rating)+" and \
           convert_to_int(substr(mfs.\"1_yr_rank\",0, \"position\"(mfs.\"1_yr_rank\",'/'))) < "+str(min_ranking)+" and \
           mfs.snapshot_date = (select mfs1.snapshot_date from mf_snapshot mfs1 where mfs1.fund = mfs.fund order by mfs1.snapshot_date desc limit 1) \
           order by mfs.category, convert_to_int(substr(mfs.\"1_yr_rank\",0, \"position\"(mfs.\"1_yr_rank\",'/'))) asc ,mfs.fund"
           
    #print(sql)
    engine = mu.sql_engine()

    holdings = pd.read_sql(sql,engine)
    #for hld in holdings:
    
    print(holdings)
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
   print(top_performing_mfs())