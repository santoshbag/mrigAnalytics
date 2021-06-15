# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag

reads NSE bhavcopy file in zip format and puts into database
format is "cmDDMMMYYYYbhav.csv.zip"
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime #import date, timedelta
import pandas as pd #import DataFrame
#from sqlalchemy import create_engine
import mrigutilities
import zipfile,re
#from bs4 import BeautifulSoup
#from time import sleep
import csv
#import numpy as np


def stockHistoryNew_download():
    datadir = os.path.dirname(__file__)
    processed_files_path = os.path.join(datadir,'..','..','data',"processed_files.csv")
    today = datetime.date.today()
    #input_dir = "F:\\NSEDATA"
    input_dir = os.path.join(datadir,'..','..','data','input')
    processed_file_list = []
#    df_list = []
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
    
    fo_csv_header_map = {'SYMBOL':'symbol',	
                  'EXPIRY_DT' : 'expiry',
                  'STRIKE_PR' : 'strike',
                  'OPTION_TYP' : 'option_type',
                  'OPEN':'open',	
                  'HIGH':'high',	
                  'LOW':'low',	
                  'CLOSE': 'close',	
                  'SETTLE_PR':'settle_price',	
                  'CONTRACTS':'contracts',	
                  'OPEN_INT': 'oi',	
                  'CHG_IN_OI': 'oi_change',	
                  'TIMESTAMP': 'date'}
    
    csv_header = [key for key in csv_header_map.keys()]
    fo_csv_header = [key for key in fo_csv_header_map.keys()]
    nifty_csv_header = [key for key in nifty_csv_header_map.keys()]
    stocksdata = pd.DataFrame()
#    niftydata = pd.DataFrame()
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
        fobhavlist = []
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
                if re.search("^fo.*zip",file):
                    fobhavlist.append(os.path.join(r,file))                
    #                print(indexfilelist)                
    #    print(stockbhavlist)
    
        for zfile in stockbhavlist:
           # print(zfile)
            if zfile not in processed_file_list:
    #            print(zfile)
                zf = zipfile.ZipFile(zfile)
                csvfiles = zf.infolist()
                for csvfile in csvfiles:
                    print("Processing Equity File "+str(csvfile))
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
                    stocksdata['close_adj'] = stocksdata['close'] 
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
    
        for zfile in fobhavlist:
           # print(zfile)
            if zfile not in processed_file_list:
    #            print(zfile)
                zf = zipfile.ZipFile(zfile)
                csvfiles = zf.infolist()
                for csvfile in csvfiles:
                    print("Processing FO File "+str(csvfile))
                    fodata = pd.read_csv(zf.open(csvfile))
                    fodata = fodata.replace({'-':None})                  
                    
                    fodata = fodata[fo_csv_header]
                    fodata = fodata.rename(columns=fo_csv_header_map)
    #                stocksdata.drop(['ISIN'],axis=1,inplace=True)
    #                try:
                    fodata.apply(pd.to_numeric, errors='ignore')
    #                stocksdata["date"] = stocksdata["date"].apply(dtm)
                    fodata['date'] = pd.to_datetime(fodata['date'])
                    fodata['add_mod_date'] = today
                    fodata.set_index('date',inplace=True)
    #                print(stocksdata.index)
    #                print(stocksdata.tail(10))
                    if write_flag:
                        fodata.to_sql('futures_options_history',engine, if_exists='append', index=True)
                        print("FO Written to Database")
                        print(fodata.tail(10))
                        writer.writerow([zfile])
                    else:
                        print(fodata.tail(10))
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
                indexdata['close_adj'] = indexdata['close']
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

#    
if __name__ == '__main__':
        
    stockHistoryNew_download()
