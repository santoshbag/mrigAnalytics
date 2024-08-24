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
import logging



# date_range = pd.bdate_range(start='02/23/2024', end = '02/24/2024',
#                          freq='C', holidays = holidays(2024,12))


datadir = os.path.dirname(__file__)
engine = mu.sql_engine()

eq_dir_qtr = os.path.join('..','resources','equity_research','input')
eq_dir_done = os.path.join('..','resources','equity_research','Done')

eq_dir_error_fie = os.path.join('..','resources','equity_research','errors','errors.log')

# Create and configure logger
logging.basicConfig(filename=eq_dir_error_fie,
                    format='%(asctime)s %(message)s',
                    filemode='a+')

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
                    sql = '''
                        insert into financial_results (symbol,period_ended, related_qtr, results, period,consolidated,timestamp ) 
                        values (%s,%s,%s,%s,%s,%s,%s) on conflict (symbol,period_ended,period) 
                        do update set
                        related_qtr = excluded.related_qtr,
                        results = excluded.results,
                        consolidated = excluded.consolidated,
                        timestamp = excluded.timestamp
                        '''
                    for i in data.index:
                        engine.execute(sql, (data.loc[i,'symbol'], data.loc[i,'period_ended'],
                                             data.loc[i,'related_qtr'],data.loc[i,'results'],
                                             data.loc[i,'period'],data.loc[i,'consolidated'],
                                             data.loc[i,'timestamp']))

                    # data.to_sql('financial_results',engine,if_exists='append',index=False)
                    print(data)#[['consolidated','xbrl_url','results']])
                except:
                    pass


def results_download_all():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    master_data = pd.DataFrame()

    qtrly_results_xml = 'https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml'
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    s = requests.Session()
    response = s.get(qtrly_results_xml, headers=headers)

    root = ET.fromstring(response.text)
    sql = '''
        insert into financial_results (symbol,period_ended, related_qtr, results, period,consolidated,timestamp )
        values (%s,%s,%s,%s,%s,%s,%s) on conflict (symbol,period_ended,period) 
        do update set
        related_qtr = excluded.related_qtr,
        results = excluded.results,
        consolidated = excluded.consolidated,
        timestamp = excluded.timestamp
        '''
    results = []
    for item in root.findall('.//item/*'):
        # print(item.tag,item.attrib,item.text)
        if item.tag == 'title':
            row = {}
            # company_name.append(item.text)
            row['COMPANY NAME'] = item.text.replace('\n', '').strip()
        if item.tag == 'link':
            row['** XBRL'] = item.text.replace('\n', '').strip()
        if item.tag == 'description':
            desc = item.text
            desc = desc.split('|')

            for d in desc:
                # print(d)
                key = d.split(':')[0]
                val = d.split(':')[1].replace('\n', '').strip()
                # print(key,val)
                if key == 'RELATING TO':
                    row['RELATING TO'] = val
                if key == 'AUDITED/UNAUDITED':
                    row['AUDITED / UNAUDITED'] = val
                if key == 'CUMULATIVE/NON-CUMULATIVE':
                    row['CUMULATIVE / NON-CUMULATIVE'] = val
                if key == 'CONSOLIDATED/NON-CONSOLIDATED':
                    row['CONSOLIDATED / NON-CONSOLIDATED'] = val
                if key == 'IND AS/ NON IND AS':
                    row['IND AS/ NON IND AS'] = val
                if key == 'PERIOD':
                    row['PERIOD'] = val
                if key == 'PERIOD ENDED':
                    row['PERIOD ENDED'] = val
        if item.tag == 'pubDate':
            row['Exchange Received Time'] = item.text.replace('\n', '').strip()
            row['Exchange Dissemination Time'] = item.text.replace('\n', '').strip()
            row['Time Taken'] = 10
        results.append(row)

    # print(results)

    results = pd.DataFrame(results)
    master_data = pd.concat([master_data,results])
    # print(master_data)
    for r, d, f in os.walk(eq_dir_qtr):
        for file in f:
            if re.search("^FINANCIAL_RESULTS.*csv", file):
                # if re.search("^FINRESULTS_ANNUAL_TATAMOTORS.*csv",file):
                # sym = os.path.basename(file).split('.')[0].split('_')[2]

                # stockbhavlist.append(os.path.join(r,file))
                file = os.path.join(r, file)
                print(file)

                data = pd.read_csv(file)
                master_data = pd.concat([master_data,data])

    cols = {'COMPANY NAME': 'symbol', 'CONSOLIDATED / NON-CONSOLIDATED': 'consolidated', 'PERIOD': 'period',
            'PERIOD ENDED': 'period_ended', 'RELATING TO': 'related_qtr', '** XBRL': 'xbrl_url'}
    # print('prev',master_data.columns)
    # print('dict',cols.keys())
    master_data = master_data[cols.keys()]
    master_data.rename(columns=cols, inplace=True)
    master_data['period_ended'] = pd.to_datetime(master_data['period_ended']).dt.date
    # print(master_data['period_ended'])
    # print(master_data['consolidated'])


    # data = data[data['period_ended'] > datetime.date(2020, 1, 1)]
    master_data = master_data[master_data['consolidated'] == 'Consolidated']
    # print('later2',master_data)

    master_data['timestamp'] = timestamp


    for i in master_data.index:
        print(master_data.loc[i,'symbol'])

        try:
            # data['results'] = data['xbrl_url'].apply(lambda x: parse_xbrl(x))
            results = parse_xbrl(master_data.loc[i,'xbrl_url'])
            # data.drop('xbrl_url', axis=1, inplace=True)
            symbol = json.loads(results)['Symbol']

        # for i in data.index:
            # print(data.loc[i,'symbol'])
            engine.execute(sql, (symbol, master_data.loc[i,'period_ended'],
                                 master_data.loc[i,'related_qtr'],results,
                                 master_data.loc[i,'period'],master_data.loc[i,'consolidated'],
                                 master_data.loc[i,'timestamp']))
            print(symbol, 'Results Loaded')
        # data.to_sql('financial_results',engine,if_exists='append',index=False)
        # print(data)  # [['consolidated','xbrl_url','results']])

        except Exception as error:
            print(master_data.loc[i,'symbol'],"  Error ",error)
            logger.error(master_data.loc[i,'symbol']+"  Error "+str(error))
            pass

    for r, d, f in os.walk(eq_dir_qtr):
        for file in f:
            if re.search("^FINANCIAL_RESULTS.*csv", file):
                os.replace(os.path.join(eq_dir_qtr, os.path.basename(file)),
                           os.path.join(eq_dir_done, os.path.basename(file)))
    print(master_data)#print(df_list[2])

#
if __name__ == '__main__':
    # results_download()
    results_download_all()

