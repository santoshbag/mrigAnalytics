# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:16:12 2018

@author: Santosh Bag

This module downloads data by using various modules

USAGE: python datarun.py (optional arguments ex. 1 3 5)

ARGUMENTS (optional)

STOCKHISTORY 1
MUTUALFUND   2
NEWS         3
YIELDS       4
STK RETURNS  5
MF RETURNS   6
INDEXMEMBERS 7
MARKET INSTR 8
FIN RESULTS  9
MARKET DB    10
STOCK LOAD   11
STOCK STRAT  12
TECHNICALS   13
CORRELATION  14
OPTION STRAT 15

"""

import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime,time,sched
# import moneycontrol as mc
import mutual_funds as mf
import strategies.stocks as st
import media.news as news
import mrigutilities as mu
import mrigstatics as ms
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
import correlations as corr
import research.analytics as ra
import json
import strategies.market_option_strategy as mos
import financial_results as fr

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
    starttime = time.monotonic()
    # calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = mu.sql_engine()
    date = engine.execute('select max(date) from daily_returns').fetchall()[0][0]
    print(str(date).replace('-',''))
    print("Populating Returns Started")
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
    print("Populating Returns Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for Populating Returns  %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

def mf_returns():
    starttime = time.monotonic()
    # calculate_returns_sql = "update stock_history set symbol='PVP' where symbol='PVP'"
    engine = mu.sql_engine()
    date = engine.execute('select max(nav_date) from mf_returns').fetchall()[0][0]
    print(str(date).replace('-',''))
    print("Populating MF Returns Started")
    sql = '''
            insert into mf_returns (scheme_name,isin,nav_date,nav,daily_arithmetic_return,daily_log_return)
            (
        (SELECT mf_history.scheme_name as scheme_name,
            mf_history.isin as isin,
            mf_history.nav_date as nav_date,
            mf_history.nav as nav,
            mf_history.nav / lag(mf_history.nav, 1) 
            OVER (PARTITION BY mf_history.scheme_name,mf_history.isin
            ORDER BY mf_history.nav_date) - 1::numeric AS daily_arith_return,
            ln(mf_history.nav / lag(mf_history.nav, 1)
            OVER (PARTITION BY mf_history.scheme_name,mf_history.isin
             ORDER BY mf_history.nav_date)) AS daily_log_return
           FROM mf_history
          WHERE nav > 0 and isin is not NULL and nav_date >= %s
          ORDER BY mf_history.scheme_name, mf_history.isin,mf_history.nav_date desc)
          )
                    on conflict (scheme_name,nav_date) do nothing;
            '''
    engine.execute(sql,(str(date).replace('-','')))
    print("Populating MF Returns Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for Populating MF Returns  %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

def stock_strategies():
    starttime = time.monotonic()

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
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for stock_strategies %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))


def update_index_constituents():
    starttime = time.monotonic()
    urls = {'NIFTY 100': 'https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv',
            'NIFTY 50': 'https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv',
            'NIFTY 500' : 'https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv',
            'NIFTY 200': 'https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv',
            'NIFTY SMALLCAP 100' : 'https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap100list.csv',
            'NIFTY MIDCAP 100': 'https://www.niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv',
            'NIFTY BANK' : 'https://www.niftyindices.com/IndexConstituent/ind_niftybanklist.csv',
            'NIFTY AUTO' : 'https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv',
            'NIFTY IT' : 'https://www.niftyindices.com/IndexConstituent/ind_niftyitlist.csv',
            'NIFTY FMCG':'https://www.niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv',
            'NIFTY PHARMA': 'https://www.niftyindices.com/IndexConstituent/ind_niftypharmalist.csv',
            'NIFTY METAL' : 'https://www.niftyindices.com/IndexConstituent/ind_niftymetallist.csv'
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
    print("Populating Index Constituent Started")
    for key in result.keys():
        sql = ''' update stock_history 
        set index_members=%s 
        where symbol=%s and date=%s
        '''
        engine.execute(sql,(result[key],key,(str(date).replace('-',''))))
    print("Populating Index Constituent Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for update_index_constituents %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

def populate_market_instruments():
    starttime = time.monotonic()
    print("Populating Market Instruments Started")
    session = mu.getKiteSession()
    ins = session.instruments()
    ins = pd.DataFrame(ins)
    engine = mu.sql_engine()
    ins['expiry'] = ins['expiry'].apply(lambda x: None if x == '' else x)
    ins['strike'] = ins['strike'].apply(lambda x: None if x == '' else x)
    ins['lot_size'] = ins['lot_size'].apply(lambda x: None if x == '' else x)
    ins['last_price'] = ins['last_price'].apply(lambda x: None if x == '' else x)
    ins['tick_size'] = ins['tick_size'].apply(lambda x: None if x == '' else x)
    ins['instrument_date'] = datetime.date.today()
    engine.execute("delete from market_instruments where instrument_date < (CURRENT_DATE - interval '10 days')")
    # print(ins)
    ins.to_sql('market_instruments', engine, index=False, if_exists='append')
    print("Populating Market Instruments Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for populate_market_instruments %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

def clean_mrigweb():
    sql = '''
    delete from os_page where load_date < (select max(load_date) from os_page); VACUUM FULL;
    '''
    mrigweb_engine = mu.sql_engine(dbname=ms.MRIGWEB)

    mrigweb_engine.execute(sql)

def populate_technicals(stocks='NIFTY 100'):
    starttime = time.monotonic()
    print("Populating Technical Indicators Started")
    engine = mu.sql_engine()

    df = ra.display_tech_analysis(stocks)
    df = df[df['date'] == max(df['date'])]
    df['ta'] = df[df.columns[5:]].apply(pd.Series.to_dict, axis=1)
    df['ta'] = df['ta'].apply(lambda x: json.dumps(x))
    df[['date', 'symbol', 'ta']].to_sql('technicals', engine, if_exists='append', index=False)
    print("Populating Technical Indicators Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for populate_technicals %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

scheduler = sched.scheduler(timefunc=time.time)
morninghour = 6
eveninghour = 16
morningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=morninghour,minute=0)
eveningtime = datetime.datetime(year=today.year,month=today.month,day=today.day,hour=eveninghour,minute=0)
#eveningtime = morningtime

def daily_datarun():
    if len(sys.argv) <= 1:
        try:
            sh.data_download()
            sh.data_insert()
        except:
            pass
        try:
            # nav.navall_download()
            mf.download_nav()
        except:
            pass
        try:
            news.get_GoogleNews()
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
            mf_returns()
        except:
            pass
        try:
            clean_mrigweb()
        except:
            pass
        # try:
        #     cp.crude_download()
        # except:
        #     pass
        # try:
        #     fx.exchange_rates_download(startdate, enddate)
        # except:
        #     pass
        # returns()
        update_index_constituents()
        populate_market_instruments()
        fr.results_download_all()

        wl.market_db_load()
        wl.mrigweb_stock_load()
        wl.strategies_stock_load()
        populate_technicals()
        corr.nifty_corr_data()
    #    mos.load_option_strategies()
    else:
        for arg in sys.argv[1:]:
            if arg == '1':
                try:
                    sh.data_download()
                    sh.data_insert()
                except:
                    pass
            elif arg == '2':
                try:
                    # nav.navall_download()
                    mf.download_nav()
                except:
                    pass
            elif arg == '3':
                try:
                    news.get_GoogleNews()
                except:
                    pass
            elif arg == '4':
                try:
                    yc.yield_download()
                except:
                    pass
            elif arg == '5':
                try:
                    returns()
                except:
                    pass
            elif arg == '6':
                try:
                    mf_returns()
                except:
                    pass
            elif arg == '7':
                update_index_constituents()
            elif arg == '8':
                populate_market_instruments()
            elif arg == '9':
                fr.results_download_all()
            elif arg == '10':
                wl.market_db_load()
            elif arg == '11':
                wl.mrigweb_stock_load()
            elif arg == '12':
                wl.strategies_stock_load()
            elif arg == '13':
                populate_technicals()
            elif arg == '14':
                corr.nifty_corr_data()
            elif arg == '15':
                mos.load_option_strategies()
            else:
                pass

if __name__ == '__main__':
    daily_datarun()
    # returns()
    # update_index_constituents()
    # populate_market_instruments()
    # corr.nifty_corr_data()
    # populate_technicals()
    # wl.market_db_load()
    # wl.mrigweb_stock_load()

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

