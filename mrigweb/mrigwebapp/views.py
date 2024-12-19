import sys,os

from rest_framework.decorators import api_view

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
import strategies.option_strategies as op_s
# Create your views here.
import data.settings_load as config
from gnews  import GNews
import pytz
import research.analytics as ran
from rest_framework import generics
from api.api_stocks import StockAPI1,StockPriceSerializer
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
import yfinance as yf
import maintenance.item_manager as im
import research.screener_TA as sta
from api.api_general import top_stocks
import api.api_general as apg
import strategies.sector_analysis as sa
import strategies.stock_prediction_LSTM as spl
import strategies.portfolio_optimization as po
import hashlib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from portfolios.portfolio import UPortfolio
from rest_framework.permissions import IsAuthenticated
import payment.razorpay as rp
import razorpay
import mrigstatics as ms
setting = config.get_settings()

IST = pytz.timezone('Asia/Kolkata')
GMT = pytz.timezone('UTC')

def home(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    return render(request, "index.html", {'GOOGLE_ADS': GOOGLE_ADS})

def stock(request,symbol='HDFCBANK'):
    indices = setting['indices_for_mrig'].keys()
    googlenews = GNews(language='en', country='IN', period='1d', start_date=None, end_date=None, max_results=10)

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

    for stk in indices:
        slist = slist + "<option value=\"" + str(stk) + " : " + str(stk) + "\">"

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
            print(news)
        else:
            if symbol == 'NIFTY 501':
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
            ratio_list = stkanalytics[14]
            income_statement = stkanalytics[15]
            balance_sheet = stkanalytics[16]

            #         fd,oc = fd.to_html(), oc.to_html()
             
            return_list = myhtml.list_to_html(return_list)
            risk_list = myhtml.list_to_html(risk_list)
              
            if not ratio_list.empty:
                # ratios = ratios.reset_index()
                ratio_list['ratios'] = ratio_list['ratios'].str.upper()
                ratio_list.rename(columns={'ratios' : 'Ratios'},inplace=True)
                ratios_head = list(ratio_list)
                # ratios_head.remove("index")
                # ratios_head.insert(0,"")
                ratios = [ratios_head] + ratio_list.values.tolist()
                ratios = myhtml.list_to_html(ratios)

            if not income_statement.empty:
                # ratios = ratios.reset_index()
                income_statement['income_statement'] = income_statement['income_statement'].str.upper()
                income_statement.rename(columns={'income_statement': 'Income Statement (Cr)'}, inplace=True)
                for col in income_statement.columns[1:]:
                    print(col)
                    income_statement[col] = income_statement[col].apply(lambda x : '{:,.0f}'.format(float(x)/10000000))
                income_statement_head = list(income_statement)
                # ratios_head.remove("index")
                # ratios_head.insert(0,"")
                income_statement = [income_statement_head] + income_statement.values.tolist()
                income_statement = myhtml.list_to_html(income_statement)

            if not balance_sheet.empty:
                # ratios = ratios.reset_index()
                balance_sheet['balance_sheet'] = balance_sheet['balance_sheet'].str.upper()
                color_row_list= [1]
                for i in balance_sheet.index:
                    if balance_sheet.loc[i,'balance_sheet'] == 'EQUITY_AND_LIABILITIES':
                        color_row_list.append(i)
                balance_sheet.rename(columns={'balance_sheet': 'Balance Sheet (Cr)'}, inplace=True)
                for col in balance_sheet.columns[1:]:
                    print(col)
                    # balance_sheet[col] = balance_sheet[col].apply(lambda x :'{:,.0f}'.format(float(x)/1000))
                    balance_sheet[col] = balance_sheet[col].apply(lambda x : mu.mrig_format(x,'{:,.0f}'))
                balance_sheet_head = list(balance_sheet)
                # ratios_head.remove("index")
                # ratios_head.insert(0,"")
                balance_sheet = [balance_sheet_head] + balance_sheet.values.tolist()
                balance_sheet = myhtml.list_to_html(balance_sheet,color_row_list=color_row_list)

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
    news = []
    stknews = googlenews.get_news(stock_desc.split('|')[0]) #+ googlenews.get_news(symbol)

    for n in stknews:
        # if 'Tata Power' in n['title']:
        dtime = n['published date']
        try:
            dtime = datetime.datetime.strptime(n['published date'], '%a, %d %b %Y %I:%M:%S %Z')
            dtime = GMT.localize(dtime)
        except:
            pass
        # print(dtime.astimezone(IST).strftime('%a, %d %b %Y %I:%M:%S'), '\n')
        # print(n['title'], '\n\n')

        # news.append([dtime,"<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"" + n['url'] + ">" +n['title']+ "</a>"])
        print("<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"" + n['url'] + "\">" +n['title']+ "</a>")
        news.append([dtime,"<a style=\"color:#f7ed4a;text-decoration:underline;\" target=\"_blank\" rel=\"noopener noreferrer\" href=\"" + n['url'] + "\">" +n['title']+ "</a>"])

    # print(news)
    return render(request, "stock.html", {"slist":slist,"symbol":symbol,
                                          "stock_desc" : stock_desc,
                                          "price_list":price_list,
                                          "return_list":return_list,
                                          "risk_list":risk_list,
                                          "ratios":ratios,
                                          "income_statement" : income_statement,
                                          "balance_sheet" : balance_sheet,
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
        # print(foliocontent)
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
            # print(pfolio_tbl)


    return render(request, "folio.html", {'port_list':port_list,
                                          'portfolio' : pfolio_tbl,
                                          'pfolio_scenario_graph' : pfolio_scenario_graph,
                                            'GOOGLE_ADS': GOOGLE_ADS})

def folio_mini(request, template=''):
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
        # print(foliocontent)
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
            # print(pfolio_tbl)


    return render(request, "folio.html", {'port_list':port_list,
                                          'portfolio' : pfolio_tbl,
                                          'pfolio_scenario_graph' : pfolio_scenario_graph,
                                            'GOOGLE_ADS': GOOGLE_ADS})



def market(request, symbol='NIFTY 50'):
    indices = setting['indices_for_mrig'].keys()

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
    for stk in indices:
        slist = slist + "<option value=\"" + str(stk) + " : " + str(stk) + "\">"
    # slist = slist + "</datalist>"
    # print(stocklist)
    for stk in stocklist:
        if stk[0] != 'symbol':
            if stk[1] != None:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[1]) + "\">"
            else:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[0]) + "\">"
    slist = slist + "</datalist>"

    # indices_list = "<input style=\"width: 130px; height: 25px;\" list=\"indices\" name=\"indices\"><datalist id=\"indices\">"
    # # print(stocklist)
    # for stk in indices:
    #     indices_list = indices_list + "<option value=\"" + str(stk) + "\">"
    # indices_list = indices_list + "</datalist>"
    # print(indices_list)
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


# def option_s(request):
#     GOOGLE_ADS = 0
#     if mrigstatics.ENVIRONMENT == 'production':
#         GOOGLE_ADS = 1
#     engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
#     os_list = ["Covered Call","Bull Put Spread", "Bear Call Spread"]
#     strategy_desc = ""
#     strategy = None
#     oc = pd.DataFrame()
#     slist = "<input style=\"width: 130px; height: 25px;\" list=\"os\" name=\"strategy\"><datalist id=\"os\">"
#     for stg in os_list:
#         slist = slist + "<option value=\""+str(stg)+"\">"
#     slist = slist + "</datalist>"
#
#     if request.method == "POST":
#       #Get the posted form
#       strategyform = fm.StrategyForm(request.POST)
#
#       if strategyform.is_valid():
#          strategy = strategyform.cleaned_data['strategy']
#
#
#          sql = "select * from os_page where strategy='"+strategy+"' limit 1"
#          os_page = pd.read_sql(sql,engine)
#
#          if not os_page.empty:
#              strategy_desc = os_page['strategy_name'][0]
#              oc = os_page['strategy_table'][0]
#
#     return render(request, "os.html", {"slist":slist,
#                                        "strategy":strategy,
#                                        "strategy_desc" : strategy_desc,
#                                        "oc":oc,
#                                        'GOOGLE_ADS': GOOGLE_ADS})


def option_s(request):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    datadir = os.path.dirname(__file__)




    os_list = ["Covered Call", "Bull Put Spread", "Bear Call Spread"]
    strategy_desc = ""
    strategy = None
    oc = pd.DataFrame()
    slist = "<input style=\"width: 130px; height: 25px;\" list=\"os\" name=\"strategy\"><datalist id=\"os\">"
    for stg in os_list:
        slist = slist + "<option value=\"" + str(stg) + "\">"
    slist = slist + "</datalist>"

    if request.method == "POST":
        # Get the posted form
        strategyform = fm.StrategyForm(request.POST)

        if strategyform.is_valid():
            strategy = strategyform.cleaned_data['strategy']

            sql = "select * from os_page where strategy='" + strategy + "' limit 1"
            os_page = pd.read_sql(sql, engine)

            if not os_page.empty:
                strategy_desc = os_page['strategy_name'][0]
                oc = os_page['strategy_table'][0]

    # json_file_path = os.path.join(datadir, '..','..','strategies','option_strategies.json')
    # f = open(json_file_path)
    # strjson = json.load(f)
    #
    # strjson = strjson['bps']
    # strjson = json.dumps(strjson)
    #
    # bps = op_s.OptionStrategy('BPS')
    # bps.set_strategy_json(strjson)
    # bps.set_symbols(['TATAMOTORS'])#,'TATAPOWER','SBIN','HDFCBANK','SRF'])
    # bps.run_strategy()

    strategy = 'BPS'
    strategy_desc = 'Bull Put Spread'

    mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    loaddate = datetime.date.today().strftime('%y%m%d')

    # strategy_basket = bps.strategy_basket#['TATAMOTORS'][0][3]

    # strategy_basket = mrig_engine.execute("select strategy_id,strategy_obj from os_page where load_date = (select max(load_date) from os_page)").fetchall()
    strategy_basket = mrig_engine.execute("select strategy_id,strategy_obj from os_page where load_date = (select max(load_date) from os_page)").fetchall()

    stratmap = {'BPS':'Bull Put Spread','BCS':'Bull Call Spread','BEARPS':'Bear Put Spread','BEARCS':'Bear Call Spread'}
    strategy_body = {}
    colormap = {0:'#0047AB',1: '#0096FF'}
    cnt = 0
    for id,strategylist in strategy_basket:
        s = json.loads(strategylist)
        s = pd.DataFrame(s[0])
        # s.drop(['obj', 'yld'], axis=1, inplace=True)
        stratname = stratmap[s['portfolio_name'].head(1).values[0].split('_')[1]]
        # s['valuation_date_time'] = s['valuation_date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # s['position_date'] = s['position_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        # s['date'] = s['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        #
        # s['expiry_date'] = s['expiry_date'].astype(str)
        # s[['max_risk','max_profit','breakeven','Yield']] = s[['max_risk','max_profit','breakeven','Yield']].applymap(mu.shortenlength)
        # s[3][['max_risk','max_profit','breakeven','Yield']] = s[3][['max_risk','max_profit','breakeven','Yield']].astype(

        # s[3]['max_risk'] = pd.to_numeric(s[3]['max_risk'], errors='coerce')

        # s[3]['max_profit'] = pd.to_numeric(s[3]['max_profit'], errors='coerce')
        # s[3]['breakeven'] = pd.to_numeric(s[3]['breakeven'], errors='coerce')
        # s[3]['Yield'] = pd.to_numeric(s[3]['Yield'], errors='coerce')

        # sql = "insert into os_page (strategy_id, strategy_obj,load_date, strategy_table, strategy_name) values (%s,%s,%s,'','')"
        # mrig_engine.execute(sql, (id, json.dumps([s[3].to_dict(), s[1],s[2]]), loaddate))

        s = s[['strategy_id', 'portfolio_name', 'underlying', 'strike','expiry_date', 'max_profit', 'max_risk', 'breakeven', 'Yield',
         'date','underlying_price']]
        s['portfolio_name'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/osa/"+\
                                         s['strategy_id']+"\">"+ s['portfolio_name']+"</a>"
        try:
            s['underlying'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/stock/"+s['underlying']+"\">"+ \
                                     s['underlying']+' ('+s['underlying_price'].map(mu.shortenlength)+")</a>"
        except:
            pass
        s = s.drop(['strategy_id','underlying_price'], axis=1)
        s.rename(columns={'Yield':'Max_Yield'},inplace=True)
        s.columns = map(lambda x: str(x).upper(), s.columns)

        # print('Inside Views \n\n',strategylist)
        strategylist_head = [list(s)]
        strategylist_body = s.values.tolist()
        # print('Inside Views \n\n',strategylist_body)

        # strategylist_tbl = [strategylist.values.tolist()
        strategylist_head_tbl = myhtml.list_to_html(strategylist_head,body_flag=False)
        strategylist_body_tbl = myhtml.list_to_html(strategylist_body,header_flag=False,span={'col':[0,0],'row' : [1,2],})
        if stratname in strategy_body.keys():
            strategy_body[stratname].append(strategylist_body_tbl)
        else:
            strategy_body[stratname] = [strategylist_body_tbl]
        cnt = cnt +1
    # pfolio_scenario_graph = pfolio[1]

    return render(request, "os.html", {"slist": slist,
                                       "strategy": strategy,
                                       "strategy_desc": stratname,
                                       "strategylist_head" : strategylist_head_tbl,
                                       "strategylist" : strategy_body,
                                       "oc": oc,
                                       'GOOGLE_ADS': GOOGLE_ADS})


# def osa(request,strategyid):
#     GOOGLE_ADS = 0
#     if mrigstatics.ENVIRONMENT == 'production':
#         GOOGLE_ADS = 1
#
#     strategy = mu.mrigsession_get(strategyid)
#
#     analytics = []
#     description = ""
#     if strategy['strategyname'] == 'coveredcall':
#         analytics = wdb.covered_call_analysis(strategy)
#         description = "Covered Call Strategy using option:"
#     if strategy['strategyname'] == 'bullputspread':
#         analytics = wdb.bull_put_spread_analysis(strategy)
#         description = "Bull Put Spread Strategy using options:"
#     if strategy['strategyname'] == 'bearcallspread':
#         analytics = wdb.bear_call_spread_analysis(strategy)
#         description = "Bear Call Spread Strategy using options:"
#     strategy_desc = analytics[0]
#     strategy_specs = analytics[1]
#     strategy_risk = analytics[2]
#     NPV_graph = analytics[3]
#     delta_graph = analytics[4]
#     gamma_graph = analytics[5]
#     theta_graph = analytics[6]
#     results = analytics[7]
#
#     long_option_desc = strategy_desc[0]+" "+strategy_desc[1].strftime('%d-%b-%Y')+ " "+str(strategy_desc[2])
#     short_option_desc = ""
#     if len(strategy_desc) >3:
#         short_option_desc = strategy_desc[0]+" "+strategy_desc[1].strftime('%d-%b-%Y')+ " "+str(strategy_desc[3])
# #
#     strategy_specs = myhtml.list_to_html(strategy_specs)
#     strategy_risk = myhtml.list_to_html(strategy_risk)
#     results = myhtml.dict_to_html(results)
#
#     return render(request, "osa.html", {"symbol":strategy_desc[0],
#                                         "strategy_desc" : description,
#                                        "long_option_desc":long_option_desc,
#                                        "short_option_desc":short_option_desc,
#                                        "strategy_specs" : strategy_specs,
#                                        "strategy_risk" : strategy_risk,
#                                        "NPV_graph" : NPV_graph,
#                                        "delta_graph" : delta_graph,
#                                        "gamma_graph" : gamma_graph,
#                                        "theta_graph" : theta_graph,
#                                        "results" : results,
#                                        'GOOGLE_ADS': GOOGLE_ADS
#                                        })


def osa(request, strategyid):
    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1

    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    stratmap = {'BPS':'Bull Put Spread','BCS':'Bull Call Spread','BEARPS':'Bear Put Spread','BEARCS':'Bear Call Spread'}

    # strategy = mu.mrigsession_get(strategyid)
    strategy = engine.execute("select strategy_obj from os_page where strategy_id='"+strategyid+"'").fetchall()[0][0]
    # print(strategy)

    strategy = json.loads(strategy)
    df = strategy[0]
    graphs = strategy[1]
    NPV_graph = strategy[2]

    df = pd.DataFrame(df)
    symbol = df['underlying'].head(1).values[0]

    # analytics = []
    # description = ""
    # if strategy['strategyname'] == 'coveredcall':
    #     analytics = wdb.covered_call_analysis(strategy)
    #     description = "Covered Call Strategy using option:"
    # if strategy['strategyname'] == 'bullputspread':
    #     analytics = wdb.bull_put_spread_analysis(strategy)
    #     description = "Bull Put Spread Strategy using options:"
    # if strategy['strategyname'] == 'bearcallspread':
    #     analytics = wdb.bear_call_spread_analysis(strategy)
    #     description = "Bear Call Spread Strategy using options:"
    # strategy_desc = df['portfolio_name'].head(1).values[0]
    strategy_desc = stratmap[df['portfolio_name'].head(1).values[0].split('_')[1]]

    strategy_risk = df[['underlying', 'security', 'direction', 'option_type', 'strike',
       'expiry_date', 'cost', 'max_profit', 'max_risk', 'breakeven', 'Yield',
         'qty','delta', 'gamma', 'theta_per_day', 'vega', 'rho']]

    strategy_risk['cost'] = strategy_risk['cost']*strategy_risk['qty']

    strategy_risk = strategy_risk.append(strategy_risk[['cost','qty','delta', 'gamma', 'theta_per_day', 'vega', 'rho']].sum(numeric_only=True), ignore_index=True).fillna('')
    # strategy_risk.loc[:,[ 'max_profit', 'max_risk', 'breakeven', 'Yield']] = strategy_risk[[ 'max_profit', 'max_risk', 'breakeven', 'Yield']].head(1).values
    strategy_risk['max_profit'] = strategy_risk['max_profit'].head(1).values[0]
    strategy_risk['max_risk'] = strategy_risk['max_risk'].head(1).values[0]
    strategy_risk['breakeven'] = strategy_risk['breakeven'].head(1).values[0]
    strategy_risk['Yield'] = strategy_risk['Yield'].head(1).values[0]
    strategy_risk.drop('underlying',axis=1,inplace=True)
    strategy_risk.rename(columns={'Yield': 'Max_Yield'}, inplace=True)
    strategy_risk.columns = map(lambda x: str(x).upper(), strategy_risk.columns)

    print(strategy_risk)
    # NPV_graph = analytics[3]
    # delta_graph = analytics[4]
    # gamma_graph = analytics[5]
    # theta_graph = analytics[6]
    # results = analytics[7]

    # long_option_desc = strategy_desc[0] + " " + strategy_desc[1].strftime('%d-%b-%Y') + " " + str(strategy_desc[2])
    # short_option_desc = ""
    # if len(strategy_desc) > 3:
    #     short_option_desc = strategy_desc[0] + " " + strategy_desc[1].strftime('%d-%b-%Y') + " " + str(strategy_desc[3])
    # #
    # strategy_specs = myhtml.list_to_html(strategy_specs)

    strategy_risk_head = [list(strategy_risk)]
    strategy_risk_body = strategy_risk.values.tolist()
    # print('Inside Views \n\n',strategylist_body)

    # strategylist_tbl = [strategylist.values.tolist()
    strategy_risk = myhtml.list_to_html(strategy_risk_head +strategy_risk_body)
    # strategylist_body_tbl = myhtml.list_to_html(strategy_risk_body, header_flag=False)

    # strategy_risk = myhtml.list_to_html(strategy_risk)
    # results = myhtml.dict_to_html(results)

    return render(request, "osa.html", {"symbol": symbol,
                                        # "strategy_desc": description,
                                        # "long_option_desc": long_option_desc,
                                        # "short_option_desc": short_option_desc,
                                        "strategy_desc": strategy_desc,
                                        "strategy_risk": strategy_risk,
                                        "graphs": graphs,
                                        "NPV_graph": NPV_graph,
                                        # "delta_graph": delta_graph,
                                        # "gamma_graph": gamma_graph,
                                        # "theta_graph": theta_graph,
                                        # "results": results,
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


def mf(request, symbol=''):
    googlenews = GNews(language='en', country='IN', period='1d', start_date=None, end_date=None, max_results=10)

    GOOGLE_ADS = 0
    if mrigstatics.ENVIRONMENT == 'production':
        GOOGLE_ADS = 1
    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    sql = "select * from stock_page where symbol='" + symbol + "'"
    stock_page = pd.read_sql(sql, engine)
    #    stocklist = list(stocklist)
    price_list, return_list, risk_list, ratios, oc = None, "", "", "", ""
    price_graph, return_graph, macd_graph, boll_graph = "", "", "", ""
    stock_desc = ""
    news = ""
    level_chart = ""
    pcr = ""
    max_pain = ""

    engine = mu.sql_engine()
    stocklist = engine.execute(
        "select distinct sm.scheme_name, sm.amc from mf_scheme_master sm inner join mf_history sh on sm.scheme_name=sh.scheme_name where sh.nav > 0").fetchall()
    slist = "<input style=\"width: 130px; height: 25px;\" list=\"stocks\" name=\"symbol\"><datalist id=\"stocks\">"

    for stk in stocklist:
        if stk[0] != 'symbol':
            if stk[1] != None:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[1]) + "\">"
            else:
                slist = slist + "<option value=\"" + str(stk[0]) + " : " + str(stk[0]) + "\">"
    slist = slist + "</datalist>"

    if request.method == "POST":
        mfform = fm.MFForm(request.POST)
        # Get the posted form
        if mfform.is_valid():
            symbol = mfform.cleaned_data['symbol']
            symbol = symbol.split(":")[0].strip()
            print(symbol)

    engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    topmfslist_aum = []
    topmfslist_ret = []

    if (symbol and symbol != ""):
        sql = "select * from stock_page where symbol='" + symbol + "'"
        stock_page = pd.read_sql(sql, engine)

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
            print(news)
        else:
            stkanalytics = wdb.mrigweb_mf(symbol)
            price_list, return_list = stkanalytics[0], stkanalytics[1]
            price_graph, return_graph = stkanalytics[2], stkanalytics[3]
            stock_desc = stkanalytics[4]
            # news = stkanalytics[10]

            #         fd,oc = fd.to_html(), oc.to_html()

            return_list = myhtml.list_to_html(return_list)
            # risk_list = myhtml.list_to_html(risk_list)
    else:
        topmfs = wdb.mrigweb_top_mfs()[0]
        for x in topmfs:
            mf = x.reset_index()
            mf_table = [list(mf)] + mf.values.tolist()
            mf_table = myhtml.list_to_html(mf_table)
            topmfslist_aum.append(mf_table)

        topmfs = wdb.mrigweb_top_mfs()[1]
        for x in topmfs:
            mf = x.reset_index()
            mf_table = [list(mf)] + mf.values.tolist()
            mf_table = myhtml.list_to_html(mf_table)
            topmfslist_ret.append(mf_table)

        testdf = topmfs[3].to_json(orient='records')
        # topmfslist_ret = []
        # topmfslist_aum = []

    price_list = myhtml.list_to_html(price_list)
    news = []
    stknews = googlenews.get_news(stock_desc.split('|')[0])  # + googlenews.get_news(symbol)
    if stknews is None:
        stknews = []

    for n in stknews:
        # if 'Tata Power' in n['title']:
        dtime = n['published date']
        try:
            dtime = datetime.datetime.strptime(n['published date'], '%a, %d %b %Y %I:%M:%S %Z')
            dtime = GMT.localize(dtime)
        except:
            pass
        # print(dtime.astimezone(IST).strftime('%a, %d %b %Y %I:%M:%S'), '\n')
        # print(n['title'], '\n\n')

        # news.append([dtime,"<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"" + n['url'] + ">" +n['title']+ "</a>"])
        print("<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"" + n['url'] + "\">" + n['title'] + "</a>")
        news.append([dtime,
                     "<a style=\"color:#f7ed4a;text-decoration:underline;\" target=\"_blank\" rel=\"noopener noreferrer\" href=\"" +
                     n['url'] + "\">" + n['title'] + "</a>"])

    # print(news)
    return render(request, "mf.html", {"slist": slist, "symbol": symbol,
                                          "stock_desc": stock_desc,
                                          "price_list": price_list,
                                          "return_list": return_list,
                                          "price_graph": price_graph,
                                          "return_graph": return_graph,
                                          "topmfslist_aum": topmfslist_aum,
                                          "topmfslist_ret" : topmfslist_ret,
                                          "news": news,
                                          'GOOGLE_ADS': GOOGLE_ADS})


# def mf(request):
#     GOOGLE_ADS = 0
#     if mrigstatics.ENVIRONMENT == 'production':
#         GOOGLE_ADS = 1
#
#     topmfslist_aum = []
#     topmfs = wdb.mrigweb_top_mfs()[0]
#     for x in topmfs:
#         mf = x.reset_index()
#         mf_table = [list(mf)] + mf.values.tolist()
#         mf_table = myhtml.list_to_html(mf_table)
#         topmfslist_aum.append(mf_table)
#
#     topmfslist_ret = []
#     topmfs = wdb.mrigweb_top_mfs()[1]
#     for x in topmfs:
#         mf = x.reset_index()
#         mf_table = [list(mf)] + mf.values.tolist()
#         mf_table = myhtml.list_to_html(mf_table)
#         topmfslist_ret.append(mf_table)
#
#     testdf = topmfs[3].to_json(orient='records')
#     # topmfslist_ret = []
#     # topmfslist_aum = []
#
#     return render(request, "mf.html",{'topmfslist_aum' : topmfslist_aum,
#                                       'topmfslist_ret' : topmfslist_ret,'testdf':testdf,'GOOGLE_ADS': GOOGLE_ADS})
    
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


class stockapi(APIView):
    # @api_view(['GET', 'POST'])

    def get(self,request,symbol,levelFlag=False,period='3m'):
        ymap = {'USDINR': 'INR=X',
                'CRUDE OIL': 'CL=F',
                'GOLD': 'GC=F'}
        if symbol in ymap.keys():
            data = yf.download(ymap[symbol], period='3mo', interval='1d')
            data['scrip'] = symbol
            data.reset_index(inplace=True)
            data = data[data.columns[:-1]]
            data.columns = [x.lower() for x in data.columns]
            json_data = data.to_json(orient='records')
            # print(symbol,'\n',json_data)
        else:
            df = StockAPI1(symbol,levelFlag,period).pricevol_data
            df.reset_index(inplace=True)
            json_data = df.to_json(orient='records')
            # print(json_data)
            # Return the JSON data
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class stockapi_levels(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request,symbol):
        endDate = datetime.date.today()
        startDate = endDate - datetime.timedelta(days=365)
        levels = mu.getLevels(symbol, startDate, endDate)
        levels = [x[1] for x in levels[0]]
        # print(levels)
        json_data = json.dumps(levels)
        # print(json_data)
        # Return the JSON data
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class stockapi_oitree(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request,symbol):
        endDate = datetime.date.today()
        startDate = endDate - datetime.timedelta(days=365)
        # levels = mu.getLevels(symbol, startDate, endDate)
        # levels = [x[1] for x in levels[0]]
        la = ran.level_analysis([symbol])

        oitree = la['oi_tree']
        oitree.drop(columns=['instrument_token', 'tradingsymbol','lot_size', 'timestamp', 'last_trade_time',
         'last_price', 'last_quantity', 'buy_quantity', 'sell_quantity','volume', 'average_price','net_change',
        'lower_circuit_limit', 'upper_circuit_limit', 'ohlc','depth'],inplace=True)
        oidict = {}
        print_expiries = sorted(set(list(oitree['expiry'])))
        for exp in print_expiries[0:min(4, len(print_expiries))]:
            x_data = list(oitree[oitree['expiry'] == exp]['strike'])
            y1_data = list(oitree[oitree['expiry'] == exp]['oi_ce' + str(exp)])
            y2_data = list(oitree[oitree['expiry'] == exp]['oi_pe' + str(exp)])
            oidict[exp.strftime('%Y-%m-%d')] = {'strikes':x_data,'oi_ce':y1_data,'oi_pe':y2_data}
        oidict['pcr'] = la['pcr']
        oidict['max_pain'] = la['max_pain']
        # oitree['expiry'] = oitree['expiry'].apply(lambda x : x.strftime('%Y-%m-%d'))
        # print(levels)
        # json_data = oidict.to_json(orient='records')
        json_data = json.dumps(oidict)
        # print(json_data)
        # Return the JSON data
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)


class stockapi_tascreen(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request,symbol):
        page_items = im.get_item(['market_graphs', 'n50_ta_screen', 'sector_graph',
                                  'NIFTY 50|levels_json', 'BANKNIFTY|levels_json'])
        for k, v in page_items.items():
            page_items = v

        if 'n50_ta_screen' in page_items.keys():
            print('N50 : Getting from Database')
            n50_ta_screen = pd.read_json(page_items['n50_ta_screen'], orient='split')
            json_data = page_items['n50_ta_screen']
        else:
            print('N50 : Creating Table')
            n50_ta_screen = sta.display_analytics()
            n50_ta_screen_json = n50_ta_screen.to_json(orient='split')
            im.set_items({'n50_ta_screen': n50_ta_screen_json})
            json_data = n50_ta_screen_json
        # print(json_data)
        # Return the JSON data
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class stockapi_stockpage(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request,symbol):
        stk_page = wdb.mrigweb_stock_mini(symbol)
        json_data = json.dumps(stk_page)
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)


class newsapi(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request):
        news = wdb.mrigweb_news()
        for k in news.keys():
            for n in news[k]:
                n[0] = n[0].strftime('%d-%b-%Y')
                n.pop(3)

        json_data = json.dumps(news)
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class stockstrategiesapi(APIView):
    # @api_view(['GET', 'POST'])
    def get(self, request,strat):
        result = wdb.stock_strategies()
        if strat == 'st_macd':
            st_macd_daily = result['st_macd_daily']
            if not st_macd_daily.empty:
                # n50_ta_screen = n50_ta_screen.reset_index()
                json_data = st_macd_daily.to_json(orient='split')
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)


class mfapi_mfpage(APIView):
    # @api_view(['GET', 'POST'])
    def get(self,request,symbol=""):
        topmfs = wdb.mrigweb_top_mfs()[0]
        topmfslist_aum = pd.DataFrame()#[]#topmfs.to_json(orient='split')
        for x in topmfs:
            x = x.reset_index()
            # print(x)
            if len(topmfslist_aum) > 0:
                topmfslist_aum = pd.concat([topmfslist_aum,x])
            else:
                topmfslist_aum = x

        # print('MF BEFORE ',topmfslist_aum)
        topmfslist_aum = topmfslist_aum.to_json(orient='split')
        # print('MF AFTER ',topmfslist_aum)


        topmfs = wdb.mrigweb_top_mfs()[1]
        topmfslist_ret = pd.DataFrame()#[]#topmfs.to_json(orient='split')
        for x in topmfs:
            x = x.reset_index()
            if len(topmfslist_ret) > 0:
                topmfslist_ret = pd.concat([topmfslist_ret,x])
            else:
                topmfslist_ret = x
        # print('MF BEFORE ', topmfslist_ret)
        topmfslist_ret = topmfslist_ret.to_json(orient='split')
        # print('MF AFTER ', topmfslist_ret)


        if len(symbol) > 1:
            stk_page = wdb.mrigweb_mf_mini(symbol)
        else:
            stk_page = {}
        stk_page['topmfslist_aum'] = topmfslist_aum
        stk_page['topmfslist_ret'] = topmfslist_ret

        json_data = json.dumps(stk_page)
        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class portfolio_api(APIView):
    def get(self, request, port_name='SB'):
        account= 'santoshbag'
        port_list = pm.portfolio_list(account)

        pfolio = pm.show_portfolio(port_name, account)
        portfolio = pfolio[0].to_json(orient='split')
        scenario_dfs_multi = pfolio[4]
        scenarios = pfolio[5]
        pfolio_head = list(pfolio[0])
        pfolio_scenario_graph = pfolio[1]
        # print(pfolio_tbl)
        greeks = ['NPV', 'delta', 'gamma', 'theta_per_day', 'vega', 'rho']
        scenario_dfs_multi = [scenario_df.to_json(orient='records') for scenario_df in scenario_dfs_multi]
        json_data = {'port_list':port_list,'portfolio' : portfolio,
                                          'scenario_dfs_multi' : scenario_dfs_multi}
        json_data = json.dumps(json_data)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)


class marketoptions_api(APIView):
    def get(self, request, symbol='NIFTY 50'):
        oc = mu.kite_OC_new([symbol])
        expiry = [exp.strftime('%Y-%m-%d') for exp in sorted(set(oc['expiry']))]
        strikes = sorted(set(oc['strike']))
        if symbol == 'NIFTY':
            symbol = 'NIFTY 50'
        if symbol == 'BANKNIFTY':
            symbol = 'NIFTY BANK'

        spot = mu.getStockQuote(symbol)
        print('MARKET OPTIONS API',symbol,spot)

        json_data = {'expiry':expiry,'strikes' : strikes,
                                          'spot' : spot}
        json_data = json.dumps(json_data)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)


class stockmovers_api(APIView):
    def get(self, request, symbol='NIFTY 500'):
        [winners,losers] = top_stocks(symbol)
        winners = pd.DataFrame(winners,columns=['symbol','change (%)'])
        winners.sort_values(by=['change (%)'],ascending=False,inplace=True)
        winners = winners.to_json(orient='split')
        losers = pd.DataFrame(losers,columns=['symbol','change (%)'])
        losers.sort_values(by=['change (%)'],ascending=True,inplace=True)
        losers = losers.to_json(orient='split')

        json_data = {'winners':winners,'losers': losers}
        json_data = json.dumps(json_data)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

# class rates_api(APIView):
#     @api_view(['POST'])
#     def post(self, request, currency='INR'):
#         params = request.data
#         print('PARAMS RECVD',params)
#         rates = apg.rates(currency,params)
#         json_data = json.dumps(rates)
#
#         return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

@api_view(['POST'])
def rates_api(request, currency='INR'):
    params = request.data
    print('PARAMS RECVD',params)
    if params is not None:
        if 'currency' in params.keys():
            currency = params['currency']
    rates = apg.rates(currency,params)
    json_data = json.dumps(rates)

    return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

@api_view(['POST'])
def bonds_api(request):
    params = request.data
    print('BONDS PARAMS RECVD',params)

    [result,scenario] = apg.bonds(params)

    # result = result.pop('Heads')
    result = pd.DataFrame([result])
    result = result.transpose().reset_index()[1:]
    result.rename(columns={'index': 'Heads',0:'Values'},inplace=True)
    cf_idx = result.index[result['Heads'] == 'Cashflow Date'].tolist()[0]
    cashflow_df = result[cf_idx+1:]
    metric_df = result[:cf_idx-2]
    cashflow_df.rename(columns={'Heads':'Cashflow Date','Values':'Cashflow Amount'},inplace=True)
    print('cashflow_df'.upper(),cashflow_df)
    cashflow_df = cashflow_df.to_json(orient='split')
    metric_df = metric_df.to_json(orient='split')
    json_data = {"metric_df" : metric_df,"cashflow_df" : cashflow_df,'scenario' : scenario}
    json_data = json.dumps(json_data)
    print(json_data)

    return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class sector_analysis_api(APIView):
    def get(self, request, symbol='NIFTY 50'):
        result = sa.analysis()

        json_data = json.dumps(result)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class stock_predict_api(APIView):
    def get(self, request, symbol='NIFTY 50'):
        result = spl.prediction(symbol)
        for key in result.keys():
            result[key]['x'] = [d.strftime('%d-%b-%Y') for d in result[key]['x']]
            result[key]['y'] = [n[0] for n in result[key]['y'].tolist()]
        json_data = json.dumps(result)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

class port_optimize_api(APIView):
    def post(self, request):
        # portfolio = request.data.get('portfolio')
        portfolio = request.data
        print('Portfolio Recieved from React',portfolio)
        optimized_port = po.port_opt(portfolio)
        port_metrics = optimized_port.combine_metrics().to_json(orient='split')
        correlation = optimized_port.calculate_correlation_matrix().values.tolist()
        print('PORT OPT CORR',correlation)
        optimization_result = optimized_port.portfolio_optimization()
        # optimization_result['weights'] = optimization_result['weights'].tolist()

        efficient_frontier = optimized_port.efficient_frontier()
        efficient_frontier_dict = {}
        for col in efficient_frontier.columns:
            efficient_frontier_dict[col] = efficient_frontier[col].tolist()

        result = {
            'port_metrics' : port_metrics,
            'correlation' : correlation,
            'optimization_result' : optimization_result,
            'efficient_frontier' : efficient_frontier_dict
        }
        # print(result)
        json_data = json.dumps(result)

        return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)

# LOGIN VIEW

from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({'message': 'CSRF cookie set'})



from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['username'], password=data['password'])
        # print('USERNAME1', user.username)

        if user:
            login(request, user)
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            # print('USERNAME2',user.username)
            return JsonResponse({'message': 'Login successful' ,'username': user.username,'access_token': str(access_token),'refresh_token': str(refresh),},status=status.HTTP_200_OK)
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

from django.contrib.auth.models import User

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
            )
            return JsonResponse({'message': data['username']+' : Registration successful'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)




'''
PORTFOLIO VIEWS
'''
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import AccessToken

# @method_decorator(csrf_exempt, name='dispatch')
@csrf_exempt
@api_view(['GET','POST','DELETE'])
# @login_required
@permission_classes([IsAuthenticated])
def portfolios(request):
    print('Portfolios endpoint accessed by:', request.user.username)  # Debug statement
    # print("Headers:", request.headers)  # Check if Authorization header is present
    # print("User:", request.user)        # Should show authenticated user
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            # print("Decoded Token:", decoded_token)
            # print("User ID from Token:", decoded_token['user_id'])
            user_id = decoded_token['user_id']
            print("User ID from Token:", user_id)
            if request.method == "GET":
                print('GET REQUEST RECVD from ', request.user.username)
                query = """
                SELECT id, name
                FROM portfolio.portfolios
                WHERE user_id = %s
                """
                # portfolios = execute_query(query, [request.user.id], fetch_all=True)
                portfolios = UPortfolio.getPortfolios(user_id)
                portfolios = [{'id' : item[0],'name' : item[1]} for item in portfolios]
                print('portfolios', portfolios)
                return JsonResponse(portfolios, safe=False)

            if request.method == "POST":
                body = json.loads(request.body)
                name = body.get("name")
                print('NEW PORTFOLIO NAME ->',name)
                if not name:
                    return JsonResponse({"error": "Portfolio name is required"}, status=400)
                query = """
                INSERT INTO portfolio.portfolios (name, user_id) VALUES (%s, %s) RETURNING id, name
                """
                # portfolio = execute_query(query, [name, request.user.id], fetch_one=True)
                portfolio = UPortfolio.create(user_id, name)
                return JsonResponse(portfolio, safe=False)

            if request.method == "DELETE":
                body = json.loads(request.body)
                portfolio_id = body.get("portfolio_id")
                if not portfolio_id:
                    return JsonResponse({"error": "Portfolio ID is required"}, status=400)

                # Delete the item
                UPortfolio.deletePortfolio(portfolio_id)

                return JsonResponse({"message": "Item deleted successfully"})

        except Exception as e:
            print("Invalid token:", str(e))
            return Response({"message": "Invalid token"}, status=401)
    #
    # if request.user.is_authenticated:
    #     return Response({"message": "Authenticated", "user": request.user.username})
    # else:
    #     return Response({"message": "Not Authenticated"}, status=401)


@csrf_exempt
@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def portfolio_items(request):
    print('Portfolio Items endpoint accessed by:', request.user.username)  # Debug statement
    print("Headers:", request.headers)  # Check if Authorization header is present
    # print("User:", request.user)        # Should show authenticated user
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            # print("Decoded Token:", decoded_token)
            # print("User ID from Token:", decoded_token['user_id'])
            user_id = decoded_token['user_id']
            # print("User ID from Token:", user_id)
            if request.method == "GET":
                # print('FETCHING ITEMS FOR PORTFOLIO ->')

                # body = json.loads(request.body)
                # portfolio_id = body.get("portfolio_id")
                portfolio_id = request.data.get("portfolio_id")

                print('FETCHING ITEMS FOR PORTFOLIO ->',portfolio_id)

                # portfolios = execute_query(query, [request.user.id], fetch_all=True)
                items = UPortfolio.getItems(portfolio_id)
                items = [{'id': item[0], 'item_type' : item[1],'name': item[2],'quantity': item[3],'purchase_price': item[4]} for item in items]
                print('items', items)
                return JsonResponse(items, safe=False)

            if request.method == "POST":
                body = json.loads(request.body)
                action = body.get("action")
                if action == "fetchP":
                    portfolio_id = body.get("portfolio_id")
                    print('FETCHING ITEMS FOR PORTFOLIO ->',portfolio_id)

                    items = UPortfolio.getItems(portfolio_id)
                    items = [{'item_type': item[0], 'name' : item[1],'quantity': item[2],'avg_price': item[3],'cmp': item[4],'investment': item[5],'pnl': item[6]} for item in items]
                    print('items', items)
                    return JsonResponse(items, safe=False)
                if action == "fetchP_C":
                    portfolio_id = body.get("portfolio_id")
                    print('FETCHING SEGMENTS FOR PORTFOLIO ->',portfolio_id)

                    items = UPortfolio.getPortfolioComp(portfolio_id)
                    items = [{'item_type': item[0], 'name' : item[1],'quantity': item[2],'avg_price': item[3],
                              'cmv': item[4],'investment': item[5],'pnl': item[6],'country': item[7],'industry': item[8],
                              'sub_industry': item[9]} for item in items]
                    print('items', items)
                    return JsonResponse(items, safe=False)
                if action == "fetchPerformance":
                    portfolio_id = body.get("portfolio_id")
                    print('FETCHING PERFORMANCE FOR PORTFOLIO ->',portfolio_id)
                    performance = {}
                    items = UPortfolio.getPortfolioValueSeries(portfolio_id)
                    # items = items.reset_index()
                    if len(items) > 0:
                        items.rename(columns={'portfolio_value':'close'},inplace=True)
                    performance['values'] = items.to_json(orient='records')
                    items = UPortfolio.getPortfolioXIRRSeries(portfolio_id)
                    if len(items) > 0:
                        items.rename(columns={'running_xirr':'close'},inplace=True)
                    performance['xirr'] = items.to_json(orient='records')
                    print('items', performance)
                    return Response(performance, content_type="application/json", status=status.HTTP_200_OK)
                if action == "fetchT":
                    portfolio_id = body.get("portfolio_id")
                    from_date = body.get("from_date")
                    to_date = body.get("to_date")
                    search_text = body.get("search_text").lower()
                    print('FETCHING TRANSACTIONS FOR PORTFOLIO ->',portfolio_id,from_date,to_date,search_text)

                    items = UPortfolio.getTransactions(portfolio_id,from_date, to_date, search_text)
                    items = [{'tran_id': item[0], 'name' : item[2],'tran_type' : item[3],'quantity': item[4],'price': item[5],'tran_date': item[6],'type' : item[7]} for item in items]
                    print('items', items)
                    return JsonResponse(items, safe=False)
                if action == "add":
                    print('ADDING ITEMS FOR PORTFOLIO ->')
                    portfolio_id = body.get("portfolio_id")
                    item_type = body.get("item_type")
                    name = body.get("name")
                    transaction = body.get("transaction")
                    quantity = body.get("quantity")
                    purchase_price = body.get("purchase_price")
                    transaction_date = body.get("transaction_date")

                    # portfolio_id = request.data.get("portfolio_id")
                    # item_type = request.data.get("type")
                    # name = request.data.get("name")
                    # quantity = request.data.get("quantity")
                    # buy_price = request.data.get("buy_price")

                    if not all([portfolio_id, item_type, name,transaction, quantity, purchase_price,transaction_date]):
                        return JsonResponse({"error": "All fields are required"}, status=400)

                    # Verify portfolio ownership
                    # id = UPortfolio.verify(request.user.username,portfolio_id)
                    # if not id:
                    #     return JsonResponse({"error": "Unauthorized access"}, status=403)


                    # items = UPortfolio.addItem(portfolio_id, item_type, name, quantity, purchase_price)
                    items = UPortfolio.addTransaction(portfolio_id, item_type, name,transaction, quantity, purchase_price,transaction_date)
                    items = [{'id': item[0], 'item_type' : item[1],'name': item[2],'transaction': item[3],'quantity': item[4],'purchase_price': item[5],'transaction_date': str(item[6])} for item in items]
                    print('items', json.dumps(items))
                    return JsonResponse(json.dumps(items), safe=False)

            if request.method == "DELETE":
                body = json.loads(request.body)
                portfolio_id = body.get("portfolio_id")
                item_name = body.get("item_name")
                if not item_name:
                    return JsonResponse({"error": "Item ID is required"}, status=400)

                # Delete the item
                query = UPortfolio.deleteItem(portfolio_id,item_name)

                return JsonResponse({"message": "Item deleted successfully"})
        except Exception as e:
            print("Invalid token:", str(e))
            return Response({"message": "Invalid token"}, status=401)

@csrf_exempt
@api_view(['GET', 'POST','DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio(request):
    if request.method == "DELETE":
        body = json.loads(request.body)
        portfolio_id = body.get("portfolio_id")
        if not portfolio_id:
            return JsonResponse({"error": "Portfolio ID is required"}, status=400)

        # Verify ownership
        id = UPortfolio.verify(request.user.username,portfolio_id)
        if not id:
            return JsonResponse({"error": "Unauthorized access"}, status=403)

        # Delete the portfolio and its items
        delete_items_query = "DELETE FROM portfolio.portfolio_items WHERE portfolio_id = %s"
        delete_portfolio_query = "DELETE FROM portfolio.portfolios WHERE id = %s"
        UPortfolio.deletePortfolio(portfolio_id)

        return JsonResponse({"message": "Portfolio deleted successfully"})

@csrf_exempt
@api_view(['GET', 'POST','DELETE'])
@permission_classes([IsAuthenticated])
def make_payment(request):
    if request.method == "POST":
        # Initialize Razorpay client
        # client = rp.Razorpay()
        client = razorpay.Client(auth=(ms.RAZORPAY_KEY_ID, ms.RAZORPAY_KEY_SECRET))
        body = json.loads(request.body)
        order_receipt = body.get("order_receipt")
        username = body.get("username")
        amount = body.get("amount")

        # Get payment details from the request
        amount = int(amount) * 100  # Convert to paise
        currency = "INR"
        receipt = username+'_'+order_receipt

        print('Payment Details recieved from Frontend -> Amount ',amount,' Receipt ',receipt)
        # Create an order
        payment = client.order.create({
            "amount": amount,
            "currency": currency,
            "receipt": receipt
        })

        # Send the order ID to the frontend
        return JsonResponse(payment)

    return JsonResponse({"error": "Invalid request method"}, status=400)
#
#
#
# @csrf_exempt
# def register_user(request):
#     engine = mu.sql_engine()
#
#     if request.method == "POST":
#         data = json.loads(request.body)
#         email = data["email"]
#         password = data["password"]
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()
#         first_name = data["first_name"]
#         last_name = data["last_name"]
#         address = data.get("address", "")
#         work_details = data.get("work_details", "")
#
#         query = """
#             INSERT INTO portfolio.users (email, password_hash, first_name, last_name, address, work_details)
#             VALUES (%s, %s, %s, %s, %s, %s);
#         """
#         try:
#             engine.execute_query(query, (email, hashed_password, first_name, last_name, address, work_details))
#             return JsonResponse({"message": "User registered successfully"}, status=201)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)
#
#
# @csrf_exempt
# def login_user(request):
#     engine = mu.sql_engine()
#
#     if request.method == "POST":
#         data = json.loads(request.body)
#         email = data["email"]
#         password = data["password"]
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()
#
#         query = "SELECT user_id FROM portfolio.users WHERE email = %s AND password_hash = %s;"
#         result = engine.execute_query(query, (email, hashed_password))
#
#         if result:
#             return JsonResponse({"user_id": result[0][0], "message": "Login successful"}, status=200)
#         else:
#             return JsonResponse({"error": "Invalid email or password"}, status=401)

# @csrf_exempt
# def delete_portfolio_items(request):
#     engine = mu.sql_engine()
#
#     if request.method == "POST":
#         data = json.loads(request.body)
#         portfolio_id = data["portfolio_id"]
#         item_ids = tuple(data["item_ids"])
#
#         query = f"DELETE FROM portfolio.portfolio_items WHERE portfolio_id = %s AND item_id IN {item_ids};"
#         engine.execute_query(query, (portfolio_id,))
#         return JsonResponse({"message": "Items deleted successfully"}, status=200)
#
# @csrf_exempt
# def create_portfolio(request):
#     engine = mu.sql_engine()
#
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_id = data.get("user_id")
#         portfolio_name = data.get("portfolio_name")
#         query = """
#             INSERT INTO portfolio.portfolios (user_id, portfolio_name)
#             VALUES (%s, %s) RETURNING portfolio_id;
#         """
#         result = engine.execute(query, (user_id, portfolio_name))
#         return JsonResponse({"portfolio_id": result[0][0]}, status=201)
#
# def get_portfolios(request, user_id):
#     engine = mu.sql_engine()
#
#     query = "SELECT portfolio_id, portfolio_name, created_at FROM portfolio.portfolios WHERE user_id = %s;"
#     portfolios = engine.execute(query, (user_id,))
#     return JsonResponse({"portfolios": portfolios})

# class MyDataFrameAPIView(APIView):
# @api_view(['GET', 'POST'])
# def stocksapi(request,symbol):
#     df = StockAPI(symbol).pricevol_data
#     json_data = df.to_json(orient='records')
#     # json_data = df.to_json()
#
#     # Return the JSON data
#     # return Response(json_data, content_type="application/json", status=status.HTTP_200_OK)
#     return JsonResponse(json_data, safe=False)

