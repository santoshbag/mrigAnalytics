import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from django.shortcuts import render
from django.http import HttpResponse
import nsepy
from mrigwebapp.myhtml import myhtml
import mrigwebapp.forms as fm
import interface.web.webdashboard as wdb
import pandas as pd
import mrigutilities as mu
import datetime
import json

# Create your views here.

def home(request):
    return render(request, "index.html", {})

def stock(request,symbol='NIFTY 50'):
    engine = mu.sql_engine()
    stocklist = engine.execute("select symbol, stock_name from security_master").fetchall()
#    stocklist = list(stocklist)
    price_list,return_list,risk_list,ratios,oc= "","","","",""
    price_graph,return_graph,macd_graph,boll_graph = "","","",""
    stock_desc = ""
    news = ""

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
         
    
    if (symbol and symbol != ""): 
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
        
        oc = oc.reset_index()
        oc['Expiry'] = "<a style=\"color:#f7ed4a;text-decoration:underline;\" href=\"/option/"+symbol+":"+oc['Expiry'].apply(lambda x:x.strftime('%d%m%Y')) +":"+ oc['Strike_Price'].apply(lambda x:str(x))+":CE\">"+oc['Expiry'].apply(lambda x:x.strftime('%d-%b-%Y'))+"</a>"
        oc['PUT_Expiry'] = oc['Expiry'].apply(lambda x:x.replace("CE","PE"))
        oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
        oc = [oc_head] + oc.values.tolist()
        oc = myhtml.list_to_html(oc,"small")
         
#         quote = nsepy.get_quote(symbol)
#         quote = myhtml.dict_to_html(quote)
       
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
                                          "news":news})


def os(request):
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
         
    
    if (strategy == "Covered Call"): 
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

    if (strategy == "Bull Put Spread"): 
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

    if (strategy == "Bear Call Spread"): 
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
       
    return render(request, "os.html", {"slist":slist,
                                       "strategy":strategy,
                                       "strategy_desc" : strategy_desc,
                                       "oc":oc})
def osa(request,strategyid):
    
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
                                       "results" : results
                                       })


def ss(request):

    criteria = {}
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
    
    
    return render(request, "ss.html", {
                                       "bm_table":bm_table,
                                       "bm_graph":bm_graph,
                                       "bm_desc":bm_desc,
                                       "scg_table":scg_table,
                                       "scg_graph":scg_graph,
                                       "scg_desc":scg_desc,
#                                       "tafa_table":tafa_table,
#                                       "tafa_graph":tafa_graph,
#                                       "tafa_desc":tafa_desc,
                                       "nh_table":nh_table,
                                       "nh_graph":nh_graph,
                                       "nh_desc":nh_desc,
                                       "gi_table":gi_table,
                                       "gi_graph":gi_graph,
                                       "gi_desc":gi_desc,
                                       "customscreen":customscreen,
                                       "strategyform":strategyform
                                       })




def option(request,opid):
    
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
        params['option_type']= keyval[3]
        option_desc = params['symbol']+" "+params['expiry'].strftime('%b')+ " "+keyval[2] + " "+ keyval[3]
        
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
                                           "oi_graph":oi_graph})


def news(request):
    
    news = wdb.mrigweb_news()
    
#    news_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ").capitalize() for x in list(news)]
#    news = [news_head] + news.values.tolist()
#    news = myhtml.list_to_html(news)
#    oc = "<img border=\"0\" src=\"{% static 'assets/images/pnl_icon.png' %}\" width=\"10\" height=\"10\"/>"
#    newstype = news[0]
#    newsdate = news[1]
#    newstitle = news[2]
#    newsdesc = news[3]


    return render(request, "news.html", {"news":news})    
    
def stock1(request):
    
#    oc = mu.test_df()
#    oc = oc[['Symbol','Open','Last']]
#    oc_head = [x.replace("CALL_","").replace("PUT_","").replace("_"," ") for x in list(oc)]
#    oc = [oc_head] + oc.values.tolist()
#    oc = myhtml.list_to_html(oc)
#    oc = "<img border=\"0\" src=\"{% static 'assets/images/pnl_icon.png' %}\" width=\"10\" height=\"10\"/>"

    oc = ['a',3]
    return render(request, "stock1.html", {"oc":oc})
    