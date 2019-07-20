# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities
import time
import csv
from requests import get
import mrigutilities as mu

def stockHistory_download(startdate=None,enddate=None,progressbar=True):
    print("Stock History download started")
#    nseStockList = open("nseStockList1.txt","r")
    errorLog = open("errorLog.txt","w")
    today = datetime.datetime.now()
    #nseStockPrices = open("nseStockHistory.csv","a+")
    
#    data_folder = "F:/Mrig Analytics/Development/data/"
    

    
    if (startdate == None or enddate == None):
        startdate= datetime.date.today() - datetime.timedelta(days=1)
        enddate= datetime.date.today()

    stocks = [key for key in nsepy.constants.symbol_list]
    #stocks = nsepy.constants.symbol_list
    
    nseStockListLength = len(stocks)
    nseStocksDownloaded = 0
    counter,stkcount = 0,0
    write_counter = 0
    stocksdata = DataFrame()

    datadir = os.path.dirname(__file__)
    nseStockPrices_path = os.path.join(datadir,'..','..','data',"nseStockHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv")
    nseStockPrices = open(nseStockPrices_path,"a+")
    
#    nseStockPrices = open(data_folder+"nseStockHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")
    
    engine = mrigutilities.sql_engine()
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"
    
    engine.execute(disable_sql)
    #engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')
    
    database_cols = {'%Deliverble':'per_deliverable_volume'}
    
    #stocks = stocks[4:6]
#    stocks = stocks[stocks.index('PONNIERODE'):]
    
    for stock in stocks:
#        print(stock)
        counter = counter + 1
        stkcount = stkcount + 1
        if len(stocks) < 50:
            steps = len(stocks)
        else:
            steps = 50
        if progressbar:
            sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(stkcount/(len(stocks)/steps)), int(100/len(stocks)*stkcount)))
            sys.stdout.flush()

        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
#                print(timecounter)
                if mrigutilities.is_connected():
                    stockdata = nsepy.get_history(symbol=stock,start=startdate,end=enddate)
                if mrigutilities.is_connected() or timecounter > 5:
                    break
                else:
                    time.sleep(60)
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
                    stocksdata['close_adj'] = stocksdata['close']
                    stocksdata['volume_adj'] = stocksdata['volume']
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
                    stocksdata['close_adj'] = stocksdata['close']
                    stocksdata['volume_adj'] = stocksdata['volume']
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
            stocksdata['close_adj'] = stocksdata['close']
            stocksdata['volume_adj'] = stocksdata['volume']
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
             stocksdata['close_adj'] = stocksdata['close']
             stocksdata['volume_adj'] = stocksdata['volume']
             stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
         except:
             pass
    print("\n"+str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
    nseStockPrices.close()
    engine.execute(enable_sql)
    engine.dispose()
    errorLog.close()
    print("Stock History download finished\n")


def nse_vol_download(eod=None):
    #"https://www.nseindia.com/content/historical/DERIVATIVES/2019/MAR/fo03MAR2019bhav.csv.zip"
    bhavcopy = "https://www.nseindia.com/archives/nsccl/volt/CMVOLT_%s.CSV"    
    if not eod:
        today = datetime.date.today()
    else:
        today = eod

    engine = mu.sql_engine()
    request = get(bhavcopy%(today.strftime('%d%m%Y')))
    
    content = request.content.decode('utf-8')
    
    cr = csv.reader(content.splitlines(), delimiter=',')
    my_list = list(cr)
    sql = "update stock_history as sh set nse_vol=c.nse_vol from (values "
    for row in my_list:
        if row[1].strip() not in ['Symbol','SYMBOL'] and row[7].strip() not in ['-']:
            sql = sql + "('%s','%s',%s),"%(row[1].strip(),row[0].strip(),row[7].strip())
    sql = sql.strip()[:-1] + ") as c(symbol,date,nse_vol) where c.symbol=sh.symbol and \
          c.date=to_char(sh.date :: DATE, 'dd-MON-YYYY')"   
#    print(sql)
    engine.execute(sql)
    
if __name__ == '__main__':
    
    startdate,enddate = None,None
    
    arguments = sys.argv[1:]    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass

    stockHistory_download(startdate,enddate)
    nse_vol_download()