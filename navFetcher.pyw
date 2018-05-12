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
mfNavHistory_path = "F:\Development\ideasTrade\mfNAVHistory.csv"
mfNavHistory = open(mfNavHistory_path,"a+")
mfISINList_path = "F:\Development\ideasTrade\mfISINList.txt"
mfISINList = open(mfISINList_path,"r")

def get_last_row(csv_filename,lines=1):
    with open(csv_filename,'r') as f:
        try:
            lastrow = deque(csv.reader(f), lines)
        except IndexError:  # empty file
            lastrow = None
        return lastrow

data = urllib.request.urlopen(NAV_URL) # read only 20 000 chars
timestamp = datetime.datetime.now()
#print(timestamp.strftime("%c"))
#data = data.split("\n") # then split it into lines
#data = data.readline()
#ISINs = ['INF846K01EW2','INF846K01131','INF209K01N82','INF090I01IQ4','INF109K016L0','INF789F01XD4']
written = False
ISINs = [line.split("\n")[0] for line in mfISINList]
if len(ISINs) > 0:
    #mfNavHistory.write("\n<Start>\n")
    last_fetched_data = get_last_row(mfNavHistory_path,len(ISINs))
    #print(last_fetched_data)
    last_data_map= {}
    for lastdata in last_fetched_data:
        last_data_map[lastdata[1]] = lastdata[0]
    #print(last_data_map)
    navs = []
    navs_cols = ['Date','ISIN Div Payout/ ISIN Growth','ISIN Div Reinvestment','Scheme Name','Net Asset Value','Repurchase Price','Sale Price','Time Stamp']
for line in data:
    line =  str(line,'utf-8')#+";"+timestamp.strftime("%x-%X")
    line = line.split(";")
    try:
        ISIN = line[1]
#    print(str(lines,'utf-8'))
        if ISIN in ISINs:
            #print(line[7].split("\r\n",1)[0],ISIN,line[3],line[4])
            #navLine = line[7].split("\r\n",1)[0]+","+ ISIN +","+ line[3]+","+ line[4]+"\r"
            current_date = line[7].split("\r\n",1)[:-1][0]
            #print(ISIN)
            if last_data_map[ISIN] != current_date:
                navs.append(line[7].split("\r\n",1)[:-1]+line[1:-1]+[timestamp.strftime("%x-%X")])
           #navs.append([timestamp.strftime("%x-%X")])
            #print(navs)
           # mfNavHistory.write(navLine)
                written= True
    except:
        pass
if written:
    navs = DataFrame(navs,columns=navs_cols)
    navs.to_csv(mfNavHistory,index=False,header=False)
    #mfNavHistory.write("\n<End>\n")
mfNavHistory.close()
mfISINList.close()

