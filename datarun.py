# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:16:12 2018

@author: Santosh Bag

This module downloads data by using various modules
"""
import sys
import datetime,time,sched
import moneycontrol as mc
import mutual_funds as mf
import strategies.stocks as st
import media.news as news
import mrigutilities as mu
import navAllFetcher as nav
import goldprice as gp
import crudeoilprices as cp
import yieldcurve as yc
import exchangeratesHistory as fx
import stockHistory as sh
import nseIndexHistory as inx
import totalreturnindicesHistory as tri
import optionChainHistory as och
import stockScreener as ss

today = datetime.date.today()

arguments = sys.argv[1:]

alldata = False

startdate= datetime.date.today() - datetime.timedelta(days=1)
enddate= datetime.date.today()

try:
    startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
    enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    alldata = arguments[2]
except:
    pass

def mf_codes():   
    if today.strftime('%A') == 'Thursday':
        mf.get_VR_MF_CODES()
        eqlist = mf.get_equity_fundlist()
        print("Getting Mutual Fund Snapshots\n")
        mf.get_fund_snapshots()
        print("Getting Mutual Fund Portfolios\n")
        mf.get_fund_portfolios(eqlist)

def corp_action_download():
    if today.strftime('%A') == 'Monday':
        mc.get_MCStockCodes()
        print("Getting Corporate Actions\n")
        mc.get_CorporateActions()
        st.stock_adjust()

def ratios_download():    
    if today.strftime('%A') == 'Tuesday' and 15 <= today.day <= 21:
        mc.get_MCStockCodes()
        print("Getting Ratios\n")
        mc.get_MCRatios()
        mc.populate_ratios_table()

def returns():
    calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = mu.sql_engine()
    print("Populating Returns")
    engine.execute(calculate_returns_sql)

def stock_strategies():
    bigm = ss.big_money_zack()
    scg = ss.small_cap_growth()
    gi = ss.growth_income()
    nh = ss.newhighs()
    tafa = ss.ta_fa()
    
    engine = mu.sql_engine()
    timestamp = "BIGM"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','bigm','%s','%s')"
#    if not bigm.empty:
    oc = bigm.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "SCG"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','scg','%s','%s')"
#    if not scg.empty:
    oc = scg.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "GI"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','gi','%s','%s')"
#    if not gi.empty:
    oc = gi.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "NH"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','nh','%s','%s')"
#    if not nh.empty:
    oc = nh.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "TAFA"+str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+str(time.localtime().tm_hour)+str(time.localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','tafa','%s','%s')"
#    if not tafa.empty:
    oc = tafa.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

scheduler = sched.scheduler(timefunc=time.time)
morningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=8,minute=0)
eveningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=18,minute=0)
#eveningtime = morningtime

if (alldata==1) or (time.localtime().tm_hour >= morningtime.hour and
    time.localtime().tm_hour <= eveningtime.hour - 2):
    try:
        nav.navall_download()
    except:
        pass
    try:
        news.get_MCNews()
    except:
        pass
    try:    
        yc.yield_download()
    except:
        pass
    try:    
        gp.gold_download()
    except:
        pass
    try:    
        cp.crude_download()
    except:
        pass
    try:    
        fx.exchange_rates_download(startdate,enddate)
    except:
        pass
#    try:    
#        stock_strategies()
#    except:
#        pass

    

if (alldata==1) or (time.localtime().tm_hour >= eveningtime.hour):
    try:    
        sh.stockHistory_download(startdate,enddate)
    except:
        pass
    try:
        inx.nseIndexHistory_download(startdate,enddate)
    except:
        pass
    try:    
        tri.tri_download(startdate,enddate)
    except:
        pass
    try:    
        ratios_download()
    except:
        pass
    try:    
        mf_codes()
    except:
        pass
    try:    
        corp_action_download()
    except:
        pass
    try:    
        returns()
    except:
        pass
    try:    
        och.oc_download_all()
    except:
        pass
    try:    
        stock_strategies()
    except:
        pass


#try:
#    try:
#        scheduler.enterabs(morningtime.timestamp(),priority=0,action=nav.navall_download())
#    except:
#        pass
#    try:
#        scheduler.enterabs(morningtime.timestamp(),priority=1,action=news.get_MCNews())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(morningtime.timestamp(),priority=2,action=yc.yield_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(morningtime.timesta8p(),priority=3,action=gp.gold_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(morningtime.timestamp(),priority=4,action=cp.crude_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(morningtime.timestamp(),priority=5,action=fx.exchange_rates_download(startdate,enddate))
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=0,action=sh.stockHistory_download(startdate,enddate))
#    except:
#        pass
#    try:
#        scheduler.enterabs(eveningtime.timestamp(),priority=1,action=inx.nseIndexHistory_download(startdate,enddate))
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=2,action=tri.tri_download(startdate,enddate))
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=3,action=ratios_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=4,action=mf_codes())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=5,action=corp_action_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=6,action=och.oc_download())
#    except:
#        pass
#    try:    
#        scheduler.enterabs(eveningtime.timestamp(),priority=7,action=returns())
#    except:
#        pass
#try:
#    scheduler.run(blocking=True)
#except KeyboardInterrupt:
#    print('Stopped.')
#    
#
#news.get_MCNews()

#weekly download of fundsnapshots and fund portfolio holdings
 
