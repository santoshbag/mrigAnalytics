# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""
import sys
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities, mrigstatics
import urllib, gzip
from bs4 import BeautifulSoup
from time import sleep

def tri_download(startdate=None,enddate=None):
    print("Total Return Indices download started")
#    nseStockList = open("nseStockList1.txt","r")
    errorLog = open("errorLog.txt","w")
#    today = datetime.datetime.now()
    #nseStockPrices = open("nseStockHistory.csv","a+")
    data_folder = "F:/Mrig Analytics/Development/data/"
    
    arguments = sys.argv[1:]
    TRI = []
    for key in mrigstatics.TR_INDICES.keys():
        TRI = TRI + mrigstatics.TR_INDICES[key]
        
    startdate_def= datetime.datetime.today() - datetime.timedelta(1)
    enddate_def = datetime.datetime.today()

    if (startdate == None or enddate == None):
        startdate= datetime.date.today() - datetime.timedelta(days=1)
        enddate= datetime.date.today()
    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass
    
    if startdate >= startdate_def.date():
        startdate = startdate_def.date() - datetime.timedelta(5)
        
    stocks = [key for key in nsepy.constants.symbol_list]
    #stocks = nsepy.constants.symbol_list
    
    
    nseStocksDownloaded = 0
    counter,stkcount = 0,0
    write_counter = 0
    stocksdata = DataFrame()
    
    nseStockPrices = open(data_folder+"totalreturnHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")
    
    engine = mrigutilities.sql_engine()
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"
    
    engine.execute(disable_sql)
    
    #engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')
    
    database_cols = {'%Deliverble':'per_deliverable_volume'}
    
    def get_history(symbol,startDate,endDate):
        df = DataFrame()
        
        TRI_URL = 'https://www.nseindia.com/products/dynaContent/equities/indices/total_returnindices.jsp?indexType=%s&fromDate=%s&toDate=%s'
        urlsymbol = symbol.replace(" ",'%20')
        urlstartdate = startDate.strftime('%d')+"-"+startDate.strftime('%m')+"-"+startDate.strftime('%Y')
        urlenddate = endDate.strftime('%d')+"-"+endDate.strftime('%m')+"-"+endDate.strftime('%Y')
        
        TRI_URL = (TRI_URL %(urlsymbol,urlstartdate,urlenddate))
        
        req = urllib.request.Request(TRI_URL,headers=nsepy.liveurls.headers)
        res = urllib.request.urlopen(req)
        res = gzip.decompress(res.read())
        
        soup = BeautifulSoup(res, 'html.parser')
        dates = soup.find_all(class_="date")
        #print(dates)
        index_val = soup.find_all(class_="number")
        #print(index_val)
        index_table = []
        index_table_cols = ['date','symbol','series','last']
        for i in range(0,len(dates)-1):
            index_table_row = [str(dates[i]).replace('<td class="date">',"").replace('</td>',""),
                                symbol,
                                'TRI',
                                str(index_val[i]).replace('<td class="number">',"").replace('</td>',"")]
            index_table_row[0] = datetime.datetime.strptime(index_table_row[0],'%d-%b-%Y')
            #print(index_table_row)
            index_table.append(index_table_row)
        #print(index_table)
        df = DataFrame(index_table,columns=index_table_cols)
        df.set_index('date',inplace=True)
        return df
    
    stocks = TRI
    nseStockListLength = len(stocks)
    
    for stock in stocks:
        #print(stock)
        counter = counter + 1
        stkcount = stkcount + 1
        if len(stocks) < 50:
            steps = len(stocks)
        else:
            steps = 50
        sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(stkcount/(len(stocks)/steps)), int(100/len(stocks)*stkcount)))
        sys.stdout.flush()

        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected():
                    stockdata = get_history(symbol=stock,startDate=startdate,endDate=enddate)
                if mrigutilities.is_connected() or timecounter > 5:
                    break
                else:
                    sleep(60)
            
    #        if counter==1:
    #            stocksdata = stockdata
    #        else:
            stocksdata = stocksdata.append(stockdata)
            if stockdata.empty:
                errorLog.write(stock+" not downloaded \n")
            else:
                nseStocksDownloaded = nseStocksDownloaded +1
        except:
            pass
        if counter >=50:
            stocksdata.index.rename('date',inplace=True)
            stocksdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
            if write_counter >=1:
                stocksdata.to_csv(nseStockPrices, header=False)
                stocksdata.reset_index(level=0, inplace=True)
                stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
                errorLog.write(stocksdata[1]+" already downloaded \n")
                stocksdata = stocksdata[0]
                try:
                    stocksdata.set_index('date',inplace=True)
                    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
                except:
                    pass
            else:
                stocksdata.to_csv(nseStockPrices)
                stocksdata.reset_index(level=0, inplace=True)
                stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
                errorLog.write(stocksdata[1]+" already downloaded \n")
                stocksdata = stocksdata[0]
                try:
                    stocksdata.set_index('date',inplace=True)
                    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
                except:
                    pass
            stocksdata = DataFrame()
            counter = 0
            write_counter = write_counter + 1
    
    stocksdata.index.rename('date',inplace=True)
    stocksdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
    if write_counter >=1:
        stocksdata.to_csv(nseStockPrices, header=False)
        stocksdata.reset_index(level=0, inplace=True)
        stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
        errorLog.write(stocksdata[1]+" already downloaded \n")
        stocksdata = stocksdata[0]
        try:
            stocksdata.set_index('date',inplace=True)
            stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
        except:
            pass
    else:
         stocksdata.to_csv(nseStockPrices)
         stocksdata.reset_index(level=0, inplace=True)
         stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
         errorLog.write(stocksdata[1]+" already downloaded \n")
         stocksdata = stocksdata[0]
         try:
             stocksdata.set_index('date',inplace=True)
             stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
         except:
             pass
    print("\n"+str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
    engine.execute(enable_sql)
    nseStockPrices.close()
    engine.dispose()
    errorLog.close()
    print("Total Return Indices download finished\n")
    
if __name__ == '__main__':
    
    startdate,enddate = None,None
    
    arguments = sys.argv[1:]    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass

    
    tri_download(startdate,enddate)