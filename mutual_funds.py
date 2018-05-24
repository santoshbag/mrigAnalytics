# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:41:11 2018

@author: Santosh Bag

This module has Mutual Fund related utilities.
Functions are present for getting mutual fund information
like Portfolio Holdings, NAV, Ratings, AUM, Category, Launch-Date, Expense Ratio

"""

import urllib,csv,requests
import datetime,pandas
from bs4 import BeautifulSoup
import mrigstatics

ALL_FUNDS_SNAPSHOT_URL ='https://www.valueresearchonline.com/funds/fundSelector/fundSelectResult.asp?funcName=snapshot&amc=4,8799,5,312,332,8,9055,181,339,11,8927,28,302,308,14,9023,298,9636,9655,319,19,218,185,21,11141,327,9054,10157,15,317,24,186,25,26,187,27,10,9521,311&cat=equityExcSec,debtsAll,hybridAll,31,32,7,6,5,4,1,30,3,2,12,15,20,21,8,10,9,13,17,11,18,19,28,26,27,24,25,23,29&exc=susp,close&schemecode=&myport=&pg=&fType=csv'
ALL_FUNDS_PORTFOLIO_URL='https://www.valueresearchonline.com/funds/fundSelector/fundSelectResult.asp?funcName=portfolio&amc=4,8799,5,312,332,8,9055,181,339,11,8927,28,302,308,14,9023,298,9636,9655,319,19,218,185,21,11141,327,9054,10157,15,317,24,186,25,26,187,27,10,9521,311&cat=equityExcSec,debtsAll,hybridAll,31,32,7,6,5,4,1,30,3,2,12,15,20,21,8,10,9,13,17,11,18,19,28,26,27,24,25,23,29&exc=susp,close&schemecode=&myport=&pg=&fType=csv'

def get_fund_snapshots():
    
    s = requests.Session()
    s.get(mrigstatics.VR_LOGIN['VR_URL'])
    s.post(mrigstatics.VR_LOGIN['VR_URL'],data=mrigstatics.VR_LOGIN['CRED'])
    download = s.get(ALL_FUNDS_SNAPSHOT_URL)
    decoded_content = download.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    data_cols = ['fund',
                 'rating',
                 'category',
                 'launch_date',
                 'expense_ratio_in_per',
                 '1_yr_ret',
                 '1_yr_rank',
                 'net_assets_in_cr']
    
    for row in my_list:
        if len(row) != len(data_cols):
            my_list.remove(row)
        else:
            row[1] = row[1].count('*')
    
    fund_snapshots = pandas.DataFrame(my_list,columns=data_cols)
    return fund_snapshots

    
def get_fund_portfolios(schemeid=None):
    if schemeid is not None:
        scheme_list = [schemeid]
    else:
        scheme_list = mrigstatics.VR_MF_CODE.keys()
        
    s = requests.Session()
    s.get(mrigstatics.VR_LOGIN['VR_URL'])
    s.post(mrigstatics.VR_LOGIN['VR_URL'],data=mrigstatics.VR_LOGIN['CRED'])
    
    VR_PORT_URL = 'https://www.valueresearchonline.com/funds/portfoliovr.asp?schemecode=%s'
    
    fund_portfolio = []
    for scheme in scheme_list:
        response = s.get(VR_PORT_URL %(scheme))
        soup = BeautifulSoup(response.text, 'html.parser')
        table= soup.find_all(id="fund-snapshot-port-holdings")
        for body in table:
            heads = body.find_all('th')
            fund_portfolio_cols = [str(head.text).strip() for head in heads][1:]
            for row in body.find_all('tr'):
                cells = row.find_all('td')
                fund_portfolio.append([str(cell.text).strip() for cell in cells][1:])
    
    for items in fund_portfolio:
        if items == []:
            fund_portfolio.remove(items)
    fund_portfolios = pandas.DataFrame(fund_portfolio,columns=fund_portfolio_cols[1:])
    s.close()
    return fund_portfolios
    
    
        
        
        
        
        
