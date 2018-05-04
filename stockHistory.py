# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""

import nsepy
from datetime import date
from pandas import DataFrame
#from sqlalchemy import create_engine


nseStockList = open("nseStockList1.txt","r")
errorLog = open("errorLog.txt","w")

#nseStockPrices = open("nseStockHistory.csv","a+")

stocks = [line.split("\n")[0] for line in nseStockList]
#stocks = nsepy.constants.symbol_list

nseStockListLength = len(stocks)
nseStocksDownloaded = 0
counter = 0
write_counter = 0
stocksdata = DataFrame()
startdate= date(2017,9,10)
enddate= date(2017,9,28)
nseStockPrices = open("nseStockHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")

#engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')


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
        if write_counter >=1:
            stocksdata.to_csv(nseStockPrices, header=False)
            #stocksdata.to_sql('stock_history',engine, if_exists='append', index=False)
        else:
            stocksdata.to_csv(nseStockPrices)
            #stocksdata.to_sql('stock_history',engine, if_exists='append', index=False, header=False)
        stocksdata = DataFrame()
        counter = 0
        write_counter = write_counter + 1
        
if write_counter >=1:
    stocksdata.to_csv(nseStockPrices, header=False)
    #stocksdata.to_sql('stock_history',engine, if_exists='append', index=False)
else:
     stocksdata.to_csv(nseStockPrices)
     #stocksdata.to_sql('stock_history',engine, if_exists='append', index=False, header=False))
print(str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
nseStockPrices.close()
errorLog.close()
