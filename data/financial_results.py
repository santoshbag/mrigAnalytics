# -*- coding: utf-8 -*-
"""
Created on Tue Jul 09 09:01:52 2024

@author: Santosh Bag

reads NSE corporate results in XBRL format and  puts into database

"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import mrigutilities as mu
import pandas as pd
import datetime
import os,sys
import kite.kite_trade as zkite
import json
import xml.etree.ElementTree as ET
import requests
import zipfile,re


# date_range = pd.bdate_range(start='02/23/2024', end = '02/24/2024',
#                          freq='C', holidays = holidays(2024,12))


datadir = os.path.dirname(__file__)
engine = mu.sql_engine()

eq_dir_qtr = os.path.join('..','resources','equity_research')
timestamp = datetime.datetime.now()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}

def getSymbol(company_desc):
    # print(company_desc)
    sym = company_desc
    try:
        sym = engine.execute("select symbol from security_master where stock_name='"+company_desc+"' limit 1").fetchone()[0]
    except:
        pass
    return sym

def parse_xbrl(url):
    result = pd.DataFrame()
    # print(url)
    i = 0
    s = requests.Session()
    response = s.get(url, headers=headers)
    # print(response.content)

    # tree = ET.fromstring(response.content)

    # tapo = 'C:\\Users\\Santosh Bag\\Downloads\\TAPO.xml'
    # tree = ET.parse(tapo)
    # tree = ET.parse(response.text)
    # root = tree.getroot()
    root = ET.fromstring(response.text)
    results = {}
    for item in root:
        if 'in-bse-fin' in item.tag:
            #         print(item.attrib,item.text)
            results[item.tag.split('}')[1]] = item.text
    finres = pd.DataFrame.from_dict(results, orient='index')
    finres.rename(columns={0: i}, inplace=True)
    # print(finres)
    # finres
    # result = pd.concat([result,finres],axis=1)
    # print('RESULT\n',result)
    i = i + 1
    results = json.dumps(results)
    return results

def results_download():
    for r,d,f in os.walk(eq_dir_qtr):
        for file in f:
            if re.search("^FINRESULTS_.*csv",file):
            # if re.search("^FINRESULTS_ANNUAL_TATAMOTORS.*csv",file):
                sym = os.path.basename(file).split('.')[0].split('_')[2]

                # stockbhavlist.append(os.path.join(r,file))
                file = os.path.join(r,file)
                print(file)
                data = pd.read_csv(file)
                cols = {'CONSOLIDATED / NON-CONSOLIDATED' : 'consolidated','PERIOD': 'period','PERIOD ENDED' : 'period_ended','RELATING TO' : 'related_qtr','** XBRL' : 'xbrl_url'}
                data = data[cols.keys()]
                data['symbol'] = sym
                data.rename(columns=cols,inplace=True)
                data['period_ended'] = pd.to_datetime(data['period_ended']).dt.date
                data = data[data['period_ended'] > datetime.date(2020,1,1)]
                data = data[data['consolidated'] == 'Consolidated']
                try:
                    data['results'] = data['xbrl_url'].apply(lambda x: parse_xbrl(x))
                    data['timestamp'] = timestamp
                    data.drop('xbrl_url', axis=1, inplace=True)
                    data.to_sql('financial_results',engine,if_exists='append',index=False)
                    print(data)#[['consolidated','xbrl_url','results']])
                except:
                    pass


def results_download_all():
    for r, d, f in os.walk(eq_dir_qtr):
        for file in f:
            if re.search("^FINANCIAL_RESULTS.*csv", file):
                # if re.search("^FINRESULTS_ANNUAL_TATAMOTORS.*csv",file):
                # sym = os.path.basename(file).split('.')[0].split('_')[2]

                # stockbhavlist.append(os.path.join(r,file))
                file = os.path.join(r, file)
                print(file)
                data = pd.read_csv(file)
                cols = {'COMPANY NAME': 'symbol', 'CONSOLIDATED / NON-CONSOLIDATED': 'consolidated', 'PERIOD': 'period',
                        'PERIOD ENDED': 'period_ended', 'RELATING TO': 'related_qtr', '** XBRL': 'xbrl_url'}
                data = data[cols.keys()]
                data.rename(columns=cols, inplace=True)
                data['period_ended'] = pd.to_datetime(data['period_ended']).dt.date
                data = data[data['period_ended'] > datetime.date(2020, 1, 1)]
                data = data[data['consolidated'] == 'Consolidated']
                try:
                    data['results'] = data['xbrl_url'].apply(lambda x: parse_xbrl(x))
                    data['timestamp'] = timestamp
                    data.drop('xbrl_url', axis=1, inplace=True)
                    data['symbol'] = data['symbol'].apply(lambda x: getSymbol(x))
                    data.to_sql('financial_results',engine,if_exists='append',index=False)
                    # print(data)  # [['consolidated','xbrl_url','results']])
                except:
                    pass
                print(data)#print(df_list[2])

#    
if __name__ == '__main__':
    results_download_all()
