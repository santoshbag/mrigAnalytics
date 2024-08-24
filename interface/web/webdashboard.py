# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:46:14 2018

@author: Santosh Bag
"""

import sys,os
import urllib.parse

from PIL import ImageTk
from PIL.Image import Image

from tradingDB import tradingDB

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from dateutil import relativedelta
import datetime
import mrigutilities as mu
import strategies.stocks as stocks
import io,base64
import stockScreener as ss
import mfScreener as ms1
import mfScreener_new as ms
import research.analytics as ra
import data.settings_load as config

import media.news as n
import nsepy
import instruments.options as options
import instruments.termstructure as ts
import instruments.index as index
import instruments.qlMaps as qlMaps
import instruments.bonds as bonds
import instruments.swaps as swaps
import instruments.options as options
import instruments.capsfloors as capsfloors
import strategies.market_instruments as mo
import research.screener_TA as sta

from fuzzywuzzy import fuzz
import mrigplots as mp
from matplotlib import colors as mcolors
import matplotlib.pyplot as plot
import matplotlib
from plotly.offline import plot as pplot
import plotly.graph_objs as go
import plotly.subplots as subplt
import maintenance.item_manager as im

import mriggraphics as mg
import json

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
engine = mu.sql_engine()
setting = config.get_settings()

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


# def mrigweb_top_mf_holdings(location,tenor='6M',sheet='None'):
#
#     today = datetime.date.today()
#     lastweek = today - datetime.timedelta(weeks=1)
#     lastmonth = today - relativedelta.relativedelta(months=1)
#
#     top_holdings = ss.top_mf_holdings()
#
#
#     top_holdings = top_holdings.head(10)
#
#     labels = ['Dates','Returns']
#     plt = mp.singleScaleLine_plots(labels,'Returns')
#
#     fig,primary,secondary = plt[0],plt[1],plt[2]
#
#     cum_returns = ["Returns(An)"]
#     color = 0
#     for sym in top_holdings['symbol']:
#         stk = stocks.Stock(sym)
#         stk.get_returns(tenor)
#         dates = list(stk.daily_logreturns.index)
#         cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
#         period = (stk.daily_logreturns.index[-1] - stk.daily_logreturns.index[0]).days/360
#         if period <= 1: period = 1
#         cum_returns.append(float(stk.daily_logreturns.sum()/period))
#         primary.plot(dates,cum_return_series,"C"+str(color),label=sym)
#         primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#         color = color + 1
#
#     if sheet != 'None':
#         sht = xw.Book.caller().sheets[sheet]
#         sht.pictures.add(fig,
#                          name='Returns',
#                          update=True,
#                          left=sht.range(location).left,
#                          top=sht.range(location).top)
#
#
#     lis = list(top_holdings['company'])
#     lis.insert(0,"Top MF Holdings")
#     ret_lis = [lis,cum_returns]
#     return ret_lis

def market_db():

    page_items = im.get_item(['market_graphs','n50_ta_screen','sector_graph',
                              'NIFTY 50|levels_json','BANKNIFTY|levels_json'])
    for k,v in page_items.items():
        page_items = v

    graphs = []
    if 'market_graphs' in page_items.keys():
        print('Market_Graphs : Getting from Database')
        graphs = json.loads(page_items['market_graphs'])

    else:
        print('Market_Graphs : Creating from Scratch')
        d = tradingDB()
        market_graphs = d.market_snapshot()
        for figure in market_graphs[2]:
            figure.update_layout(width=500, height=300,
                                 yaxis_domain=[0.2, 1.0],
                                 yaxis2_domain=[0.0, 0.2])
            figure.update_xaxes(showline=True,
                                linewidth=2,
                                linecolor='ivory',
                                mirror=True)

            figure.update_layout(
                margin=dict(l=0, r=0, b=10, t=50, pad=1),
                paper_bgcolor="ivory"
            )
            plt_div = pplot(figure, output_type='div')
            graphs.append(plt_div)
        market_graphs_json = json.dumps(graphs)
        im.set_items({'market_graphs': market_graphs_json})


    if 'n50_ta_screen' in page_items.keys():
        print('N50 : Getting from Database')
        n50_ta_screen = pd.read_json(page_items['n50_ta_screen'], orient='split')
    else:
        print('N50 : Creating Table')
        n50_ta_screen = sta.display_analytics()
        n50_ta_screen_json = n50_ta_screen.to_json(orient='split')
        im.set_items({'n50_ta_screen' : n50_ta_screen_json})

    indices = setting['indices_for_mrig'].keys()
    # indices = ["NIFTY 50", "NIFTY BANK", "INDIA VIX", "NIFTY SMALLCAP 100",
    #            "NIFTY MIDCAP 100", "NIFTY PRIVATE BANK", "NIFTY PSU BANK", "NIFTY IT", "NIFTY AUTO",
    #            "NIFTY PHARMA", "NIFTY FMCG", "NIFTY FINANCIAL SERVICES", "NIFTY REALTY",
    #            "NIFTY HEALTHCARE INDEX", "NIFTY INDIA CONSUMPTION", "NIFTY INFRASTRUCTURE", "NIFTY COMMODITIES",
    #            "NIFTY ENERGY", "NIFTY 100", "NIFTY METAL"
    #            ]
    if 'sector_graph' in page_items.keys():
        print('Sector_Graph : Getting from Database')
        sector_graph = page_items['sector_graph']
    else:
        print('Sector_Graph : Creating from Scratch')
        engine = mu.sql_engine()
        fig = subplt.make_subplots(rows=4,
                                   cols=5,
                                   shared_xaxes=True,
                                   vertical_spacing=0.04,
                                   subplot_titles=indices)
        sql = """
        select date, symbol, close from stock_history where symbol in {} 
        and date > now() - interval '720 days' order by date desc
        """
        inx = str(indices).replace('[', '(').replace(']', ')')
        inx_data = pd.read_sql(sql.format(inx), engine)
        # inx_data

        coord = []
        for i in [1, 2, 3, 4, ]:
            for j in [1, 2, 3, 4, 5]:
                coord.append((i, j))
        for crd, indx in list(zip(coord, range(0, 20))):
            fig.add_trace(go.Scatter(x=inx_data['date'],
                                     y=inx_data[inx_data['symbol'] == indices[indx]]['close'],
                                     line=dict(color='blue',
                                               width=1,
                                               shape='spline'), showlegend=False), row=crd[0], col=crd[1])

        #     fig.layout.annotations[indx+1]['text'] = indices[indx]
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        fig.update_annotations(font_size=10)
        fig.update_layout(width=1000, height=700)
        sector_graph=pplot(fig, output_type='div')
        # sector_graph_json = json.dumps(sector_graph)
        im.update_items({'sector_graph' : str(sector_graph)})

    # graphs1 = []
    # for buf in market_graphs1[0]:
    #     buf.seek(0)
    #     img = buf.getvalue()
    #     buf.close()
    #     img = base64.b64encode(img)
    #     img = img.decode('utf-8')
    #     graphs.append(img)




    # nifty_chart1 = (base64.b64encode(market_graphs1[0][0].seek(0).getvalue())).decode('utf-8')
    # banknifty_chart1 = (base64.b64encode(market_graphs1[0][1].seek(0).getvalue())).decode('utf-8')
    # vix_chart1 = (base64.b64encode(market_graphs1[0][2].seek(0).getvalue())).decode('utf-8')
    # usdinr_chart1 = (base64.b64encode(market_graphs1[0][3].seek(0).getvalue())).decode('utf-8')
    # crude_chart1 = (base64.b64encode(market_graphs1[0][4].seek(0).getvalue())).decode('utf-8')
    # gold_chart1 = (base64.b64encode(market_graphs1[0][5].seek(0).getvalue())).decode('utf-8')
    if 'NIFTY 50|levels_json' in page_items.keys():
        print('Stock Levels : Getting from Database')
        levels_json = json.loads(page_items['NIFTY 50|levels_json'])
        level_chart = levels_json[0]
        pcr = levels_json[1]
        max_pain = levels_json[2]
        nifty_levels = [level_chart, pcr, max_pain]
    else:
        levels = ra.level_analysis(['NIFTY'])
        level_chart = levels['level_chart']
        pcr = levels['pcr']
        max_pain = levels['max_pain']
        nifty_levels = [level_chart, pcr, max_pain]
        levels_json = json.dumps(nifty_levels)
        im.set_items({'NIFTY 50|levels_json': levels_json})
        print('NIFTY 50  Levels Populated')

    if 'BANKNIFTY|levels_json' in page_items.keys():
        print('Stock Levels : Getting from Database')
        levels_json = json.loads(page_items['BANKNIFTY|levels_json'])
        level_chart = levels_json[0]
        pcr = levels_json[1]
        max_pain = levels_json[2]
        banknifty_levels = [level_chart, pcr, max_pain]
    else:
        levels = ra.level_analysis(['BANKNIFTY'])
        level_chart = levels['level_chart']
        pcr = levels['pcr']
        max_pain = levels['max_pain']
        banknifty_levels = [level_chart, pcr, max_pain]
        levels_json = json.dumps(banknifty_levels)
        im.set_items({'BANKNIFTY|levels_json': levels_json})
        print('BANKNIFTY  Levels Populated')
    return {'graphs' : graphs,
            'n50_ta_screen' : n50_ta_screen,
            'sector_graph' : sector_graph,
            'nifty_levels' : nifty_levels,
            'banknifty_levels' : banknifty_levels
            }

def stock_strategies():
    page_items = im.get_item(['st_macd_daily'])
    for k,v in page_items.items():
        page_items = v


    if 'st_macd_daily' in page_items.keys():
        print('ST_MACD : Getting from Database')
        st_macd_daily = pd.read_json(page_items['st_macd_daily'], orient='split')
    else:
        print('ST_MACD : Creating Table')
        st_macd_daily = sta.display_analytics()
        st_macd_daily_json = st_macd_daily.to_json(orient='split')
        im.set_items({'st_macd_daily' : st_macd_daily_json})

    return {'st_macd_daily' : st_macd_daily,
            }

def mrigweb_top_mfs(n=5):
    topmfs = ms.top_aum_mfs()
    assetlist1 = []
    # column_map = {'fund':'Fund Name','rating':'Rating','launch_date':'Launch Date',
    #           'expense_ratio_in_per':'Expense Ratio','1_yr_ret':'Return (1Yr)',
    #           '1_yr_rank':'Rank','net_assets_in_cr':'Net Assets (Cr)',
    #           'mf_category_name':'Category Name','Net Asset Value':'NAV'}
    #
    column_map = {'scheme_asset_type_1':'Asset Class','scheme_asset_type_2':'Sub Asset Class','aum':'Net Assets (Cr)',
              'scheme':'Fund','daily_log_return' : 'Return'}
    for asset in set(topmfs['scheme_asset_type_1']):
        if n == -1:
            mfs = topmfs[topmfs['scheme_asset_type_1'] == asset].sort_values(by='aum',ascending=False)
        else:
            mfs = topmfs[topmfs['scheme_asset_type_1'] == asset].sort_values(by='aum',ascending=False).head(n)
        mfs.rename(columns=column_map, inplace=True)
        mfs.set_index("Asset Class", inplace=True)
        #
        assetlist1.append(mfs)

    assetlist2 = []
    toppermfs = ms.top_performing_mfs()


    for asset in set(toppermfs['scheme_asset_type_1']):
        if n == -1:
            mfs = toppermfs[toppermfs['scheme_asset_type_1'] == asset].sort_values(by='daily_log_return', ascending=False)
        else:
            mfs = toppermfs[toppermfs['scheme_asset_type_1'] == asset].sort_values(by='daily_log_return', ascending=False).head(n)
        mfs.rename(columns=column_map, inplace=True)
        mfs.set_index("Asset Class", inplace=True)
        #
        assetlist2.append(mfs)

    # topmfs = topmfs[list(column_map.keys())]

    return [assetlist1,assetlist2]

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

    index_maps = {'symbol':'Company'}
    column_maps = {'ret24W':'24 Week Return','ret12W':'12 Week Return','ret4W':'4 Week Return'}
    top_holdings.rename(index=index_maps,columns=column_maps,inplace=True)

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

    index_maps = {'symbol':'Company'}
    column_maps = {'symbol' : 'Company','industry' : 'Industry','close' : 'Price',
                   'eps_growth' : 'EPS Growth','price_to_bv' : 'P/BV','pe' : 'P/E',
                   'price_to_earningsgrowth' : 'PEG','return_on_equity' : 'ROE',
                   'ps' : 'P/S','net_profit_margin' : 'Profit Margin',
                   'current_ratio' : 'Current Ratio','eps_growth_median' : 'Industry EPS Growth',
                   'pemedian' : 'Industry PE','psmedian' : 'Industry PS'}
    columns = ['industry','close','eps_growth','price_to_bv','pe','price_to_earningsgrowth',
               'return_on_equity','ps','net_profit_margin','current_ratio','eps_growth_median',
               'pemedian','psmedian']
    
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
    
    top_holdings = top_holdings[columns]        
    top_holdings.rename(columns=column_maps,inplace=True)
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
    top_holdings = top_holdings.head(10)
    
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
    index_maps = {'symbol':'Company'}
    column_maps = {'symbol' : 'Company','industry' : 'Industry','close' : 'Price',
                   'eps_growth' : 'EPS Growth','price_to_bv' : 'P/BV','pe' : 'P/E',
                   'beta' : 'BETA','return_on_equity' : 'ROE','divyld' : 'Div Yld',
                   'net_profit_margin' : 'Profit Margin','niftydivyld' : 'Nifty Div Yld',
                   'niftype' : 'Nifty PE','niftypb' : 'Nifty PB','niftyroe' : 'Nifty ROE'}


    columns = ['industry','close','eps_growth','price_to_bv','pe','beta',
               'return_on_equity','divyld','net_profit_margin','niftydivyld','niftype',
               'niftypb','niftyroe']
    
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
    top_holdings = top_holdings[columns]        
    top_holdings.rename(columns=column_maps,inplace=True)
    return [top_holdings,gi_graph]

def mrigweb_custom_screener(criteria):

    today = datetime.date.today()
    lastweek = today - datetime.timedelta(weeks=1)
    lastmonth = today - relativedelta.relativedelta(months=1)

#    top_holdings = mu.get_stored_stock_strategies('gi')
    top_holdings = ss.custom_stock_screener(criteria)
    
    return top_holdings
    
def mrigweb_news(newsid=None):
    
    # try:
    #     n.get_MCNews()
    # except:
    #     pass
    #
    if newsid is None:
        sql = "select distinct type, date, title, description,id,guid from media \
               where date > ((select max(date) from media) - interval '1 day') \
               order by type ,date desc"
    else:
        sql = "select distinct type, date, title, description,body,id,guid from media \
               where id='"+newsid+"' limit 1"
    
    engine =  mu.sql_engine()
    
    news = pd.read_sql(sql,engine)
    news.drop_duplicates(subset=['title'],inplace=True)

    newstype = list(news.type)
    newsdate = list(news.date)
    newstitle = list(news.title)
    newsdesc = list(news.description)
    if newsid is not None:
        newsbody = list(news.body)
    newsids = list(news.id)
    newsurls = list(news.guid)

    # print(newsids)

    news = {}
    for t in newstype:
        news[t] = []
    
    i = 0
    if newsid is not None:
        for t in newstype:
            news[t].append([newsdate[i],newstitle[i],newsdesc[i],newsids[i],newsbody[i],newsurls[i]])
            i = i + 1
    else:
        for t in newstype:
            news[t].append([newsdate[i],newstitle[i],newsdesc[i],newsids[i],newsurls[i]])
            i = i + 1

    return news


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
    price_labels,quotes = [], []
    try:
        price_labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
        quotes = [index.quote['lastPrice'],
                  index.quote['open'],
                  index.quote['previousclose'],
                  index.quote['dayhigh'],
                  index.quote['daylow'],
                  index.quote['high52'],
                  index.quote['low52']]
    except:
        pass
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
    if symbol != 'NIFTY 50':
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
    risk = index.get_risk()
    risklabels,risknumbers = [],[]
    for key in risk.keys():
        risklabels.append(key)
        risknumbers.append(risk[key])
    
    risk_list = [risklabels,risknumbers]
##    sht.range('D14').value = [risklabels,risknumbers]
#             
#             
    index.get_ratios()
##    ratios = [list(index.ratio_data.columns),index.ratio_data.values.tolist()[0]]
#    
##    sht.range('D18:J500').clear_contents()
    rd = pd.DataFrame()
    if not index.ratio_data.empty:
##        ratios = [['Ratio Date',index.ratio_data.index[0]],[" "," "]]
##        ratioheads = list(index.ratio_data.columns)
##        ratiovals = index.ratio_data.values.tolist()[0]
##        for i in range(2,len(index.ratio_data.columns)):
##            if ratiovals[i] != '':
##                if abs(float(ratiovals[i])) > 100000.00:
##                    ratios.append([ratioheads[i].replace('_',' ').upper()+' (lacs)',float(ratiovals[i])/100000])
##                else:
##                    ratios.append([ratioheads[i].replace('_',' ').upper(),ratiovals[i]])
        rd = index.ratio_data.transpose()
#        to_drop = ['symbol','download_date','rank','business_per_branch','business_per_employ', 'interest_income_per_branch','interest_income_per_employee', 'net_profit_per_branch','net_profit_per_employee']
#        rd.drop(to_drop,axis=0,inplace=True)
        rd.rename(index={'pe':'Price Earnings','pb':'Price Book','div_yield':'Dividend Yield'},inplace=True)
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
    
#    news = [item for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
    news = [(item[0].strftime('%d-%b-%Y'),item[1],item[2]) for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
              
    optionchain = index.optionChain()
#    sht.range('W3:AR500').clear_contents()
#    sht.range('W3').value = optionchain
    return [price_list,return_list,risk_list,rd,optionchain,price_graph,return_graph,macd_graph,boll_graph,stock_desc,news]

    
def mrigweb_stock(symbol,tenor='1Y'):
    
    page_items = im.get_item([symbol+'|return_list',symbol+'|risk_list',
                              symbol+'|price_graph',symbol+'|return_graph',
                              symbol+'|macd_graph',symbol+'|boll_graph',
                              symbol+'|levels_json'])
    for k,v in page_items.items():
        page_items = v

    stk = stocks.Stock(symbol)
    stock_desc = stk.stock_name + " | "+stk.industry+" | ISIN: "+ stk.isin
    nifty = stocks.Index('NIFTY 50')
    price_labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
    quotes = []
    quotes.append(stk.quote['lastPrice']) if 'lastPrice' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['open']) if 'open' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['prev_close']) if 'prev_close' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['high']) if 'high' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['low']) if 'low' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['high52']) if 'high52' in stk.quote.keys() else quotes.append("")
    quotes.append(stk.quote['low52']) if 'low52' in stk.quote.keys() else quotes.append("")
    # print(quotes)
#    if len(stk.quote) > 0:
#        quotes = [stk.quote['lastPrice'],
#                  stk.quote['open'],
#                  stk.quote['previousclose'],
#                  stk.quote['dayhigh'],
#                  stk.quote['daylow'],
#                  stk.quote['high52'],
#                  stk.quote['low52']]
#    else:
#        quotes = []
    price_list = [price_labels,quotes]
    print(price_list)

    cum_returns = []
    ohlcv = pd.DataFrame()
    return_labels = ['1W', '4W', '12W', '24W', '1Y', '3Y']
    if symbol+'|return_list' in page_items.keys():
        print('Return List : Getting from Database')
        return_list = json.loads(page_items[symbol+'|return_list'])
    else:
        print('Return List : Starting from Scratch')
        return_labels_1 = []
        for i in range(0, len(return_labels)):
            stk.get_returns(return_labels[i])
            ret_df = stk.daily_logreturns
            ret_df = ret_df[ret_df['symbol'] == symbol]
            # cum_returns.append('NA')
            # try:
            if not ret_df.empty:
                period = (ret_df.index[-1] - ret_df.index[0]).days / 360
                if period <= 1:
                    period = 1
                # print(ret_df['daily_log_returns'].sum())
                # return_period = (float(ret_df['daily_log_returns'].sum() / period))
                return_period = ("{:.2%}".format(float(ret_df['daily_log_returns'].sum() / period)))
                cum_returns.append(return_period)
                return_labels_1.append(return_labels[i])
                # print(cum_returns)
                # except:
            #     pass
        return_list = [return_labels_1, cum_returns]
        return_list_json = json.dumps(return_list)
        im.update_items({symbol+'|return_list': return_list_json})

             
    if symbol+'|price_graph' in page_items.keys():
        print('Price Graph : Getting from Database')
        price_graph = page_items[symbol+'|price_graph']
    else:
        print('Price Graph : Starting from Scratch')
        stk.get_price_vol(tenor)
        dates = list(stk.pricevol_data.index)

# labels = ['Dates','Price']
    # plt = mp.singleScaleLine_plots(labels,'Price')
    #
    # fig,primary,secondary = plt[0],plt[1],plt[2]
    #
    # primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    # primary.plot(dates,list(stk.pricevol_data['20_day_SMA']),"C2",label='20 Day SMA')
    # primary.plot(dates,list(stk.pricevol_data['60_day_SMA']),"C3",label='60 Day SMA')
    # primary.plot(dates,list(stk.pricevol_data['100_day_SMA']),"C4",label='100 Day SMA')
    # primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    #
    # buffer = io.BytesIO()
    # fig.savefig(buffer,format="PNG")
    # price_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    # buffer.close()
    # plot.close(fig)

        ohlcv = stk.pricevol_data.reset_index()
        price_graph = mg.plotly_candlestick(stk.symbol,ohlcv,[20,60,100])

        price_graph.update_layout(width=1000, height=500,
                             yaxis_domain=[0.2, 1.0],
                             yaxis2_domain=[0.0, 0.2])
        price_graph.update_xaxes(showline=True,
                            linewidth=2,
                            linecolor='ivory',
                            mirror=True)

        price_graph.update_layout(
            margin=dict(l=0, r=0, b=10, t=50, pad=1),
            paper_bgcolor="ivory"
        )
        price_graph = pplot(price_graph, output_type='div')
        im.update_items({symbol+'|price_graph' : price_graph})
    
    # labels = ['Dates','Price']
    # plt = mp.singleScaleLine_plots(labels,'Bands')
    #
    # fig,primary,secondary = plt[0],plt[1],plt[2]
    #
    # primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    # primary.plot(dates,list(stk.pricevol_data['Bollinger_Band']),"C2",label='Bollinger')
    # primary.plot(dates,list(stk.pricevol_data['Bollinger_UBand']),"C3",label='Boll Upper')
    # primary.plot(dates,list(stk.pricevol_data['Bollinger_LBand']),"C4",label='Boll Lower')
    # primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    #
    # buffer = io.BytesIO()
    # fig.savefig(buffer,format="PNG")
    # boll_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    # buffer.close()
    # plot.close(fig)

    if symbol+'|boll_graph' in page_items.keys():
        print('Bollinger Graph : Getting from Database')
        boll_graph = page_items[symbol+'|boll_graph']
    else:
        print('Bollinger Graph : Starting from Scratch')
        boll_graph = mg.plotly_tech_indicators(stk.symbol, ohlcv, ['Bollinger_Band', 'Bollinger_UBand', 'Bollinger_LBand'])

        boll_graph.update_layout(width=500, height=300,
                                  yaxis_domain=[0.0, 1.0])
        boll_graph.update_xaxes(showline=True,
                                 linewidth=2,
                                 linecolor='ivory',
                                 mirror=True)

        boll_graph.update_layout(
            margin=dict(l=0, r=0, b=10, t=50, pad=1),
            paper_bgcolor="ivory"
        )
        boll_graph = pplot(boll_graph, output_type='div')
        im.update_items({symbol+'|boll_graph': boll_graph})

    # labels = ['Dates','Price','MACD']
    # plt = mp.singleScaleLine_plots(labels,'MACD')
    #
    # fig,primary,secondary = plt[0],plt[1],plt[2]
    # dates = list(stk.pricevol_data.index)
    #
    # primary.plot(dates,list(stk.pricevol_data.close_adj),"C1",label='Close')
    # secondary.plot(dates,list(stk.pricevol_data['MACD']),"C2",label='MACD')
    # secondary.plot(dates,list(stk.pricevol_data['MACDS']),"C3",label='MACD Signal')
    # primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
    # secondary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
    #
    # buffer = io.BytesIO()
    # fig.savefig(buffer,format="PNG")
    # macd_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
    # buffer.close()
    # plot.close(fig)


    if symbol+'|macd_graph' in page_items.keys():
        print('MACD Graph : Getting from Database')
        macd_graph = page_items[symbol+'|macd_graph']
    else:
        print('MACD Graph : Starting from scratch')
        macd_graph = mg.plotly_tech_indicators(stk.symbol, ohlcv, ['MACD', 'MACDS'],subplots=2)

        macd_graph.update_layout(width=500, height=300,
                                 yaxis_domain=[0.2, 1.0])
        macd_graph.update_xaxes(showline=True,
                                linewidth=2,
                                linecolor='ivory',
                                mirror=True)

        macd_graph.update_layout(
            margin=dict(l=0, r=0, b=10, t=50, pad=1),
            paper_bgcolor="ivory")

        macd_graph = pplot(macd_graph, output_type='div')
        im.update_items({symbol+'|macd_graph':macd_graph})

#     labels = ['Dates','Returns']
#     plt = mp.singleScaleLine_plots(labels,'Returns')
#     fig,primary,secondary = plt[0],plt[1],plt[2]
#     stk.get_returns(tenor)
#     nifty.get_returns(tenor)
#     dates = list(stk.daily_logreturns.index)
#     cum_return_series = list(stk.daily_logreturns.daily_log_returns.cumsum())
#     nifty_dates = list(nifty.daily_logreturns.index)
#     nifty_cum_return_series = list(nifty.daily_logreturns.daily_log_returns.cumsum())
#     primary.plot(dates,cum_return_series,"C3",label=symbol)
#     primary.plot(nifty_dates,nifty_cum_return_series,"C4",label='NIFTY')
#     if(stk.industry != ""):
#         industry_ret = ss.sector_returns("10",tenor)
#         industry_ret_dates = list(industry_ret[industry_ret['industry'] == stk.industry].index)
#         industry_ret_cum_return_series = list(industry_ret[industry_ret['industry'] == stk.industry].daily_log_returns.cumsum())
#         primary.plot(industry_ret_dates,industry_ret_cum_return_series,"C2",label=stk.industry)
#     primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=True, ncol=5)
#
#     buffer = io.BytesIO()
#     fig.savefig(buffer,format="PNG")
#     return_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#     buffer.close()
#     plot.close(fig)

    if symbol+'|return_graph' in page_items.keys():
        print('Return Graph : Getting from Database')
        return_graph = page_items[symbol+'|return_graph']
    else:
        stk_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.symbol]
        stk_ret['cum_ret'] = stk_ret['daily_log_returns'].cumsum()

        benchmark1_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.get_benchmark_index1()]
        benchmark1_ret['cum_ret'] = benchmark1_ret['daily_log_returns'].cumsum()
        benchmark2_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.get_benchmark_index2()]
        benchmark2_ret['cum_ret'] = benchmark2_ret['daily_log_returns'].cumsum()

        return_graph = go.Figure(data=[go.Scatter(x=stk_ret.index,
                        y= stk_ret['cum_ret'], name=stk.symbol),
                             go.Scatter(x=benchmark1_ret.index,
                        y= benchmark1_ret['cum_ret'], name=stk.get_benchmark_index1()),
                             go.Scatter(x=benchmark2_ret.index,
                        y= benchmark2_ret['cum_ret'], name=stk.get_benchmark_index2())])

        return_graph.update_layout(width=1000, height=500, title='Returns')
        return_graph = pplot(return_graph, output_type='div')
        im.update_items({symbol+'|return_graph' : return_graph})

    if symbol+'|risk_list' in page_items.keys():
        print('Return List : Getting from Database')
        risk_list = json.loads(page_items[symbol+'|risk_list'])
    else:
        risk = stk.get_risk()
        risklabels,risknumbers = [],[]
        for key in risk.keys():
            risklabels.append(key)
            # risknumbers.append(risk[key])
            r = risk[key]
            try:
                r = '{:.2%}'.format(r)
                # print('Risk in Percentage---->',r)
            except:
                pass
            risknumbers.append(r)
        risk_list = [risklabels,risknumbers]
        risk_list_json = json.dumps(risk_list)
        im.update_items({symbol+'|risk_list': risk_list_json})
#    sht.range('D14').value = [risklabels,risknumbers]
             
    if symbol+'|ratio_list' in page_items.keys():
        print('Ratio List : Getting from Database')
        ratio_list = pd.read_json(page_items[symbol+'|ratio_list'], orient='split')
    else:
        print('Ratio List : Creating Table')
        stk.get_ratios()
        ratio_list = stk.ratio_data
        ratio_list_json = ratio_list.to_json(orient='split')
        im.set_items({symbol+'|ratio_list': ratio_list_json})

    if symbol+'|income_statement' in page_items.keys():
        print('Income Statement : Getting from Database')
        income_statement = pd.read_json(page_items[symbol+'|income_statement'], orient='split')
    else:
        print('Income Statement : Creating Table')
        stk.get_income_statement()
        income_statement = stk.income_statement
        income_statement_json = income_statement.to_json(orient='split')
        im.set_items({symbol+'|income_statement': income_statement_json})

    if symbol+'|balance_sheet' in page_items.keys():
        print('Balance Sheet : Getting from Database')
        balance_sheet = pd.read_json(page_items[symbol+'|balance_sheet'], orient='split')
    else:
        print('Balance Sheet : Creating Table')
        stk.get_balance_sheet()
        balance_sheet = stk.balance_sheet
        balance_sheet_json = balance_sheet.to_json(orient='split')
        im.set_items({symbol+'|balance_sheet': balance_sheet_json})


#    sht.range('D18:J500').clear_contents()
    rd = pd.DataFrame()
#     if not stk.ratio_data.empty:
# #        ratios = [['Ratio Date',stk.ratio_data.index[0]],[" "," "]]
# #        ratioheads = list(stk.ratio_data.columns)
# #        ratiovals = stk.ratio_data.values.tolist()[0]
# #        for i in range(2,len(stk.ratio_data.columns)):
# #            if ratiovals[i] != '':
# #                if abs(float(ratiovals[i])) > 100000.00:
# #                    ratios.append([ratioheads[i].replace('_',' ').upper()+' (lacs)',float(ratiovals[i])/100000])
# #                else:
# #                    ratios.append([ratioheads[i].replace('_',' ').upper(),ratiovals[i]])
#         rd = stk.ratio_data.transpose()
#         to_drop = ['symbol','download_date','rank','business_per_branch','business_per_employ', 'interest_income_per_branch','interest_income_per_employee', 'net_profit_per_branch','net_profit_per_employee']
#         rd.drop(to_drop,axis=0,inplace=True)
#         rd.rename(index=lambda x: x.upper().replace('_'," "),inplace=True)
# #        rd.rename(columns=lambda x: x.upper().replace('_'," "),inplace=True)
#         rd.replace('',np.nan,inplace=True)
#         rd.dropna(how='all',axis=0,inplace=True)
#        sht.range('D19').value = rd
    
    sql = "select distinct date, title, description from media \
           where date > ((select max(date) from media) - interval '2 days') \
           order by date desc"
           
    
    engine =  mu.sql_engine()
    
    news = engine.execute(sql).fetchall()
    
    news = [(item[0].strftime('%d-%b-%Y'),item[1],item[2]) for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
              
    optionchain = pd.DataFrame()
    # optionchain = stk.optionChain()

    if symbol+'|levels_json' in page_items.keys():
        print('Stock Levels : Getting from Database')
        levels_json = json.loads(page_items[symbol+'|levels_json'])
        level_chart = levels_json[0]
        pcr = levels_json[1]
        max_pain = levels_json[2]
    else:
        stk.get_levels()
        level_chart = stk.level_chart
        # level_chart = base64.b64encode(level_chart.getvalue()).decode('utf-8').replace('\n', '')
        pcr = stk.pcr
        max_pain = stk.max_pain
        levels = [level_chart,pcr,max_pain]
        levels_json = json.dumps(levels)
        im.update_items({symbol+'|levels_json' : levels_json})
        print(symbol+'  Levels Populated')


#    sht.range('W3:AR500').clear_contents()
#    sht.range('W3').value = optionchain
    return [price_list,return_list,risk_list,rd,optionchain,price_graph,return_graph,macd_graph,boll_graph,stock_desc,news,level_chart,pcr,max_pain,ratio_list,income_statement,balance_sheet]


def mrigweb_mf(symbol, tenor='1Y'):
    page_items = im.get_item([symbol + '|return_list', symbol + '|risk_list',
                              symbol + '|price_graph', symbol + '|return_graph',
                              symbol + '|macd_graph', symbol + '|boll_graph',
                              symbol + '|levels_json'])
    for k, v in page_items.items():
        page_items = v

    stk = stocks.MutualFunds(symbol)
    stock_desc = stk.symbol + " | " + stk.asset_type_1 + " | ISIN: " + stk.isin
    nifty = stocks.Index('NIFTY 50')
    price_labels = ['Last NAV']
    quotes = []
    quotes.append(stk.quote)
    price_list = [price_labels, quotes]
    print(price_list)

    cum_returns = []
    ohlcv = pd.DataFrame()
    return_labels = ['1W', '4W', '12W', '24W', '1Y', '3Y']
    if symbol + '|return_list' in page_items.keys():
        print('Return List : Getting from Database')
        return_list = json.loads(page_items[symbol + '|return_list'])
    else:
        print('Return List : Starting from Scratch')
        return_labels_1 = []
        for i in range(0, len(return_labels)):
            stk.get_returns(return_labels[i])
            ret_df = stk.daily_logreturns
            ret_df = ret_df[ret_df['symbol'] == symbol]
            # cum_returns.append('NA')
            # try:
            if not ret_df.empty:
                period = (ret_df.index[-1] - ret_df.index[0]).days / 360
                if period <= 1:
                    period = 1
                # print(ret_df['daily_log_returns'].sum())
                # return_period = (float(ret_df['daily_log_returns'].sum() / period))
                return_period = ("{:.2%}".format(float(ret_df['daily_log_returns'].sum() / period)))
                cum_returns.append(return_period)
                return_labels_1.append(return_labels[i])
                # print(cum_returns)
                # except:
            #     pass
        return_list = [return_labels_1, cum_returns]
        return_list_json = json.dumps(return_list)
        im.update_items({symbol + '|return_list': return_list_json})

    if symbol + '|price_graph' in page_items.keys():
        print('Price Graph : Getting from Database')
        price_graph = page_items[symbol + '|price_graph']
    else:
        print('Price Graph : Starting from Scratch')
        stk.get_price_vol(tenor)
        dates = list(stk.pricevol_data.index)

        ohlcv = stk.pricevol_data.reset_index()
        price_graph = mg.plotly_line_graph(list(ohlcv['nav_date']),[list(ohlcv['nav'])],fig_title=symbol,y_names=['NAV'])

        price_graph.update_layout(width=1000, height=500,
                                  yaxis_domain=[1.0, 1.0])
        price_graph.update_xaxes(showline=True,
                                 linewidth=2,
                                 linecolor='ivory',
                                 mirror=True)

        price_graph.update_layout(
            margin=dict(l=0, r=0, b=10, t=50, pad=1),
            paper_bgcolor="ivory"
        )
        price_graph = pplot(price_graph, output_type='div')
        im.update_items({symbol + '|price_graph': price_graph})

    if symbol + '|return_graph' in page_items.keys():
        print('Return Graph : Getting from Database')
        return_graph = page_items[symbol + '|return_graph']
    else:
        stk_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.symbol]
        stk_ret['cum_ret'] = stk_ret['daily_log_returns'].cumsum()

        benchmark1_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.get_benchmark_index1()]
        benchmark1_ret['cum_ret'] = benchmark1_ret['daily_log_returns'].cumsum()
        benchmark2_ret = stk.daily_logreturns[stk.daily_logreturns['symbol'] == stk.get_benchmark_index2()]
        benchmark2_ret['cum_ret'] = benchmark2_ret['daily_log_returns'].cumsum()

        return_graph = go.Figure(data=[go.Scatter(x=stk_ret.index,
                                                  y=stk_ret['cum_ret'], name=stk.symbol),
                                       go.Scatter(x=benchmark1_ret.index,
                                                  y=benchmark1_ret['cum_ret'], name=stk.get_benchmark_index1()),
                                       go.Scatter(x=benchmark2_ret.index,
                                                  y=benchmark2_ret['cum_ret'], name=stk.get_benchmark_index2())])

        return_graph.update_layout(width=1000, height=500, title='Returns')
        return_graph = pplot(return_graph, output_type='div')
        im.update_items({symbol + '|return_graph': return_graph})

    # sql = "select distinct date, title, description from media \
    #        where date > ((select max(date) from media) - interval '2 days') \
    #        order by date desc"
    #
    # engine = mu.sql_engine()
    #
    # news = engine.execute(sql).fetchall()
    #
    # news = [(item[0].strftime('%d-%b-%Y'), item[1], item[2]) for item in news if
    #         fuzz.token_set_ratio(symbol, item[1]) > 97]

    return [price_list, return_list, price_graph, return_graph,stock_desc]
def mrigweb_funds(symbol,tenor='1Y'):
    
#    sheet='Stock'
#    sht = xw.Book.caller().sheets[sheet]
#    symbol = sht.range('B2').value
#    tenor = sht.range('M2').value
    # Get Specs
    
    sql = "select mfg.mf_category_name as \"Category Name\", mfs.fund as \"Fund Name\", mfs.launch_date as \"Launch Date\", \
           mfs.expense_ratio_in_per as \"Expense Ratio\", mfs.rating as Rating, mfs.\"1_yr_rank\" as Rank, \
           mfs.\"1_yr_ret\" as \"Return(1Yr)\", mfs.net_assets_in_cr as \"Net Assets(Cr)\" from mf_snapshot mfs inner join mf_categories mfg on mfs.category=mfg.mf_category_code \
           where mfs.fund='%s' order by mfs.snapshot_date desc limit 1"

    engine =  mu.sql_engine()
    mf_spec = pd.read_sql(sql%(symbol),engine)           
    
    """
    NAV History--------------------------
    """
    
    sql =  "select mnh.\"Date\", mnh.\"Scheme Name\", mnh.\"Net Asset Value\" from mf_nav_history mnh where \
           mnh.\"Scheme Name\" = (select \"Scheme Name\" from mf_nav_history where \"Scheme Name\" like ( '%%' || '"+symbol+"' || '%%') limit 1) \
           and mnh.\"Date\" > now() - interval '1 year'"
    mf_navs = pd.read_sql(sql,engine)
    if not mf_navs.empty:
        mf_navs = mf_navs[['Date','Net Asset Value']]           
        scheme_desc = mf_navs['Scheme Name'].iloc[0]
    nifty = stocks.Index('NIFTY 50')

    """
    Holdings History--------------------------
    """
    
    sql =  "select mfp.company as Company, mfp.sector as Sector, mfp.holding_current as \"Holding(Current)\",\
            mfp.holding_3yhigh as \"Holding(3Y High)\", mfp.holding_3ylow as \"Holding(3Y Low)\" from mf_portfolios mfp where \
            mfp.fund = (select fund from mf_portfolios where fund like ( '%%' || '"+symbol+"' || '%%') limit 1) \
            and mfp.download_date = (select max(download_date) from mf_portfolios where fund = (select fund from mf_portfolios \
            where fund like ( '%%' || '"+symbol+"' || '%%') limit 1) )"

    mf_navs = pd.read_sql(sql,engine)
    if not mf_navs.empty:
        mf_navs = mf_navs[['Date','Net Asset Value']]           
        scheme_desc = mf_navs['Scheme Name'].iloc[0]
    
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
    plot.close(fig)
    
    
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
    plot.close(fig)
    
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
    plot.close(fig)
    
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
    plot.close(fig)

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
    rd = pd.DataFrame()
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
    
    news = [(item[0].strftime('%d-%b-%Y'),item[1],item[2]) for item in news if fuzz.token_set_ratio(symbol,item[1]) > 97]
              
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

def mrigweb_covered_call(live=False):
#    sheet='Covered Calls'
#    sht = xw.Book.caller().sheets[sheet]
#    sht.range('B3:L500').clear_contents()
    oc = ss.covered_call(live=live)
    oc = oc[0]
#    oc_analytic = pd.DataFrame()
    if not oc.empty:

        oc['Initial_Yield'] = oc['CALL_LTP']/oc['Underlying']
        oc['Outlay'] = oc['Underlying']*oc['Lot']
        oc['Max_Profit'] = (oc['CALL_LTP'] + oc['Strike_Price'] - oc['Underlying'])*oc['Lot'] 
        oc['Max_Risk'] = oc['CALL_LTP']*oc['Lot'] - oc['Outlay']
        oc['Max_Yield'] = abs(oc['Max_Profit']/oc['Max_Risk'])

    return oc


def mrigweb_bull_put_spread(live=False):
    oc = ss.bull_put_spread(live=live)
    oc = oc[0]
#    oc_analytic = pd.DataFrame()

    if not oc.empty:
        oc['Initial_Yield'] = (oc['Higher_Strike_LTP']-oc['PUT_LTP'])/(oc['Higher_Strike']-oc['Strike_Price'])
        oc['Net_Credit'] = (oc['Higher_Strike_LTP']-oc['PUT_LTP'])*oc['Lot']
        oc['Max_Risk'] = (oc['Higher_Strike']-oc['Strike_Price'])*oc['Lot'] - oc['Net_Credit']
        oc['Max_Yield'] = abs(oc['Net_Credit']/oc['Max_Risk'])
        
    return oc


def mrigweb_option_strategy(live=False):
    oc = ss.bull_put_spread(live=live)
    oc = oc[0]
    #    oc_analytic = pd.DataFrame()

    if not oc.empty:
        oc['Initial_Yield'] = (oc['Higher_Strike_LTP'] - oc['PUT_LTP']) / (oc['Higher_Strike'] - oc['Strike_Price'])
        oc['Net_Credit'] = (oc['Higher_Strike_LTP'] - oc['PUT_LTP']) * oc['Lot']
        oc['Max_Risk'] = (oc['Higher_Strike'] - oc['Strike_Price']) * oc['Lot'] - oc['Net_Credit']
        oc['Max_Yield'] = abs(oc['Net_Credit'] / oc['Max_Risk'])

    return oc

def mrigweb_bear_call_spread(live=False):
    oc = ss.bear_call_spread(live=live)
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
    ltp = opid['ltp']
    option_type = opid['option_type']
    
    option = mo.MarketOptions(symbol,strike,expiry,option_type)    
    underlying_spot = option.underlying['lastPrice']
    moneyness = "ATM"
    if option_type[0] == 'C':
        if (strike - underlying_spot) < 0:
            moneyness = "ITM"
        if (strike - underlying_spot) > 0:
            moneyness = "OTM"
    if option_type[0] == 'P':
        if (strike - underlying_spot) > 0:
            moneyness = "ITM"
        if (strike - underlying_spot) < 0:
            moneyness = "OTM"
    
    sql = "select lot from futures_option_lots where symbol='%s'"
    engine = mu.sql_engine()
    lot = "NA"
    try:
        lot = engine.execute(sql%('NIFTY' if symbol=='NIFTY 50' else symbol)).fetchall()
        lot = lot[0][0]
    except:
        pass
    contract_specs = [['Underlying','Option Type','Strike','Expiry',
                       'Lot','LTP','Underlying','Moneyness'],
                      [symbol,option_type_map[option_type],strike,expiry,
                       lot,ltp,underlying_spot,moneyness]]
    
    """
    Option History----------------------------------------------------------------------
    """
    oh = option.get_price_vol()
    OI,dates,close = [],[],[]
    if not oh.empty:
        print(oh)
        dates = list(oh.index)
#        print(dates)
        close = list(oh['Price'])
#        print(close)
        OI = list(oh['Open Interest'])
#        print(OI)
#        oh = oh.loc[[d for d in list(oh.index) if (enddate-d)% datetime.timedelta(days=3) == datetime.timedelta(0) ]]
        oh = oh.sort_index(ascending=0)
#        print(oh)
    
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

    results = option.valuation(ltp)
    
    """
    Risk Profile and Greeks
    """
    
    underlying_spot_range = [max(underlying_spot/100,0.5)*i for i in range(1,200)]
    
    NPV = []
    delta = []
    gamma = []
    theta = []
    
    for spot in underlying_spot_range:
        result = option.scenario_analysis({'spot':spot})
        NPV.append(result['NPV']- option.ltp)
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

def mrigweb_ff_rates(reference_date=None,params=None):

#   Default Flat Forward Rate 
    reference_date = datetime.date.today()
    curvename = 'Flat_Forward_1'
    day_count = 'Actual-360'
    calendar = 'India'
    flat_rate = '0.02'
    compounding = 'Compounded'
    compounding_frequency = 'Quarterly'
    shiftparameter = '0'
    curves = []

    if params:
        curvename = params['curvename']
        day_count = params['day_count']
        calendar = params['calendar']
        flat_rate = params['flat_rate']
        compounding = params['compounding']
        compounding_frequency = params['compounding_frequency']
        shiftparameter = params['shiftparameter']
    
    objid = curvename
    
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'flat_rate' : float(flat_rate.strip()),
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}
    
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 

        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
#        print(args)
        ffyc = ts.FlatForwardYieldCurve(reference_date,float(flat_rate))
        args.update({'shiftparameter' : [[0]]})
        ffyc.setupCurve(args)
        curves.append(ffyc)
#    start = ffyc.getReferenceDate()
#    forwardstart = start + datetime.timedelta(days=180)
#    dates = [start+datetime.timedelta(days=180*i) for i in range(0,80)]
#    tenors = [datetime.timedelta(days=180*i)/datetime.timedelta(days=360) for i in range(0,80)] 
#    discounts = ffyc.getDiscountFactor(dates)
#    #baseforwards = [basecurve.getForwardRate(start,start+datetime.timedelta(days=180*i)) for i in range(0,20)]
#    forwards = [ffyc.getForwardRate(forwardstart,forwardstart+datetime.timedelta(days=180*i)) for i in range(0,80)]
#    zeroes = [ffyc.getZeroRate(start+datetime.timedelta(days=180*i)) for i in range(0,80)]
#
#    labels = ['Years','Rates','Discount Factors']
#    plt = mp.singleScaleLine_plots(labels,curvename)
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    
#    fig.subplots_adjust(left=0.125,top=0.85)
#
#    primary.plot(tenors[1:],zeroes[1:],"C2",linestyle='--',label="Spot")
#    primary.plot(tenors[1:],forwards[1:],"C3",linestyle='--',label="6M Forward")
#    primary.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter('{0:.2%}'.format))    
#    secondary.plot(tenors[1:],discounts[1:],"C1",label='Discount Factors')
        if shiftparameter != '0':
            ffyc_shifted = ts.FlatForwardYieldCurve(reference_date,float(flat_rate))
            args.update({'shiftparameter' : [[float(shiftparameter)]]})
            ffyc_shifted.setupCurve(args)
            curves.append(ffyc_shifted)
#        discounts_shifted = ffyc_shifted.getDiscountFactor(dates)
#        zeroes_shifted = [ffyc_shifted.getZeroRate(start+datetime.timedelta(days=180*i)) for i in range(0,80)]
#        primary.plot(tenors[1:],zeroes_shifted[1:],"C4",linestyle='--',label="Spot_shifted")
#        secondary.plot(tenors[1:],discounts_shifted[1:],"C5",label='DF Shifted')
#    primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
#    secondary.legend(loc='upper center', bbox_to_anchor=(0.7, -0.10),fancybox=True, shadow=True, ncol=5)
#
#    
#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    ffyc_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
        
    return curves

def mrigweb_szc_rates(curve_currency='INR',reference_date=None,params=None):

    engine = mu.sql_engine()
    reference_date = datetime.date.today()
    try:
        reference_date = engine.execute("select curvedate from yieldcurve where curve='"+curve_currency+"' order by curvedate desc limit 1").fetchall()
        reference_date = reference_date[0][0]
#        print(reference_date)
    except:
        pass
#    print(reference_date)
    day_count = 'Actual-360'
    calendar = 'India'
    interpolation = 'Linear'
    compounding = 'Compounded'
    compounding_frequency = 'Quarterly'
    shiftparameter = '0'
    curves = []
    if params:
        day_count = params['day_count']
        calendar = params['calendar']
        interpolation = params['interpolation']
        compounding = params['compounding']
        compounding_frequency = params['compounding_frequency']
        shiftparameter = params['shiftparameter']
    
    objid = curve_currency
    
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip(),
            'interpolation' : interpolation.strip()}
    
    if mu.args_inspector(args)[0]:
        for key in args:
            objid = objid + "|" + str(args[key]) 
        
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        szyc = ts.SpotZeroYieldCurve(curve_currency,reference_date)
        args.update({'shiftparameter' : [[0]]})
        szyc.setupCurve(args)
        curves.append(szyc)
#    start = szyc.getReferenceDate()
#    forwardstart = start + datetime.timedelta(days=180)
#    dates = [start+datetime.timedelta(days=180*i) for i in range(0,80)]
#    tenors = [datetime.timedelta(days=180*i)/datetime.timedelta(days=360) for i in range(0,80)] 
#    discounts = szyc.getDiscountFactor(dates)
#    #baseforwards = [basecurve.getForwardRate(start,start+datetime.timedelta(days=180*i)) for i in range(0,20)]
#    forwards = [szyc.getForwardRate(forwardstart,forwardstart+datetime.timedelta(days=180*i)) for i in range(0,80)]
#    zeroes = [szyc.getZeroRate(start+datetime.timedelta(days=180*i)) for i in range(0,80)]
#
#    labels = ['Years','Rates','Discount Factors']
#    plt = mp.singleScaleLine_plots(labels,curve_currency+" Curve "+reference_date.strftime('%d-%b-%Y'))
#
#    fig,primary,secondary = plt[0],plt[1],plt[2]
#    fig.subplots_adjust(left=0.125,top=0.85)
#    
#    primary.plot(tenors[1:],zeroes[1:],"C2",linestyle='--',label="Spot")
#    primary.plot(tenors[1:],forwards[1:],"C3",linestyle='--',label="6M Forward")
#    primary.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter('{0:.2%}'.format))    
#    secondary.plot(tenors[1:],discounts[1:],"C1",label='Discount Factors')
        if shiftparameter != '0':
            szyc_shifted = ts.SpotZeroYieldCurve(curve_currency,reference_date)
            args.update({'shiftparameter' : [[float(shiftparameter)]]})
            szyc_shifted.setupCurve(args)
            curves.append(szyc_shifted)
#            discounts_shifted = szyc_shifted.getDiscountFactor(dates)
#            zeroes_shifted = [szyc_shifted.getZeroRate(start+datetime.timedelta(days=180*i)) for i in range(0,80)]
#            primary.plot(tenors[1:],zeroes_shifted[1:],"C4",linestyle='--',label="Spot_shifted")
#            secondary.plot(tenors[1:],discounts_shifted[1:],"C5",label='Discount Factors Shifted')
#        primary.legend(loc='upper center', bbox_to_anchor=(0.2, -0.10),fancybox=True, shadow=True, ncol=5)
#        secondary.legend(loc='upper center', bbox_to_anchor=(0.7, -0.10),fancybox=True, shadow=True, ncol=5)


#    buffer = io.BytesIO()
#    fig.savefig(buffer,format="PNG")
#    szyc_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
#    buffer.close()
        
    return curves

def mrigweb_ratePlot(curves=[],desc=[]):
    labels = ['Years','Rates','Discount Factors']
    if len(curves) > 0:
        start = curves[0].getReferenceDate()
        plt = mp.singleScaleLine_plots(labels,"Rate Curve "+ start.strftime('%d-%b-%Y'))
    
        fig,primary,secondary = plt[0],plt[1],plt[2]
        fig.subplots_adjust(left=0.125,top=0.85)
        colorcount = 0
        curvecount = 0
        for curve in curves:
            start = curve.getReferenceDate()
            forwardstart = start + datetime.timedelta(days=180)
            dates = [start+datetime.timedelta(days=180*i) for i in range(0,80)]
            tenors = [datetime.timedelta(days=180*i)/datetime.timedelta(days=360) for i in range(0,80)] 
            discounts = curve.getDiscountFactor(dates)
    #        print(discounts)
            #baseforwards = [basecurve.getForwardRate(start,start+datetime.timedelta(days=180*i)) for i in range(0,20)]
            forwards = [curve.getForwardRate(forwardstart,forwardstart+datetime.timedelta(days=180*i)) for i in range(0,80)]
            zeroes = [curve.getZeroRate(start+datetime.timedelta(days=180*i)) for i in range(0,80)]    
            colorcount = colorcount + 1
            primary.plot(tenors[1:],zeroes[1:],"C"+str(colorcount),linestyle='--',label="Spot_"+desc[curvecount])
            colorcount = colorcount + 1
            primary.plot(tenors[1:],forwards[1:],"C"+str(colorcount),linestyle='--',label="6M Forward_"+desc[curvecount])
            primary.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter('{0:.2%}'.format))    
            colorcount = colorcount + 1
            secondary.plot(tenors[1:],discounts[1:],"C"+str(colorcount),label="Discount Factors_"+desc[curvecount])
            primary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),fancybox=True, shadow=False, ncol=10,fontsize=5)
            secondary.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20),fancybox=True, shadow=False, ncol=5,fontsize=5)
#            fig.suptitle("Rate Curve "+ start.strftime('%d-%b-%Y'))
            curvecount = curvecount + 1
    
        buffer = io.BytesIO()
        fig.savefig(buffer,format="PNG")
        curve_graph = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
        buffer.close()
        
    return curve_graph
    

def mrigweb_Libor(index_name,
                 curve_currency='INR',
                 tenor='3M',
                 day_count='30-360',
                 calendar='India',
                 settlement_days=3,
                 yieldcurvehandle=None):
    
    args = {'index_name':index_name.strip(),
            'curve_currency' : curve_currency.strip(),
            'tenor' : tenor.strip(),
            'day_count':day_count.strip(),                                     
            'calendar': calendar.strip(),
            'settlement_days' : int(settlement_days)}
    
    if mu.args_inspector(args)[0]:
        ych = yieldcurvehandle.getCurveHandle()
        libor = index.Libor(args['index_name'],
                            args['tenor'],
                            args['settlement_days'],
                            args['curve_currency'],
                            args['calendar'],
                            args['day_count'],
                            ych)
        return libor
    else:
        return None
    

def mrigweb_Bond(issue_name,
                 issue_date,
                 maturity_date,
                 face_value=100,
                 day_count='30-360',
                 calendar='India',
                 business_convention='Following',
                 month_end='True',
                 settlement_days=3,
                 date_generation='Backward',
                 coupon_frequency='Semiannual',
                 fixed_coupon_rate=None,
                 floating_coupon_index=None,
                 floating_coupon_spread=0,
                 inArrears=True,
                 cap=None,
                 floor=None,
                 fixing=None,
                 conversionRatio=None,
                 conversionPrice=None,
                 credit_spread=None,
                 call_schedule=None,
                 put_schedule=None,
                 dividend_schedule=None):
    
    
    bondType,bond = None, None
    # Check for fixed rate bond
    if floating_coupon_index != None:
#    if floating_coupon_index.strip() in objectmap.keys():
        bondType = 'floatingratebond'
    if fixed_coupon_rate != None:
        bondType = 'fixedratebond'
    if conversionRatio != None:
        bondType = 'convertiblebond'
    if ((conversionRatio == None) and not(None in [call_schedule,put_schedule])):
        bondType = 'callablebond'

    print(bondType)
    if bondType != None:    
    
        args = {'issue_name':issue_name.strip(),
                'issue_date':issue_date,
                'maturity_date':maturity_date,
                'facevalue':face_value,                      
                'day_count':day_count.strip(),
                'calendar': calendar.strip(),
                'business_convention' : business_convention.strip(),
                'month_end': month_end,
                'settlement_days':int(settlement_days),
                'date_generation' :date_generation.strip(),
                'coupon_frequency' :coupon_frequency.strip(),
                'inArrears' : inArrears}
        
        if mu.args_inspector(args)[0]:
            for arg_name in args:
                try:
                    args[arg_name] = qlMaps.QL[args[arg_name]]
                except:
                    pass
                
            if bondType == 'fixedratebond':
                args['coupon_rates'] = fixed_coupon_rate
                bond = bonds.FixedRateBond(args)
    
            if bondType == 'floatingratebond':
                args['coupon_index'] = floating_coupon_index.getIndex()
                args['coupon_spread'] = floating_coupon_spread
                if cap != None :
                    args['cap'] = [cap]
                else:
                    args['cap'] = []
                if floor != None :
                    args['floor'] = [floor]
                else:
                    args['floor'] = []
                args['fixing'] = fixing
                bond = bonds.FloatingRateBond(args)
                bond.setBlackPricer()
            
            if bondType == 'convertiblebond':
                args['coupon_rates'] = fixed_coupon_rate
                args['conversion_ratio'] = conversionRatio
                args['conversion_price'] = conversionPrice
                args['credit_spread'] = credit_spread
                args['call_schedule'] = call_schedule
                args['put_schedule'] = put_schedule
                args['dividend_schedule'] = dividend_schedule
                bond = bonds.FixedRateConvertibleBond(args)

            if bondType == 'callablebond':
                args['coupon_rates'] = fixed_coupon_rate
                args['call_schedule'] = call_schedule
                args['put_schedule'] = put_schedule
                bond = bonds.FixedRateCallableBond(args)
    return bond
    
def mrigweb_Analytics(assetobject,args):
    resultset = {'Heads' : 'Values'}
    assettype = str(type(assetobject))[8:-2].split(".")[-1]
    #resultset = assettype
    cashflow = {}
    #Asset is Bond
    if assettype in ["FixedRateBond", "FloatingRateBond", "Bond"]:
        discount_curve = args['Discount Curve']
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = assetobject
        bond.valuation(discount_curve)
        resultset.update(bond.getAnalytics())
        
    if assettype in ["FixedRateConvertibleBond"]:
        underlying_spot = args['Underlying Spot']
        discount_curve = args['Discount Curve']
        volatility_curve = args['Volatility Curve']
        dividend_curve = args['Dividend Curve']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = assetobject
        bond.valuation(underlying_spot,
                         discount_curve,
                         volatility_curve,
                         dividend_curve)

        resultset.update(bond.getAnalytics())
    
    if assettype in ["FixedRateCallableBond"]:
        discount_curve = args['Discount Curve']
        mean_reversion = args['Mean Reversion']
        rate_vol = args['Short Rate Vol']
        grid_points = args['Hull White Grid Pts']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        bond = assetobject
        bond.valuation(discount_curve,
                       mean_reversion,
                       rate_vol,
                       int(grid_points))

        resultset.update(bond.getAnalytics())

    if assettype in ["VanillaFixedFLoatSwap"]:
        discount_curve = args['Discount Curve']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        swap = assetobject
        swap.valuation(discount_curve)

        resultset.update(swap.getAnalytics())

    if assettype in ["CapsFloors"]:
        discount_curve= args['Discount Curve']
        volatility_curve = args['Volatility Curve']
        #print(underlying_spot)
#        discount_curve_handle = objectmap[discount_curve_id].getCurveHandle()
        capfloor = assetobject
        capfloor.valuation(discount_curve,
                           volatility_curve)

        resultset.update(capfloor.getAnalytics())

#Cashflow Formatting for Display
    if 'cashflows' in resultset.keys():
        offset=1
        for tup in resultset['cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Cashflow Date'] = 'Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('cashflows')

    if 'Fixed Leg Cashflows' in resultset.keys():
        offset=2
        for tup in resultset['Fixed Leg Cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Fixed Leg Cashflow Date'] = 'Fixed Leg Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('Fixed Leg Cashflows')
    if 'Floating Leg Cashflows' in resultset.keys():
        offset=3
        for tup in resultset['Floating Leg Cashflows']:
            cashflow[tup[0].strftime('%m/%d/%Y')+' '*offset] = tup[1]
        resultset['-----------------'] = '-----------------'
        resultset['Floating Leg Cashflow Date'] = 'Floating Leg Cashflow Amount'
        resultset.update(cashflow)
        resultset.pop('Floating Leg Cashflows')
    
    
    
    #Asset is Option
    if assettype in ["Option", "VanillaEuropeanOption", "VanillaAmericanOption"]:
        underlying_spot = args['Underlying Spot']
        discount_curve = args['Discount Curve']
        volatility_curve = args['Volatility Curve']
        dividend_curve = args['Dividend Curve']
        valuation_method = args['Valuation Method']
        
        option = assetobject
        option.valuation(underlying_spot,
                         discount_curve,
                         volatility_curve,
                         dividend_curve,
                         valuation_method)
        resultset.update(assetobject.getAnalytics())
    return resultset


def mrigweb_FlatDividendYieldCurve(reference_date,
                                 day_count='30-360',
                                 calendar='India',
                                 flat_rate=0,
                                 compounding='Compounded',
                                 compounding_frequency='Annual'):
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'flat_rate' : flat_rate,
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}
    fdyc = None
    if mu.args_inspector(args)[0]:

        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        fdyc = ts.FlatDividendYieldCurve(reference_date,flat_rate)
        fdyc.setupCurve(args)
    return fdyc

def mrigweb_FlatVolatilityCurve(reference_date,
                                 day_count='30-360',
                                 calendar='India',
                                 spot_vols=0,
                                 compounding='Compounded',
                                 compounding_frequency='Annual'):
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'spot_vols' : spot_vols,
            'compounding' : compounding.strip(),
            'compounding_frequency' :compounding_frequency.strip()}

    fvyc = None
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        fvyc = ts.FlatVolatilityCurve(reference_date,spot_vols)
        fvyc.setupCurve(args)
    return fvyc

def mrigweb_ConstantVolatilityCurve(spot_vols):
    args = {'spot_vols' : spot_vols}
    
    cvc = None
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        cvc = ts.ConstantVolatilityCurve(spot_vols)
    return cvc
    
def mrigweb_CapFloorVolatilitySurface(day_count='30-360',
                                 calendar='India',
                                 business_convention='Following',
                                 settlement_days=3,
                                 strikes=None,
                                 expiries=None,
                                 vols=None):
    cfvs = None
    args = {'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'business_convention' : business_convention.strip(),
            'settlement_days':int(settlement_days)}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
        args['strikes'] = strikes
        args['expiries'] = expiries
        args['vols'] = vols        
        cfvs = ts.CapFloorVolatilitySurface(args)
    return cfvs

def mrigweb_Swap(fixed_pay,
                 maturity_date,
                 face_value,
                 fixedleg_day_count='30-360',
                 fixedleg_calendar='India',
                 fixedleg_business_convention='Following',
                 fixedleg_month_end='True',
                 fixedleg_date_generation='Backward',
                 fixedleg_coupon_frequency='Semiannual',
                 fixedleg_coupon_rate=None,
                 floatleg_day_count='30-360',
                 floatleg_calendar='India',
                 floatleg_business_convention='Following',
                 floatleg_month_end='True',
                 floatleg_date_generation='Backward',
                 floatleg_coupon_frequency='Semiannual',
                 floatleg_index=None,
                 floatleg_coupon_spread=0,
                 floatleg_fixing=None):
    
    
    swapType,swap = None, None
    # Check for fixed rate bond
    if fixedleg_coupon_rate != None:
        swapType = 'fixedfloatswap'
    
    if swapType != None:    
    
        fixedleg_args = {'pay_recieve_flag':fixed_pay.strip(),
                'maturity_date':maturity_date,
                'facevalue':face_value,                      
                'day_count':fixedleg_day_count.strip(),
                'calendar': fixedleg_calendar.strip(),
                'business_convention' : fixedleg_business_convention.strip(),
                'month_end': fixedleg_month_end,
                'date_generation' :fixedleg_date_generation.strip(),
                'coupon_frequency' :fixedleg_coupon_frequency.strip()}

        floatleg_args = {'day_count':floatleg_day_count.strip(),
                'calendar': floatleg_calendar.strip(),
                'business_convention' : floatleg_business_convention.strip(),
                'month_end': floatleg_month_end,
                'date_generation' :floatleg_date_generation.strip(),
                'coupon_frequency' :floatleg_coupon_frequency.strip()}  
        
        if (mu.args_inspector(fixedleg_args)[0] and mu.args_inspector(floatleg_args)[0]):
            for arg_name in fixedleg_args:
                try:
                    fixedleg_args[arg_name] = qlMaps.QL[fixedleg_args[arg_name]]
                except:
                    pass

            for arg_name in floatleg_args:
                try:
                    floatleg_args[arg_name] = qlMaps.QL[floatleg_args[arg_name]]
                except:
                    pass
                
                
            if swapType == 'fixedfloatswap':
                fixedleg_args['coupon_rates'] = fixedleg_coupon_rate
                floatleg_args['coupon_index'] = floatleg_index.getIndex()
                floatleg_args['coupon_spread'] = floatleg_coupon_spread
                floatleg_args['fixing'] = floatleg_fixing             
                swap = swaps.VanillaFixedFLoatSwap(fixedleg_args,floatleg_args)
    return swap

def mrigweb_CapFloor(option_name,
                 start_date,
                 maturity_date,
                 cap_or_floor,
                 strike,
                 face_value=1000000,
                 day_count='30-360',
                 calendar='India',
                 business_convention='Following',
                 month_end='True',
                 settlement_days=3,
                 date_generation='Forward',
                 coupon_frequency='Quarterly',
                 floating_coupon_index=None,
                 floating_coupon_spread=0,
                 fixing=None):
    
    capfloor = None
    args = {'option_name':option_name.strip(),
            'start_date':start_date,
            'maturity_date':maturity_date,
            'cap_or_floor': cap_or_floor.strip(),
            'strike':strike,
            'facevalue':face_value,                      
            'day_count':day_count.strip(),
            'calendar': calendar.strip(),
            'business_convention' : business_convention.strip(),
            'month_end': month_end,
            'settlement_days':int(settlement_days),
            'date_generation' :date_generation.strip(),
            'coupon_frequency' :coupon_frequency.strip()}
    
    if mu.args_inspector(args)[0]:
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
    
        args['coupon_index'] = floating_coupon_index.getIndex()
        args['coupon_spread'] = floating_coupon_spread
        args['fixing'] = fixing
        capfloor = capsfloors.CapsFloors(args)
        
    return capfloor

def mrigweb_Option(option_name,
                 underlying_name,
                 maturity_date,
                 option_type,
                 strike,
                 exercise_type,
                 day_count='30-360',
                 calendar='India'):
    
    
    args = {'option_name':option_name.strip(),
            'underlying_name':underlying_name.strip(),
            'maturity_date':maturity_date,
            'option_type':option_type.strip(),
            'strike': strike,                               
            'exercise_type':exercise_type.strip(),
            'day_count':day_count.strip(),
            'calendar':calendar.strip()}
    
    option = None
    if mu.args_inspector(args)[0]:
        
        for arg_name in args:
            try:
                args[arg_name] = qlMaps.QL[args[arg_name]]
            except:
                pass
            
        if exercise_type == 'European':
            option = options.VanillaEuropeanOption(args)

        if exercise_type == 'American':
            option = options.VanillaAmericanOption(args)

    return option
