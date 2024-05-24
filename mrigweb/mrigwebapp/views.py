import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from django.shortcuts import render
from django.http import request
import nsepy
from mrigwebapp.myhtml import myhtml
import mrigwebapp.forms as fm
import interface.web.webdashboard as wdb
import pandas as pd
import mrigutilities as mu
import mrigstatics
import datetime
import json
import urllib.parse
import portfolios.portfolio_manager as pm
from django.conf import settings
from django.http import HttpResponse, Http404
import strategies.stocks as stocks

# Create your views here.

def home(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    return render(request, "index.html", {'GOOGLE_ADS': GOOGLE_ADS})

def stock(request,symbol='HDFCBANK'):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    sql = "select * from stock_page where symbol='"+symbol+"'"
    stock_page = pd.read_sql(sql,engine)
#    stocklist = list(stocklist)
    price_list,return_list,risk_list,ratios,oc= "","","","",""
    price_graph,return_graph,macd_graph,boll_graph = "","","",""
    stock_desc = ""
    news = ""
    level_chart = ""
    pcr = ""
    max_pain = ""

    engine = mu.sql_engine()
    stocklist = engine.execute("select distinct sm.symbol, sm.stock_name from security_master sm inner join stock_history sh on sm.symbol=sh.symbol where sh.series='EQ'").fetchall()
    slist = "<input style=\"width: 130px; height: 25px;\" list=\"stocks\" name=\"symbol\"><datalist id=\"stocks\">"
    for stk in stocklist:
        if stk[0] != 'symbol':
            if stk[1] != None:
                slist = slist + "<option value=\""+str(stk[0])+" : "+str(stk[1])+"\">"
            else:
                slist = slist + "<option value=\""+str(stk[0])+" : "+str(stk[0])+"\">"
    slist = slist + "</datalist>"
    
    if request.method == "POST":
      #Get the posted form
      stockform = fm.StockForm(request.POST)
      
      if stockform.is_valid():
         symbol = stockform.cleaned_data['symbol']
         symbol = symbol.split(":")[0].strip()
         print(symbol)
         
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    
    if (symbol and symbol != ""): 
        sql = "select * from stock_page where symbol='"+symbol+"'"
        stock_page = pd.read_sql(sql,engine)
        
        if not stock_page.empty:
            price_list = stock_page['price_list'][0]
            return_list = stock_page['return_list'][0]
            risk_list = stock_page['risk_list'][0]
            ratios = stock_page['ratios'][0]
            oc = stock_page['oc'][0]
            price_graph = stock_page['price_graph'][0]
            price_graph = bytes(price_graph)
            price_graph = price_graph.decode('utf-8')
            return_graph = stock_page['return_graph'][0]
            return_graph = bytes(return_graph)
            return_graph = return_graph.decode('utf-8')
            macd_graph = stock_page['macd_graph'][0]
            macd_graph = bytes(macd_graph)
            macd_graph = macd_graph.decode('utf-8')
            boll_graph = stock_page['boll_graph'][0]
            boll_graph = bytes(boll_graph)
            boll_graph = boll_graph.decode('utf-8')
            stock_desc = stock_page['stock_description'][0]
            news = stock_page['news'][0]
            news = json.loads(news)
        else:
            if symbol == 'NIFTY 50':
                stkanalytics = wdb.mrigweb_index(symbol)
            else:
                stkanalytics = wdb.mrigweb_stock(symbol)
            price_list,return_list,risk_list,ratios,oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], stkanalytics[3], stkanalytics[4]
            price_graph,return_graph,macd_graph,boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], stkanalytics[8]
            stock_desc = stkanalytics[9]
            news = stkanalytics[10]
            level_chart = stkanalytics[11]
            pcr = stkanalytics[12]
            max_pain = stkanalytics[13]
            #         fd,oc = fd.to_html(), oc.to_html()
             
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
                oc['PUT_Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+symbol+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +":"+ oc['Strike_Price'].apply(lambda x:str(x))+":"+ oc['PUT_LTP'].apply(lambda x:str(x))+":PE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
                oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+symbol+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +":"+ oc['Strike_Price'].apply(lambda x:str(x))+":"+ oc['CALL_LTP'].apply(lambda x:str(x))+":CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
#                oc['PUT_Expiry'] = oc['Expiry'].apply(lambda x:x.replace("CE","PE"))
                oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
                oc = [oc_head] + oc.values.tolist()
                oc = myhtml.list_to_html(oc,"small")

#     price_labels = ['Last Price','Open','Previous Close','Day High', 'Day Low','52 Week High','52 Week Low']
#     quotes = []
#
#     if symbol == 'NIFTY 50':
#         stk = stocks.Index('NIFTY 50')
#     else:
#         stk = stocks.Stock(symbol)
#     quotes.append(stk.quote['lastPrice']) if 'lastPrice' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['open']) if 'open' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['prev_close']) if 'previousclose' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['dayhigh']) if 'dayhigh' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['daylow']) if 'daylow' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['high52']) if 'high52' in stk.quote.keys() else quotes.append("")
#     quotes.append(stk.quote['low52']) if 'low52' in stk.quote.keys() else quotes.append("")
# #    if len(stk.quote) > 0:
# #        quotes = [stk.quote['lastPrice'],
# #                  stk.quote['open'],
# #                  stk.quote['previousclose'],
# #                  stk.quote['dayhigh'],
# #                  stk.quote['daylow'],
# #                  stk.quote['high52'],
# #                  stk.quote['low52']]
# #    else:
# #        quotes = []
#     price_list = [price_labels,quotes]
    price_list = myhtml.list_to_html(price_list)
            
    return render(request, "stock.html", {"slist":slist,"symbol":symbol,
                                          "stock_desc" : stock_desc,
                                          "price_list":price_list,
                                          "return_list":return_list,
                                          "risk_list":risk_list,
                                          "ratios":ratios,
                                          "oc":oc,
                                          "price_graph":price_graph,
                                          "return_graph":return_graph,
                                          "macd_graph":macd_graph,
                                          "boll_graph":boll_graph,
                                          "news":news,
                                          "level_chart":level_chart,
                                          "pcr":pcr,
                                          "max_pain":max_pain,
                                          'GOOGLE_ADS': GOOGLE_ADS})


def folio(request, template=''):
    # print(kwargs)
    # print('folioid',folioid)
    # print('template',template)
    resultParams = urllib.parse.parse_qs(template)
    template_map = {'eqfo' : 'equity_options_futures.csv',
                    '':'none'}
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    print(request.user.username)
    if (request.method == 'POST') and ('portfolio_file' in request.FILES.keys()):
        myfile = request.FILES['portfolio_file']
        foliocontent = pd.read_csv(myfile)
        foliocontent['account_id'] = request.user.username
        foliocontent['portfolio_currency'] = 'INR'
        foliocontent = pm.add_portfolio(foliocontent)
        print(foliocontent)
        foliocontent_head = list(foliocontent)
        # print(n50_ta_screen['Security'])
        # n50_ta_screen_head.remove("index")
        # n50_ta_screen_head.insert(0, "")
        foliocontent = [foliocontent_head] + foliocontent.values.tolist()
        foliocontent = myhtml.list_to_html(foliocontent)
        # fs = FileSystemStorage()
        # filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)
        return render(request, "folio.html", {
            'foliocontent': foliocontent
        })

    if request.method == 'GET' and template is not None:
        if 'dl_file' in resultParams.keys():
            file = template_map[resultParams['dl_file']]
            print(file)
            file_path = os.path.join(settings.MEDIA_ROOT,'downloads', file)
            print(file_path)
            if os.path.exists(file_path):
                print('file exists')
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="text/csv")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response

    port_list=[]
    pfolio_tbl = pd.DataFrame()
    pfolio_scenario_graph = ""
    if request.user.is_authenticated:
        account = request.user.username
        port_list = pm.portfolio_list(account)
        if 'port_name' in resultParams.keys():
            port_name = resultParams['port_name']
            pfolio = pm.show_portfolio(port_name[0], account)
            pfolio_head = list(pfolio[0])
            pfolio_tbl = [pfolio_head] + pfolio[0].values.tolist()
            pfolio_tbl = myhtml.list_to_html(pfolio_tbl)
            pfolio_scenario_graph = pfolio[1]
            print(pfolio_tbl)


    return render(request, "folio.html", {'port_list':port_list,
                                          'portfolio' : pfolio_tbl,
                                          'pfolio_scenario_graph' : pfolio_scenario_graph,
                                            'GOOGLE_ADS': GOOGLE_ADS})


def market(request, symbol='NIFTY 50'):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])

    result = wdb.market_db()
    market_graphs = result['graphs']
    n50_ta_screen = result['n50_ta_screen']
    # market_graphs1 = result['graphs1']
    sector_graph = result['sector_graph']
    nifty_levels = result['nifty_levels']
    nifty_level_chart = ''
    if len(nifty_levels) > 0:
        nifty_level_chart = nifty_levels[0]
    banknifty_levels = result['banknifty_levels']
    banknifty_level_chart = ''
    if len(banknifty_levels) > 0:
        banknifty_level_chart = banknifty_levels[0]

    if not n50_ta_screen.empty:
        # n50_ta_screen = n50_ta_screen.reset_index()
        n50_ta_screen['Security'] = n50_ta_screen['Security'].apply(lambda x: '<a href="/stock/'+str(x)+'" style="color:aliceblue;">'+str(x)+'</a>')
        n50_ta_screen_head = list(n50_ta_screen)
        print(n50_ta_screen['Security'])
        # n50_ta_screen_head.remove("index")
        # n50_ta_screen_head.insert(0, "")
        n50_ta_screen = [n50_ta_screen_head] + n50_ta_screen.values.tolist()
        n50_ta_screen = myhtml.list_to_html(n50_ta_screen)

    # sql = "select * from stock_page where symbol='" + symbol + "'"
    # stock_page = pd.read_sql(sql, engine)
    # #    stocklist = list(stocklist)
    price_list, return_list, risk_list, ratios, oc = "", "", "", "", ""
    price_graph, return_graph, macd_graph, boll_graph = "", "", "", ""
    stock_desc = ""
    news = ""
    engine = mu.sql_engine()
    stocklist = engine.execute(
        "select distinct sm.symbol, sm.stock_name from security_master sm inner join stock_history sh on sm.symbol=sh.symbol where sh.series='EQ'").fetchall()
    slist = "<input style=\"width: 130px; height: 25px;\" list=\"stocks\" name=\"symbol\"><datalist id=\"stocks\">"
    # print(stocklist)
    for stk in stocklist:
        if stk[0] != 'symbol':
            if stk[1] != None:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[1]) + "\">"
            else:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[0]) + "\">"
    slist = slist + "</datalist>"
    #
    # if request.method == "POST":
    #     # Get the posted form
    #     stockform = fm.StockForm(request.POST)
    #
    #     if stockform.is_valid():
    #         symbol = stockform.cleaned_data['symbol']
    #         symbol = symbol.split(":")[0].strip()
    #         print(symbol)
    #
    # engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    #
    # if (symbol and symbol != ""):
    #     sql = "select * from stock_page where symbol='" + symbol + "'"
    #     stock_page = pd.read_sql(sql, engine)
    #
    #     if not stock_page.empty:
    #         price_list = stock_page['price_list'][0]
    #         return_list = stock_page['return_list'][0]
    #         risk_list = stock_page['risk_list'][0]
    #         ratios = stock_page['ratios'][0]
    #         oc = stock_page['oc'][0]
    #         price_graph = stock_page['price_graph'][0]
    #         price_graph = bytes(price_graph)
    #         price_graph = price_graph.decode('utf-8')
    #         return_graph = stock_page['return_graph'][0]
    #         return_graph = bytes(return_graph)
    #         return_graph = return_graph.decode('utf-8')
    #         macd_graph = stock_page['macd_graph'][0]
    #         macd_graph = bytes(macd_graph)
    #         macd_graph = macd_graph.decode('utf-8')
    #         boll_graph = stock_page['boll_graph'][0]
    #         boll_graph = bytes(boll_graph)
    #         boll_graph = boll_graph.decode('utf-8')
    #         stock_desc = stock_page['stock_description'][0]
    #         news = stock_page['news'][0]
    #         news = json.loads(news)
    #     else:
    #         if symbol == 'NIFTY 50':
    #             stkanalytics = wdb.mrigweb_index(symbol)
    #         else:
    #             stkanalytics = wdb.mrigweb_stock(symbol)
    #         price_list, return_list, risk_list, ratios, oc = stkanalytics[0], stkanalytics[1], stkanalytics[2], \
    #         stkanalytics[3], stkanalytics[4]
    #         price_graph, return_graph, macd_graph, boll_graph = stkanalytics[5], stkanalytics[6], stkanalytics[7], \
    #         stkanalytics[8]
    #         stock_desc = stkanalytics[9]
    #         news = stkanalytics[10]
    #         #         fd,oc = fd.to_html(), oc.to_html()
    #
    #         return_list = myhtml.list_to_html(return_list)
    #         risk_list = myhtml.list_to_html(risk_list)
    #
    #         if not ratios.empty:
    #             ratios = ratios.reset_index()
    #             ratios_head = list(ratios)
    #             ratios_head.remove("index")
    #             ratios_head.insert(0, "")
    #             ratios = [ratios_head] + ratios.values.tolist()
    #             ratios = myhtml.list_to_html(ratios)
    #
    #         if not oc.empty:
    #             oc = oc.reset_index()
    #             oc[
    #                 'PUT_Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/" + symbol + ":" + \
    #                                 oc['Expiry'].apply(lambda x: x.strftime('%d%m%Y')) + ":" + oc['Strike_Price'].apply(
    #                 lambda x: str(x)) + ":" + oc['PUT_LTP'].apply(lambda x: str(x)) + ":PE\">" + oc['Expiry'].apply(
    #                 lambda x: x.strftime('%d-%b-%Y')) + "</a>"
    #             oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/" + symbol + ":" + \
    #                            oc['Expiry'].apply(lambda x: x.strftime('%d%m%Y')) + ":" + oc['Strike_Price'].apply(
    #                 lambda x: str(x)) + ":" + oc['CALL_LTP'].apply(lambda x: str(x)) + ":CE\">" + oc['Expiry'].apply(
    #                 lambda x: x.strftime('%d-%b-%Y')) + "</a>"
    #             #                oc['PUT_Expiry'] = oc['Expiry'].apply(lambda x:x.replace("CE","PE"))
    #             oc_head = [x.replace("CALL_", "").replace("PUT_", "").replace("_", " ") for x in list(oc)]
    #             oc = [oc_head] + oc.values.tolist()
    #             oc = myhtml.list_to_html(oc, "small")
    #
    # price_labels = ['Last Price', 'Open', 'Previous Close', 'Day High', 'Day Low', '52 Week High', '52 Week Low']
    # quotes = []
    #
    # if symbol == 'NIFTY 50':
    #     stk = stocks.Index('NIFTY 50')
    # else:
    #     stk = stocks.Stock(symbol)
    # quotes.append(stk.quote['lastPrice']) if 'lastPrice' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['open']) if 'open' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['previousclose']) if 'previousclose' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['dayhigh']) if 'dayhigh' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['daylow']) if 'daylow' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['high52']) if 'high52' in stk.quote.keys() else quotes.append("")
    # quotes.append(stk.quote['low52']) if 'low52' in stk.quote.keys() else quotes.append("")
    # #    if len(stk.quote) > 0:
    # #        quotes = [stk.quote['lastPrice'],
    # #                  stk.quote['open'],
    # #                  stk.quote['previousclose'],
    # #                  stk.quote['dayhigh'],
    # #                  stk.quote['daylow'],
    # #                  stk.quote['high52'],
    # #                  stk.quote['low52']]
    # #    else:
    # #        quotes = []
    # price_list = [price_labels, quotes]
    # price_list = myhtml.list_to_html(price_list)

    return render(request, "market.html", {"slist":slist,
                                           "nifty_graph": market_graphs[0],
                                           "bnifty_graph": market_graphs[1],
                                           "vix_graph": market_graphs[2],
                                           "usdinr_graph": market_graphs[3],
                                           "crude_graph": market_graphs[4],
                                           "gold_graph": market_graphs[5],
                                           "n50_ta_screen" : n50_ta_screen,
                                           "sector_graph": sector_graph,
                                           "nifty_level_chart": nifty_level_chart,
                                           "banknifty_level_chart" :banknifty_level_chart,
                                           'GOOGLE_ADS': GOOGLE_ADS})


def option_s(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])    
    os_list = ["Covered Call","Bull Put Spread", "Bear Call Spread"]
    strategy_desc = ""
    strategy = None
    oc = pd.DataFrame()
    slist = "<input style=\"width: 130px; height: 25px;\" list=\"os\" name=\"strategy\"><datalist id=\"os\">"
    for stg in os_list:
        slist = slist + "<option value=\""+str(stg)+"\">"
    slist = slist + "</datalist>"
    
    if request.method == "POST":
      #Get the posted form
      strategyform = fm.StrategyForm(request.POST)
      
      if strategyform.is_valid():
         strategy = strategyform.cleaned_data['strategy']
         
    
         sql = "select * from os_page where strategy='"+strategy+"' limit 1"
         os_page = pd.read_sql(sql,engine)
        
         if not os_page.empty:
             strategy_desc = os_page['strategy_name'][0]
             oc = os_page['strategy_table'][0]
           
    return render(request, "os.html", {"slist":slist,
                                       "strategy":strategy,
                                       "strategy_desc" : strategy_desc,
                                       "oc":oc,
                                       'GOOGLE_ADS': GOOGLE_ADS})
def osa(request,strategyid):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    
    strategy = mu.mrigsession_get(strategyid)
    
    analytics = []
    description = ""
    if strategy['strategyname'] == 'coveredcall':
        analytics = wdb.covered_call_analysis(strategy)
        description = "Covered Call Strategy using option:"
    if strategy['strategyname'] == 'bullputspread':
        analytics = wdb.bull_put_spread_analysis(strategy)
        description = "Bull Put Spread Strategy using options:"
    if strategy['strategyname'] == 'bearcallspread':
        analytics = wdb.bear_call_spread_analysis(strategy)
        description = "Bear Call Spread Strategy using options:"
    strategy_desc = analytics[0]
    strategy_specs = analytics[1]
    strategy_risk = analytics[2]
    NPV_graph = analytics[3]
    delta_graph = analytics[4]
    gamma_graph = analytics[5]
    theta_graph = analytics[6]
    results = analytics[7]

    long_option_desc = strategy_desc[0]+" "+strategy_desc[1].strftime('%d-%b-%Y')+ " "+str(strategy_desc[2])
    short_option_desc = ""
    if len(strategy_desc) >3:
        short_option_desc = strategy_desc[0]+" "+strategy_desc[1].strftime('%d-%b-%Y')+ " "+str(strategy_desc[3])
#    
    strategy_specs = myhtml.list_to_html(strategy_specs)
    strategy_risk = myhtml.list_to_html(strategy_risk)
    results = myhtml.dict_to_html(results)
       
    return render(request, "osa.html", {"symbol":strategy_desc[0],
                                        "strategy_desc" : description,
                                       "long_option_desc":long_option_desc,
                                       "short_option_desc":short_option_desc,
                                       "strategy_specs" : strategy_specs,
                                       "strategy_risk" : strategy_risk,
                                       "NPV_graph" : NPV_graph,
                                       "delta_graph" : delta_graph,
                                       "gamma_graph" : gamma_graph,
                                       "theta_graph" : theta_graph,
                                       "results" : results,
                                       'GOOGLE_ADS': GOOGLE_ADS
                                       })


def ss(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    criteria = {}
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    customscreen = ""
    strategyform = ""
    if request.method == "POST":
      #Get the posted form
      print("method is post")
      strategyform = fm.StockStrategyForm(request.POST)

    result = wdb.stock_strategies()
    st_macd_daily = result['st_macd_daily']
    if not st_macd_daily.empty:
        # n50_ta_screen = n50_ta_screen.reset_index()
        st_macd_daily['symbol'] = st_macd_daily['symbol'].apply(lambda x: '<a href="/stock/'+str(x)+'" style="color:aliceblue;">'+str(x)+'</a>')
        st_macd_daily_head = list(st_macd_daily)
        print(st_macd_daily['symbol'])
        # n50_ta_screen_head.remove("index")
        # n50_ta_screen_head.insert(0, "")
        st_macd_daily = [st_macd_daily_head] + st_macd_daily.values.tolist()
        st_macd_daily = myhtml.list_to_html(st_macd_daily)
    # sql = "select * from ss_page "
    # ss_page = pd.read_sql(sql,engine)
    #
    # if not ss_page.empty:
    #     bm_desc = 'Big Money Momentum Strategy'
    #     bm_table = ss_page.loc[ss_page['strategy_name'] == bm_desc]['strategy_table'].values[0]
    #     bm_graph = ss_page.loc[ss_page['strategy_name'] == bm_desc]['strategy_graph'].values[0]
    #     bm_graph = bytes(bm_graph)
    #     bm_graph = bm_graph.decode('utf-8')
    #     scg_desc = 'Small Cap Growth Stocks'
    #     scg_table = ss_page.loc[ss_page['strategy_name'] == scg_desc]['strategy_table'].values[0]
    #     scg_graph = ss_page.loc[ss_page['strategy_name'] == scg_desc]['strategy_graph'].values[0]
    #     scg_graph = bytes(scg_graph)
    #     scg_graph = scg_graph.decode('utf-8')
    #     nh_desc = 'New Highs making Stocks'
    #     nh_table = ss_page.loc[ss_page['strategy_name'] == nh_desc]['strategy_table'].values[0]
    #     nh_graph = ss_page.loc[ss_page['strategy_name'] == nh_desc]['strategy_graph'].values[0]
    #     nh_graph = bytes(nh_graph)
    #     nh_graph = nh_graph.decode('utf-8')
    #     gi_desc = 'Growth and Income Stocks'
    #     gi_table = ss_page.loc[ss_page['strategy_name'] == gi_desc]['strategy_table'].values[0]
    #     gi_graph = ss_page.loc[ss_page['strategy_name'] == gi_desc]['strategy_graph'].values[0]
    #     gi_graph = bytes(gi_graph)
    #     gi_graph = gi_graph.decode('utf-8')

    
    return render(request, "ss.html", {
                                       "st_macd_daily":st_macd_daily,
#                                        "bm_graph":bm_graph,
#                                        "bm_desc":bm_desc,
#                                        "scg_table":scg_table,
#                                        "scg_graph":scg_graph,
#                                        "scg_desc":scg_desc,
# #                                       "tafa_table":tafa_table,
# #                                       "tafa_graph":tafa_graph,
# #                                       "tafa_desc":tafa_desc,
#                                        "nh_table":nh_table,
#                                        "nh_graph":nh_graph,
#                                        "nh_desc":nh_desc,
#                                        "gi_table":gi_table,
#                                        "gi_graph":gi_graph,
#                                        "gi_desc":gi_desc,
                                       'GOOGLE_ADS': GOOGLE_ADS
#                                       "customscreen":customscreen,
#                                       "strategyform":strategyform
                                       })


def screener(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    criteria = {}
#    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    customscreen = ""
    strategyform = ""
    if request.method == "POST":
      #Get the posted form
      print("method is post")
      strategyform = fm.StockStrategyForm(request.POST)
      

      if strategyform.is_valid():
#          strategy = strategyform.cleaned_data['strategy']
#          criteria['marketcap_aggf'] = strategyform.cleaned_data['marketcap_aggf']
          criteria['marketcap_aggp'] = strategyform.cleaned_data['marketcap_aggp']
          criteria['marketcap_aggpnum'] = strategyform.cleaned_data['marketcap_aggpnum']
          criteria['marketcap_op'] = strategyform.cleaned_data['marketcap_op']
          criteria['marketcap_abs_filter'] = strategyform.cleaned_data['marketcap_abs_filter']
#          criteria['marketcap_bm_f'] = strategyform.cleaned_data['marketcap_bm_f']
          criteria['price_aggf'] = strategyform.cleaned_data['price_aggf']
          criteria['price_aggp'] = strategyform.cleaned_data['price_aggp']
          criteria['price_aggpnum'] = strategyform.cleaned_data['price_aggpnum']
          criteria['price_op'] = strategyform.cleaned_data['price_op']
          criteria['price_abs_filter'] = strategyform.cleaned_data['price_abs_filter']
#          criteria['price_bm_f'] = strategyform.cleaned_data['price_bm_f']
          criteria['volume_aggf'] = strategyform.cleaned_data['volume_aggf']
          criteria['volume_aggp'] = strategyform.cleaned_data['volume_aggp']
          criteria['volume_aggpnum'] = strategyform.cleaned_data['volume_aggpnum']
          criteria['volume_op'] = strategyform.cleaned_data['volume_op']
          criteria['volume_abs_filter'] = strategyform.cleaned_data['volume_abs_filter']
#          criteria['volume_bm_f'] = strategyform.cleaned_data['volume_bm_f']
          criteria['pricevolume_aggf'] = strategyform.cleaned_data['pricevolume_aggf']
          criteria['pricevolume_aggp'] = strategyform.cleaned_data['pricevolume_aggp']
          criteria['pricevolume_aggpnum'] = strategyform.cleaned_data['pricevolume_aggpnum']
          criteria['pricevolume_op'] = strategyform.cleaned_data['pricevolume_op']
          criteria['pricevolume_abs_filter'] = strategyform.cleaned_data['pricevolume_abs_filter']
#          criteria['pricevolume_bm_f'] = strategyform.cleaned_data['pricevolume_bm_f']
          criteria['pricereturn_aggf'] = strategyform.cleaned_data['pricereturn_aggf']
          criteria['pricereturn_aggp'] = strategyform.cleaned_data['pricereturn_aggp']
          criteria['pricereturn_aggpnum'] = strategyform.cleaned_data['pricereturn_aggpnum']
          criteria['pricereturn_op'] = strategyform.cleaned_data['pricereturn_op']
          criteria['pricereturn_abs_filter'] = strategyform.cleaned_data['pricereturn_abs_filter']
          criteria['pricereturn_bm_f'] = strategyform.cleaned_data['pricereturn_bm_f']
          criteria['basiceps_aggf'] = strategyform.cleaned_data['basiceps_aggf']
          criteria['basiceps_aggp'] = strategyform.cleaned_data['basiceps_aggp']
          criteria['basiceps_aggpnum'] = strategyform.cleaned_data['basiceps_aggpnum']
          criteria['basiceps_op'] = strategyform.cleaned_data['basiceps_op']
          criteria['basiceps_abs_filter'] = strategyform.cleaned_data['basiceps_abs_filter']
          criteria['basiceps_bm_f'] = strategyform.cleaned_data['basiceps_bm_f']
          criteria['dividendyield_aggf'] = strategyform.cleaned_data['dividendyield_aggf']
          criteria['dividendyield_aggp'] = strategyform.cleaned_data['dividendyield_aggp']
          criteria['dividendyield_aggpnum'] = strategyform.cleaned_data['dividendyield_aggpnum']
          criteria['dividendyield_op'] = strategyform.cleaned_data['dividendyield_op']
          criteria['dividendyield_abs_filter'] = strategyform.cleaned_data['dividendyield_abs_filter']
          criteria['dividendyield_bm_f'] = strategyform.cleaned_data['dividendyield_bm_f']
          criteria['pe_aggf'] = strategyform.cleaned_data['pe_aggf']
          criteria['pe_aggp'] = strategyform.cleaned_data['pe_aggp']
          criteria['pe_aggpnum'] = strategyform.cleaned_data['pe_aggpnum']
          criteria['pe_op'] = strategyform.cleaned_data['pe_op']
          criteria['pe_abs_filter'] = strategyform.cleaned_data['pe_abs_filter']
          criteria['pe_bm_f'] = strategyform.cleaned_data['pe_bm_f']
          criteria['ps_aggf'] = strategyform.cleaned_data['ps_aggf']
          criteria['ps_aggp'] = strategyform.cleaned_data['ps_aggp']
          criteria['ps_aggpnum'] = strategyform.cleaned_data['ps_aggpnum']
          criteria['ps_op'] = strategyform.cleaned_data['ps_op']
          criteria['ps_abs_filter'] = strategyform.cleaned_data['ps_abs_filter']
          criteria['ps_bm_f'] = strategyform.cleaned_data['ps_bm_f']
          criteria['pb_aggf'] = strategyform.cleaned_data['pb_aggf']
          criteria['pb_aggp'] = strategyform.cleaned_data['pb_aggp']
          criteria['pb_aggpnum'] = strategyform.cleaned_data['pb_aggpnum']
          criteria['pb_op'] = strategyform.cleaned_data['pb_op']
          criteria['pb_abs_filter'] = strategyform.cleaned_data['pb_abs_filter']
          criteria['pb_bm_f'] = strategyform.cleaned_data['pb_bm_f']
          criteria['peg_aggf'] = strategyform.cleaned_data['peg_aggf']
          criteria['peg_aggp'] = strategyform.cleaned_data['peg_aggp']
          criteria['peg_aggpnum'] = strategyform.cleaned_data['peg_aggpnum']
          criteria['peg_op'] = strategyform.cleaned_data['peg_op']
          criteria['peg_abs_filter'] = strategyform.cleaned_data['peg_abs_filter']
          criteria['peg_bm_f'] = strategyform.cleaned_data['peg_bm_f']
          criteria['roe_aggf'] = strategyform.cleaned_data['roe_aggf']
          criteria['roe_aggp'] = strategyform.cleaned_data['roe_aggp']
          criteria['roe_aggpnum'] = strategyform.cleaned_data['roe_aggpnum']
          criteria['roe_op'] = strategyform.cleaned_data['roe_op']
          criteria['roe_abs_filter'] = strategyform.cleaned_data['roe_abs_filter']
          criteria['roe_bm_f'] = strategyform.cleaned_data['roe_bm_f']
          criteria['roa_aggf'] = strategyform.cleaned_data['roa_aggf']
          criteria['roa_aggp'] = strategyform.cleaned_data['roa_aggp']
          criteria['roa_aggpnum'] = strategyform.cleaned_data['roa_aggpnum']
          criteria['roa_op'] = strategyform.cleaned_data['roa_op']
          criteria['roa_abs_filter'] = strategyform.cleaned_data['roa_abs_filter']
          criteria['roa_bm_f'] = strategyform.cleaned_data['roa_bm_f']
          criteria['netprofitmargin_aggf'] = strategyform.cleaned_data['netprofitmargin_aggf']
          criteria['netprofitmargin_aggp'] = strategyform.cleaned_data['netprofitmargin_aggp']
          criteria['netprofitmargin_aggpnum'] = strategyform.cleaned_data['netprofitmargin_aggpnum']
          criteria['netprofitmargin_op'] = strategyform.cleaned_data['netprofitmargin_op']
          criteria['netprofitmargin_abs_filter'] = strategyform.cleaned_data['netprofitmargin_abs_filter']
          criteria['netprofitmargin_bm_f'] = strategyform.cleaned_data['netprofitmargin_bm_f']
          criteria['operatingprofitmargin_aggf'] = strategyform.cleaned_data['operatingprofitmargin_aggf']
          criteria['operatingprofitmargin_aggp'] = strategyform.cleaned_data['operatingprofitmargin_aggp']
          criteria['operatingprofitmargin_aggpnum'] = strategyform.cleaned_data['operatingprofitmargin_aggpnum']
          criteria['operatingprofitmargin_op'] = strategyform.cleaned_data['operatingprofitmargin_op']
          criteria['operatingprofitmargin_abs_filter'] = strategyform.cleaned_data['operatingprofitmargin_abs_filter']
          criteria['operatingprofitmargin_bm_f'] = strategyform.cleaned_data['operatingprofitmargin_bm_f']
          criteria['currentratio_aggf'] = strategyform.cleaned_data['currentratio_aggf']
          criteria['currentratio_aggp'] = strategyform.cleaned_data['currentratio_aggp']
          criteria['currentratio_aggpnum'] = strategyform.cleaned_data['currentratio_aggpnum']
          criteria['currentratio_op'] = strategyform.cleaned_data['currentratio_op']
          criteria['currentratio_abs_filter'] = strategyform.cleaned_data['currentratio_abs_filter']
          criteria['currentratio_bm_f'] = strategyform.cleaned_data['currentratio_bm_f']
          criteria['quickratio_aggf'] = strategyform.cleaned_data['quickratio_aggf']
          criteria['quickratio_aggp'] = strategyform.cleaned_data['quickratio_aggp']
          criteria['quickratio_aggpnum'] = strategyform.cleaned_data['quickratio_aggpnum']
          criteria['quickratio_op'] = strategyform.cleaned_data['quickratio_op']
          criteria['quickratio_abs_filter'] = strategyform.cleaned_data['quickratio_abs_filter']
          criteria['quickratio_bm_f'] = strategyform.cleaned_data['quickratio_bm_f']
          criteria['debtequity_aggf'] = strategyform.cleaned_data['debtequity_aggf']
          criteria['debtequity_aggp'] = strategyform.cleaned_data['debtequity_aggp']
          criteria['debtequity_aggpnum'] = strategyform.cleaned_data['debtequity_aggpnum']
          criteria['debtequity_op'] = strategyform.cleaned_data['debtequity_op']
          criteria['debtequity_abs_filter'] = strategyform.cleaned_data['debtequity_abs_filter']
          criteria['debtequity_bm_f'] = strategyform.cleaned_data['debtequity_bm_f']
          criteria['assetturnover_aggf'] = strategyform.cleaned_data['assetturnover_aggf']
          criteria['assetturnover_aggp'] = strategyform.cleaned_data['assetturnover_aggp']
          criteria['assetturnover_aggpnum'] = strategyform.cleaned_data['assetturnover_aggpnum']
          criteria['assetturnover_op'] = strategyform.cleaned_data['assetturnover_op']
          criteria['assetturnover_abs_filter'] = strategyform.cleaned_data['assetturnover_abs_filter']
          criteria['assetturnover_bm_f'] = strategyform.cleaned_data['assetturnover_bm_f']
          criteria['inventoryturnover_aggf'] = strategyform.cleaned_data['inventoryturnover_aggf']
          criteria['inventoryturnover_aggp'] = strategyform.cleaned_data['inventoryturnover_aggp']
          criteria['inventoryturnover_aggpnum'] = strategyform.cleaned_data['inventoryturnover_aggpnum']
          criteria['inventoryturnover_op'] = strategyform.cleaned_data['inventoryturnover_op']
          criteria['inventoryturnover_abs_filter'] = strategyform.cleaned_data['inventoryturnover_abs_filter']
          criteria['inventoryturnover_bm_f'] = strategyform.cleaned_data['inventoryturnover_bm_f']
          criteria['volatility_aggf'] = strategyform.cleaned_data['volatility_aggf']
          criteria['volatility_aggp'] = strategyform.cleaned_data['volatility_aggp']
          criteria['volatility_aggpnum'] = strategyform.cleaned_data['volatility_aggpnum']
          criteria['volatility_op'] = strategyform.cleaned_data['volatility_op']
          criteria['volatility_abs_filter'] = strategyform.cleaned_data['volatility_abs_filter']
          criteria['volatility_bm_f'] = strategyform.cleaned_data['volatility_bm_f']
          criteria['beta_aggf'] = strategyform.cleaned_data['beta_aggf']
          criteria['beta_aggp'] = strategyform.cleaned_data['beta_aggp']
          criteria['beta_aggpnum'] = strategyform.cleaned_data['beta_aggpnum']
          criteria['beta_op'] = strategyform.cleaned_data['beta_op']
          criteria['beta_abs_filter'] = strategyform.cleaned_data['beta_abs_filter']
          criteria['beta_bm_f'] = strategyform.cleaned_data['beta_bm_f']
          criteria['sharpe_aggf'] = strategyform.cleaned_data['sharpe_aggf']
          criteria['sharpe_aggp'] = strategyform.cleaned_data['sharpe_aggp']
          criteria['sharpe_aggpnum'] = strategyform.cleaned_data['sharpe_aggpnum']
          criteria['sharpe_op'] = strategyform.cleaned_data['sharpe_op']
          criteria['sharpe_abs_filter'] = strategyform.cleaned_data['sharpe_abs_filter']
          criteria['sharpe_bm_f'] = strategyform.cleaned_data['sharpe_bm_f']


          cs = wdb.mrigweb_custom_screener(criteria)
          if not cs.empty:
              cs = cs.reset_index()
              cs['symbol'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+cs['symbol']+"\">"+cs['symbol']+"</a>"
              customscreen = [[str(x).replace("_", " ").capitalize() for x in list(cs)]] + cs.values.tolist()
              customscreen = myhtml.list_to_html(customscreen)
      else:
          print(strategyform.errors)

#    sql = "select * from ss_page "
#    ss_page = pd.read_sql(sql,engine)
#    
#    if not ss_page.empty:
#        bm_desc = ss_page['strategy_name'][0]
#        bm_table = ss_page['strategy_table'][0]
#        bm_graph = ss_page['strategy_graph'][0]
#        bm_graph = bytes(bm_graph)
#        bm_graph = bm_graph.decode('utf-8')
#        scg_desc = ss_page['strategy_name'][1]
#        scg_table = ss_page['strategy_table'][1]
#        scg_graph = ss_page['strategy_graph'][1]
#        scg_graph = bytes(scg_graph)
#        scg_graph = scg_graph.decode('utf-8')
#        nh_desc = ss_page['strategy_name'][2]
#        nh_table = ss_page['strategy_table'][2]
#        nh_graph = ss_page['strategy_graph'][2]
#        nh_graph = bytes(nh_graph)
#        nh_graph = nh_graph.decode('utf-8')
#        gi_desc = ss_page['strategy_name'][3]
#        gi_table = ss_page['strategy_table'][3]
#        gi_graph = ss_page['strategy_graph'][3]
#        gi_graph = bytes(gi_graph)
#        gi_graph = gi_graph.decode('utf-8')
#
    
    return render(request, "screener.html", {
#                                       "bm_table":bm_table,
#                                       "bm_graph":bm_graph,
#                                       "bm_desc":bm_desc,
#                                       "scg_table":scg_table,
#                                       "scg_graph":scg_graph,
#                                       "scg_desc":scg_desc,
##                                       "tafa_table":tafa_table,
##                                       "tafa_graph":tafa_graph,
##                                       "tafa_desc":tafa_desc,
#                                       "nh_table":nh_table,
#                                       "nh_graph":nh_graph,
#                                       "nh_desc":nh_desc,
#                                       "gi_table":gi_table,
#                                       "gi_graph":gi_graph,
#                                       "gi_desc":gi_desc,
                                       "customscreen":customscreen,
                                       "strategyform":strategyform,
                                       'GOOGLE_ADS': GOOGLE_ADS
                                       })
    

def option(request,opid):
    
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    """

    engine = mu.sql_engine()
    stocklist = engine.execute("select symbol, stock_name from security_master").fetchall()

    slist = "<input list=\"stocks\" name=\"symbol\"><datalist id=\"stocks\">"
    for stk in stocklist:
        slist = slist + "<option value=\""+str(stk[0])+"\">"
    slist = slist + "</datalist>"

    slist = "<input list=\"expirydates\" name=\"expiry\"><datalist id=\"expirydates\">"
    for dates in mu.get_futures_expiry(datetime.date.today(),datetime.date.today()):
        slist = slist + "<option value=\""+dates.strftime('%d%m%Y')+"\">"
    slist = slist + "</datalist>"
    slist = "<input list=\"strikes\" name=\"strike\"><datalist id=\"strikes\">"
    for strikes in mu.getStrikes():
        slist = slist + "<option value=\""+str(stk[0])+"\">"
    slist = slist + "</datalist><input type=\"submit\">"
    slist = "<input list=\"types\" name=\"callput\"><datalist id=\"types\">"
    slist = slist + "<option value=\"CE\"/><option value=\"PE\"/>\""
    slist = slist + "<input type=\"submit\">"
   
    """
    option_desc = ""
    contract_specs = []
    oh = pd.DataFrame()
    price_graph = ""
    results = {}
    NPV_graph = ""
    delta_graph = ""
    gamma_graph = ""
    theta_graph = ""
    
    if opid:
        params = {}
        keyval = str(opid).split(":")
        params['symbol']= keyval[0]
        params['expiry']= datetime.datetime.strptime(keyval[1],'%d%m%Y').date()
        params['strike']= float(keyval[2])
        params['ltp'] = -1
        try:
            params['ltp']= float(keyval[3])
        except:
            pass
        params['option_type']= keyval[4]
        option_desc = params['symbol']+" "+params['expiry'].strftime('%b')+ " "+keyval[2] + " "+ keyval[4]
        
        op = wdb.mrigweb_options(params)
        contract_specs = op[0]
        oh = op[1]
        price_graph = op[2]
        results = op[3]
        NPV_graph = op[4]
        delta_graph = op[5]
        gamma_graph = op[6]
        theta_graph = op[7]
        oi_graph = op[8]
    
    contract_specs = myhtml.list_to_html(contract_specs)
    oh = oh.reset_index()
    oh = [list(oh)] + oh.values.tolist()
    oh = myhtml.list_to_html(oh)
    results = [[str(key).capitalize().replace("_"," ") for key in results.keys()],[results[key] for key in results.keys()]]
    results = myhtml.list_to_html(results)

    return render(request, "option.html", {"option_desc":option_desc,
                                           "oh":oh,
                                           "contract_specs":contract_specs,
                                           "price_graph":price_graph,
                                           "results":results,
                                           "NPV_graph":NPV_graph,
                                           "delta_graph":delta_graph,
                                           "gamma_graph":gamma_graph,
                                           "theta_graph":theta_graph,
                                           "oi_graph":oi_graph,
                                           'GOOGLE_ADS': GOOGLE_ADS})


def news(request,newsid=None):
    
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    news = wdb.mrigweb_news(newsid)
    
#    news_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ").capitalize() for x in list(news)]
#    news = [news_head] + news.values.tolist()
#    news = myhtml.list_to_html(news)
#    oc = "<img border=\"0\" src=\"{% static 'assets/images/pnl_icon.png' %}\" width=\"10\" height=\"10\"/>"
#    newstype = news[0]
#    newsdate = news[1]
#    newstitle = news[2]
#    newsdesc = news[3]


    return render(request, "news.html", {"news":news,'GOOGLE_ADS': GOOGLE_ADS})    

def ia(request):
    return render(request, "ia.html")

def ra(request):
    return render(request, "ra.html")

def softs(request):
    return render(request, "softs.html")

def ds(request):
    return render(request, "ds.html")

def about(request):
    return render(request, "about.html")

def rates(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    sz_params = {}
    ff_params = {}
    
    SZYC_INR = wdb.mrigweb_szc_rates()
    SZYC_USD = wdb.mrigweb_szc_rates('USD')
    SZYC_GBP = wdb.mrigweb_szc_rates('GBP')
    LIBOR_3M_INR = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=SZYC_INR[0])
    LIBOR_6M_INR = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=SZYC_INR[0])
    LIBOR_3M_USD = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD', yieldcurvehandle=SZYC_USD[0])
    LIBOR_6M_USD = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M', yieldcurvehandle=SZYC_USD[0])
    LIBOR_3M_GBP = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M', yieldcurvehandle=SZYC_GBP[0])
    LIBOR_6M_GBP = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M', yieldcurvehandle=SZYC_GBP[0])

    szyc = wdb.mrigweb_szc_rates()
    ffyc = wdb.mrigweb_ff_rates()
#    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    ffyc_graph = wdb.mrigweb_ratePlot(ffyc,['Flat','Flat_shifted'])
    szyc_graph = wdb.mrigweb_ratePlot(szyc,['INR','INR_shifted'])
    
    if request.method == "POST":
      #Get the posted form
      reference_date = datetime.date.today()
      print("method is post")
      if 'szc_form' in request.POST:
#          print("szc clicked ------")
          rateform = fm.SZC_InterestRateForm(request.POST)
          if rateform.is_valid():
              print("----szc form valid----")
              sz_params['curve_currency'] = rateform.cleaned_data['szc_currency']
              sz_params['day_count'] = rateform.cleaned_data['szc_daycount']
              sz_params['calendar'] = rateform.cleaned_data['szc_calendar']
              sz_params['compounding'] = rateform.cleaned_data['szc_compounding']
              sz_params['compounding_frequency'] = rateform.cleaned_data['szc_frequency']    
              sz_params['interpolation'] = rateform.cleaned_data['szc_interpolation']    
              sz_params['shiftparameter'] = rateform.cleaned_data['szc_parallelshift']   
              print(sz_params)
              szyc = wdb.mrigweb_szc_rates(sz_params['curve_currency'],reference_date,sz_params)
#              szyc_graph = szyc[0]
              szyc_graph = wdb.mrigweb_ratePlot(szyc,['INR','INR_shifted'])
          
      if 'ff_form' in request.POST:
          rateform = fm.FF_InterestRateForm(request.POST)
          if rateform.is_valid():
              print("----ff form valid----")
              ff_params['curvename'] = rateform.cleaned_data['ff_curvename']
              ff_params['currency'] = rateform.cleaned_data['ff_currency']
              ff_params['day_count'] = rateform.cleaned_data['ff_daycount']
              ff_params['calendar'] = rateform.cleaned_data['ff_calendar']
              ff_params['compounding'] = rateform.cleaned_data['ff_compounding']
              ff_params['compounding_frequency'] = rateform.cleaned_data['ff_frequency']    
              ff_params['flat_rate'] = rateform.cleaned_data['ff_flatrate']    
              ff_params['shiftparameter'] = rateform.cleaned_data['ff_parallelshift']   
              print(ff_params)
          
              ffyc = wdb.mrigweb_ff_rates(reference_date,ff_params)
              ffyc_graph = wdb.mrigweb_ratePlot(ffyc,['Flat','Flat_shifted'])
    
    return render(request, "ra_rates.html" , {'ffyc_graph':ffyc_graph,
                                              'szyc_graph':szyc_graph,
                                              'GOOGLE_ADS': GOOGLE_ADS
                                                })

def bonds(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    objectmap = {}
    objectmap['None'] = None
    objectmap['SZYC_INR'] = wdb.mrigweb_szc_rates()
    objectmap['SZYC_USD'] = wdb.mrigweb_szc_rates('USD')
    objectmap['SZYC_GBP'] = wdb.mrigweb_szc_rates('GBP')
    objectmap['LIBOR_3M_INR'] = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_6M_INR'] = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_3M_USD'] = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_6M_USD'] = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_3M_GBP'] = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M', yieldcurvehandle=objectmap['SZYC_GBP'][0])
    objectmap['LIBOR_6M_GBP'] = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M', yieldcurvehandle=objectmap['SZYC_GBP'][0])
    
    resultset = "" 
    face_value=100
    day_count='30-360'
    calendar='India'
    business_convention='Following'
    month_end='True'
    settlement_days=3
    date_generation='Backward'
    coupon_frequency='Semiannual'
    fixed_coupon_rate=None
    floating_coupon_index=None
    floating_coupon_spread=0
    inArrears=True
    cap=None
    floor=None
    fixing=None
    conversionRatio=None
    conversionPrice=None
    credit_spread=None
    call_date_1 = None
    call_date_2 = None
    call_date_3 = None
    call_date_4 = None
    call_date_5 = None
    put_date_1 = None
    put_date_2 = None
    put_date_3 = None
    put_date_4 = None
    put_date_5 = None
    
    call_schedule=None
    call_schedule_date = []
    call_schedule_price = []
    put_schedule=None
    put_schedule_date = []
    put_schedule_price = []
    dividend_schedule=None    

    if request.method == "POST":
      #Get the posted form
      reference_date = datetime.date.today()
      print("bond method is post")
      if 'bond_form' in request.POST:
          bondform = fm.BondForm(request.POST)
          if bondform.is_valid():
              print("----bond form valid----")
              issue_name = bondform.cleaned_data['bondsname']             
              issue_date = bondform.cleaned_data['issue_date']
              issue_date = datetime.datetime.strptime(issue_date,'%Y-%m-%d').date()
              maturity_date = bondform.cleaned_data['maturity_date']
              maturity_date = datetime.datetime.strptime(maturity_date,'%Y-%m-%d').date()
              face_value = float(bondform.cleaned_data['facevalue'])
              day_count= bondform.cleaned_data['daycount']
              calendar = bondform.cleaned_data['calendar']
              currency = bondform.cleaned_data['currency']
              business_convention = bondform.cleaned_data['business_convention']
              month_end = bool(bondform.cleaned_data['month_end'])
              settlement_days  = float(bondform.cleaned_data['settlement_days'])
              date_generation  = bondform.cleaned_data['date_generation']
              coupon_frequency  = bondform.cleaned_data['coupon_frequency']
              fixed_coupon_rate  = float(bondform.cleaned_data['fixed_coupon_rate'])
              floating_coupon_index  = bondform.cleaned_data['floating_coupon_index']
              floating_coupon_index = objectmap[floating_coupon_index]
              try:
                  floating_coupon_spread  = float(bondform.cleaned_data['floating_coupon_spread'])
              except:
                  pass
              inArrears  = bool(bondform.cleaned_data['inarrears'])
              try:
                  cap  = float(bondform.cleaned_data['cap'])
              except:
                  pass
              try:
                  floor  = float(bondform.cleaned_data['floor'])
              except:
                  pass
              try:
                  fixing  = float(bondform.cleaned_data['last_libor'])
              except:
                  pass
              try:
                  conversionRatio  = float(bondform.cleaned_data['conversion_ratio'])
              except:
                  pass
              try:
                  conversionPrice  = float(bondform.cleaned_data['conversion_price'])
              except:
                  pass
              try:
                  credit_spread  = float(bondform.cleaned_data['credit_spread'])
              except:
                  pass
              call_date_1 =  bondform.cleaned_data['call_date_1']
              call_price_1 =  bondform.cleaned_data['call_price_1']
              try:
                  call_date_1 = datetime.datetime.strptime(call_date_1,'%Y-%m-%d').date()
                  call_schedule_date.append(call_date_1)
                  call_schedule_price.append(float(call_price_1))
              except:
                  pass
              call_date_2 =  bondform.cleaned_data['call_date_2']
              call_price_2 =  bondform.cleaned_data['call_price_2']
              try:
                  call_date_2 = datetime.datetime.strptime(call_date_2,'%Y-%m-%d').date()
                  call_schedule_date.append(call_date_2)
                  call_schedule_price.append(float(call_price_2))
              except:
                  pass
              call_date_3 =  bondform.cleaned_data['call_date_3']
              call_price_3 =  bondform.cleaned_data['call_price_3']
              try:
                  call_date_3 = datetime.datetime.strptime(call_date_3,'%Y-%m-%d').date()
                  call_schedule_date.append(call_date_3)
                  call_schedule_price.append(float(call_price_3))
              except:
                  pass
              call_date_4 =  bondform.cleaned_data['call_date_4']
              call_price_4 =  bondform.cleaned_data['call_price_4']
              try:
                  call_date_4 = datetime.datetime.strptime(call_date_4,'%Y-%m-%d').date()
                  call_schedule_date.append(call_date_4)
                  call_schedule_price.append(float(call_price_4))
              except:
                  pass
              call_date_5 =  bondform.cleaned_data['call_date_5']
              call_price_5 =  bondform.cleaned_data['call_price_5']
              try:
                  call_date_5 = datetime.datetime.strptime(call_date_5,'%Y-%m-%d').date()
                  call_schedule_date.append(call_date_5)
                  call_schedule_price.append(float(call_price_5))
              except:
                  pass
              
              if len(call_schedule_date) > 0:
                  call_schedule = [call_schedule_date,call_schedule_price]

              put_date_1 =  bondform.cleaned_data['put_date_1']
              put_price_1 =  bondform.cleaned_data['put_price_1']
              try:
                  put_date_1 = datetime.datetime.strptime(put_date_1,'%Y-%m-%d').date()
                  put_schedule_date.append(put_date_1)
                  put_schedule_price.append(float(put_price_1))
              except:
                  pass
              put_date_2 =  bondform.cleaned_data['put_date_2']
              put_price_2 =  bondform.cleaned_data['put_price_2']
              try:
                  put_date_2 = datetime.datetime.strptime(put_date_2,'%Y-%m-%d').date()
                  put_schedule_date.append(put_date_2)
                  put_schedule_price.append(float(put_price_2))
              except:
                  pass
              put_date_3 =  bondform.cleaned_data['put_date_3']
              put_price_3 =  bondform.cleaned_data['put_price_3']
              try:
                  put_date_3 = datetime.datetime.strptime(put_date_3,'%Y-%m-%d').date()
                  put_schedule_date.append(put_date_3)
                  put_schedule_price.append(float(put_price_3))
              except:
                  pass
              put_date_4 =  bondform.cleaned_data['put_date_4']
              put_price_4 =  bondform.cleaned_data['put_price_4']
              try:
                  put_date_4 = datetime.datetime.strptime(put_date_4,'%Y-%m-%d').date()
                  put_schedule_date.append(put_date_4)
                  put_schedule_price.append(float(put_price_4))
              except:
                  pass
              put_date_5 =  bondform.cleaned_data['put_date_5']
              put_price_5 =  bondform.cleaned_data['put_price_5']
              try:
                  put_date_5 = datetime.datetime.strptime(put_date_5,'%Y-%m-%d').date()
                  put_schedule_date.append(put_date_5)
                  put_schedule_price.append(float(put_price_5))
              except:
                  pass
              
              if len(put_schedule_date) > 0:
                  put_schedule = [put_schedule_date,put_schedule_price]


#Valuation Parameters
              discount_curve  = bondform.cleaned_data['discount_curve']
              discount_curve = objectmap[discount_curve][0]
              volatility_curve  = float(bondform.cleaned_data['volatility_curve'])
              volatility_curve = wdb.mrigweb_ConstantVolatilityCurve(volatility_curve)
              dividend_curve  = float(bondform.cleaned_data['dividend_curve'])
              dividend_curve = wdb.mrigweb_FlatDividendYieldCurve(reference_date,flat_rate=dividend_curve)
              underlying_spot  = float(bondform.cleaned_data['underlying_spot'])
              mean_reversion  = float(bondform.cleaned_data['mean_reversion'])
              shortrate_vol  = float(bondform.cleaned_data['shortrate_vol'])
              hwgrid_pts  = float(bondform.cleaned_data['hwgrid_pts'])

              print(issue_date)
              print(call_schedule)
              print(put_schedule)
              print(conversionRatio)
          else:
              print(bondform.errors)
                      
      bond = wdb.mrigweb_Bond(issue_name,issue_date,maturity_date,
                 face_value,day_count,calendar,business_convention,
                 month_end,settlement_days,date_generation,coupon_frequency,
                 fixed_coupon_rate,floating_coupon_index,floating_coupon_spread,
                 inArrears,cap,floor,fixing,conversionRatio,conversionPrice,
                 credit_spread,call_schedule,put_schedule,dividend_schedule) 
      
      valuation_args = {'Underlying Spot' : underlying_spot,
                        'Discount Curve' : discount_curve,
                        'Volatility Curve' : volatility_curve,
                        'Dividend Curve' : dividend_curve,
                        'Mean Reversion' : mean_reversion,
                        'Short Rate Vol' : shortrate_vol,
                        'Hull White Grid Pts' : hwgrid_pts}
      
      resultset = wdb.mrigweb_Analytics(bond,valuation_args)
      resultset = myhtml.dict_to_html(resultset)
    return render(request, "ra_bonds.html",{'resultset' : resultset,'GOOGLE_ADS': GOOGLE_ADS})

def options(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    objectmap = {}
    objectmap['None'] = None
    objectmap['SZYC_INR'] = wdb.mrigweb_szc_rates()
    objectmap['SZYC_USD'] = wdb.mrigweb_szc_rates('USD')
    objectmap['SZYC_GBP'] = wdb.mrigweb_szc_rates('GBP')
    objectmap['LIBOR_3M_INR'] = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_6M_INR'] = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_3M_USD'] = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_6M_USD'] = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_3M_GBP'] = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M', yieldcurvehandle=objectmap['SZYC_GBP'][0])
    objectmap['LIBOR_6M_GBP'] = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M', yieldcurvehandle=objectmap['SZYC_GBP'][0])

    resultset = ""
    if request.method == "POST":
      #Get the posted form
      reference_date = datetime.date.today()
      print("option method is post")
      if 'option_form' in request.POST:
          optionform = fm.OptionForm(request.POST)
          if optionform.is_valid():
              print("----swap form valid----")
              option_name = optionform.cleaned_data['optionname']
              underlying_name = optionform.cleaned_data['underlyingname']
              maturity_date = optionform.cleaned_data['maturity_date']
              maturity_date = datetime.datetime.strptime(maturity_date,'%Y-%m-%d').date()
              strike = float(optionform.cleaned_data['strike'])
              option_type = optionform.cleaned_data['option_type']
              exercise_type = optionform.cleaned_data['exercise_type']
              currency = optionform.cleaned_data['currency']
              day_count= optionform.cleaned_data['daycount']
              calendar = optionform.cleaned_data['calendar']
#Valuation Parameters
              discount_curve  = optionform.cleaned_data['discount_curve']
              discount_curve = objectmap[discount_curve][0]
              volatility_curve  = float(optionform.cleaned_data['volatility_curve'])
              volatility_curve = wdb.mrigweb_FlatVolatilityCurve(reference_date,spot_vols=volatility_curve)
              dividend_curve  = float(optionform.cleaned_data['dividend_curve'])
              dividend_curve = wdb.mrigweb_FlatDividendYieldCurve(reference_date,flat_rate=dividend_curve)
              underlying_spot  = float(optionform.cleaned_data['underlying_spot'])
              valuation_method  = optionform.cleaned_data['valuation_method']
          else:
              print(optionform.errors)

      option = wdb.mrigweb_Option(option_name,underlying_name,maturity_date,
                 option_type,strike,exercise_type,day_count,calendar)
      
      valuation_args = {'Discount Curve' : discount_curve,
                        'Volatility Curve' : volatility_curve,
                        'Underlying Spot' : underlying_spot,
                        'Dividend Curve' : dividend_curve,
                        'Valuation Method' : valuation_method}

      resultset = wdb.mrigweb_Analytics(option,valuation_args)
      resultset = myhtml.dict_to_html(resultset)

    return render(request, "ra_options.html",{'resultset' : resultset,'GOOGLE_ADS': GOOGLE_ADS})

def swaps(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    objectmap = {}
    objectmap['None'] = None
    objectmap['SZYC_INR'] = wdb.mrigweb_szc_rates()
    objectmap['SZYC_USD'] = wdb.mrigweb_szc_rates('USD')
    objectmap['SZYC_GBP'] = wdb.mrigweb_szc_rates('GBP')
    objectmap['LIBOR_3M_INR'] = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_6M_INR'] = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_3M_USD'] = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_6M_USD'] = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_3M_GBP'] = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M', yieldcurvehandle=objectmap['SZYC_GBP'][0])
    objectmap['LIBOR_6M_GBP'] = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M', yieldcurvehandle=objectmap['SZYC_GBP'][0])

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
    floatleg_fixing=None
    
    resultset = ""
    if request.method == "POST":
      #Get the posted form
      reference_date = datetime.date.today()
      print("swap method is post")
      if 'swap_form' in request.POST:
          swapform = fm.SwapForm(request.POST)
          if swapform.is_valid():
              print("----swap form valid----")
              fixed_pay = swapform.cleaned_data['fixed_pay_recieve']
              maturity_date = swapform.cleaned_data['fixed_maturity_date']
              maturity_date = datetime.datetime.strptime(maturity_date,'%Y-%m-%d').date()
              face_value = float(swapform.cleaned_data['fixed_facevalue'])
              fixedleg_day_count= swapform.cleaned_data['fixed_daycount']
              fixedleg_calendar = swapform.cleaned_data['fixed_calendar']
              fixedleg_business_convention = swapform.cleaned_data['fixed_business_convention']
              fixedleg_month_end = bool(swapform.cleaned_data['fixed_month_end'])
              fixedleg_date_generation  = swapform.cleaned_data['fixed_date_generation']
              fixedleg_coupon_frequency  = swapform.cleaned_data['fixed_coupon_frequency']
              fixedleg_coupon_rate  = float(swapform.cleaned_data['fixed_coupon_rate'])
              floatleg_day_count= swapform.cleaned_data['float_daycount']
              floatleg_calendar = swapform.cleaned_data['float_calendar']
              floatleg_business_convention = swapform.cleaned_data['float_business_convention']
              floatleg_month_end = bool(swapform.cleaned_data['float_month_end'])
              floatleg_date_generation  = swapform.cleaned_data['float_date_generation']
              floatleg_coupon_frequency  = swapform.cleaned_data['float_coupon_frequency']
              floatleg_index  = swapform.cleaned_data['floating_coupon_index']
              floatleg_index = objectmap[floatleg_index]
              try:
                  floatleg_coupon_spread  = float(swapform.cleaned_data['floating_coupon_spread'])
              except:
                  pass
              try:
                  floatleg_fixing  = float(swapform.cleaned_data['last_libor'])
              except:
                  pass

#Valuation Parameters
              discount_curve  = swapform.cleaned_data['discount_curve']
              discount_curve = objectmap[discount_curve][0]

          else:
              print(swapform.errors)
                      
      swap = wdb.mrigweb_Swap(fixed_pay, maturity_date,
                 face_value,fixedleg_day_count, fixedleg_calendar,
                 fixedleg_business_convention,fixedleg_month_end,fixedleg_date_generation,
                 fixedleg_coupon_frequency,fixedleg_coupon_rate,floatleg_day_count,
                 floatleg_calendar,floatleg_business_convention,floatleg_month_end,
                 floatleg_date_generation,floatleg_coupon_frequency,floatleg_index,
                 floatleg_coupon_spread,floatleg_fixing)
      
      valuation_args = {'Discount Curve' : discount_curve}
      
      resultset = wdb.mrigweb_Analytics(swap,valuation_args)
      resultset = myhtml.dict_to_html(resultset)
    return render(request, "ra_swaps.html",{'resultset' : resultset,'GOOGLE_ADS': GOOGLE_ADS})

def capsfloors(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    objectmap = {}
    objectmap['None'] = None
    objectmap['SZYC_INR'] = wdb.mrigweb_szc_rates()
    objectmap['SZYC_USD'] = wdb.mrigweb_szc_rates('USD')
    objectmap['SZYC_GBP'] = wdb.mrigweb_szc_rates('GBP')
    objectmap['LIBOR_3M_INR'] = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_6M_INR'] = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_3M_USD'] = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_6M_USD'] = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M', yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_3M_GBP'] = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M', yieldcurvehandle=objectmap['SZYC_GBP'][0])
    objectmap['LIBOR_6M_GBP'] = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M', yieldcurvehandle=objectmap['SZYC_GBP'][0])

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
    fixing=None

    resultset = ""
    if request.method == "POST":
      #Get the posted form
      reference_date = datetime.date.today()
      print("swap method is post")
      if 'capsfloors_form' in request.POST:
          capfloorform = fm.CapFloorForm(request.POST)
          if capfloorform.is_valid():
              print("----swap form valid----")
              option_name = capfloorform.cleaned_data['capfloorname']
              start_date = capfloorform.cleaned_data['start_date']
              start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
              maturity_date = capfloorform.cleaned_data['maturity_date']
              maturity_date = datetime.datetime.strptime(maturity_date,'%Y-%m-%d').date()
              cap_or_floor = capfloorform.cleaned_data['option_type']
              face_value = float(capfloorform.cleaned_data['facevalue'])
              strike = float(capfloorform.cleaned_data['strike'])
              currency = capfloorform.cleaned_data['currency']
              day_count= capfloorform.cleaned_data['daycount']
              calendar = capfloorform.cleaned_data['calendar']
              business_convention = capfloorform.cleaned_data['business_convention']
              month_end = bool(capfloorform.cleaned_data['month_end'])
              settlement_days  = float(capfloorform.cleaned_data['settlement_days'])
              date_generation  = capfloorform.cleaned_data['date_generation']
              coupon_frequency  = capfloorform.cleaned_data['coupon_frequency']
              floating_coupon_index  = capfloorform.cleaned_data['floating_coupon_index']
              floating_coupon_index = objectmap[floating_coupon_index]
              try:
                  floating_coupon_spread  = float(capfloorform.cleaned_data['floating_coupon_spread'])
              except:
                  pass
              try:
                  fixing  = float(capfloorform.cleaned_data['last_libor'])
              except:
                  pass
#Valuation Parameters
              discount_curve  = capfloorform.cleaned_data['discount_curve']
              discount_curve = objectmap[discount_curve][0]
              volatility_curve  = float(capfloorform.cleaned_data['volatility_curve'])
              volatility_curve = wdb.mrigweb_ConstantVolatilityCurve(volatility_curve)
          else:
              print(capfloorform.errors)

      capfloor = wdb.mrigweb_CapFloor(option_name,start_date,maturity_date,
                 cap_or_floor,strike,face_value,day_count,calendar,
                 business_convention,month_end,settlement_days,
                 date_generation,coupon_frequency,floating_coupon_index,
                 floating_coupon_spread,fixing)
      
      valuation_args = {'Discount Curve' : discount_curve,
                        'Volatility Curve' : volatility_curve}
      
      resultset = wdb.mrigweb_Analytics(capfloor,valuation_args)
      resultset = myhtml.dict_to_html(resultset)

    return render(request, "ra_capsfloors.html",{'resultset' : resultset,'GOOGLE_ADS': GOOGLE_ADS})

def portfolio(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    return render(request, "ra_portfolio.html")

def mf(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    topmfslist_aum = []
    topmfs = wdb.mrigweb_top_mfs()[0]
    for x in topmfs:
        mf = x.reset_index()
        mf_table = [list(mf)] + mf.values.tolist()
        mf_table = myhtml.list_to_html(mf_table)
        topmfslist_aum.append(mf_table)

    topmfslist_ret = []
    topmfs = wdb.mrigweb_top_mfs()[1]
    for x in topmfs:
        mf = x.reset_index()
        mf_table = [list(mf)] + mf.values.tolist()
        mf_table = myhtml.list_to_html(mf_table)
        topmfslist_ret.append(mf_table)

    testdf = topmfs[3].to_json(orient='records')
    # topmfslist_ret = []
    # topmfslist_aum = []

    return render(request, "mf.html",{'topmfslist_aum' : topmfslist_aum,
                                      'topmfslist_ret' : topmfslist_ret,'testdf':testdf,'GOOGLE_ADS': GOOGLE_ADS})
    
def stock1(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    
#    oc = mu.test_df()
#    oc = oc[['Symbol','Open','Last']]
#    oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#    oc = [oc_head] + oc.values.tolist()
#    oc = myhtml.list_to_html(oc)
#    oc = "<img border=\"0\" src=\"{% static 'assets/images/pnl_icon.png' %}\" width=\"10\" height=\"10\"/>"
    sql = "select image from images limit 1"
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    image = engine.execute(sql).fetchall()
    image = bytes(image[0][0])
    image = image.decode("utf-8")
    oc = ['a',3]
    return render(request, "stock1.html", {"oc":image,'GOOGLE_ADS': GOOGLE_ADS})
    