# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 19:33:54 2018

This module deals with data downloads and manipulation from Money Control
@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import requests
import datetime,pandas,time
from bs4 import BeautifulSoup
import mrigstatics,mrigutilities
from time import sleep
import pandas as pd

def get_MCStockCodes():
    response = requests.Response()
    url = mrigstatics.MC_URLS['MC_CODES_URL']
    timecounter = 0
    while True:
        timecounter = timecounter + 1
        if mrigutilities.is_connected():    
            s = requests.Session()
            response = s.get(url)
        if mrigutilities.is_connected() or timecounter > 5:
            break
        else:
            sleep(60)
    soup = BeautifulSoup(response.text, 'html.parser')
        
    engine = mrigutilities.sql_engine()
    timestamp = datetime.datetime.now()

    stock_code_dict = {}
    stock_table = soup.find_all(class_='pcq_tbl MT10')
    stock_rows = stock_table[0].find_all(class_='bl_12')
    for row in stock_rows:
        linkstring = row['href'].split('/')
        try:
            stock_code_dict[row.text] = linkstring[-1] +":" + linkstring[-2]
        except:
            pass
    
    sql = "INSERT INTO codes (code_date, code_name, code_value) VALUES ( '" + timestamp.strftime('%Y-%m-%d') + "', 'MONEY_CONTROL_STOCK_CODES' , " \
         + "'" + str(stock_code_dict)[1:-1].replace("'","").replace(",","|") +"')"
    #print(sql)
    engine.execute(sql)
    
def get_MCRatios(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    response = requests.Response()
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_RATIOS_URL'] + symbol.split(":")[-1].strip()+"/ratiosVI/"+symbol.split(":")[-2].strip()
        timecounter = 0
        while True:
            print(symbol)
            timecounter = timecounter + 1
            if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                s = requests.Session()
                response = s.get(url)
                print(symbol+" downloaded")
            if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                break
            else:
                sleep(60)
                    
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        ratios_dict = {}
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            ratio_table = soup.find_all(class_='table4')[2]  # table 3 contains the ratios.
            rows = ratio_table.find_all("tr")
            ratio_dates = [row.text for row in rows[2].find_all("td")[1:]]
            for i in range(1,len(ratio_dates)+1):
                ratio_date = "30-"+ratio_dates[i-1].split(" ")[0]+"-"+ratio_dates[i-1].split(" ")[1]
                ratio_date = datetime.datetime.strptime(ratio_date,'%d-%b-%y')
                for row in rows[4:-4]:
                    try:
                        ratio_name = row.find_all("td")[0].text.strip().replace(",","")
                        if ratio_name != "":
                            ratios_dict[ratio_name] = row.find_all("td")[i].text.strip().replace(",","")
                    except:
                        pass
                ratios_dict_str =  str(ratios_dict)[1:-1].replace("'","").replace(",","|").replace("%","per")  
                sql = "INSERT INTO ratios_1 (symbol, ratio_date, download_date, ratios_dictionary) VALUES ( '" \
                                                  + sym + "','" \
                                                  + ratio_date.strftime('%Y-%m-%d') + "','" \
                                                  + timestamp.strftime('%Y-%m-%d') + "','" \
                                                  + ratios_dict_str +"')"
                #print(sql)
                try:
                    engine.execute(sql)
                    successful_download.append(sym)
                except:
                    pass
        except:
            pass
        print("Downloaded Ratios for "+symbol+" | "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        #print(ratios_dict_str)
        #engine.execute(sql)
def populate_ratios_table():
    
    engine = mrigutilities.sql_engine()
    ratioList = []
    sql = "select * from ratios_1"
    ratios = engine.execute(sql).fetchall()
    sql  = "select column_name from information_schema.columns where table_schema ='public' and table_name ='ratios'"
    columns = engine.execute(sql).fetchall()
    columns = [column[0] for column in columns]
    sql  = "select code_value from codes where code_name ='ratios'"
    column_maps = engine.execute(sql).fetchall()
    column_maps = {code.split(":")[0]:code.split(":")[1] for code in column_maps[0][0].split("|")}
    for line in ratios:
        datavector = ["" for column in columns]
        datavector[0] = line[0]
        datavector[1] = line[1]
        datavector[2] = line[2]
        ratioline = [code.split(":") for code in line[3].split("|")]
        for item in ratioline:
            try:
                datavector[columns.index(column_maps[item[0]])] = item[1]
            except:
                pass
        ratioList.append(datavector)
    #print(ratioList)
    ratioList = pandas.DataFrame(ratioList,columns=columns)
    ratioList = mrigutilities.clean_df_db_dups(ratioList,'ratios',engine,dup_cols=["symbol","ratio_date"],leftIdx=True)
    ratioList = ratioList[0]
    #print(ratioList)
    ratioList.to_sql('ratios',engine, if_exists='append', index=False)
    

def get_FaceValue(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_CODES_URL'] +"finance-general/"+ symbol.split(":")[-1].strip()+"/"+symbol.split(":")[-2].strip()
        #print(url)
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        nsesym = soup.find_all(class_="FL gry10")[0]
        nsesym = nsesym.contents[2].split(":")[1].strip()
#        marketcap = soup.find_all(class_="FR gD_12")[0].text.strip()
        facevalue = soup.find_all(class_="FR gD_12")[10].text.strip()
        update_tuple = ""
        update_tuple = update_tuple + "('"+nsesym+"','"+facevalue+"'),"
    sql = "UPDATE security_master as sm set "\
                              + "sm.face_value = c.face_value "\
                              + "from (values "+update_tuple[:-1] + ") "\
                              + "as c(nsesym,face_value) "\
                              + "where c.nsesym = sm.symbol"
        #print(sql)
    #try:
    engine.execute(sql)
    #except:
    #    pass
    #print(ratios_dict_str)
        #engine.execute(sql)

def get_OutShares(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    #sql = "select symbol, close from stock_history where date in (select max(date) from stock_history)"
    #prices = pandas.read_sql(sql,engine,index_col='symbol')
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    slist = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_CODES_URL'] +"finance-general/"+ symbol.split(":")[-1].strip()+"/"+symbol.split(":")[-2].strip()
        #print(url)
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        nsesym = soup.find_all(class_="FL gry10")[0]
        nsesym = nsesym.contents[2].split(":")[1].strip()
        sector = soup.find_all(class_="FL gry10")[0].contents[7].text.strip()
        marketcap = soup.find_all(class_="FR gD_12")[0].text.strip().replace(",","")
        price = soup.find_all(class_="th03 gD_12")[22].text.strip().replace(",","")
        try:
            outshares = float(marketcap)/float(price)*10000000
            slist.append([nsesym,sector,marketcap,price,outshares])
        except:
            pass
#        update_tuple = ""
#        update_tuple = update_tuple + "('"+nsesym+"','"+int(float(marketcap)*10000000/float(prices.loc[nsesym]['close']))+"'),"
#    sql = "UPDATE security_master as sm set "\
#                              + "sm.outstanding_shares = c.outshares "\
#                              + "from (values "+update_tuple[:-1] + ") "\
#                              + "as c(nsesym,outshares) "\
#                              + "where c.nsesym = sm.symbol"
    slist = pandas.DataFrame(slist,columns=['symbol','sector','marketcap_cr','price','outshares'])
    slist.to_csv("stock_sector1.csv",index=False,header=True)
    #try:
        #engine.execute(sql)
    #except:
    #    pass
    #print(ratios_dict_str)
        #engine.execute(sql)

def get_OutShares_NSE(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select distinct symbol from security_master"
    codes = engine.execute(sql).fetchall()
    codes = [code[0] for code in codes]
    #sql = "select symbol, close from stock_history where date in (select max(date) from stock_history)"
    #prices = pandas.read_sql(sql,engine,index_col='symbol')
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    slist = []
    for symbol in symbollist:
        url = "https://nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol="+symbol.strip()+"&illiquid=0&smeFlag=0&itpFlag=0"
        #url = mrigstatics.MC_URLS['MC_CODES_URL'] +"finance-general/"+ symbol.split(":")[-1].strip()+"/"+symbol.split(":")[-2].strip()
        #print(url)
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        div = soup.find("div" , {"id":"responseDiv"})
        marketcap = div.text[div.text.find(":", div.text.find("cm_ffm"))+2:div.text.find(".", div.text.find("cm_ffm"))+3].replace(",","")
        vwap = div.text[div.text.find(":", div.text.find("averagePrice"))+2:div.text.find(".", div.text.find("averagePrice"))+3].replace(",","")
        fv = div.text[div.text.find(":", div.text.find("faceValue"))+2:div.text.find(".", div.text.find("faceValue"))+3]        
        name = div.text[div.text.find(":", div.text.find("companyName"))+2:div.text.find(",", div.text.find("companyName"))-1]
        exdate = div.text[div.text.find(":", div.text.find("exDate"))+2:div.text.find(",", div.text.find("exDate"))-1]
        recorddate = div.text[div.text.find(":", div.text.find("recordDate"))+2:div.text.find(",", div.text.find("recordDate"))-1]
        dividend = div.text[div.text.find(":", div.text.find("purpose"))+2:div.text.find(",", div.text.find("purpose"))-1]
        
        try:
            outshares = float(marketcap)/float(vwap)*10000000
            slist.append([symbol,name,fv,marketcap,vwap,outshares,dividend,exdate,recorddate])
        except:
            pass
#        update_tuple = ""
#        update_tuple = update_tuple + "('"+nsesym+"','"+int(float(marketcap)*10000000/float(prices.loc[nsesym]['close']))+"'),"
#    sql = "UPDATE security_master as sm set "\
#                              + "sm.outstanding_shares = c.outshares "\
#                              + "from (values "+update_tuple[:-1] + ") "\
#                              + "as c(nsesym,outshares) "\
#                              + "where c.nsesym = sm.symbol"
    slist = pandas.DataFrame(slist,columns=['symbol','name','facev','marketcap_cr','vwap','outshares','dividend','exdate','recorddate'])
    slist.to_csv("stock_nse.csv",index=False,header=True)
    #try:
        #engine.execute(sql)
    #except:
    #    pass
    #print(ratios_dict_str)
        #engine.execute(sql)
        
def get_NSELive():
    
    quote = {}
    sql = "select * from live where symbol='%s' order by date desc limit 1"
    engine = mrigutilities.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    quote_df = pd.read_sql(sql%('NIFTY 50'),engine)
    if not quote_df.empty:
        quote_df.drop('date',axis=1,inplace=True)
        quote = quote_df.to_dict()
        for key in quote.keys():
            quote[key] = quote[key][0]
        quote['lastPrice'] = quote['quote']
    

    try:
        url = "http://www.moneycontrol.com/indian-indices/cnx-nifty-9.html"
        #url = mrigstatics.MC_URLS['MC_CODES_URL'] +"finance-general/"+ symbol.split(":")[-1].strip()+"/"+symbol.split(":")[-2].strip()
        #print(url)
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sym = soup.find("div" , {"class":"FL gr_35"})
        if not sym:
            sym = soup.find("div" , {"class":"FL r_35"})
        if sym:
            lastPrice = sym.text
            quote['lastPrice'] = lastPrice
        sym = soup.find_all(class_="tbldtldata b_15")
#        print(sym)
        if sym:
            sym = sym[0].find_all("td")
            quote['open'] = sym[3].text.split(':')[1].strip().replace(',','')
            quote['dayhigh'] = sym[4].text.split(':')[1].strip().replace(',','')
            quote['high52'] = sym[5].text.strip().replace(',','')
            quote['previousclose'] = sym[6].text.split(':')[1].strip().replace(',','')
            quote['daylow'] = sym[7].text.split(':')[1].strip().replace(',','')
            quote['low52'] = sym[8].text.strip().replace(',','')
    except:
        pass
    print(quote)    
    return quote
            
       
def get_MCQtrly_Results(symbol=None):
    
    response = requests.Response()
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_QTRLY_RESULTS_URL'] + symbol.split(":")[-1].strip()+"/results/quarterly-results/"+symbol.split(":")[-2].strip()
        timecounter = 0
        while True:
            timecounter = timecounter + 1
            if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                s = requests.Session()
                response = s.get(url)
            if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                break
            else:
                sleep(60)
                
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        qtrly_results_dict = {}
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            qtrly_results_table = soup.find_all(class_='table4')[2]  # table 3 contains the ratios.
            rows = qtrly_results_table.find_all("tr")
            qtrly_results_dates = [row.text for row in rows[2].find_all("td")[1:]]
            for i in range(1,len(qtrly_results_dates)+1):
                qtrly_results_date = "30-"+qtrly_results_dates[i-1].split("'")[0].strip()+"-"+qtrly_results_dates[i-1].split("'")[1].strip()
                qtrly_results_date = datetime.datetime.strptime(qtrly_results_date,'%d-%b-%y')
                for row in rows[4:-4]:
                    try:
                        qtrly_results_name = row.find_all("td")[0].text.strip().replace(",","")
                        if qtrly_results_name != "":
                            qtrly_results_dict[qtrly_results_name] = row.find_all("td")[i].text.strip().replace(",","")
                        
                    except:
                        pass
                qtrly_results_dict_str =  str(qtrly_results_dict)[1:-1].replace("'","").replace(",","|").replace("%","per")  
                sql = "INSERT INTO qtrly_results (symbol, qtrly_results_date, download_date, qtrly_results_dictionary, source) VALUES ( '" \
                                                  + sym + "','" \
                                                  + qtrly_results_date.strftime('%Y-%m-%d') + "','" \
                                                  + timestamp.strftime('%Y-%m-%d') + "','" \
                                                  + qtrly_results_dict_str + "', 'MONEYCONTROL')"
                #print(sql)
                try:
                    engine.execute(sql)
                    successful_download.append(sym)
                except:
                    pass
            
            print("Downloaded Qtrly Results for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        except:
            pass
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_BalanceSheet(symbol=None):
    
    response = requests.Response()
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    symitercount = 0
    startlist = 0# +78 +8 +201 + 13 +129 #+218+94+65+26
    for symbol in symbollist[startlist:]:
        symitercount = symitercount +1
        url = mrigstatics.MC_URLS['MC_BALANCE_SHEET_URL'] + symbol.split(":")[-1].strip()+"/balance-sheetVI/"+symbol.split(":")[-2].strip()
        timecounter = 0
        while True:
            timecounter = timecounter + 1
            if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                s = requests.Session()
                response = s.get(url)
            if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                break
            else:
                sleep(60)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        balance_sheet_dict = {}
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            balance_sheet_table = soup.find_all(class_='table4')[2]  # table 3 contains the ratios.
            rows = balance_sheet_table.find_all("tr")
            balance_sheet_dates = [row.text for row in rows[0].find_all("td")[1:]]
            for i in range(1,len(balance_sheet_dates)+1):
                balance_sheet_date = "30-"+balance_sheet_dates[i-1].split(" ")[0].strip()+"-"+balance_sheet_dates[i-1].split(" ")[1].strip()
                balance_sheet_date = datetime.datetime.strptime(balance_sheet_date,'%d-%b-%y')
                for row in rows[4:-4]:
                    try:
                        balance_sheet_name = row.find_all("td")[0].text.strip().replace(",","")
                        if balance_sheet_name != "":
                            balance_sheet_dict[balance_sheet_name] = row.find_all("td")[i].text.strip().replace(",","")
                        
                    except:
                        pass
                balance_sheet_dict_str =  str(balance_sheet_dict)[1:-1].replace("'","").replace(",","|").replace("%","per")  
                sql = "INSERT INTO balance_sheet (symbol, balance_sheet_date, download_date, balance_sheet_dictionary, source) VALUES ( '" \
                                                  + sym + "','" \
                                                  + balance_sheet_date.strftime('%Y-%m-%d') + "','" \
                                                  + timestamp.strftime('%Y-%m-%d') + "','" \
                                                  + balance_sheet_dict_str + "', 'MONEYCONTROL')"
                #print(sql)
                try:
                    engine.execute(sql)
                    successful_download.append(sym)
                except:
                    pass
            
            print("Downloaded Balance Sheet Results for "+str(len(set(successful_download)))+ " of "+ str(symitercount)+" stocks")
        except:
            pass
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_ProfitLossStatement(symbol=None):
    
    response = requests.Response()
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    startlist = 0# + 112 + 22 + 88 +12 + 60
    for symbol in symbollist[startlist:]:
        url = mrigstatics.MC_URLS['MC_PROFIT_LOSS_URL'] + symbol.split(":")[-1].strip()+"/profit-lossVI/"+symbol.split(":")[-2].strip()
        timecounter = 0
        while True:
            timecounter = timecounter + 1
            if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                s = requests.Session()
                response = s.get(url)
            if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                break
            else:
                sleep(60)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        pnl_statement_dict = {}
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            pnl_statement_table = soup.find_all(class_='table4')[2]  # table 3 contains the ratios.
            rows = pnl_statement_table.find_all("tr")
            pnl_statement_dates = [row.text for row in rows[0].find_all("td")[1:]]
            for i in range(1,len(pnl_statement_dates)+1):
                pnl_statement_date = "30-"+pnl_statement_dates[i-1].split(" ")[0].strip()+"-"+pnl_statement_dates[i-1].split(" ")[1].strip()
                pnl_statement_date = datetime.datetime.strptime(pnl_statement_date,'%d-%b-%y')
                for row in rows[4:-4]:
                    try:
                        pnl_statement_name = row.find_all("td")[0].text.strip().replace(",","")
                        if pnl_statement_name != "":
                            pnl_statement_dict[pnl_statement_name] = row.find_all("td")[i].text.strip().replace(",","")
                    except:
                        pass
                pnl_statement_dict_str =  str(pnl_statement_dict)[1:-1].replace("'","").replace(",","|").replace("%","per")  
                sql = "INSERT INTO pnl_statement (symbol, pnl_statement_date, download_date, pnl_statement_dictionary, source) VALUES ( '" \
                                                  + sym + "','" \
                                                  + pnl_statement_date.strftime('%Y-%m-%d') + "','" \
                                                  + timestamp.strftime('%Y-%m-%d') + "','" \
                                                  + pnl_statement_dict_str + "', 'MONEYCONTROL')"
                #print(sql)
                try:
                    engine.execute(sql)
                    successful_download.append(sym)
                except:
                    pass
            
            print("Downloaded Profit and Loss Results for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        except:
            pass

        #print(ratios_dict_str)
        #engine.execute(sql)

def get_CashFLowStatement(symbol=None):
    
    response = requests.Response()
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    startlist = 0# + 41 +63 + 191 +232 +250#+94+65+26
    for symbol in symbollist[startlist:]:
        url = mrigstatics.MC_URLS['MC_CASHFLOW_STATEMENT_URL'] + symbol.split(":")[-1].strip()+"/cash-flowVI/"+symbol.split(":")[-2].strip()
        timecounter = 0
        while True:
            timecounter = timecounter + 1
            if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                s = requests.Session()
                response = s.get(url)
            if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                break
            else:
                sleep(60)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        cashflow_statement_dict = {}
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            cashflow_statement_table = soup.find_all(class_='table4')[2]  # table 3 contains the ratios.
            rows = cashflow_statement_table.find_all("tr")
            cashflow_statement_dates = [row.text for row in rows[0].find_all("td")[1:]]
            for i in range(1,len(cashflow_statement_dates)+1):
                cashflow_statement_date = "30-"+cashflow_statement_dates[i-1].split(" ")[0].strip()+"-"+cashflow_statement_dates[i-1].split(" ")[1].strip()
                cashflow_statement_date = datetime.datetime.strptime(cashflow_statement_date,'%d-%b-%y')
                for row in rows[4:-4]:
                    try:
                        cashflow_statement_name = row.find_all("td")[0].text.strip().replace(",","")
                        if cashflow_statement_name != "":
                            cashflow_statement_dict[cashflow_statement_name] = row.find_all("td")[i].text.strip().replace(",","")
                    except:
                        pass
                cashflow_statement_dict_str =  str(cashflow_statement_dict)[1:-1].replace("'","").replace(",","|").replace("%","per")  
                sql = "INSERT INTO cashflow_statement (symbol, cashflow_statement_date, download_date, cashflow_statement_dictionary, source) VALUES ( '" \
                                                  + sym + "','" \
                                                  + cashflow_statement_date.strftime('%Y-%m-%d') + "','" \
                                                  + timestamp.strftime('%Y-%m-%d') + "','" \
                                                  + cashflow_statement_dict_str + "', 'MONEYCONTROL')"
                #print(sql)
                try:
                    engine.execute(sql)
                    successful_download.append(sym)
                except:
                    pass
            print("Downloaded Cash Flow Statement Results for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        except:
            pass
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_CorporateActions(symbol=None):
    
    response = requests.Response()
    engine = mrigutilities.sql_engine()
    sql = "select code_value, code_date from codes where code_name='MONEY_CONTROL_STOCK_CODES' order by code_date desc limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    bm_sym = []
    div_sym = []
    split_sym = []
    bonus_sym = []
    rights_sym = []

#    pos = symbollist.index('DI:daburindia')
    startlist = symbollist.index('FR:futureretail')
    for symbol in symbollist:#[startlist:]:
        print(symbol+"---------")
        meeting_url = mrigstatics.MC_URLS['MC_CORP_ACTION_URL'] + symbol.split(":")[-1].strip()+"/board-meetings/"+symbol.split(":")[-2].strip()
        dividend_url = mrigstatics.MC_URLS['MC_CORP_ACTION_URL'] + symbol.split(":")[-1].strip()+"/dividends/"+symbol.split(":")[-2].strip()
        bonus_url = mrigstatics.MC_URLS['MC_CORP_ACTION_URL'] + symbol.split(":")[-1].strip()+"/bonus/"+symbol.split(":")[-2].strip()
        rights_url = mrigstatics.MC_URLS['MC_CORP_ACTION_URL'] + symbol.split(":")[-1].strip()+"/rights/"+symbol.split(":")[-2].strip()
        splits_url = mrigstatics.MC_URLS['MC_CORP_ACTION_URL'] + symbol.split(":")[-1].strip()+"/splits/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        
        # Download Meeting details
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                    s = requests.Session()
                    response = s.get(meeting_url)
                if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                    break
                else:
                    sleep(60)
        except ConnectionError as e:
            print("Santosh Error---")
            time.sleep(2*60)
            response = s.get(meeting_url)
            
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
        
        try:
            sym = soup.find_all(class_="FL gry10")[0]
            sym = sym.contents[2].split(":")[1].strip()
            meeting_table = soup.find_all(class_='tbldivid')
            rows = meeting_table[0].find_all("tr")
            select_sql = "SELECT to_char(meeting_date, 'YYYY-MM-DD'), meeting_detail from corporate_actions where symbol = '"+sym+"' and corporate_action_type = 'MEETING'"
            meeting_sql = "INSERT INTO corporate_actions (symbol, corporate_action_type, download_date, source, meeting_date, meeting_detail) VALUES " 
            insert_data_list = []
            for row in rows:
                try:
                    meeting_date = row.find_all("td")[0].text.strip().replace(",","")
                    meeting_date = datetime.datetime.strptime(meeting_date,'%d-%m-%Y')
                    if meeting_date != "":
                        meeting_detail = row.find_all("td")[1].text.strip().replace(",","").replace("'","_").replace("%"," per")
                        insert_data_list.append((meeting_date.strftime('%Y-%m-%d'),meeting_detail))
    #                    meeting_sql = meeting_sql + "('"+sym + "','MEETING','" \
    #                          + timestamp.strftime('%Y-%m-%d') + "','" \
    #                          + meeting_date.strftime('%Y-%m-%d') + "','" \
    #                          + meeting_detail + "', 'MONEYCONTROL'),"           
                except:
                    pass
                #print(sql)
            #print(meeting_sql)
            #engine.execute(meeting_sql[:-1])
            existing_data = engine.execute(select_sql).fetchall()
            existing_data = [tuple(a) for a in existing_data]
            #print(insert_data_list)
            #print("#################")
            insert_data_list = set(insert_data_list) - set(existing_data)
            #print(existing_data)
            #print("-----")
            #print(insert_data_list)
            for data in insert_data_list:
                meeting_sql = meeting_sql + "('"+sym + "','MEETING','" \
                              + timestamp.strftime('%Y-%m-%d') + "','MONEYCONTROL','" \
                              + data[0] + "','" \
                              + data[1] + "'),"
            #engine.execute(meeting_sql[:-1])
            try:
                engine.execute(meeting_sql[:-1])
                successful_download.append(sym)
                bm_sym.append(sym)
                #print("Downloaded Board Meetings for "+sym)
            except:
                pass
        except:
            pass
            
            # Download Dividends
        #response = s.get(dividend_url)
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                    s = requests.Session()
                    response = s.get(dividend_url)
                if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                    break
                else:
                    sleep(60)
        except ConnectionError as e:
            print("Santosh Error---")
            time.sleep(2*60)
            response = s.get(dividend_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()

        try:
            dividend_table = soup.find_all(class_='tbldivid')
            rows = dividend_table[0].find_all("tr")
            select_sql = "SELECT to_char(announcement_date, 'YYYY-MM-DD'), record_date,dividend_per, dividend_remark from corporate_actions where symbol = '"+sym+"' and corporate_action_type = 'DIVIDEND'"
            dividend_sql = "INSERT INTO corporate_actions (symbol, corporate_action_type, download_date, source, announcement_date,record_date, dividend_per, dividend_remark) VALUES "
            insert_data_list = []
            for row in rows:
                try:
                    announcement_date = row.find_all("td")[0].text.strip().replace(",","")
                    announcement_date = datetime.datetime.strptime(announcement_date,'%d-%m-%y')
                    record_date = row.find_all("td")[1].text.strip().replace(",","")
                    #record_date = datetime.datetime.strptime(record_date,'%d-%m-%y')
                    if announcement_date != "":
                        dividend_per = row.find_all("td")[3].text.strip().replace(",","").replace("%","per")
                        dividend_remark = row.find_all("td")[4].text.strip().replace(",","").replace("%","per")
                        insert_data_list.append((announcement_date.strftime('%Y-%m-%d'),record_date,dividend_per,dividend_remark))
    #                    dividend_sql = dividend_sql + "( '" \
    #                                  + sym + "','DIVIDEND','" \
    #                                  + timestamp.strftime('%Y-%m-%d') + "','" \
    #                                  + announcement_date.strftime('%Y-%m-%d') + "','" \
    #                                  + record_date + "','" \
    #                                  + dividend_per + "','" +dividend_remark + "','MONEYCONTROL'),"
                except:
                    pass
            
            existing_data = engine.execute(select_sql).fetchall()
            existing_data = [tuple(a) for a in existing_data]
            #print(insert_data_list)
            #print("#################")
            insert_data_list = set(insert_data_list) - set(existing_data)
            #print(existing_data)
            #print("-----")
            #print(insert_data_list)
            for data in insert_data_list:
                dividend_sql = dividend_sql + "('"+sym + "','DIVIDEND','" \
                              + timestamp.strftime('%Y-%m-%d') + "','MONEYCONTROL','" \
                              + data[0] + "','" \
                              + data[1] + "','" \
                              + data[2] + "','" \
                              + data[3] + "'),"
            #print(dividend_sql)
            #engine.execute(dividend_sql[:-1])
            try:
                engine.execute(dividend_sql[:-1])
                successful_download.append(sym)
                div_sym.append(sym)
                #print("Downloaded Dividends for "+sym)
            except:
                pass
        except:
            pass
        #print(ratios_dict_str)
        #engine.execute(sql)

        # Download Bonus
        response = s.get(bonus_url)
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                    s = requests.Session()
                    response = s.get(bonus_url)
                if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                    break
                else:
                    sleep(60)
        except ConnectionError as e:
            print("Santosh Error---")
            time.sleep(2*60)
            response = s.get(bonus_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()

        try:
            bonus_table = soup.find_all(class_='tbldivid')
            rows = bonus_table[0].find_all("tr")
            select_sql = "SELECT to_char(announcement_date, 'YYYY-MM-DD'), record_date, ex_date, bonus_ratio from corporate_actions where symbol = '"+sym+"' and corporate_action_type = 'BONUS'"
            bonus_sql = "INSERT INTO corporate_actions (symbol, corporate_action_type, download_date, source, announcement_date,record_date, ex_date, bonus_ratio) VALUES "
            insert_data_list = []
            for row in rows:
                try:
                    announcement_date = row.find_all("td")[0].text.strip().replace(",","")
                    announcement_date = datetime.datetime.strptime(announcement_date,'%d-%m-%Y')
                    record_date = row.find_all("td")[1].text.strip().replace(",","")
                    ex_date = row.find_all("td")[3].text.strip().replace(",","")
    
                    if announcement_date != "":
                        bonus_ratio = row.find_all("td")[1].text.strip().replace(",","").replace("%"," per")
                        insert_data_list.append((announcement_date.strftime('%Y-%m-%d'),record_date,ex_date,bonus_ratio))
    #                    bonus_sql = bonus_sql + "( '" \
    #                                          + sym + "','BONUS','" \
    #                                          + timestamp.strftime('%Y-%m-%d') + "','" \
    #                                          + announcement_date.strftime('%Y-%m-%d') + "','" \
    #                                          + record_date + "','" \
    #                                          + ex_date + "','" \
    #                                          + bonus_ratio + "', 'MONEYCONTROL'),"
                except:
                    pass
            
            existing_data = engine.execute(select_sql).fetchall()
            existing_data = [tuple(a) for a in existing_data]
            #print(insert_data_list)
            #print("#################")
            insert_data_list = set(insert_data_list) - set(existing_data)
            #print(existing_data)
            #print("-----")
            #print(insert_data_list)
            for data in insert_data_list:
                bonus_sql = bonus_sql + "('"+sym + "','BONUS','" \
                              + timestamp.strftime('%Y-%m-%d') + "','MONEYCONTROL','" \
                              + data[0] + "','" \
                              + data[1] + "','" \
                              + data[2] + "','" \
                              + data[3] + "'),"
            #print(sql)
            try:
                engine.execute(bonus_sql[:-1])
                successful_download.append(sym)
                bonus_sym.append(sym)
                #print("Downloaded Bonuses for "+sym)
            except:
                pass
        except:
            pass
        
        
        # Download Rights
        #response = s.get(rights_url)
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                    s = requests.Session()
                    response = s.get(rights_url)
                if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                    break
                else:
                    sleep(60)
        except ConnectionError as e:
            print("Santosh Error---")
            time.sleep(2*60)
            response = s.get(rights_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
        
        try:
            rights_table = soup.find_all(class_='tbldivid')
            rows = rights_table[0].find_all("tr")
            select_sql = "SELECT to_char(announcement_date, 'YYYY-MM-DD'), record_date, ex_date, rights_ratio, rights_premium from corporate_actions where symbol = '"+sym+"' and corporate_action_type = 'RIGHTS'"
            rights_sql = "INSERT INTO corporate_actions (symbol, corporate_action_type, download_date, source, announcement_date,record_date, ex_date, rights_ratio, rights_premium) VALUES "
            insert_data_list = []
            for row in rows:
                try:
                    announcement_date = row.find_all("td")[0].text.strip().replace(",","")
                    announcement_date = datetime.datetime.strptime(announcement_date,'%d-%m-%Y')
                    record_date = row.find_all("td")[4].text.strip().replace(",","")
                    #record_date = datetime.datetime.strptime(record_date,'%d-%m-%Y')
                    ex_date = row.find_all("td")[5].text.strip().replace(",","")
                    #ex_date = datetime.datetime.strptime(ex_date,'%d-%m-%Y')
    
                    if announcement_date != "":
                        rights_ratio = row.find_all("td")[1].text.strip().replace(",","").replace("%"," per")
                        rights_premium = row.find_all("td")[3].text.strip().replace(",","").replace("%"," per")
                        insert_data_list.append((announcement_date.strftime('%Y-%m-%d'),record_date,ex_date,rights_ratio,rights_premium))
    #                    rights_sql = rights_sql + "( '" \
    #                                          + sym + "','RIGHTS','" \
    #                                          + timestamp.strftime('%Y-%m-%d') + "','" \
    #                                          + announcement_date.strftime('%Y-%m-%d') + "','" \
    #                                          + record_date + "','" \
    #                                          + ex_date + "','" \
    #                                          + rights_ratio + "','" +rights_premium + "','MONEYCONTROL'),"
                except:
                    pass
                        
           # print(rights_sql)
            #engine.execute(rights_sql[:-1])
            
            existing_data = engine.execute(select_sql).fetchall()
            existing_data = [tuple(a) for a in existing_data]
            #print(insert_data_list)
            #print("#################")
            insert_data_list = set(insert_data_list) - set(existing_data)
            #print(existing_data)
            #print("-----")
            #print(insert_data_list)
            for data in insert_data_list:
                rights_sql = rights_sql + "('"+sym + "','RIGHTS','" \
                              + timestamp.strftime('%Y-%m-%d') + "','MONEYCONTROL','" \
                              + data[0] + "','" \
                              + data[1] + "','" \
                              + data[2] + "','" \
                              + data[3] + "','" \
                              + data[4] + "'),"
                
            try:
                engine.execute(rights_sql[:-1])
                successful_download.append(sym)
                rights_sym.append(sym)
                #print("Downloaded Rights for "+sym)
            except:
                pass
        except:
            pass
        
        #print(ratios_dict_str)
        #engine.execute(sql)

        # Download Splits
        #response = s.get(splits_url)
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com"):    
                    s = requests.Session()
                    response = s.get(splits_url)
                if (mrigutilities.is_connected() and mrigutilities.is_connected("www.moneycontrol.com")) or timecounter > 5:
                    break
                else:
                    sleep(60)
        except ConnectionError as e:
            print("Santosh Error---")
            time.sleep(2*60)
            response = s.get(splits_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
        
        try:
            splits_table = soup.find_all(class_='tbldivid')
            rows = splits_table[0].find_all("tr")
            select_sql = "SELECT to_char(announcement_date, 'YYYY-MM-DD'), ex_date, split from corporate_actions where symbol = '"+sym+"' and corporate_action_type = 'SPLITS'"
            split_sql = "INSERT INTO corporate_actions (symbol, corporate_action_type, download_date, source, announcement_date, ex_date, split) VALUES "
            insert_data_list = []
            for row in rows:
                try:
                    announcement_date = row.find_all("td")[0].text.strip().replace(",","")
                    announcement_date = datetime.datetime.strptime(announcement_date,'%d-%m-%Y')
                    ex_date = row.find_all("td")[3].text.strip().replace(",","")
                    #ex_date = datetime.datetime.strptime(ex_date,'%d-%m-%Y')
    
                    if announcement_date != "":
                        split_ratio = float(row.find_all("td")[1].text.strip().replace(",",""))/float(row.find_all("td")[2].text.strip().replace(",",""))
                        insert_data_list.append((announcement_date.strftime('%Y-%m-%d'),ex_date,str(split_ratio)))
    #                    split_sql = split_sql + "( '" \
    #                                          + sym + "','SPLITS','" \
    #                                          + timestamp.strftime('%Y-%m-%d') + "','" \
    #                                          + announcement_date.strftime('%Y-%m-%d') + "','" \
    #                                          + ex_date + "','" \
    #                                          + split_ratio + "','MONEYCONTROL'),"
    
                except:
                    pass
                                #print(sql)
            existing_data = engine.execute(select_sql).fetchall()
            existing_data = [tuple(a) for a in existing_data]
            #print(insert_data_list)
            #print("#################")
            insert_data_list = set(insert_data_list) - set(existing_data)
            #print(existing_data)
            #print("-----")
            #print(insert_data_list)
            for data in insert_data_list:
                split_sql = split_sql + "('"+sym + "','SPLITS','" \
                              + timestamp.strftime('%Y-%m-%d') + "','MONEYCONTROL','" \
                              + data[0] + "','" \
                              + data[1] + "','" \
                              + str(data[2]) + "'),"
            
            #engine.execute(split_sql[:-1])
            try:
                engine.execute(split_sql[:-1])
                successful_download.append(sym)
                split_sym.append(sym)
                #print("Downloaded Splits for "+sym)
            except:
                pass
        except:
            pass
        
    print("Downloaded Corporate Actions for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
    print("Downloaded Board Meetings for "+str(bm_sym))
    print("Downloaded Bonus for "+str(bonus_sym))
    print("Downloaded Dividends for "+str(div_sym))
    print("Downloaded Rights for "+str(rights_sym))
    print("Downloaded Splits for "+str(split_sym))
        #print(ratios_dict_str)
        #engine.execute(sql)



if __name__ == '__main__':
#    get_MCStockCodes()
    
#    get_MCRatios()
#    populate_ratios_table()
#    get_MCQtrly_Results()
    #get_MCQtrly_Results("MS24:marutisuzukiindia")
#    get_BalanceSheet()

#    get_ProfitLossStatement()
#    get_BalanceSheet()       
#    get_CashFLowStatement()
    #get_OutShares_NSE()
#    get_CorporateActions()
    get_NSELive()
