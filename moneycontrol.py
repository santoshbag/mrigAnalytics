# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 19:33:54 2018

This module deals with data downloads and manipulation from Money Control
@author: Santosh Bag
"""

import requests
import datetime,pandas
from bs4 import BeautifulSoup
import mrigstatics,mrigutilities


def get_MCStockCodes():
    url = mrigstatics.MC_URLS['MC_CODES_URL']
    s = requests.Session()
    response = s.get(url)
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
    sql = "select code_value from codes where code_name='MONEY_CONTROL_STOCK_CODES' limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_RATIOS_URL'] + symbol.split(":")[-1].strip()+"/ratiosVI/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        ratios_dict = {}
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
            sql = "INSERT INTO ratios (symbol, ratio_date, download_date, ratios_dictionary) VALUES ( '" \
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
        
        print("Downloaded Ratios for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        #print(ratios_dict_str)
        #engine.execute(sql)
        
def get_MCQtrly_Results(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value from codes where code_name='MONEY_CONTROL_STOCK_CODES' limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_QTRLY_RESULTS_URL'] + symbol.split(":")[-1].strip()+"/results/quarterly-results/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        qtrly_results_dict = {}
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
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_BalanceSheet(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value from codes where code_name='MONEY_CONTROL_STOCK_CODES' limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_BALANCE_SHEET_URL'] + symbol.split(":")[-1].strip()+"/balance-sheetVI/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        balance_sheet_dict = {}
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
        
        print("Downloaded Balance Sheet Results for "+str(len(set(successful_download)))+ " of "+ str(len(symbollist))+" stocks")
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_ProfitLossStatement(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value from codes where code_name='MONEY_CONTROL_STOCK_CODES' limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_PROFIT_LOSS_URL'] + symbol.split(":")[-1].strip()+"/profit-lossVI/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        pnl_statement_dict = {}
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
        #print(ratios_dict_str)
        #engine.execute(sql)

def get_CashFLowStatement(symbol=None):
    
    engine = mrigutilities.sql_engine()
    sql = "select code_value from codes where code_name='MONEY_CONTROL_STOCK_CODES' limit 1"
    codes = engine.execute(sql).fetchall()
    codes = [code.split(": ")[1] for code in codes[0][0].split("|")]
    if not symbol:
        symbollist = codes
    else:
        symbollist = [symbol]
    successful_download = []
    for symbol in symbollist:
        url = mrigstatics.MC_URLS['MC_CASHFLOW_STATEMENT_URL'] + symbol.split(":")[-1].strip()+"/cash-flowVI/"+symbol.split(":")[-2].strip()
        s = requests.Session()
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        timestamp = datetime.datetime.now()
    
        cashflow_statement_dict = {}
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
        #print(ratios_dict_str)
        #engine.execute(sql)




if __name__ == '__main__':
    #get_MCStockCodes()
    
#    get_MCRatios()
#    get_MCQtrly_Results()
    #get_MCQtrly_Results("MS24:marutisuzukiindia")
#    get_BalanceSheet("MS24:marutisuzukiindia")
#    get_BalanceSheet()   
    #get_ProfitLossStatement()
    get_CashFLowStatement()

