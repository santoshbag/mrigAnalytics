# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag
"""
import sys
from time import sleep
import nsepy
import datetime #import date, timedelta
from pandas import DataFrame
#from sqlalchemy import create_engine
import mrigutilities

def nseIndexHistory_download(startdate=None,enddate=None):
#    nseIndexList = open("nseStockList1.txt","r")
    print("NSE Indices download started")
    errorLog = open("errorLog.txt","a+")
#    today = datetime.datetime.now()
    #nseStockPrices = open("nseStockHistory.csv","a+")
    data_folder = "F:/Mrig Analytics/Development/data/"
    
    arguments = sys.argv[1:]
    
    if (startdate == None or enddate == None):
        startdate= datetime.date.today() - datetime.timedelta(days=1)
        enddate= datetime.date.today()
    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass
    
    #Indices = [key for key in nsepy.constants.symbol_list]
    indices = nsepy.constants.NSE_INDICES
    #Indices = nsepy.constants.symbol_list
    
    nseIndexListLength = len(indices)
    nseIndicesDownloaded = 0
    counter,stkcount = 0,0
    write_counter = 0
    indicesdata = DataFrame()
    
    nseIndexPrices = open(data_folder+"nseIndexHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")
    
    errorLog.write("\n########### START OF nseIndexHistory_ErrorLog for Period --"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y") +"---###########\n")
    engine = mrigutilities.sql_engine()
    
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"
    
    engine.execute(disable_sql)
    
    #Indices = Indices[4:6]
    
    for index in indices:
        #print(index)
        counter = counter + 1
        stkcount = stkcount + 1
        """ Progress Animation routine starts"""
        if len(indices) < 50:
            steps = len(indices)
        else:
            steps = 50
        sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(stkcount/(len(indices)/steps)), int(100/len(indices)*stkcount)))
        sys.stdout.flush()        
        """ Progress Animation routine ends"""
        
        try:
            timecounter = 0
            while True:
                timecounter = timecounter + 1
                if mrigutilities.is_connected():
                    indexdata = nsepy.get_history(symbol=index,start=startdate,end=enddate,index=True)
                    index_pe_data = nsepy.get_index_pe_history(symbol=index,start=startdate,end=enddate)
                if mrigutilities.is_connected() or timecounter > 5:
                    break
                else:
                    sleep(60)
                    
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
                indicesdata.reset_index(level=0, inplace=True)
                indicesdata = mrigutilities.clean_df_db_dups(indicesdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
                errorLog.write(indicesdata[1]+" already downloaded \n")
                indicesdata = indicesdata[0]
                try:
                    indicesdata.set_index('date',inplace=True)
                    indicesdata['close_adj'] = indicesdata['close']
                    indicesdata['volume_adj'] = indicesdata['volume']
                    indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
                except:
                    pass
            else:
                indicesdata.to_csv(nseIndexPrices)
                indicesdata.reset_index(level=0, inplace=True)
                indicesdata = mrigutilities.clean_df_db_dups(indicesdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
                errorLog.write(indicesdata[1]+" already downloaded \n")
                indicesdata = indicesdata[0]
                try:
                    indicesdata.set_index('date',inplace=True)
                    indicesdata['close_adj'] = indicesdata['close']
                    indicesdata['volume_adj'] = indicesdata['volume']
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
        indicesdata.reset_index(level=0, inplace=True)
        indicesdata = mrigutilities.clean_df_db_dups(indicesdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
        errorLog.write(indicesdata[1]+" already downloaded \n")
        indicesdata = indicesdata[0]
        try:
            indicesdata.set_index('date',inplace=True)
            indicesdata['close_adj'] = indicesdata['close']
            indicesdata['volume_adj'] = indicesdata['volume']
            indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
        except:
            pass
    else:
         indicesdata.to_csv(nseIndexPrices)
         indicesdata.reset_index(level=0, inplace=True)
         indicesdata = mrigutilities.clean_df_db_dups(indicesdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
         errorLog.write(indicesdata[1]+" already downloaded \n")
         indicesdata = indicesdata[0]
         try:
            indicesdata.set_index('date',inplace=True)
            indicesdata['close_adj'] = indicesdata['close']
            indicesdata['volume_adj'] = indicesdata['volume']
            indicesdata.to_sql('stock_history',engine, if_exists='append', index=True)
         except:
            pass
    print("\n"+str(nseIndicesDownloaded) +" Indices downloaded of a total of "+ str(nseIndexListLength)+" Indices ")
    engine.execute(enable_sql)
    nseIndexPrices.close()
    errorLog.write("\n########### END OF nseIndexHistory_ErrorLog for Period --"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y") +"---###########\n")
    errorLog.close()
    print("NSE Indices download finished\n")
    
if __name__ == '__main__':
    
    startdate,enddate = None,None
    
    arguments = sys.argv[1:]    
    try:
        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
    except:
        pass

    nseIndexHistory_download(startdate,enddate)