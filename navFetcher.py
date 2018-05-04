# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 05:35:56 2017

@author: Santosh Bag
"""

import urllib.request
from pandas import DataFrame

NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt?t=09082017092931"
mfNavHistory = open("F:\Development\ideasTrade\mfNAVHistory.csv","a+")
mfISINList = open("F:\Development\ideasTrade\mfISINList.txt","r")

data = urllib.request.urlopen(NAV_URL) # read only 20 000 chars
#data = data.split("\n") # then split it into lines
#data = data.readline()
#ISINs = ['INF846K01EW2','INF846K01131','INF209K01N82','INF090I01IQ4','INF109K016L0','INF789F01XD4']
ISINs = [line.split("\n")[0] for line in mfISINList]
if len(ISINs) > 0:
    #mfNavHistory.write("\n<Start>\n")
    navs = []
    navs_cols = ['Date','ISIN Div Payout/ ISIN Growth','ISIN Div Reinvestment','Scheme Name','Net Asset Value','Repurchase Price','Sale Price']
for line in data:
    line =  str(line,'utf-8')
    line = line.split(";")
    try:
        ISIN = line[1]
#    print(str(lines,'utf-8'))
        if ISIN in ISINs:
            #print(line[7].split("\r\n",1)[0],ISIN,line[3],line[4])
            #navLine = line[7].split("\r\n",1)[0]+","+ ISIN +","+ line[3]+","+ line[4]+"\r"
            navs.append(line[7].split("\r\n",1)[:-1]+line[1:-1])
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