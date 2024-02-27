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
import pandas as pd

ALL_FUNDS_SNAPSHOT_URL ='https://www.valueresearchonline.com/funds/fundSelector/fundSelectResult.asp?funcName=snapshot&amc=4,8799,5,312,332,8,9055,181,339,11,8927,28,302,308,14,9023,298,9636,9655,319,19,218,185,21,11141,327,9054,10157,15,317,24,186,25,26,187,27,10,9521,311&cat=equityExcSec,debtsAll,hybridAll,31,32,7,6,5,4,1,30,3,2,12,15,20,21,8,10,9,13,17,11,18,19,28,26,27,24,25,23,29&exc=susp,close&schemecode=&myport=&pg=&fType=csv'
ALL_FUNDS_PORTFOLIO_URL='https://www.valueresearchonline.com/funds/fundSelector/fundSelectResult.asp?funcName=portfolio&amc=4,8799,5,312,332,8,9055,181,339,11,8927,28,302,308,14,9023,298,9636,9655,319,19,218,185,21,11141,327,9054,10157,15,317,24,186,25,26,187,27,10,9521,311&cat=equityExcSec,debtsAll,hybridAll,31,32,7,6,5,4,1,30,3,2,12,15,20,21,8,10,9,13,17,11,18,19,28,26,27,24,25,23,29&exc=susp,close&schemecode=&myport=&pg=&fType=csv'

engine = mrigutilities.sql_engine()


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

def download_nav(download_mode='mfsingle'):
    # sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    # dir_loc = os.path.join(os.path.dirname(__file__), '..','data')

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    mf_dir = os.path.join('..', '..', 'data', 'MF')

    req = requests.Session()

    '''
    ******************************************
    This code snippet downloads historical data for all mutual funds 
    from AMFI website for a particular list of years and stores them
    in csv files.

    input is a list of years

    ******************************************

    '''
    nav_dir = os.path.join(mf_dir, 'NAV')

    download = download_mode

    if download == 'mfsingleannual':
        amfi_url = 'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf={}&frmdt={}&todt={}'
        # print(amfi_url.format('43','01-Jan-2023','31-Dec-2023'))
        # mf_no = 43
        amfi_amc = []
        years = [2020, 2021, 2022, 2023, 2024]
        # years = [2023]
        for mf_no in range(1, 1000):
            # for mf_no in [9]:
            for year in years:
                from_date = '01-Jan-' + str(year)
                to_date = '31-Dec-' + str(year)
                amfi = amfi_url.format(str(mf_no), from_date, to_date)
                #         data = req.get(amfi)
                try:
                    data = pd.read_csv(amfi, sep=';')
                    amc = data['Scheme Code'].loc[1]
                    amfi_amc.append([mf_no, amc])
                    print(amc, mf_no)
                    local_file = os.path.join(nav_dir, str(amc) + '_' + from_date + '_' + to_date + '.csv')
                    print(str(local_file))
                    data.to_csv(local_file)
                except:
                    pass

    elif download == 'mfsingle':
        amfi_url = 'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf={}&frmdt={}&todt={}'
        # print(amfi_url.format('43','01-Jan-2023','31-Dec-2023'))
        # mf_no = 43
        # years = [2023]
        backdays = 1
        to_date = datetime.datetime.now().strftime('%d-%b-%Y')
        from_date = (datetime.datetime.now() - datetime.timedelta(backdays)).strftime('%d-%b-%Y')

        for mf_no in range(1, 200):
            # for mf_no in [9]:
            amfi = amfi_url.format(str(mf_no), from_date, to_date)
            #         data = req.get(amfi)
            try:
                data = pd.read_csv(amfi, sep=';')
                amc = data['Scheme Code'].loc[1]
                print(amc, mf_no)
                local_file = os.path.join(nav_dir, str(amc) + '_' + from_date + '_' + to_date + '.csv')
                print(str(local_file))
                data.to_csv(local_file)
            except:
                pass

    elif download == 'daily':
        amfi_url = 'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}&todt={}'
        # print(amfi_url.format('43','01-Jan-2023','31-Dec-2023'))
        # mf_no = 43
        amfi_amc = []
        to_date = datetime.datetime.now().strftime('%d-%b-%Y')
        from_date = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%d-%b-%Y')
        amfi = amfi_url.format(from_date, to_date)
        #         data = req.get(amfi)
        try:
            data = pd.read_csv(amfi, sep=';')
            #         amc = data['Scheme Code'].loc[1]
            #         amfi_amc.append([mf_no,amc])
            #         print(amc,mf_no)
            local_file = os.path.join(nav_dir, 'ALL_MF_' + from_date + '_' + to_date + '.csv')
            print(str(local_file))
            data.to_csv(local_file)
        except:
            pass

    elif download == 'allmf':
        amfi_url = 'https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}&todt={}'
        # print(amfi_url.format('43','01-Jan-2023','31-Dec-2023'))
        # mf_no = 43
        amfi_amc = []
        #     years = [2020,2021,2022,2023,2024]
        # years = [2023]
        from_date = '01-Jan-2024'
        to_date = '31-Dec-2024'
        amfi = amfi_url.format(from_date, to_date)
        #         data = req.get(amfi)
        try:
            data = pd.read_csv(amfi, sep=';')
            #         amc = data['Scheme Code'].loc[1]
            #         amfi_amc.append([mf_no,amc])
            #         print(amc,mf_no)
            local_file = os.path.join(nav_dir, 'ALLMF_' + from_date + '_' + to_date + '.csv')
            print(str(local_file))
            data.to_csv(local_file)
        except:
            pass
    print('download complete!')

    '''
    *****************************************
    This code snippet reads the downloaded csv files containing 
    historical mf and nav data and loads it into database table
    'mf_history'

    *****************************************
    '''

    nav_dir = os.path.join(mf_dir, 'NAV')
    processed_dir = os.path.join(mf_dir, 'Processed')

    col_map = {
        'Date': 'nav_date',
        'Scheme Type': 'scheme_type',
        'Scheme Name': 'scheme_name',
        'ISIN Div Payout/ISIN Growth': 'isin',
        'Net Asset Value': 'nav'
    }
    # file = 'G:\Mrig Analytics\data\MF\Aditya Birla Sun Life Mutual Fund_01-Jan-2023_31-Dec-2023.csv'
    for file in os.listdir(nav_dir):
        filename = os.fsdecode(file)
        print(filename)
        data = pd.read_csv(os.path.join(nav_dir, filename))
        amc = data['Scheme Code'].loc[1]
        # data
        print(amc)
        data['Scheme Type'] = ''
        data['amc'] = amc
        data.drop(data[data['Scheme Code'] == amc].index, inplace=True)
        data['Net Asset Value'] = data[['Net Asset Value']].apply(pd.to_numeric, errors='coerce').fillna(-1)

        data = data.reset_index()
        scm_lst = list(data[data['Date'].isna()]['Scheme Code'])
        inx_lst = list(data[data['Date'].isna()]['Scheme Code'].index)
        data.drop(columns=['index', 'Scheme Code', 'Unnamed: 0'], inplace=True)
        scm_dict = {}
        for i in range(0, len(scm_lst)):
            scm_dict[scm_lst[i]] = inx_lst[i]

        for i in range(0, len(scm_lst) - 1):
            start = scm_dict[scm_lst[i]] + 1
            end = scm_dict[scm_lst[i + 1]] - 1
            data['Scheme Type'].loc[start:end] = scm_lst[i]
        data['Scheme Type'].loc[scm_dict[scm_lst[-1]] + 1:len(data)] = scm_lst[-1]
        data.rename(columns=col_map, inplace=True)
        data = data[['nav_date', 'scheme_type', 'scheme_name', 'amc', 'isin', 'nav']]
        data.to_sql('mf_history', engine, if_exists='append', index=False)
        os.replace(os.path.join(nav_dir, filename), os.path.join(processed_dir, filename))
    print('Load Done')

def mf_scheme_info():
    '''
    Code to load scheme info to database
    '''

    mf_dir = os.path.join('..', '..', 'data', 'MF')

    scheme_dir = os.path.join(mf_dir, 'GENERAL')
    scheme_col_map = {'AMC': 'amc',
                      'Code': 'scheme_code',
                      'Scheme NAV Name': 'scheme_name',
                      'Scheme Type': 'scheme_subscrip_type',
                      'Scheme Minimum Amount': 'min_inv_amt',
                      'Launch Date': 'launch_date',
                      ' Closure Date': 'close_date',
                      'ISIN Div Payout/ ISIN Growth': 'isin',
                      'ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment': 'isin'
                      }

    for file in os.listdir(scheme_dir):
        filename = os.fsdecode(file)
        print(filename)
        data = pd.read_csv(os.path.join(scheme_dir, filename))
        data['scheme_asset_type_1'] = data['Scheme Category']
        data['scheme_asset_type_2'] = ''
        data['scheme_asset_type_1'] = data['Scheme Category'].apply(lambda x: x.split('-')[0].strip())
        try:
            data['scheme_asset_type_2'] = data['Scheme Category'].apply(lambda x: x.split('-')[-1].strip())
        except:
            pass

        data['scheme_plan_type_1'] = ''
        data['scheme_plan_type_2'] = ''
        data['scheme_plan_type_1'] = data['Scheme NAV Name'].apply(
            lambda x: 'Direct' if ('Direct' in x.split()) else 'Regular')
        data['scheme_plan_type_1'] = data['Scheme NAV Name'].apply(
            lambda x: 'Direct' if ('DIRECT' in x.split()) else 'Regular')
        data['scheme_plan_type_2'] = data['Scheme NAV Name'].apply(
            lambda x: 'Growth' if ('Growth' in x.split()) else 'Dividend')
        data['scheme_plan_type_2'] = data['Scheme NAV Name'].apply(
            lambda x: 'Growth' if ('GROWTH' in x.split()) else 'Dividend')
        data.rename(columns=scheme_col_map, inplace=True)
        data.drop(columns=['Scheme Category', 'Scheme Name'], inplace=True)

    print(data.columns)
    data.to_sql('mf_scheme_master', engine, index=False, if_exists='append')

def scheme_aum():
    '''
    Code to insert AUM in scheme master database
    '''

    mf_dir = os.path.join('..', '..', 'data', 'MF')

    aum_dir = os.path.join(mf_dir, 'AUM')

    for file in os.listdir(aum_dir):
        filename = os.fsdecode(file)
        print(filename)
        data = pd.read_csv(os.path.join(aum_dir, filename), names=['code', 'scheme_name', 'aum', 'aum1'], header=None)
        data['aum'] = data['aum'] + data['aum1']
        data.drop(data[data['scheme_name'].isna()].index, inplace=True)
        data.drop(data[data['aum'].isna()].index, inplace=True)

        data.drop(columns=['code', 'aum1'], inplace=True)

    print(data)
    sql = """
    DROP TABLE IF EXISTS temp_scheme_aum;

    CREATE TABLE IF NOT EXISTS temp_scheme_aum (
        scheme_name text,
        aum text
    )
    """

    engine.execute(sql)
    data.to_sql('temp_scheme_aum', engine, if_exists='replace', index=False)

    sql = """
        UPDATE mf_scheme_master 
        SET aum = t.aum
        FROM temp_scheme_aum as t
        WHERE mf_scheme_master.scheme_name = t.scheme_name
    """
    engine.execute(sql)
    

if __name__ == '__main__':
#    
#     today = datetime.date.today()
# #    #weekly download of fundsnapshots and fund portfolio holdings
# #
#     if today.strftime('%A') == 'Thursday':
#         get_VR_MF_CODES()
#         eqlist = get_equity_fundlist()
#         get_fund_snapshots()
#         get_fund_portfolios(eqlist)
# #
##    fs = get_fund_portfolios(eqlist)
#    #fs = get_fund_snapshots()
    #print (fs)
    download_nav()
      
        
        
        
