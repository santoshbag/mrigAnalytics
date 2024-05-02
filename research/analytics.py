
import sys, os

from matplotlib import pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime  # import date, timedelta
import pandas as pd  # import DataFrame
# from sqlalchemy import create_engine
import mrigutilities
import mrigstatics as ms
import nsepy
import mriggraphics as mg
import zipfile, re
import yfinance as yf
# from bs4 import BeautifulSoup
# from time import sleep
import csv
import research.screener_TA as sta
import numpy as np
import io,base64
import pandas_ta as ta

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView

import kite.kite_account as ka

# kite_object = ka.kite_account()
# today = datetime.date.today()
today = datetime.datetime.now()
engine = mrigutilities.sql_engine()

yahoomap = {'NIFTY' : '^NSEI',
            'BANKNIFTY' : '^NSEBANK',}
def level_analysis(scrip):
    m_expiry1 = mrigutilities.last_thursday_of_month(datetime.date.today())
    m_expiry2 = mrigutilities.last_thursday_of_month(m_expiry1 + datetime.timedelta(days=30))
    m_expiry3 = mrigutilities.last_thursday_of_month(m_expiry2 + datetime.timedelta(days=30))
    today = datetime.date.today()
    expiry_list = [m_expiry1, m_expiry2, m_expiry3]

    if ('NIFTY' in scrip):
        days = (3 - today.weekday() + 7) % 7
        expiry1 = today + datetime.timedelta(days=days)
        expiry2 = expiry1 + datetime.timedelta(days=7)
        expiry3 = expiry2 + datetime.timedelta(days=7)
        expiry4 = expiry3 + datetime.timedelta(days=7)
        expiry_list = [expiry1, expiry2, expiry3 ,expiry4]

    if ('BANKNIFTY' in scrip):
        expiry_list = []
        days = (2 - today.weekday() + 7) % 7
        expiry1 = today + datetime.timedelta(days=days)
        # expiry_list.append(m_expiry1) if ((m_expiry1 - expiry1).days == 1) else expiry_list.append(expiry1)
        expiry2 = expiry1 + datetime.timedelta(days=7)
        # expiry_list.append(m_expiry1) if ((m_expiry1 - expiry2).days == 1) else expiry_list.append(expiry2)
        expiry3 = expiry2 + datetime.timedelta(days=7)
        # expiry_list.append(m_expiry1) if ((m_expiry1 - expiry3).days == 1) else expiry_list.append(expiry3)
        # m_expiry = m_expiry1 if ((m_expiry1 - expiry3) == 1) else expiry3
        expiry4 = expiry3 + datetime.timedelta(days=7)
        # expiry_list.append(m_expiry1) if ((m_expiry1 - expiry4).days == 1) else expiry_list.append(expiry4)
        # m_expiry = m_expiry1 if ((m_expiry1 - expiry4) == 1) else expiry4
        expiry_list = [expiry1, expiry2, expiry3,expiry4]

    # CORRECT FOR HOLIDAYS
    holidays = ms.NSE_HOLIDAYS.keys()
    expiry_list_tmp = expiry_list
    expiry_list = []
    for expiry in expiry_list_tmp:
        if expiry.strftime('%d-%b-%Y') in holidays:
            expiry_list.append(expiry - datetime.timedelta(days = 1))
        else:
            expiry_list.append(expiry)

    print(scrip,' EXPIRIES', expiry_list)

    # scrip = ['TATAPOWER', 'BANKNIFTY']
    oc = mrigutilities.kite_OC(scrip, expiry_list)
    print(scrip,'  OPTION CHAIN ',oc)
    if oc is not None:
        # print(set(oc['expiry']))
        oc.reset_index(inplace=True)
        oi_tree = oc
        pcr = None
        pcr_str = ""
        # for expiry in sorted(set(list(oc['expiry'])), reverse=True):
        for expiry in expiry_list:
            print( expiry_list[0])
            ce_oi_sum = oc[(oc['tradingsymbol'].str[-2:] == 'CE') & (oc['expiry'] == expiry)][
                'oi'].sum()
            pe_oi_sum = oc[(oc['tradingsymbol'].str[-2:] == 'PE') & (oc['expiry'] == expiry)][
                'oi'].sum()
            oi_tree['oi_ce' + str(expiry)] = oc.loc[(oc['tradingsymbol'].str[-2:] == 'CE') & (
                    oc['expiry'] == expiry), 'oi'] / ce_oi_sum if ce_oi_sum else 0
            oi_tree['oi_pe' + str(expiry)] = -oc.loc[(oc['tradingsymbol'].str[-2:] == 'PE') & (
                    oc['expiry'] == expiry), 'oi'] / pe_oi_sum if pe_oi_sum else 0
            try:
                pcr = pe_oi_sum /ce_oi_sum if (expiry == expiry_list[0]) else pcr
                pcr_str = '            ' + 'PCR : ' + '{0:.2f}'.format(pcr)
            except:
                pass
        oi_tree.fillna(0, inplace=True)

        max_pain_oc = oc[oc['expiry'] == expiry_list[0]]
        if scrip[0] in ['NIFTY','BANKNIFTY']:
            yahooscrip = yahoomap[scrip[0]]
        else:
            yahooscrip = scrip[0]+'.NS'
        last_price = yf.download(yahooscrip,period='1d')['Close'].values[0]
        last_price_str = '({0:.2f})'.format(last_price)
        max_pain = None
        max_pain_str = ""
        if ((max_pain_oc is not None) & (len(max_pain_oc) > 0)) :
            print("max_pain_oc",max_pain_oc)
            max_pain_oc['itm x oi'] = max_pain_oc[['strike', 'tradingsymbol', 'oi']].apply(
                lambda x: max(last_price - x['strike'], 0) * x['oi'] if (x['tradingsymbol'][-2:] == 'CE') else max(
                    x['strike'] - last_price, 0) * x['oi'], axis=1)
            max_pain_oc = max_pain_oc.groupby(by=['strike'], as_index=False)['itm x oi'].sum().fillna(0).round()
            max_pain = max_pain_oc.sort_values(['itm x oi'], ascending=False).head(1)['strike'].values[0]
            max_pain_str = '      Max Pain : ' + '{0:.2f}'.format(max_pain)

        oi_tree.sort_values(by=['expiry', 'strike'], ascending=[True, True], inplace=True)
        num_charts = 4 if scrip[0] in ['NIFTY','BANKNIFTY'] else 3
        fig, ax = plt.subplots(1, num_charts, figsize=(20, 10), squeeze=False)
        fig.suptitle(scrip[0] + last_price_str+pcr_str+max_pain_str, fontsize=15)
        print(scrip[0]+' Number of Charts for '+str(num_charts))
        # oi_tree[['oi_ce','oi_pe']].plot(kind='barh')
        i = 0
        last_price = yf.download(yahooscrip,period='1d')['Close'].values[0]
        bar_height = min(10,0.003*last_price) if last_price < 30000 else min(20,0.003*last_price)
        for exp in sorted(set(list(oi_tree['expiry']))):
            print(exp)
            ax1 = ax[0, i]
            ax1.set_title(exp)
            ax1.grid()
            ax2 = ax[0, i].twinx()
            x_data = oi_tree[oi_tree['expiry'] == exp]['strike']
            y1_data = oi_tree[oi_tree['expiry'] == exp]['oi_ce' + str(exp)]
            y2_data = oi_tree[oi_tree['expiry'] == exp]['oi_pe' + str(exp)]
            if i == 0:
                ax1.set_ylabel('STRIKE',fontsize=16)
            else:
                ax1.set_ylabel('', fontsize=16)
            ax1.set_xlabel('OPEN INTEREST',fontsize=16)
            ax1.tick_params(axis='y', labelsize=12)

            ax1.barh(x_data, y1_data, color='b', height=bar_height)

            # ax2.set_ylabel('STRIKE')

            # ax2.tick_params(axis='y', labelsize=10)
            ax2.barh(x_data, y2_data, color='g',height=bar_height)
            ax2.get_yaxis().set_visible(False)
            i += 1

        buffer = io.BytesIO()
        fig.savefig(buffer,format="PNG")
        level_chart = base64.b64encode(buffer.getvalue()).decode('utf-8').replace('\n', '')
        buffer.close()
        # return [fig,oi_tree ,pcr ,max_pain]
        return {'level_chart' : level_chart,
                'oi_tree': oi_tree,
                'pcr': pcr,
                'max_pain': max_pain}
    else:
        return None

def apply_strat(x,CustomStrategy):
    x.ta.strategy(CustomStrategy)
    return x
def display_tech_analysis(stocks='NIFTY 100'):
    # get the stock name from the entry box
    df = pd.DataFrame()
    cnt = 1

    engine = mrigutilities.sql_engine()
    period_date = datetime.date.today() - datetime.timedelta(days=180)

    print('<<<<<<<<<<' + str(stocks) + '>>>>>>>>>>')

    if stocks == 'NIFTY 100':
        slist = str(ms.NIFTY_100).replace('{', '(').replace('}', ')')
    elif stocks == 'NIFTY 50':
        slist = str(ms.NIFTY_50).replace('{', '(').replace('}', ')')
    else:
        slist = str(stocks).replace('[', '(').replace(']', ')')

    slist = slist.replace(')', ",'NIFTY 50','NIFTY BANK')")
    sql = "select date,symbol, high as High,low as Low,close as Close from stock_history where \
    symbol in {} and date > '{}' \
    order by symbol, date asc".format(slist, period_date.strftime('%Y%m%d'))
    # print(sql)
    data = pd.read_sql(sql, engine)
    # print(data)
    CustomStrategy = ta.Strategy(
        name="Momo and Volatility",
        description=" MACD and SuperTrend",
        ta=[
            {"kind": "macd"},
            {"kind": "supertrend", "period": 7, "multiplier": 3},
        ]
    )

    # data = data[data['symbol'] == 'SBIN']
    newdf = data.groupby(['symbol']).apply(apply_strat,CustomStrategy=CustomStrategy)
    # newdf = pd.DataFrame()
    # print('NEWDF----',newdf)
    return newdf

def spot_fut_analysis(scrip):
    '''
    SPOT FUT SPREAD
    '''

    sql = "select date, 'spot' as expiry, close from stock_history where symbol = '%s' and date > (now() - interval '1 year') order by date desc"
    spot = pd.read_sql(sql % (scrip), engine)
    expiry = ['20240328', '20240425', '20240530']
    sql = "select date, expiry ,close from futures_options_history \
            where symbol = '%s' and option_type not in ('CE','PE') \
            and date > (now() - interval '1 year') order by date desc"
    fut = pd.read_sql(sql % (scrip), engine)
    spot_fut = pd.concat([spot, fut])

    spot_fut_p = spot_fut.pivot(index=['date'], columns=['expiry'], values=['close'])
    spot_fut_p.columns = spot_fut_p.columns.droplevel(level=0)
    # spot_fut_p
    spot_fut_new = pd.DataFrame()
    for i in range(0, len(spot_fut_p)):
        try:
            df = pd.DataFrame(spot_fut_p.iloc[i]).dropna().transpose()
            # print(df)
            # df.columns[0]
            df = df.rename(
                columns={df.columns[0]: "near", df.columns[1]: "mid", df.columns[2]: "far", df.columns[3]: "spot"})
            spot_fut_new = pd.concat([spot_fut_new, df])
        except:
            pass

    spot_fut_new['near_sprd'] = spot_fut_new['near'] - spot_fut_new['spot']
    spot_fut_new['mid_sprd'] = spot_fut_new['mid'] - spot_fut_new['near']
    spot_fut_new['far_sprd'] = spot_fut_new['far'] - spot_fut_new['mid']
    return (spot_fut_new)

if __name__ == '__main__':
    level_analysis(['NIFTY'])
