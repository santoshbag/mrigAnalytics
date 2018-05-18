# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""
import sys
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
#from sqlalchemy import create_engine
import mrigutilities


nseIndexList = open("nseStockList1.txt","r")
errorLog = open("errorLog.txt","w")
today = datetime.datetime.now()
#nseStockPrices = open("nseStockHistory.csv","a+")
data_folder = "F:/Mrig Analytics/Development/data/"

arguments = sys.argv[1:]

startdate= datetime.date(2018,1,2)
enddate= datetime.date(2018,5,4)

startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))

#Indices = [key for key in nsepy.constants.symbol_list]
indices = nsepy.constants.NSE_INDICES
#Indices = nsepy.constants.symbol_list

nseIndexListLength = len(indices)
nseIndicesDownloaded = 0
counter = 0
write_counter = 0
indicesdata = DataFrame()

nseIndexPrices = open(data_folder+"nseIndexHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")

engine = mrigutilities.sql_engine()

#Indices = Indices[4:6]

for index in indices:
    #print(index)
    counter = counter + 1
    try:
        indexdata = nsepy.get_history(symbol=index,start=startdate,end=enddate,index=True)
        index_pe_data = nsepy.get_index_pe_history(symbol=index,start=startdate,end=enddate)
        indexdata = indexdata.merge(right=index_pe_data,how='outer',right_index=True,left_index=True)
        indexdata.insert(loc=0,column='Symbol',value=index)
        indexdata.insert(loc=1,column='Series',value='IN')
#        if counter==1:
#            stocksdata = stockdata
#        else:
        indicesdata = indicesdata.append(indexdata)
        if indexdata.empty:
            errorLog.write(index+" not downloaded \n")
        else:
            nseIndicesDownloaded = nseIndicesDownloaded +1
    except:
        pass
    if counter >=50:
        indicesdata.index.rename('date',inplace=True)
        indicesdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('/','').replace('%deliverble','per_deliverable_volume'),inplace=True)
        if write_counter >=1:
            indicesdata.to_csv(nseIndexPrices, header=False)
            try:
                indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
            except:
                pass
        else:
            indicesdata.to_csv(nseIndexPrices)
            try:
                indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
            except:
                pass        
        indicesdata = DataFrame()
        counter = 0
        write_counter = write_counter + 1

indicesdata.index.rename('date',inplace=True)
indicesdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('/','').replace('%deliverble','per_deliverable_volume'),inplace=True)        
if write_counter >=1:
    indicesdata.to_csv(nseIndexPrices, header=False)
    try:
        indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
    except:
        pass
else:
     indicesdata.to_csv(nseIndexPrices)
     try:
        indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
     except:
        pass
print(str(nseIndicesDownloaded) +" Indices downloaded of a total of "+ str(nseIndexListLength)+" Indices ")
nseIndexPrices.close()
errorLog.close()
