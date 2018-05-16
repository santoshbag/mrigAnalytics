# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 05:35:56 2017

@author: Santosh Bag
"""
import datetime,csv
import urllib.request
from pandas import DataFrame
from collections import deque
from sqlalchemy import create_engine


NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt?t=09082017092931"
mfNavHistory_path = "F:\Mrig Analytics\Development\data\mfNAVAllHistory.csv"
mfNavHistory = open(mfNavHistory_path,"a+")

engine = create_engine('postgresql+psycopg2://postgres:xanto007@localhost:5432/RB_WAREHOUSE')

def get_last_row(csv_filename,lines=1):
    with open(csv_filename,'r') as f:
        try:
            lastrow = deque(csv.reader(f), lines)
        except IndexError:  # empty file
            lastrow = None
        return lastrow

data = urllib.request.urlopen(NAV_URL) # read only 20 000 chars
timestamp = datetime.datetime.now()
last_fetched_data = get_last_row(mfNavHistory_path)
last_download_date = None
headerAbsent = True
try:
    last_download_date = last_fetched_data[0][7].split("-")[0]
    headerAbsent = False
except:
    pass
if last_download_date != timestamp.strftime("%x"):
    written = False
    navs = []
    navs_cols = ['Date','Fund House','Scheme Type','ISIN Div Payout/ ISIN Growth','ISIN Div Reinvestment','Scheme Name','Net Asset Value','Repurchase Price','Sale Price','Time Stamp']
    mutual_fund_scheme_type = ""
    mutual_fund_house = ""
    sub_header_count = 0
    for line in data:
        line =  str(line,'utf-8')#+";"+timestamp.strftime("%x-%X")
        line = line.split(";")
        if len(line) > 1:
            sub_header_count = 0
            try:
                current_date = line[7].split("\r\n",1)[:-1][0]
                navs.append(line[7].split("\r\n",1)[:-1]+[mutual_fund_house,mutual_fund_scheme_type]+line[1:-1]+[timestamp.strftime("%x-%X")])
                written= True
            except:
                pass
        else:
            if line[0].strip():    
                sub_header_count = sub_header_count + 1
                #print("sub_header_count "+ str(sub_header_count))
                if sub_header_count == 2:
                    mutual_fund_scheme_type = mutual_fund_house
                    mutual_fund_house= line[0]
                    #print("mutual_fund_scheme_type ->" + mutual_fund_scheme_type)
                    sub_header_count = 0
                else:
                    mutual_fund_house= line[0]
                    #print("mutual_fund_house -> " + mutual_fund_house)
    if written:
        navs = DataFrame(navs[1:],columns=navs_cols)
        navs.to_csv(mfNavHistory,index=False,header=headerAbsent)
        navs = navs.drop('Time Stamp',axis=1)
        try:
            navs.to_sql('mf_nav_history',engine, if_exists='append', index=False)
        except:
            pass
        #mfNavHistory.write("\n<End>\n")
mfNavHistory.close()