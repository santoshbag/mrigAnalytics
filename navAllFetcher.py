# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 05:35:56 2017

@author: Santosh Bag
"""
import datetime,csv
import urllib.request
from pandas import DataFrame
from collections import deque

NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt?t=09082017092931"
mfNavHistory_path = "F:\Development\ideasTrade\mfNAVAllHistory.csv"
mfNavHistory = open(mfNavHistory_path,"a+")

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
    navs_cols = ['Date','ISIN Div Payout/ ISIN Growth','ISIN Div Reinvestment','Scheme Name','Net Asset Value','Repurchase Price','Sale Price','Time Stamp']
    for line in data:
        line =  str(line,'utf-8')#+";"+timestamp.strftime("%x-%X")
        line = line.split(";")
        if len(line) > 1:
            try:
                current_date = line[7].split("\r\n",1)[:-1][0]
                navs.append(line[7].split("\r\n",1)[:-1]+line[1:-1]+[timestamp.strftime("%x-%X")])
                written= True
            except:
                pass
    if written:
        navs = DataFrame(navs[1:],columns=navs_cols)
        navs.to_csv(mfNavHistory,index=False,header=headerAbsent)
        #mfNavHistory.write("\n<End>\n")
mfNavHistory.close()