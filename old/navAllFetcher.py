# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 05:35:56 2017

@author: Santosh Bag
"""
import datetime
import urllib.request
from pandas import DataFrame
#from sqlalchemy import create_engine
import mrigutilities

def navall_download():
    print("Mutual Fund NAVS download started", end =" ")
    NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt?t=09082017092931"
    mfNavHistory_path = "F:\Mrig Analytics\Development\data\mfNAVAllHistory.csv"
    mfNavHistory = open(mfNavHistory_path,"a+")
    
    engine = mrigutilities.sql_engine()
    
    data = urllib.request.urlopen(NAV_URL) # read only 20 000 chars
    timestamp = datetime.datetime.now()
    navs_cols = ['Date','Fund House','Scheme Type','ISIN Div Payout/ ISIN Growth','ISIN Div Reinvestment','Scheme Name','Net Asset Value','Repurchase Price','Sale Price','Time Stamp']
    last_fetched_data = mrigutilities.get_last_row(mfNavHistory_path)
    last_download_date = None
    headerAbsent = True
    try:
        last_download_date = last_fetched_data[0][navs_cols.index('Time Stamp')].split("-")[0]
        #print(last_download_date)
        headerAbsent = False
    except:
        pass
    if last_download_date != timestamp.strftime("%x"):
        written = False
        navs = []
        mutual_fund_scheme_type = ""
        mutual_fund_house = ""
        sub_header_count = 0
        for line in data:
            line =  str(line,'utf-8')#+";"+timestamp.strftime("%x-%X")
            #print(line)
            line = line.split(";")
            #print(line)
            if len(line) > 1:
                sub_header_count = 0
                #print(line)
                try:
                    current_date = line[-1].split("\r\n",1)[:-1][0]
                    navs.append(line[-1].split("\r\n",1)[:-1]+[mutual_fund_house,mutual_fund_scheme_type]+line[1:-1]+["",""]+[timestamp.strftime("%x-%X")])
                    #print(navs)
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
            #navs = DataFrame(navs[22:23],columns=navs_cols)
            #print(navs.tail(n=20))
            navs.to_csv(mfNavHistory,index=False,header=headerAbsent)
            navs = navs.drop('Time Stamp',axis=1)
            dt_handling = "to_char(\"Date\",'dd-Mon-YYYY') as \"Date\""
            navs = mrigutilities.clean_df_db_dups(navs,'mf_nav_history',engine,dup_cols=["Date","Scheme Name"],date_handling=dt_handling)[0]
            try:
                navs.to_sql('mf_nav_history',engine, if_exists='append', index=False)
            except:
                pass
            #mfNavHistory.write("\n<End>\n")
    mfNavHistory.close()
    print("Mutual Fund NAVS download finished\n")
    
if __name__ == '__main__':
    navall_download()