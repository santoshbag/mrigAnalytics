# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""
import sys,csv
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
from sqlalchemy import create_engine
import mrigutilities

nseStockList = open("F:/Mrig Analytics/Development/mrigAnalytics/notdownloaded.csv","r")
errorLog = open("errorLog.txt","w")
today = datetime.datetime.now()
#nseStockPrices = open("nseStockHistory.csv","a+")

data_folder = "F:/Mrig Analytics/Development/data/"

#arguments = sys.argv[1:]

startdate= datetime.date(2018,1,2)
enddate= datetime.date(2018,9,7)

#startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
#enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
reader = csv.reader(nseStockList)
stocks = [[row[1],row[0]] for row in reader]

#stocks = nsepy.constants.symbol_list

nseStockListLength = len(stocks)
nseStocksDownloaded = 0
counter = 0
write_counter = 0
stocksdata = DataFrame()

nseStockPrices = open(data_folder+"nseStockHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")

engine = mrigutilities.sql_engine()
disable_sql = "alter table stock_history disable trigger return_trigger"
enable_sql = "alter table stock_history enable trigger return_trigger"

engine.execute(disable_sql)
#print(stocks)

#engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')

database_cols = {'%Deliverble':'per_deliverable_volume'}

#stocks = stocks[4:6]
for stock in stocks:
    #print(stock)
    counter = counter + 1
    #print(stock)
    try:
        startdate = datetime.datetime.strptime(stock[1],'%m/%d/%y').date() + datetime.timedelta(days=1)
        
        stockdata = nsepy.get_history(symbol=stock[0],start=startdate,end=enddate)
                
        #print(stockdata)
#        if counter==1:
#            stocksdata = stockdata
#        else:
        print(stock)
        #print(stockdata)
        #stocksdata = stocksdata.append(stockdata)
        if stockdata.empty:
            errorLog.write(stock+" not downloaded \n")
        else:
            nseStocksDownloaded = nseStocksDownloaded +1
    
#    if counter >=50:
        stockdata.index.rename('date',inplace=True)
        stockdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
    #    if write_counter >=1:
        stockdata.to_csv(nseStockPrices, header=False)
        stockdata.reset_index(level=0, inplace=True)
        stockdata = mrigutilities.clean_df_db_dups(stockdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
        errorLog.write(stockdata[1]+" already downloaded \n")
        stockdata = stockdata[0]
    
        stockdata.set_index('date',inplace=True)
        stockdata['close_adj'] = stockdata['close']
        stockdata['volume_adj'] = stockdata['volume']
        #print(stocksdata)
        stockdata.to_sql('stock_history',engine, if_exists='append', index=True)
    except:
        pass
print(str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
nseStockPrices.close()
engine.execute(enable_sql)
engine.dispose()
errorLog.close()
