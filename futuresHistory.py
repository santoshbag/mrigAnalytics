# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:46:42 2018

@author: Santosh Bag
"""

import sys
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
#from sqlalchemy import create_engine
#from dateutil import relativedelta
import mrigutilities


nseFutList = open("nseStockList1.txt","r")
errorLog = open("errorLog.txt","w")
today = datetime.datetime.now()
#nseStockPrices = open("nseStockHistory.csv","a+")

data_folder = "F:/Mrig Analytics/Development/data/"

arguments = sys.argv[1:]

startdate= datetime.date(2018,1,2)
enddate= datetime.date(2018,5,4)

startdate= datetime.date(int(arguments[0][0:4]),
                         int(arguments[0][4:6]),
                            int(arguments[0][6:8]))
enddate= datetime.date(int(arguments[1][0:4]),
                       int(arguments[1][4:6]),
                          int(arguments[1][6:8]))

stocks = [key for key in nsepy.constants.symbol_list]
indices = nsepy.constants.NSE_INDICES

stocks = stocks + indices

#Futures = nsepy.constants.symbol_list

nseStockListLength = len(stocks)
nseFuturesDownloaded = 0
counter = 0
write_counter = 0
futuresdata = DataFrame()

nseFutPrices = open(data_folder+"nseFuturesHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")

engine = mrigutilities.sql_engine()

#engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')

expiryList = mrigutilities.get_futures_expiry(startdate,enddate)
#Futures = Futures[4:6]

for stock in stocks:
    #print(stock)
    for dt in expiryList:
        counter = counter + 1
        try:
            futdata = nsepy.get_history(symbol=stock,
                                        start=startdate,
                                        end=enddate,
                                        index=(stock in indices),
                                        futures=True,
                                        expiry_date=dt)
    #        if counter==1:
    #            futuresdata = futdata
    #        else:
            futuresdata = futuresdata.append(futdata)
            if futdata.empty:
                errorLog.write(stock+" not downloaded \n")
            else:
                nseFuturesDownloaded = nseFuturesDownloaded +1
        except:
            pass
        if counter >=50:
            futuresdata.index.rename('date',inplace=True)
            futuresdata.rename(columns=lambda x: x.lower().replace(" ",'_'),inplace=True)
            if write_counter >=1:
                futuresdata.to_csv(nseFutPrices, header=False)
                futuresdata.reset_index(level=0,inplace=True)
                futuresdata = mrigutilities.clean_df_db_dups(futuresdata,'futures_history',engine,dup_cols=["date","symbol","expiry"])
                try:
                    futuresdata.set_index('date',inplace=True)
                    futuresdata.to_sql('futures_history',
                                       engine,
                                       if_exists='append',
                                       index=True)
                except:
                    pass
            else:
                futuresdata.to_csv(nseFutPrices)
                futuresdata.reset_index(level=0,inplace=True)
                futuresdata = mrigutilities.clean_df_db_dups(futuresdata,'futures_history',engine,dup_cols=["date","symbol","expiry"])
                try:
                    futuresdata.set_index('date',inplace=True)
                    futuresdata.to_sql('futures_history',
                                       engine,
                                       if_exists='append', 
                                       index=True)
                except:
                    pass
            futuresdata = DataFrame()
            counter = 0
            write_counter = write_counter + 1

futuresdata.index.rename('date',inplace=True)
futuresdata.rename(columns=lambda x: x.lower().replace(" ",'_'),inplace=True)
if write_counter >=1:
    futuresdata.to_csv(nseFutPrices, header=False)
    futuresdata.reset_index(level=0,inplace=True)
    futuresdata = mrigutilities.clean_df_db_dups(futuresdata,'futures_history',engine,dup_cols=["date","symbol","expiry"])
    try:
        futuresdata.set_index('date',inplace=True)
        futuresdata.to_sql('futures_history',
                           engine, 
                           if_exists='append', 
                           index=True)
    except:
        pass
else:
     futuresdata.to_csv(nseFutPrices)
     futuresdata.reset_index(level=0,inplace=True)
     futuresdata = mrigutilities.clean_df_db_dups(futuresdata,'futures_history',engine,dup_cols=["date","symbol","expiry"])
     try:
         futuresdata.set_index('date',inplace=True)
         futuresdata.to_sql('futures_history',
                            engine, 
                            if_exists='append', 
                            index=True)
     except:
         pass
print(str(nseFuturesDownloaded) +" Futures downloaded of a total of "+ str(nseStockListLength)+" Futures ")
nseFutPrices.close()
engine.dispose()
errorLog.close()
