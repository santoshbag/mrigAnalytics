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
import mrigutilities

nseStockList = open("nseStockList1.txt","r")
errorLog = open("errorLog.txt","w")
today = datetime.datetime.now()
#nseStockPrices = open("nseStockHistory.csv","a+")

data_folder = "F:/Mrig Analytics/Development/data/"

arguments = sys.argv[1:]

startdate= datetime.date(2018,1,2)
enddate= datetime.date(2018,5,4)

startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))

stocks = [key for key in nsepy.constants.symbol_list]
#stocks = nsepy.constants.symbol_list

nseStockListLength = len(stocks)
nseStocksDownloaded = 0
counter = 0
write_counter = 0
stocksdata = DataFrame()

nseStockPrices = open(data_folder+"nseStockHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")

engine = mrigutilities.sql_engine()

#engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')

database_cols = {'%Deliverble':'per_deliverable_volume'}

#stocks = stocks[4:6]

for stock in stocks:
    #print(stock)
    counter = counter + 1
    try:
        stockdata = nsepy.get_history(symbol=stock,start=startdate,end=enddate)
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
            try:
                stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
            except:
                pass
        else:
            stocksdata.to_csv(nseStockPrices)
            try:
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
    try:
        stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
    except:
        pass
else:
     stocksdata.to_csv(nseStockPrices)
     try:
         stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
     except:
         pass
print(str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
nseStockPrices.close()
engine.dispose()
errorLog.close()
