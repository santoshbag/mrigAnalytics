# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 17:08:19 2019

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import sqlalchemy
import mrigutilities as mu
import mrigstatics
import interface.web.webdashboard as wdb
from mrigweb.mrigwebapp.myhtml import myhtml
import pandas as pd
import json
import time

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
import research.analytics as ra
import io,base64
import stockScreener as ss
import mfScreener as ms1
import mfScreener_new as ms
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
import strategies.marketoptions as mo
import research.screener_TA as sta

from fuzzywuzzy import fuzz
# import mrigplots as mp
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
engine_mrigweb = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
today = datetime.date.today()
# def stock_page_load():
#     starttime = time.monotonic()
#     engine = mu.sql_engine()
#     stocklist = engine.execute("select distinct sm.symbol, sm.stock_name from security_master sm inner join stock_history sh on sm.symbol=sh.symbol where sh.series='EQ'").fetchall()
#
# #    stocklist = list(stocklist)
#     price_list,return_list,risk_list,ratios,oc= "","","","",""
#     price_graph,return_graph,macd_graph,boll_graph = "","","",""
#     stock_desc = ""
#     news = ""
#     NIFTY50 = mu.getNifty50()
#     NIFTY50.append('NIFTY 50')
# #    NIFTY200 = NIFTY200[4:6]
# #    header = ['symbol','stock_description','price_list','return_list','risk_list','ratios','oc',
# #              'news','price_graph','return_graph','macd_graph','boll_graph','slist']
#
# #    stocklist = [['AMBUJACEM','Ambuja Cements Limited']]
#     engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
#     stocklist = [(stk[0],stk[1]) for stk in stocklist]
#     stocklist.append(('NIFTY 50','NIFTY 50'))
# #    stocklist = [('ICICIBANK','ICICIBANK')]
#     stocks_codes = {}
#     for stk in stocklist:
#         sql = "insert into stock_page (symbol,stock_description,price_list,return_list,risk_list,ratios,oc,\
#               news,price_graph,return_graph,macd_graph,boll_graph,slist) values "
#
#     #         stock_code = []
#         symbol = stk[0]
# #        print(symbol)
#         stocks_codes[symbol] = stk[1]
#         sym = ['TECHM','JSWSTEEL','SBIN','HINDUNILVR','UPL','TATAMOTORS','ULTRACEMCO','HDFCBANK','CIPLA','LT','BAJAJFINSV','ONGC','MARUTI','INDUSINDBK','ICICIBANK','GAIL','TITAN','YESBANK','GRASIM','M&M','HINDPETRO']
#      #        stock_code.append(symbol)
#         if symbol in list(set(NIFTY50) - set(sym)):
#             print(symbol)
#             if symbol == 'NIFTY 50':
#                 stkanalytics = wdb.mrigweb_index(symbol)
#             else:
#                 stkanalytics = wdb.mrigweb_stock(symbol)
#             price_list,return_list,risk_list,ratios,oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], stkanalytics[3], stkanalytics[4]
#             price_graph,return_graph,macd_graph,boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], stkanalytics[8]
#             stock_desc = stkanalytics[9]
#             news = stkanalytics[10]
#             print(news)
#             #         fd,oc = fd.to_html(), oc.to_html()
#
#             price_list = myhtml.list_to_html(price_list)
#             return_list = myhtml.list_to_html(return_list)
#             risk_list = myhtml.list_to_html(risk_list)
#
#             if not ratios.empty:
#                 ratios = ratios.reset_index()
#                 ratios_head = list(ratios)
#                 ratios_head.remove("index")
#                 ratios_head.insert(0,"")
#                 ratios = [ratios_head] + ratios.values.tolist()
#                 ratios = myhtml.list_to_html(ratios)
#
#             if not oc.empty:
#                 oc = oc.reset_index()
#                 oc['PUT_Expiry'] = "<a style=\"color\:#f7ed4a;text-decoration\:underline;\" href=\"/option/"+symbol+"\:"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +"\:"+ oc['Strike_Price'].apply(lambda x:str(x))+"\:"+ oc['PUT_LTP'].apply(lambda x:str(x))+"\:PE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
#                 oc['Expiry'] = "<a style=\"color\:#f7ed4a;text-decoration\:underline;\" href=\"/option/"+symbol+"\:"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +"\:"+ oc['Strike_Price'].apply(lambda x:str(x))+"\:"+ oc['CALL_LTP'].apply(lambda x:str(x))+"\:CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
# #                print(oc['PUT_Expiry'].head(2))
# #                oc['PUT_Expiry'] = oc['Expiry'].apply(lambda x:x.replace("CE","PE"))
#                 oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#                 oc = [oc_head] + oc.values.tolist()
#                 oc = myhtml.list_to_html(oc,"small")
#
#         #         stock_code = [symbol,stock_desc,price_list,return_list,risk_list,ratios,oc,news
#         #                       ,price_graph,return_graph,macd_graph,boll_graph,stocklist]
#             sql = sql + " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'), "% (symbol,stock_desc.replace("'","''"),price_list,return_list,risk_list,ratios,oc,json.dumps(news)
#                            ,price_graph,return_graph,macd_graph,boll_graph,"")
#             sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT stock_page_pkey DO UPDATE SET \
#                      stock_description=EXCLUDED.stock_description, \
#                      price_list=EXCLUDED.price_list, \
#                      return_list=EXCLUDED.return_list, \
#                      risk_list=EXCLUDED.risk_list, \
#                      ratios=EXCLUDED.ratios, \
#                      oc=EXCLUDED.oc, \
#                      news=EXCLUDED.news, \
#                      price_graph=EXCLUDED.price_graph, \
#                      return_graph=EXCLUDED.return_graph, \
#                      macd_graph=EXCLUDED.macd_graph, \
#                      boll_graph=EXCLUDED.boll_graph, \
#                      slist=EXCLUDED.slist"
#
#     #    stocks_codes.append(stock_code)
#     #    stocks_codes = pd.DataFrame(stocks_codes,columns=header)
#
#      #   stocks_codes.to_sql('stock_page',engine,if_exists='append',index=False)
#     #    print(sql)
# #            try:
# #            print("a")
#             engine.execute(sqlalchemy.text(sql))
# #            except:
# #                pass
# #    slist = json.dumps(stocks_codes)
# #    slist.replace("'","")
# #    engine.execute("UPDATE stock_page set slist='%s'"%slist)
#     elapsed = time.monotonic() - starttime
#     print("------------------Time Taken for Stock load %s hrs %s mins %s sec-------------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
#
# def ss_page_load():
#     starttime = time.monotonic()
#     engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
#     bm = wdb.mrigweb_bigmoneyzacks()
#     bm_table = bm[0]
#     bm_table = bm_table.reset_index()
#     try:
#         bm_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+bm_table['symbol']+"\">"+bm_table['symbol']+"</a>"
#     except:
#         pass
#     bm_table = [list(bm_table)] + bm_table.values.tolist()
#     bm_table = myhtml.list_to_html(bm_table)
#     bm_graph = bm[1]
#     bm_desc = "Big Money Momentum Strategy"
#
#     sql = "insert into ss_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_graph=EXCLUDED.strategy_graph "
#
#     engine.execute(sql%(bm_desc,bm_table,bm_graph))
#
#     scg = wdb.mrigweb_smallcapgrowth()
#     scg_table = scg[0]
#     scg_table = scg_table.reset_index()
#     try:
#         scg_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+scg_table['symbol']+"\">"+scg_table['symbol']+"</a>"
#     except:
#         pass
#
#     scg_table = [list(scg_table)] + scg_table.values.tolist()
#     scg_table = myhtml.list_to_html(scg_table)
#     scg_graph = scg[1]
#     scg_desc = "Small Cap Growth Stocks"
#
#     sql = "insert into ss_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_graph=EXCLUDED.strategy_graph "
#
#     engine.execute(sql%(scg_desc,scg_table,scg_graph))
#
# #    tafa = wdb.mrigweb_tafa()
# #    tafa_table = tafa[0]
# #    tafa_table = tafa_table.reset_index()
# #    tafa_table = [list(tafa_table)] + tafa_table.values.tolist()
# #    tafa_table = myhtml.list_to_html(tafa_table)
# #    tafa_graph = tafa[1]
# #    tafa_desc = "Technical Analysis Fundamental Analysis Stocks"
#
#     nh = wdb.mrigweb_newhighs()
#     nh_table = nh[0]
#     nh_table = nh_table.reset_index()
#     try:
#         nh_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+nh_table['symbol']+"\">"+nh_table['symbol']+"</a>"
#     except:
#         pass
#     nh_table = [list(nh_table)] + nh_table.values.tolist()
#     nh_table = myhtml.list_to_html(nh_table)
#     nh_graph = nh[1]
#     nh_desc = "New Highs making Stocks"
#     sql = "insert into ss_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_graph=EXCLUDED.strategy_graph "
#
#     engine.execute(sql%(nh_desc,nh_table,nh_graph))
#
#     gi = wdb.mrigweb_growthincome()
#     gi_table = gi[0]
#     gi_table = gi_table.reset_index()
#     try:
#         gi_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+gi_table['symbol']+"\">"+gi_table['symbol']+"</a>"
#     except:
#         pass
#     gi_table = [list(gi_table)] + gi_table.values.tolist()
#     gi_table = myhtml.list_to_html(gi_table)
#     gi_graph = gi[1]
#     gi_desc = "Growth and Income Stocks"
#     sql = "insert into ss_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_graph=EXCLUDED.strategy_graph "
#
#     engine.execute(sql%(gi_desc,gi_table,gi_graph))
#     elapsed = time.monotonic() - starttime
#     print("-----------------Time Taken for Stock Strategy load %s hrs %s mins %s sec-------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
#
# def os_page_load():
#
#     starttime = time.monotonic()
#     engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
#     oc = wdb.mrigweb_covered_call()
# #        price_list,return_list,risk_list,ratios,oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], stkanalytics[3], stkanalytics[4]
# #        price_graph,return_graph,macd_graph,boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], stkanalytics[8]
#     strategy = "Covered Call"
#     strategy_desc = "Covered Call Strategy for NSE Stock Options"
#     #         fd,oc = fd.to_html(), oc.to_html()
#     oc = oc.reset_index()
#     oc['ExpiryDUP'] = oc['Expiry']
#     oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
#     oc['Id'] = ""
#     for i in range(len(oc)):
#         rowdict = oc.iloc[i].to_dict()
#         rowdict['strategyname'] = 'coveredcall'
#         for key in rowdict.keys():
#             rowdict[key] = str(rowdict[key])
#         sessionid = mu.mrigsession_write(rowdict)
#         oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">CC_"+str(i)+"</a>"
#     oc['Expiry'] = oc['ExpiryDUP']
#     oc.drop(['CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty','ExpiryDUP'],axis=1,inplace=True)
#     oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":"+oc['CALL_LTP'].apply(lambda x:str(x))+":CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
#     oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
#     oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
#     oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#     oc = [oc_head] + oc.values.tolist()
#     oc = myhtml.list_to_html(oc)
#     sql = "insert into os_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_name=EXCLUDED.strategy_name"
#
#     engine.execute(sql%(strategy,strategy_desc,oc))
#
#     oc = wdb.mrigweb_bull_put_spread()
#     strategy = "Bull Put Spread"
#     strategy_desc = "Bull Put Spread Strategy for NSE Stock Options"
#     oc = oc.reset_index()
#     oc['ExpiryDUP'] = oc['Expiry']
#     oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
#     oc['Id'] = ""
#     for i in range(len(oc)):
#         rowdict = oc.iloc[i].to_dict()
#         rowdict['strategyname'] = 'bullputspread'
#         for key in rowdict.keys():
#             rowdict[key] = str(rowdict[key])
#         sessionid = mu.mrigsession_write(rowdict)
#         oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">BPS_"+str(i)+"</a>"
#
#     oc['Expiry'] = oc['ExpiryDUP']
#     oc.drop(['PUT_OI','PUT_BidQty','PUT_BidPrice','PUT_AskPrice','PUT_AskQty','ExpiryDUP'],axis=1,inplace=True)
#     oc['Higher_Strike'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Higher_Strike'].apply(lambda x:str(x))+":"+oc['Higher_Strike_LTP'].apply(lambda x:str(x))+":PE\">"+oc['Higher_Strike'].apply(lambda x:str(x))+"</a>"
#     oc['Strike_Price'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":"+oc['PUT_LTP'].apply(lambda x:str(x))+":PE\">"+oc['Strike_Price'].apply(lambda x:str(x))+"</a>"
#     oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
#     oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
#     oc_head = [x.replace("Strike_Price","Lower_Strike").replace("PUT_LTP","Lower_Strike_LTP").replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#     oc = [oc_head] + oc.values.tolist()
#     oc = myhtml.list_to_html(oc)
#
#     sql = "insert into os_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_name=EXCLUDED.strategy_name"
#
#     engine.execute(sql%(strategy,strategy_desc,oc))
#
#     oc = wdb.mrigweb_bear_call_spread()
#     strategy = "Bear Call Spread"
#     strategy_desc = "Bear Call Spread Strategy for NSE Stock Options"
#     oc = oc.reset_index()
#     oc['ExpiryDUP'] = oc['Expiry']
#     oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
#     oc['Id'] = ""
#     for i in range(len(oc)):
#         rowdict = oc.iloc[i].to_dict()
#         rowdict['strategyname'] = 'bearcallspread'
#         for key in rowdict.keys():
#             rowdict[key] = str(rowdict[key])
#         sessionid = mu.mrigsession_write(rowdict)
#         oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">BCS_"+str(i)+"</a>"
#
#     oc['Expiry'] = oc['ExpiryDUP']
#     oc.drop(['CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty','ExpiryDUP'],axis=1,inplace=True)
#     oc['Lower_Strike'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Lower_Strike'].apply(lambda x:str(x))+":"+oc['Lower_Strike_LTP'].apply(lambda x:str(x))+":CE\">"+oc['Lower_Strike'].apply(lambda x:str(x))+"</a>"
#     oc['Strike_Price'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":"+oc['CALL_LTP'].apply(lambda x:str(x))+":CE\">"+oc['Strike_Price'].apply(lambda x:str(x))+"</a>"
#     oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
#     oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
#     oc_head = [x.replace("Strike_Price","Higher_Strike").replace("CALL_LTP","Higher_Strike_LTP").replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#     oc = [oc_head] + oc.values.tolist()
#     oc = myhtml.list_to_html(oc)
#     sql = "insert into os_page values ('%s','%s','%s') \
#            ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
#            strategy_table=EXCLUDED.strategy_table, \
#            strategy_name=EXCLUDED.strategy_name"
#
#     engine.execute(sql%(strategy,strategy_desc,oc))
#     elapsed = time.monotonic() - starttime
#     print("--------Time Taken for Option Strategy load %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))


def market_db_load():
    starttime = time.monotonic()
    print('Market_Graphs : Creating from Scratch')
    graphs = []
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

    print('N50 : Creating Table')
    n50_ta_screen = sta.display_analytics()
    n50_ta_screen_json = n50_ta_screen.to_json(orient='split')
    im.set_items({'n50_ta_screen' : n50_ta_screen_json})

    indices = ["NIFTY 50", "NIFTY BANK", "INDIA VIX", "NIFTY SMALLCAP 100",
               "NIFTY MIDCAP 100", "NIFTY PRIVATE BANK", "NIFTY PSU BANK", "NIFTY IT", "NIFTY AUTO",
               "NIFTY PHARMA", "NIFTY FMCG", "NIFTY FINANCIAL SERVICES", "NIFTY REALTY",
               "NIFTY HEALTHCARE INDEX", "NIFTY CONSUMPTION", "NIFTY INFRASTRUCTURE", "NIFTY COMMODITIES",
               "NIFTY ENERGY", "NIFTY 100", "NIFTY METAL"
               ]

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
    im.set_items({'sector_graph' : str(sector_graph)})

    levels = ra.level_analysis(['NIFTY'])
    level_chart = levels['level_chart']
    pcr = levels['pcr']
    max_pain = levels['max_pain']
    levels = [level_chart,pcr,max_pain]
    levels_json = json.dumps(levels)
    im.set_items({'NIFTY 50|levels_json' : levels_json})
    print('NIFTY 50  Levels Populated')

    levels = ra.level_analysis(['BANKNIFTY'])
    level_chart = levels['level_chart']
    pcr = levels['pcr']
    max_pain = levels['max_pain']
    levels = [level_chart, pcr, max_pain]
    levels_json = json.dumps(levels)
    im.set_items({'BANKNIFTY|levels_json': levels_json})
    print('BANKNIFTY  Levels Populated')

    elapsed = time.monotonic() - starttime
    print("--------Time Taken for Market DashBoard load %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))


def mrigweb_stock_load(symbollist=['NIFTY_100'],tenor='1Y',force=0):
    starttime = time.monotonic()
    load_dates = pd.read_sql('select distinct item,load_date from webpages',engine_mrigweb)
    nifty_100 = engine.execute("select index_members from stock_history where symbol='NIFTY 100' and index_members is not NULL order by date desc limit 1").fetchall()[0][0]
    nifty_100 = nifty_100.strip('][').split(', ')
    nifty_100 = [x[1:-1] for x in nifty_100]

    # symbollist = sorted(mrigstatics.NIFTY_100) if symbollist[0] == 'NIFTY_100' else symbollist
    symbollist = sorted(nifty_100) if symbollist[0] == 'NIFTY_100' else symbollist

    symbols_loaded = []
    for symbol in symbollist:
        load_date = load_dates[load_dates['item'].str.contains(symbol)]['load_date'].values
        # print(load_date)
        if(not(today in load_date ) or (force == 1)):
            stk = stocks.Stock(symbol)
            # stock_desc = stk.stock_name + " | " + stk.industry + " | ISIN: " + stk.isin
            # nifty = stocks.Index('NIFTY 50')
            # price_labels = ['Last Price', 'Open', 'Previous Close', 'Day High', 'Day Low', '52 Week High', '52 Week Low']
            # quotes = []
            # quotes.append(stk.quote['lastPrice']) if 'lastPrice' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['open']) if 'open' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['previousclose']) if 'previousclose' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['dayhigh']) if 'dayhigh' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['daylow']) if 'daylow' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['high52']) if 'high52' in stk.quote.keys() else quotes.append("")
            # quotes.append(stk.quote['low52']) if 'low52' in stk.quote.keys() else quotes.append("")
            # price_list = [price_labels, quotes]

            cum_returns = []
            return_labels = ['1W', '4W', '12W', '24W', '1Y', '3Y']
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
                    return_period = (float(ret_df['daily_log_returns'].sum() / period))
                    cum_returns.append(return_period)
                    return_labels_1.append(return_labels[i])
                    # print(cum_returns)
                    # except:
                #     pass
            return_list = [return_labels_1, cum_returns]
            return_list_json = json.dumps(return_list)
            im.set_items({symbol+'|return_list' : return_list_json})
            print(symbol+'  Return List Populated')

            stk.get_price_vol(tenor)
            dates = list(stk.pricevol_data.index)

            ohlcv = stk.pricevol_data.reset_index()
            price_graph = mg.plotly_candlestick(stk.symbol, ohlcv, [20, 60, 100])

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
            im.set_items({symbol+'|price_graph': price_graph})
            print(symbol+'  Price Graph Populated')


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
            im.set_items({symbol+'|boll_graph': boll_graph})
            print(symbol+'  Boll Graph Populated')


            macd_graph = mg.plotly_tech_indicators(stk.symbol, ohlcv, ['MACD', 'MACDS'])

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
            im.set_items({symbol+'|macd_graph': macd_graph})
            print(symbol+'  MACD Graph Populated')


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
            im.set_items({symbol+'|return_graph': return_graph})
            print(symbol+'  Return Graph Populated')


            risk = stk.get_risk()
            risklabels, risknumbers = [], []
            for key in risk.keys():
                risklabels.append(key)
                risknumbers.append(risk[key])

            risk_list = [risklabels, risknumbers]
            risk_list_json = json.dumps(risk_list)
            im.set_items({symbol+'|risk_list' : risk_list_json})
            print(symbol+'  Risk List Populated')

            #
            # rd = pd.DataFrame()
            #
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
            #
            # optionchain = pd.DataFrame()
            # # optionchain = stk.optionChain()
            #
            stk.get_levels()
            level_chart = stk.level_chart
            # level_chart = base64.b64encode(level_chart.getvalue()).decode('utf-8').replace('\n', '')
            pcr = stk.pcr
            max_pain = stk.max_pain
            levels = [level_chart,pcr,max_pain]
            levels_json = json.dumps(levels)
            im.set_items({symbol+'|levels_json' : levels_json})
            print(symbol+'  Levels Populated')
            symbols_loaded.append((symbol))
            print('# SYMBOLS LOADED  ' + str(len(symbols_loaded)))
            print(symbols_loaded)
        else:
            print('-------SKIPPING-----',symbol,'----AS LOAD DATE----',str(load_date))
    elapsed = time.monotonic() - starttime
    print('# SYMBOLS LOADED  '+str(len(symbols_loaded)))
    print(symbols_loaded)
    print("--------Time Taken for Market DashBoard load %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))


if __name__ == '__main__':
     market_db_load()
     mrigweb_stock_load(force=1)
