# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 17:08:19 2019

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import interface.web.webdashboard as wdb
from mrigweb.mrigwebapp.myhtml import myhtml
import pandas as pd
import json
import time


def stock_page_load():
    starttime = time.monotonic()
    engine = mu.sql_engine()
    stocklist = engine.execute("select distinct sm.symbol, sm.stock_name from security_master sm inner join stock_history sh on sm.symbol=sh.symbol where sh.series='EQ'").fetchall()
#    stocklist = list(stocklist)
    price_list,return_list,risk_list,ratios,oc= "","","","",""
    price_graph,return_graph,macd_graph,boll_graph = "","","",""
    stock_desc = ""
    news = ""

#    header = ['symbol','stock_description','price_list','return_list','risk_list','ratios','oc',
#              'news','price_graph','return_graph','macd_graph','boll_graph','slist']

#    stocklist = [['ICICIBANK','ici']]
    stocks_codes = {}
    sql = "insert into stock_page (symbol,stock_description,price_list,return_list,risk_list,ratios,oc,\
              news,price_graph,return_graph,macd_graph,boll_graph,slist) values "    
    for stk in stocklist:
        
    #         stock_code = []
        symbol = stk[0]
        stocks_codes[symbol] = stk[1]
     #        stock_code.append(symbol)
        if symbol == 'NIFTY 50':
            stkanalytics = wdb.mrigweb_index(symbol)
        else:
            stkanalytics = wdb.mrigweb_stock(symbol)
        price_list,return_list,risk_list,ratios,oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], stkanalytics[3], stkanalytics[4]
        price_graph,return_graph,macd_graph,boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], stkanalytics[8]
        stock_desc = stkanalytics[9]
        news = stkanalytics[10]
        #         fd,oc = fd.to_html(), oc.to_html()
         
        price_list = myhtml.list_to_html(price_list)
        return_list = myhtml.list_to_html(return_list)
        risk_list = myhtml.list_to_html(risk_list)
          
        if not ratios.empty:
            ratios = ratios.reset_index()
            ratios_head = list(ratios)
            ratios_head.remove("index")
            ratios_head.insert(0,"")
            ratios = [ratios_head] + ratios.values.tolist()
            ratios = myhtml.list_to_html(ratios)
        
        if not oc.empty:
            oc = oc.reset_index()
            oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+symbol+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +":"+ oc['Strike_Price'].apply(lambda x:str(x))+":CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
            oc['PUT_Expiry'] = oc['Expiry'].apply(lambda x:x.replace("CE","PE"))
            oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
            oc = [oc_head] + oc.values.tolist()
            oc = myhtml.list_to_html(oc,"small")
        
    #         stock_code = [symbol,stock_desc,price_list,return_list,risk_list,ratios,oc,news
    #                       ,price_graph,return_graph,macd_graph,boll_graph,stocklist]
        sql = sql + " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'), "% (symbol,stock_desc,price_list,return_list,risk_list,ratios,oc,news
                       ,price_graph,return_graph,macd_graph,boll_graph,json.dumps(stocks_codes))
        sql = sql.strip()[:-1] + " ON CONFLICT ON CONSTRAINT stock_page_pkey DO UPDATE SET \
                 stock_description=EXCLUDED.stock_description, \
                 price_list=EXCLUDED.price_list, \
                 return_list=EXCLUDED.return_list, \
                 risk_list=EXCLUDED.risk_list, \
                 ratios=EXCLUDED.ratios, \
                 oc=EXCLUDED.oc, \
                 news=EXCLUDED.news, \
                 price_graph=EXCLUDED.price_graph, \
                 return_graph=EXCLUDED.return_graph, \
                 macd_graph=EXCLUDED.macd_graph, \
                 boll_graph=EXCLUDED.boll_graph, \
                 slist=EXCLUDED.slist"
                 
#    stocks_codes.append(stock_code)
#    stocks_codes = pd.DataFrame(stocks_codes,columns=header)
        engine = mu.sql_engine('MRIGWEB')
 #   stocks_codes.to_sql('stock_page',engine,if_exists='append',index=False)
#    print(sql)
        engine.execute(sql)  
    elapsed = time.monotonic() - starttime
    print("Time Taken for Stock load %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))

def ss_page_load():
    starttime = time.monotonic()
    engine = mu.sql_engine('MRIGWEB')    
    bm = wdb.mrigweb_bigmoneyzacks()
    bm_table = bm[0]
    bm_table = bm_table.reset_index()
    try:
        bm_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+bm_table['symbol']+"\">"+bm_table['symbol']+"</a>"
    except:
        pass
    bm_table = [list(bm_table)] + bm_table.values.tolist()
    bm_table = myhtml.list_to_html(bm_table)
    bm_graph = bm[1]
    bm_desc = "Big Money Momentum Strategy"
    
    sql = "insert into ss_page values ('%s','%s','%s') \
           ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table, \
           strategy_graph=EXCLUDED.strategy_graph "
           
    engine.execute(sql%(bm_desc,bm_table,bm_graph))

    scg = wdb.mrigweb_smallcapgrowth()    
    scg_table = scg[0]
    scg_table = scg_table.reset_index()
    try:
        scg_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+scg_table['symbol']+"\">"+scg_table['symbol']+"</a>"
    except:
        pass

    scg_table = [list(scg_table)] + scg_table.values.tolist()
    scg_table = myhtml.list_to_html(scg_table)
    scg_graph = scg[1]
    scg_desc = "Small Cap Growth Stocks"

    sql = "insert into ss_page values ('%s','%s','%s') \
           ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table, \
           strategy_graph=EXCLUDED.strategy_graph "
           
    engine.execute(sql%(scg_desc,scg_table,scg_graph))

#    tafa = wdb.mrigweb_tafa()
#    tafa_table = tafa[0]
#    tafa_table = tafa_table.reset_index()
#    tafa_table = [list(tafa_table)] + tafa_table.values.tolist()
#    tafa_table = myhtml.list_to_html(tafa_table)
#    tafa_graph = tafa[1]
#    tafa_desc = "Technical Analysis Fundamental Analysis Stocks"

    nh = wdb.mrigweb_newhighs()
    nh_table = nh[0]
    nh_table = nh_table.reset_index()
    try:
        nh_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+nh_table['symbol']+"\">"+nh_table['symbol']+"</a>"
    except:
        pass
    nh_table = [list(nh_table)] + nh_table.values.tolist()
    nh_table = myhtml.list_to_html(nh_table)
    nh_graph = nh[1]
    nh_desc = "New Highs making Stocks"
    sql = "insert into ss_page values ('%s','%s','%s') \
           ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table, \
           strategy_graph=EXCLUDED.strategy_graph "
           
    engine.execute(sql%(nh_desc,nh_table,nh_graph))

    gi = wdb.mrigweb_growthincome()
    gi_table = gi[0]
    gi_table = gi_table.reset_index()
    try:
        gi_table['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+gi_table['symbol']+"\">"+gi_table['symbol']+"</a>"
    except:
        pass
    gi_table = [list(gi_table)] + gi_table.values.tolist()
    gi_table = myhtml.list_to_html(gi_table)
    gi_graph = gi[1]
    gi_desc = "Growth and Income Stocks"
    sql = "insert into ss_page values ('%s','%s','%s') \
           ON CONFLICT ON CONSTRAINT ss_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table, \
           strategy_graph=EXCLUDED.strategy_graph "
           
    engine.execute(sql%(gi_desc,gi_table,gi_graph))
    elapsed = time.monotonic() - starttime
    print("Time Taken for Stock Strategy load %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
    
def os_page_load():

    starttime = time.monotonic()
    engine = mu.sql_engine('MRIGWEB')
    oc = wdb.mrigweb_covered_call()
#        price_list,return_list,risk_list,ratios,oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], stkanalytics[3], stkanalytics[4]
#        price_graph,return_graph,macd_graph,boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], stkanalytics[8]
    strategy_desc = "Covered Call Strategy for NSE Stock Options"
    #         fd,oc = fd.to_html(), oc.to_html()
    oc = oc.reset_index()
    oc['ExpiryDUP'] = oc['Expiry']
    oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
    oc['Id'] = ""
    for i in range(len(oc)):
        rowdict = oc.iloc[i].to_dict()
        rowdict['strategyname'] = 'coveredcall'
        for key in rowdict.keys():
            rowdict[key] = str(rowdict[key])
        sessionid = mu.mrigsession_write(rowdict)
        oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">CC_"+str(i)+"</a>"
    oc['Expiry'] = oc['ExpiryDUP']
    oc.drop(['CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty','ExpiryDUP'],axis=1,inplace=True)
    oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
    oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
    oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
    oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
    oc = [oc_head] + oc.values.tolist() 
    oc = myhtml.list_to_html(oc)
    sql = "insert into os_page values ('%s','%s') \
           ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table "
           
    engine.execute(sql%(strategy_desc,oc))

    oc = wdb.mrigweb_bull_put_spread()

    strategy_desc = "Bull Put Spread Strategy for NSE Stock Options"
    oc = oc.reset_index()
    oc['ExpiryDUP'] = oc['Expiry']
    oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
    oc['Id'] = ""
    for i in range(len(oc)):
        rowdict = oc.iloc[i].to_dict()
        rowdict['strategyname'] = 'bullputspread'
        for key in rowdict.keys():
            rowdict[key] = str(rowdict[key])
        sessionid = mu.mrigsession_write(rowdict)
        oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">BPS_"+str(i)+"</a>"

    oc['Expiry'] = oc['ExpiryDUP']
    oc.drop(['PUT_OI','PUT_BidQty','PUT_BidPrice','PUT_AskPrice','PUT_AskQty','ExpiryDUP'],axis=1,inplace=True)
    oc['Higher_Strike'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Higher_Strike'].apply(lambda x:str(x))+":PE\">"+oc['Higher_Strike'].apply(lambda x:str(x))+"</a>"
    oc['Strike_Price'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":PE\">"+oc['Strike_Price'].apply(lambda x:str(x))+"</a>"
    oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
    oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
    oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
    oc = [oc_head] + oc.values.tolist() 
    oc = myhtml.list_to_html(oc)

    sql = "insert into os_page values ('%s','%s') \
           ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table "
           
    engine.execute(sql%(strategy_desc,oc))

    oc = wdb.mrigweb_bear_call_spread()

    strategy_desc = "Bear Call Spread Strategy for NSE Stock Options"
    oc = oc.reset_index()
    oc['ExpiryDUP'] = oc['Expiry']
    oc['Expiry'] = oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))
    oc['Id'] = ""
    for i in range(len(oc)):
        rowdict = oc.iloc[i].to_dict()
        rowdict['strategyname'] = 'bearcallspread'
        for key in rowdict.keys():
            rowdict[key] = str(rowdict[key])
        sessionid = mu.mrigsession_write(rowdict)
        oc['Id'].iloc[i] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+sessionid+"\">BCS_"+str(i)+"</a>"
    
    oc['Expiry'] = oc['ExpiryDUP']
    oc.drop(['CALL_OI','CALL_BidQty','CALL_BidPrice','CALL_AskPrice','CALL_AskQty','ExpiryDUP'],axis=1,inplace=True)
    oc['Lower_Strike'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Lower_Strike'].apply(lambda x:str(x))+":CE\">"+oc['Lower_Strike'].apply(lambda x:str(x))+"</a>"
    oc['Strike_Price'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+oc['Symbol']+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y'))+":"+ oc['Strike_Price'].apply(lambda x:str(x))+":CE\">"+oc['Strike_Price'].apply(lambda x:str(x))+"</a>"
    oc['Symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+oc['Symbol']+"\">"+oc['Symbol']+"</a>"
    oc = oc.reindex(columns=['Id'] + list(oc.columns[:-1]))
    oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
    oc = [oc_head] + oc.values.tolist() 
    oc = myhtml.list_to_html(oc)
    sql = "insert into os_page values ('%s','%s') \
           ON CONFLICT ON CONSTRAINT os_page_pkey DO UPDATE SET \
           strategy_table=EXCLUDED.strategy_table "
           
    engine.execute(sql%(strategy_desc,oc))
    elapsed = time.monotonic() - starttime
    print("Time Taken for Option Strategy load %s hrs %s mins %s sec" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))
       
        
if __name__ == '__main__':
    stock_page_load()
