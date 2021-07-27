# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:16:12 2018

@author: Santosh Bag

This module downloads data by using various modules
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from time import localtime
from datetime import date, datetime, timedelta


from mrigutilities import sql_engine
import navAllFetcher as nav
import goldprice as gp
import crudeoilprices as cp
import yieldcurve as yc
import exchangeratesHistory as fx
import stockHistoryNew as shnew
#import nseIndexHistory as inx
import totalreturnindicesHistory as tri
import optionChainHistory as och
import stockScreener as ss
import optionHistory as oh
#import webserver_load as wl
#import Bhavcopy as bc

today = date.today()

arguments = sys.argv[1:]

alldata = ['1']
progressbar = True

startdate= date.today() - timedelta(days=1)
enddate= date.today()

try:
    startdate= date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
    enddate= date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    alldata = arguments[2].split(sep=',')
    progressbar = bool(int(arguments[3]))
except:
    pass
print(startdate)
print(enddate)
print(alldata)
datadir = os.path.dirname(__file__)

def mf_codes():   
    if today.strftime('%A') == 'Thursday':
        import mutual_funds as mf
        mf.get_VR_MF_CODES()
        eqlist = mf.get_equity_fundlist()
        print("Getting Mutual Fund Snapshots\n")
        mf.get_fund_snapshots()
        print("Getting Mutual Fund Portfolios\n")
        mf.get_fund_portfolios(eqlist)

def corp_action_download():
    if today.strftime('%A') == 'Monday':
        import moneycontrol as mc
        import strategies.stocks as st
        mc.get_MCStockCodes()
        print("Getting Corporate Actions\n")
        mc.get_CorporateActions()
        st.stock_adjust()

def ratios_download():    
    if today.strftime('%A') == 'Tuesday' and 15 <= today.day <= 21:
        import moneycontrol as mc
        mc.get_MCStockCodes()
        print("Getting Ratios\n")
        mc.get_MCRatios()
        mc.populate_ratios_table()

def returns():
#    calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = sql_engine()
    print("Populating Returns")
#    engine.execute(calculate_returns_sql)
    engine.execute(open(os.path.join(datadir,'..','sql_queries','returns_ver2.sql'),"r").read())

def return_correlations():
#    calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = sql_engine()
    print("Populating Returns")
#    engine.execute(calculate_returns_sql)
    engine.execute(open(os.path.join(datadir,'..','sql_queries','return_correlations.sql'),"r").read())

def stock_strategies():

    print("Populating Stock Strategies Started----\n")
    bigm = ss.big_money_zack()
    scg = ss.small_cap_growth()
    gi = ss.growth_income()
    nh = ss.newhighs()
    tafa = ss.ta_fa()
    
    engine = sql_engine()
    timestamp = "BIGM"+str(localtime().tm_year)+str(localtime().tm_mon)+str(localtime().tm_mday)+str(localtime().tm_hour)+str(localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','bigm','%s','%s')"
#    if not bigm.empty:
    oc = bigm.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "SCG"+str(localtime().tm_year)+str(localtime().tm_mon)+str(localtime().tm_mday)+str(localtime().tm_hour)+str(localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','scg','%s','%s')"
#    if not scg.empty:
    oc = scg.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "GI"+str(localtime().tm_year)+str(localtime().tm_mon)+str(localtime().tm_mday)+str(localtime().tm_hour)+str(localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','gi','%s','%s')"
#    if not gi.empty:
    oc = gi.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "NH"+str(localtime().tm_year)+str(localtime().tm_mon)+str(localtime().tm_mday)+str(localtime().tm_hour)+str(localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','nh','%s','%s')"
#    if not nh.empty:
    oc = nh.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)

    timestamp = "TAFA"+str(localtime().tm_year)+str(localtime().tm_mon)+str(localtime().tm_mday)+str(localtime().tm_hour)+str(localtime().tm_min)
    sql = "insert into strategies (name,type,date,strategy_df) values ('%s','tafa','%s','%s')"
#    if not tafa.empty:
    oc = tafa.reset_index()
    oc = oc.to_string()
    sql = (sql %(timestamp,today.strftime('%Y-%m-%d'),oc))
    engine.execute(sql)
    print("Populating Stock Strategies Finished----\n")    


morninghour = 6
eveninghour = 20
morningtime = datetime(year=today.year,month=today.month,day=today.day,hour=morninghour,minute=0)
eveningtime = datetime(year=today.year,month=today.month,day=today.day,hour=eveninghour,minute=0)
#eveningtime = morningtime

#if ('1' in alldata) or (localtime().tm_hour >= morningtime.hour and
#    localtime().tm_hour <= eveningtime.hour - 2):
if (len(alldata) > 0):
    if ('1' in alldata):
        try:
            print("NAVS")
            nav.navall_download()
        except:
            pass
        try:
            print("BHAVCOPY")
            shnew.stockHistoryNew_download()
#            bc.bhavcopy_download()
        except:
            pass
        try:
            print("NEWS")
            import media.news as news
            news.get_MCNews()
        except:
            pass
        try:
            print("RATES")
            yc.yield_download()
        except:
            pass
        try:
            print("GOLD")
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
            tri.tri_download(startdate,enddate,progressbar)
        except:
            pass
        try:    
           oh.optionHistory_download()
        except:
            pass    
#        try:    
#            och.oc_download_all(progressbar)
#        except:
#            pass
        try:    
            stock_strategies()
        except:
            pass
        try:    
            oh.optionLot_download()
        except:
            pass
        try:    
            returns()
        except:
            pass
#        try:    
#            return_correlations()
#        except:
#            pass
    if '2' in alldata:
        try:
            print("NAVS")
            nav.navall_download()
        except:
            pass
    if '3' in alldata:
        try:
            print("BHAVCOPY")
            shnew.stockHistoryNew_download()
#            bc.bhavcopy_download()
        except:
            pass
    if '4' in alldata:
        try:
            print("NEWS")
            import media.news as news
            news.get_MCNews()
        except:
            pass
    if '5' in alldata:
        try:
            print("RATES")
            yc.yield_download()
        except:
            pass
    if '6' in alldata:
        try:
            print("GOLD")
            gp.gold_download()
        except:
            pass
    if '7' in alldata:
        try:    
            cp.crude_download()
        except:
            pass
    if '8' in alldata:
        try:    
            fx.exchange_rates_download(startdate,enddate)
        except:
            pass
    if '9' in alldata:
        try:    
            ratios_download()
        except:
            pass
    if '10' in alldata:
        try:    
            mf_codes()
        except:
            pass
    if '11' in alldata:
        try:    
            corp_action_download()
        except:
            pass
    if '12' in alldata:
        try:    
            tri.tri_download(startdate,enddate,progressbar)
        except:
            pass
    if '13' in alldata:
        try:    
           oh.optionHistory_download()
        except:
            pass    
    if '14' in alldata:
        try:    
            och.oc_download_all(progressbar)
        except:
            pass
    if '15' in alldata:
        try:    
            stock_strategies()
        except:
            pass
    if '16' in alldata:
        try:    
            oh.optionLot_download()
        except:
            pass
    if '17' in alldata:
        try:    
            returns()
        except:
            pass
    if '18' in alldata:
        try:    
            return_correlations()
        except:
            pass
    
 #    try:    
#        stock_strategies()
#    except:
#        pass

#    wl.stock_page_load()
#    wl.ss_page_load()
#    wl.os_page_load()
    

#if (alldata==1) or (localtime().tm_hour >= eveningtime.hour):
#    try:    
#        sh.stockHistory_download(startdate,enddate,progressbar)
#    except:
#        pass
#    try:
#        inx.nseIndexHistory_download(startdate,enddate,progressbar)
#    except:
#        pass
#    try:    
#        tri.tri_download(startdate,enddate,progressbar)
#    except:
#        pass
#    try:    
#       oh.optionHistory_download()
#    except:
#        pass    
#    try:    
#        returns()
#    except:
#        pass
#    try:    
#        och.oc_download_all(progressbar)
#    except:
#        pass
##    try:    
##        stock_strategies()
##    except:
##        pass
#    try:    
#        oh.optionLot_download()
#    except:
#        pass
##    wl.stock_page_load()
##    wl.ss_page_load()
##    wl.os_page_load()
#    
#
##try:
##    try:
##        scheduler.enterabs(morningtime.timestamp(),priority=0,action=nav.navall_download())
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
 
