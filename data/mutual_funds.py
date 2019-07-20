# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:41:11 2018

@author: Santosh Bag

This module has Mutual Fund related utilities.
Functions are present for getting mutual fund information
like Portfolio Holdings, NAV, Ratings, AUM, Category, Launch-Date, Expense Ratio

"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import urllib,csv,requests
import datetime,pandas
from bs4 import BeautifulSoup
import mrigstatics,mrigutilities

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
    downloaddate = datetime.date.today().strftime('%Y-%m-%d')
    snapshotdate = my_list[1][0].split(" ")[1]
    data_cols = ['fund',
                 'rating',
                 'category',
                 'launch_date',
                 'expense_ratio_in_per',
                 '1_yr_ret',
                 '1_yr_rank',
                 'net_assets_in_cr',
                 'snapshot_date',
                 'download_date']
    
    for row in my_list:
        if len(row) != len(data_cols)-2:
            my_list.remove(row)
        else:
            row[1] = row[1].count('*')
            row.append(snapshotdate)
            row.append(downloaddate)
    
    fund_snapshots = pandas.DataFrame(my_list[2:],columns=data_cols)
    engine = mrigutilities.sql_engine()
    fund_snapshots.to_sql('mf_snapshot',engine, if_exists='append', index=False)
    return fund_snapshots

def get_VR_MF_CODES():
    s = requests.Session()
    s.get(mrigstatics.VR_LOGIN['VR_URL'])
    s.post(mrigstatics.VR_LOGIN['VR_URL'],data=mrigstatics.VR_LOGIN['CRED'])
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    engine = mrigutilities.sql_engine()

    VR_CODE_URL = 'https://www.valueresearchonline.com/funds/fundSelector/default.asp?amc=4%2C8799%2C5%2C312%2C332%2C8%2C9055%2C181%2C339%2C8927%2C28%2C302%2C308%2C14%2C9023%2C298%2C9636%2C9655%2C319%2C19%2C218%2C185%2C21%2C11141%2C327%2C9054%2C10157%2C15%2C11%2C317%2C24%2C186%2C25%2C26%2C187%2C27%2C10%2C9521%2C311&cat=equityAll%2CdebtsAll%2ChybridAll%2C100%2C101%2C102%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C111%2C112%2C113%2C114%2C115%2C116%2C117%2C118%2C119%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C137%2C138%2C139%2C140%2C141%2C142%2C143%2C144&exc=susp%2Cclose%2C3Star%2C2Star%2C1Star%2CnotRated'
    response = s.get(VR_CODE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    fundlist= soup.find_all(class_="fundName")
    code_value = ""
    for fund in fundlist:
        fundname = fund.text.strip().replace('\r',"").replace('\n',"").replace('\t',"").replace("'","''")
        fundcode = fund['href'].split("=")[1].strip()
        code_value = code_value + "|" + fundcode+":"+ fundname
    
    sql = "insert into codes values ('"+today+"','VR_MF_CODES','"+code_value[1:]+"')"
    engine.execute(sql)
    
    
def get_fund_portfolios(schemeid=None):
    if schemeid is not None:
        scheme_list = schemeid
    else:
        scheme_list = mrigstatics.VR_MF_CODE.keys()
        
    s = requests.Session()
    s.get(mrigstatics.VR_LOGIN['VR_URL'])
    s.post(mrigstatics.VR_LOGIN['VR_URL'],data=mrigstatics.VR_LOGIN['CRED'])
    
    VR_PORT_URL = 'https://www.valueresearchonline.com/funds/portfoliovr.asp?schemecode=%s'
    
    fund_portfolio = []
    fund_portfolio_cols = ['fund',
                      'company',
                      'sector',
                      'pe',
                      'holding_3yhigh',
                      'holding_3ylow',
                      'holding_current',
                      'holding_date',
                      'download_date']
    for scheme in scheme_list:
        response = s.get(VR_PORT_URL %(scheme[0]))
        soup = BeautifulSoup(response.text, 'html.parser')
        table= soup.find_all(id="fund-snapshot-port-holdings")
        downloaddate = datetime.date.today().strftime('%Y-%m-%d')
        holdingdate = downloaddate
        try:
            holdingdate = soup.find_all(class_='footnote')[2].text.split(" ")
            holdingdate = holdingdate[3][:-1]+"-"+holdingdate[2]+"-"+holdingdate[4]
        except:
            pass
        for body in table:
            #heads = body.find_all('th')
            #fund_portfolio_cols = [str(head.text).strip() for head in heads][1:]
            for row in body.find_all('tr')[2:]:
                cells = row.find_all('td')
#                fund_portfolio.append(scheme)
                fund_portfolio.append([scheme[1]] + [str(cell.text).strip() for cell in cells][1:]+[holdingdate,downloaddate])
#                fund_portfolio.append(holdingdate)
#                fund_portfolio.append(downloaddate)
#    print(fund_portfolio)            
    
    for items in fund_portfolio:
        if items == []:
            fund_portfolio.remove(items)
    fund_portfolios = pandas.DataFrame(fund_portfolio,columns=fund_portfolio_cols)
    engine = mrigutilities.sql_engine()
    fund_portfolios.to_sql('mf_portfolios',engine, if_exists='append', index=False)
    s.close()
    return fund_portfolios
    
def get_equity_fundlist():
    engine = mrigutilities.sql_engine()

    sql = "select fund from mf_snapshot where category like 'EQ%%'"
    eqfs = engine.execute(sql).fetchall()
    
    sql = "select code_value , code_date from codes where code_name='VR_MF_CODES' order by code_date desc limit 1"
    mfcodes = engine.execute(sql).fetchall()
    mfcodes = {code.split(":")[1]:code.split(":")[0] for code in mfcodes[0][0].split("|")}
    mfeqcodes = []
    for fund in eqfs:
        try:
            mfeqcodes.append([mfcodes[fund[0]],fund[0]])
        except:
            pass
        
    return mfeqcodes
    
        
if __name__ == '__main__':
#    
    today = datetime.date.today()
#    #weekly download of fundsnapshots and fund portfolio holdings
#    
    if today.strftime('%A') == 'Thursday':
        get_VR_MF_CODES()
        eqlist = get_equity_fundlist()
        get_fund_snapshots()
        get_fund_portfolios(eqlist)
#
##    fs = get_fund_portfolios(eqlist)
#    #fs = get_fund_snapshots()
    #print (fs)
      
        
        
        
