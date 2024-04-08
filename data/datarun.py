# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:16:12 2018

@author: Santosh Bag

This module downloads data by using various modules
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime,time,sched
# import moneycontrol as mc
import mutual_funds as mf
import strategies.stocks as st
import media.news as news
import mrigutilities as mu
import navAllFetcher as nav
import goldprice as gp
import crudeoilprices as cp
import yieldcurve as yc
import exchangeratesHistory as fx
import stockHistoryNew as sh
import nseIndexHistory as inx
import totalreturnindicesHistory as tri
import optionChainHistory as och
import stockScreener as ss
import optionHistory as oh
import webserver_load as wl
import requests
from io import StringIO
import pandas as pd



today = datetime.date.today()

arguments = sys.argv[1:]

alldata = 0
progressbar = True

startdate= datetime.date.today() - datetime.timedelta(days=1)
enddate= datetime.date.today()

try:
    startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
    enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    alldata = int(arguments[2])
    progressbar = bool(int(arguments[3]))
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

# def corp_action_download():
#     if today.strftime('%A') == 'Monday':
#         mc.get_MCStockCodes()
#         print("Getting Corporate Actions\n")
#         mc.get_CorporateActions()
#         st.stock_adjust()
#
# def ratios_download():
#     if today.strftime('%A') == 'Tuesday' and 15 <= today.day <= 21:
#         mc.get_MCStockCodes()
#         print("Getting Ratios\n")
#         mc.get_MCRatios()
#         mc.populate_ratios_table()

def returns():
    # calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = mu.sql_engine()
    date = engine.execute('select max(date) from daily_returns').fetchall()[0][0]
    print(str(date).replace('-',''))
    print("Populating Returns")
    sql = '''insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)
            (
            (SELECT stock_history.symbol as symbol,
                stock_history.date as date,
                stock_history.close_adj as price,
                stock_history.close_adj / lag(stock_history.close_adj, 1) OVER (PARTITION BY stock_history.symbol ORDER BY stock_history.date) - 1::numeric AS daily_arithmetic_returns,
                ln(stock_history.close_adj / lag(stock_history.close_adj, 1) OVER (PARTITION BY stock_history.symbol ORDER BY stock_history.date)) AS daily_log_returns
               FROM stock_history
              WHERE stock_history.series in ('EQ','IN') and close_adj <> 0 and stock_history.date >= %s
              ORDER BY stock_history.symbol, stock_history.date
            )
            ) 
            on conflict (symbol,date) do nothing;
            '''
    engine.execute(sql,(str(date).replace('-','')))

def stock_strategies():

    print("Populating Stock Strategies Started----\n")
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
    print("Populating Stock Strategies Finished----\n")    


def update_index_constituents():
    urls = {'NIFTY 100': 'https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv',
            'NIFTY 50': 'https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv'
            }
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}

    result = {}
    # print(headers)
    for key in urls.keys():
        req = requests.get(urls[key], headers=headers)
        # print(req)
        data = StringIO(req.text)
        df = pd.read_csv(data)
        result[key] = str(df['Symbol'].tolist())

    engine = mu.sql_engine()
    date = engine.execute("select max(date) from stock_history where symbol='NIFTY 50'").fetchall()[0][0]
    disable_sql = "alter table stock_history disable trigger return_trigger"
    # enable_sql = "alter table stock_history enable trigger return_trigger"
    engine.execute(disable_sql)
    print(str(date).replace('-', ''))
    print("Populating Index Constituent")
    for key in result.keys():
        sql = ''' update stock_history 
        set index_members=%s 
        where symbol=%s and date=%s
        '''
        engine.execute(sql,(result[key],key,(str(date).replace('-',''))))



scheduler = sched.scheduler(timefunc=time.time)
morninghour = 6
eveninghour = 16
morningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=morninghour,minute=0)
eveningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=eveninghour,minute=0)
#eveningtime = morningtime

def daily_datarun():
    try:
        sh.stockHistoryNew_download()
    except:
        pass
    try:
        # nav.navall_download()
        mf.download_nav()
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
        returns()
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
        fx.exchange_rates_download(startdate, enddate)
    except:
        pass
    returns()
    update_index_constituents()

    wl.market_db_load()
    wl.mrigweb_stock_load()

if __name__ == '__main__':
    daily_datarun()
    # update_index_constituents()
#
# if (alldata==1) or (time.localtime().tm_hour >= morningtime.hour and
#     time.localtime().tm_hour <= eveningtime.hour - 2):
#     print("MORNING RUN")
#     try:
#         sh.stockHistoryNew_download()
#     except:
#         pass
#     try:
#         # nav.navall_download()
#         mf.download_nav()
#     except:
#         pass
#     try:
#         news.get_MCNews()
#     except:
#         pass
#     try:
#         yc.yield_download()
#     except:
#         pass
#     try:
#         gp.gold_download()
#     except:
#         pass
#     try:
#         cp.crude_download()
#     except:
#         pass
#     try:
#         fx.exchange_rates_download(startdate,enddate)
#     except:
#         pass
#     # try:
#     #     # ratios_download()
#     # except:
#     #     pass
#     # try:
#     #     # mf_codes()
#     # except:
#     #     pass
#     # try:
#     #     # corp_action_download()
#     # except:
#     #     pass
# #    try:
# #        stock_strategies()
# #    except:
# #        pass
#
#
# if (alldata==1) or (time.localtime().tm_hour >= eveningtime.hour):
#     print("EVENING RUN")
# ##    try:
# #        sh.stockHistory_download(startdate,enddate,progressbar)
# ##    except:
# ##        pass
# #    try:
# #        inx.nseIndexHistory_download(startdate,enddate,progressbar)
# #    except:
# #        pass
# #    try:
# #        tri.tri_download(startdate,enddate,progressbar)
# #    except:
# #        pass
# #    try:
# #        returns()
# #    except:
# #        pass
# #    try:
# #        och.oc_download_all()
# #    except:
# #        pass
# #    try:
# #        stock_strategies()
# #    except:
# #        pass
# #    try:
# #        oh.optionHistory_download()
# #    except:
# #        pass
# #    try:
# #        oh.optionLot_download()
# #    except:
# #        pass
# #     wl.stock_page_load()
# #     wl.ss_page_load()
# #     wl.os_page_load()
#
#
# #try:
# #    try:
# #        scheduler.enterabs(morningtime.timestamp(),priority=0,action=nav.navall_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(morningtime.timestamp(),priority=1,action=news.get_MCNews())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(morningtime.timestamp(),priority=2,action=yc.yield_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(morningtime.timesta8p(),priority=3,action=gp.gold_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(morningtime.timestamp(),priority=4,action=cp.crude_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(morningtime.timestamp(),priority=5,action=fx.exchange_rates_download(startdate,enddate))
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=0,action=sh.stockHistory_download(startdate,enddate))
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=1,action=inx.nseIndexHistory_download(startdate,enddate))
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=2,action=tri.tri_download(startdate,enddate))
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=3,action=ratios_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=4,action=mf_codes())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=5,action=corp_action_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=6,action=och.oc_download())
# #    except:
# #        pass
# #    try:
# #        scheduler.enterabs(eveningtime.timestamp(),priority=7,action=returns())
# #    except:
# #        pass
# #try:
# #    scheduler.run(blocking=True)
# #except KeyboardInterrupt:
# #    print('Stopped.')
# #
# #
# #news.get_MCNews()
#
# #weekly download of fundsnapshots and fund portfolio holdings
#

