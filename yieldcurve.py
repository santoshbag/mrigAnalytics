# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:41:11 2018

@author: Santosh Bag

This module downloads yield curves for different currencies.
"""

import requests
import datetime,pandas
from bs4 import BeautifulSoup
import mrigstatics,mrigutilities

def get_yieldCurve(currency="INR"):
    
    s = requests.Session()
    response = s.get(mrigstatics.WGB_YIELD_URL[currency])
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    yield_table_num = {'INR':3,
                       'USD':3,
                       'GBP':3}
    
    price_table_num = {'INR':5,
                       'USD':5,
                       'GBP':5}
    
    curve_date = str(soup.find_all('p')[0].find_all(class_='w3-small')[0].text).replace('Last Update: ',"").replace(' GMT+2',"").split(" ")
    curve_date = curve_date[0]+"-"+curve_date[1]+"-"+curve_date[2]
    curve_date = datetime.datetime.strptime(curve_date,'%d-%b-%Y' )
    tables = soup.find_all("table")
    
    yield_table = []
    price_table = []
    
    yield_heads = tables[yield_table_num[currency]].find_all('th')
    yield_table_cols = [col.text for col in yield_heads]
    yield_table_cols = ['ResidualMaturity','Yield','Chg 1M','Chg 6M']
            
    for row in tables[yield_table_num[currency]].find_all('tr'):
        cells = row.find_all('td')
        yield_table.append([str(cell.text).strip().replace("%","") for cell in cells][1:5])
        
    
    price_heads = tables[price_table_num[currency]].find_all('th')
    price_table_cols = [col.text for col in price_heads]
    price_table_cols.pop(3)
#    print(yield_table_cols)
    
    for row in tables[price_table_num[currency]].find_all('tr'):
        cells = row.find_all('td')
        price_table.append([str(cell.text).strip().replace("%","") for cell in cells][1:])    
    
    dupindex = []    
    for items in yield_table:
        if items == []:
            dupindex.append(yield_table.index(items))
    for dups in dupindex:
        yield_table.pop(dups)
    
    dupindex = []    
    for items in price_table:
        if items == []:
            dupindex.append(price_table.index(items))
    for dups in dupindex:
        price_table.pop(dups)
    
#    print(yield_table)
    yield_table = pandas.DataFrame(yield_table,columns=mrigutilities.get_finalColumns(yield_table_cols))
    yield_table.rename(columns=lambda x: x.replace("%",'_per'),inplace=True)
    yield_table.insert(0,column='curvedate',value=curve_date)
    yield_table.insert(1,column='curve',value=currency)
    price_table = pandas.DataFrame(price_table[1:-1],columns=mrigutilities.get_finalColumns(price_table_cols[1:]))
    price_table.rename(columns=lambda x: x.replace("%",'_per'),inplace=True)
    price_table.insert(0,column='curvedate',value=curve_date)
    price_table.insert(1,column='curve',value=currency)
    
    yield_table = yield_table.merge(price_table,how='left',on=['curvedate','curve','tenor','yield'])
    
    s.close()
    return yield_table

def yield_download():
    print("Yield Curves download started", end =" ")
    yieldCurveHistory_path = "F:\Mrig Analytics\Development\data\yieldCurveHistory.csv"
    yieldCurveHistory = open(yieldCurveHistory_path,"a+")
    
    last_fetched_data = mrigutilities.get_last_row(yieldCurveHistory_path)
    if last_fetched_data is None:
        headerAbsent = True
    else:
        headerAbsent = False
    
    engine = mrigutilities.sql_engine()
    timestamp = datetime.datetime.now()
    
    for currency in mrigstatics.CURVE_LIST:
        yield_table = get_yieldCurve(currency)
        yield_table.insert(len(yield_table.columns),column='timestamp',value=timestamp)
        yield_table.to_csv(yieldCurveHistory,index=False,header=headerAbsent)
        yield_table = yield_table.drop("timestamp",axis=1)
        yield_table = mrigutilities.clean_df_db_dups(yield_table,'yieldcurve',engine,dup_cols=["curvedate","curve","tenor"])[0]
        try:
            yield_table.to_sql('yieldcurve',engine, if_exists='append', index=False)
        except:
            pass
    yieldCurveHistory.close()
    print("Yield Curves download finished\n")
    
if __name__ == '__main__':
    yield_download()