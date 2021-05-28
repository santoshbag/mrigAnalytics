# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag

reads NSE bhavcopy file in zip format and puts into database
format is "cmDDMMMYYYYbhav.csv.zip"
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import nsepy
import datetime #import date, timedelta
import pandas as pd #import DataFrame
from sqlalchemy import create_engine
import mrigutilities, mrigstatics
import urllib, zipfile,re
from bs4 import BeautifulSoup
from time import sleep
import csv
import numpy as np


datadir = os.path.dirname(__file__)
processed_files_path = os.path.join(datadir,'..','..','data',"processed_files.csv")
#input_dir = "F:\\NSEDATA"
input_dir = os.path.join(datadir,'..','..','data','input')
processed_file_list = []
df_list = []
write_flag=True
engine = mrigutilities.sql_engine()
disable_sql = "alter table stock_history disable trigger return_trigger"
enable_sql = "alter table stock_history enable trigger return_trigger"
engine.execute(disable_sql)

csv_header_map = {'SYMBOL':'symbol',	
              'SERIES' : 'series',	
              'OPEN':'open',	
              'HIGH':'high',	
              'LOW':'low',	
              'CLOSE': 'close',	
              'LAST':'last',	
              'PREVCLOSE':'prev_close',	
              'TOTTRDQTY': 'volume',	
              'TOTTRDVAL': 'turnover',	
              'TIMESTAMP': 'date',	
              'TOTALTRADES' : 'trades'}
nifty_csv_header_map = {'Index Name':'symbol',	
              'High Index Value':'high',
              'Open Index Value':'open',	
              'Low Index Value':'low',	
              'Closing Index Value': 'close',	
              'Index Date':'date',	
              'Volume': 'volume',	
              'Turnover (Rs. Cr.)': 'turnover',
              'P/E':'pe',
              'P/B':'pb',
              'Div Yield': 'div_yield'}

csv_header = [key for key in csv_header_map.keys()]
nifty_csv_header = [key for key in nifty_csv_header_map.keys()]
stocksdata = pd.DataFrame()
niftydata = pd.DataFrame()
dtm = lambda x: datetime.datetime.strptime(str(x), "%d-%m-%Y")
    
with open(processed_files_path,'a+') as processed_file:
    processed_file.seek(0)
    reader = csv.reader(processed_file,delimiter='\t')

    for row in reader:
        if row:
            processed_file_list.append(row)
    processed_file_list = [f[0] for f in processed_file_list]
#    print(processed_file_list)
with open(processed_files_path,'a+') as processed_file:
    writer = csv.writer(processed_file,delimiter='\t')
    
#    print("Exisiting List")
#    print(processed_file_list)
    stockbhavlist = []
    indexfilelist = []
    for r,d,f in os.walk(input_dir):
#        for folder in d:
#    #        if '24012020' in folder:
#            for r1,d1,f1 in os.walk(os.path.join(r,folder)):
#                for f12 in f1:
#                    if re.search("^cm.*zip",f12):
#                        stockbhavlist.append(os.path.join(r1,f12))
        for file in f:
            if re.search("^cm.*zip",file):
                stockbhavlist.append(os.path.join(r,file))
#                print(file)
            if re.search("^ind_close_all_.*csv",file):
                indexfilelist.append(os.path.join(r,file))
#                print(indexfilelist)                
#    print(stockbhavlist)

    for zfile in stockbhavlist:
       # print(zfile)
        if zfile not in processed_file_list:
#            print(zfile)
            zf = zipfile.ZipFile(zfile)
            csvfiles = zf.infolist()
            for csvfile in csvfiles:
                print("Processing Equity File "+csvfile)
                stocksdata = pd.read_csv(zf.open(csvfile))
                stocksdata = stocksdata.replace({'-':None})                  
                
                stocksdata = stocksdata[csv_header]
                stocksdata = stocksdata[stocksdata['SERIES']=='EQ']
                stocksdata = stocksdata.rename(columns=csv_header_map)
#                stocksdata.drop(['ISIN'],axis=1,inplace=True)
#                try:
                stocksdata.apply(pd.to_numeric, errors='ignore')
#                stocksdata["date"] = stocksdata["date"].apply(dtm)
                stocksdata['date'] = pd.to_datetime(stocksdata['date'])
                stocksdata.set_index('date',inplace=True)
#                print(stocksdata.index)
#                print(stocksdata.tail(10))
                if write_flag:
                    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
                    print("Equity Written to Database")
                    print(stocksdata.tail(10))
                    writer.writerow([zfile])
                else:
                    print(stocksdata.tail(10))
#                except:
#                    pass
#
    for csvfile in indexfilelist:
        if csvfile not in processed_file_list:
            print("Processing Index File "+csvfile)
            indexdata = pd.read_csv(csvfile)
            indexdata = indexdata.replace({'-':None})                  
            indexdata = indexdata[nifty_csv_header]
            indexdata = indexdata.rename(columns=nifty_csv_header_map)
    
            indexdata['symbol'] = indexdata['symbol'].str.upper()   
            indexdata['series'] ='IN'
            indexdata = indexdata.apply(pd.to_numeric, errors='ignore')
            indexdata['turnover'] = indexdata['turnover'] * 10000000
            indexdata["date"] = indexdata["date"].apply(dtm)
    
    #        indexdata['date'] = pd.to_datetime(indexdata['date'])
    
    #                stocksdata.drop(['ISIN'],axis=1,inplace=True)
    #                try:
            indexdata.set_index('date',inplace=True)
    #        print(indexdata.index)

            if write_flag:
                indexdata.to_sql('stock_history',engine, if_exists='append', index=True)
                print("Indices Written to Database")
                print(indexdata.tail(10))
                writer.writerow([csvfile])
            else:
                print(indexdata.tail(10))                
#                except:
#                    pass
#             
engine.execute(enable_sql)             

#print(df_list[2])    
           
            
    

#def stockHistoryNew_download(startdate=None,enddate=None,progressbar=True):
#    print("Total Return Indices download started")
##    nseStockList = open("nseStockList1.txt","r")
#    errorLog = open("errorLog.txt","w")
##    today = datetime.datetime.now()
#    #nseStockPrices = open("nseStockHistory.csv","a+")
##    data_folder = "F:/Mrig Analytics/Development/data/"
#    
#    arguments = sys.argv[1:]
#    TRI = []
#    for key in mrigstatics.TR_INDICES.keys():
#        TRI = TRI + mrigstatics.TR_INDICES[key]
#        
#    startdate_def= datetime.datetime.today() - datetime.timedelta(1)
#    enddate_def = datetime.datetime.today()
#
#    if (startdate == None or enddate == None):
#        startdate= datetime.date.today() - datetime.timedelta(days=1)
#        enddate= datetime.date.today()
#    
#    try:
#        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
#        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
#    except:
#        pass
#    
#    if startdate >= startdate_def.date():
#        startdate = startdate_def.date() - datetime.timedelta(5)
#        
#    stocks = [key for key in nsepy.constants.symbol_list]
#    #stocks = nsepy.constants.symbol_list
#    
#    stocks = ['ICICIBANK']
#    
#    nseStocksDownloaded = 0
#    counter,stkcount = 0,0
#    write_counter = 0
#    stocksdata = DataFrame()
#    
##    nseStockPrices = open(data_folder+"totalreturnHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv","a+")
#
#    datadir = os.path.dirname(__file__)
#    nseStockPrices_path = os.path.join(datadir,'..','..','data',"totalreturnHistory_"+startdate.strftime("%d-%b-%Y")+"_"+enddate.strftime("%d-%b-%Y")+".csv")
#    nseStockPrices = open(nseStockPrices_path,"a+")
#    
#    engine = mrigutilities.sql_engine()
#    disable_sql = "alter table stock_history disable trigger return_trigger"
#    enable_sql = "alter table stock_history enable trigger return_trigger"
#    
#    engine.execute(disable_sql)
#    
#    #engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')
#    
#    database_cols = {'%Deliverble':'per_deliverable_volume'}
#    
#    def get_history(symbol,startDate,endDate):
#        df = DataFrame()
#        
#        TRI_URL = 'https://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?symbol=%s&segmentLink=3&symbolCount=2&series=EQ&dateRange=+&fromDate=%s&toDate=%s&dataType=PRICEVOLUMEDELIVERABLE'
#        urlsymbol = symbol.replace(" ",'%20')
#        urlstartdate = startDate.strftime('%d')+"-"+startDate.strftime('%m')+"-"+startDate.strftime('%Y')
#        urlenddate = endDate.strftime('%d')+"-"+endDate.strftime('%m')+"-"+endDate.strftime('%Y')
#        
#        TRI_URL = (TRI_URL %(urlsymbol,urlstartdate,urlenddate))
#        
#        req = urllib.request.Request(TRI_URL,headers=nsepy.liveurls.headers)
#        res = urllib.request.urlopen(req)
#        res = gzip.decompress(res.read())
#        
#        soup = BeautifulSoup(res, 'html.parser')
#        dates = soup.find_all(class_="date")
#        #print(dates)
#        index_val = soup.find_all(class_="number")
#        #print(index_val)
#        index_table = []
#        index_table_cols = ['date','symbol','series','last']
#        for i in range(0,len(dates)-1):
#            index_table_row = [str(dates[i]).replace('<td class="date">',"").replace('</td>',""),
#                                symbol,
#                                'EQ',
#                                str(index_val[i]).replace('<td class="number">',"").replace('</td>',"")]
#            index_table_row[0] = datetime.datetime.strptime(index_table_row[0],'%d-%b-%Y')
#            #print(index_table_row)
#            index_table.append(index_table_row)
#        #print(index_table)
#        df = DataFrame(index_table,columns=index_table_cols)
#        df.set_index('date',inplace=True)
#        return df
#    
#    stocks = TRI
#    nseStockListLength = len(stocks)
#    
#    for stock in stocks:
#        #print(stock)
#        counter = counter + 1
#        stkcount = stkcount + 1
#        if len(stocks) < 50:
#            steps = len(stocks)
#        else:
#            steps = 50
#        if progressbar:
#            sys.stdout.write("\r[%-*s] %d%%" % (steps,'='*int(stkcount/(len(stocks)/steps)), int(100/len(stocks)*stkcount)))
#            sys.stdout.flush()
#
#        try:
#            timecounter = 0
#            while True:
#                timecounter = timecounter + 1
#                if mrigutilities.is_connected():
#                    stockdata = get_history(symbol=stock,startDate=startdate,endDate=enddate)
#                    print(stockdata)
#                if mrigutilities.is_connected() or timecounter > 5:
#                    break
#                else:
#                    sleep(60)
#            
#    #        if counter==1:
#    #            stocksdata = stockdata
#    #        else:
#            stocksdata = stocksdata.append(stockdata)
#            if stockdata.empty:
#                errorLog.write(stock+" not downloaded \n")
#            else:
#                nseStocksDownloaded = nseStocksDownloaded +1
#        except:
#            pass
#        if counter >=50:
#            stocksdata.index.rename('date',inplace=True)
#            stocksdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
#            if write_counter >=1:
#                stocksdata.to_csv(nseStockPrices, header=False)
#                stocksdata.reset_index(level=0, inplace=True)
#                stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
#                errorLog.write(stocksdata[1]+" already downloaded \n")
#                stocksdata = stocksdata[0]
#                try:
#                    stocksdata.set_index('date',inplace=True)
#                    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
#                except:
#                    pass
#            else:
#                stocksdata.to_csv(nseStockPrices)
#                stocksdata.reset_index(level=0, inplace=True)
#                stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
#                errorLog.write(stocksdata[1]+" already downloaded \n")
#                stocksdata = stocksdata[0]
#                try:
#                    stocksdata.set_index('date',inplace=True)
#                    stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
#                except:
#                    pass
#            stocksdata = DataFrame()
#            counter = 0
#            write_counter = write_counter + 1
#    
#    stocksdata.index.rename('date',inplace=True)
#    stocksdata.rename(columns=lambda x: x.lower().replace(" ",'_').replace('%deliverble','per_deliverable_volume'),inplace=True)
#    if write_counter >=1:
#        stocksdata.to_csv(nseStockPrices, header=False)
#        stocksdata.reset_index(level=0, inplace=True)
#        stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
#        errorLog.write(stocksdata[1]+" already downloaded \n")
#        stocksdata = stocksdata[0]
#        try:
#            stocksdata.set_index('date',inplace=True)
#            stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
#        except:
#            pass
#    else:
#         stocksdata.to_csv(nseStockPrices)
#         stocksdata.reset_index(level=0, inplace=True)
#         stocksdata = mrigutilities.clean_df_db_dups(stocksdata,'stock_history',engine,dup_cols=["date","symbol","series"],leftIdx=True)
#         errorLog.write(stocksdata[1]+" already downloaded \n")
#         stocksdata = stocksdata[0]
#         try:
#             stocksdata.set_index('date',inplace=True)
#             stocksdata.to_sql('stock_history',engine, if_exists='append', index=True)
#         except:
#             pass
#    print("\n"+str(nseStocksDownloaded) +" Stocks downloaded of a total of "+ str(nseStockListLength)+" Stocks ")
#    engine.execute(enable_sql)
#    nseStockPrices.close()
#    engine.dispose()
#    errorLog.close()
#    print("Total Return Indices download finished\n")
#    
#if __name__ == '__main__':
#    
#    startdate,enddate = None,None
#    arguments = sys.argv[1:]    
#    try:
#        startdate= datetime.date(int(arguments[0][0:4]),int(arguments[0][4:6]),int(arguments[0][6:8]))
#        enddate= datetime.date(int(arguments[1][0:4]),int(arguments[1][4:6]),int(arguments[1][6:8]))
#    except:
#        pass
#
#    
#    stockHistoryNew_download(startdate,enddate)
