# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 12:16:12 2018

@author: Santosh Bag

@author: Santosh Bag

This module downloads data by using various modules
"""

import datetime
import moneycontrol as mc
import mutual_funds as mf
import strategies.stocks as st
import media.news as news

today = datetime.date.today()

news.get_MCNews()

#weekly download of fundsnapshots and fund portfolio holdings
    
if today.strftime('%A') == 'Thursday':
    mf.get_VR_MF_CODES()
    eqlist = mf.get_equity_fundlist()
    print("Getting Mutual Fund Snapshots\n")
    mf.get_fund_snapshots()
    print("Getting Mutual Fund Portfolios\n")
    mf.get_fund_portfolios(eqlist)

if today.strftime('%A') == 'Monday':
    mc.get_MCStockCodes()
    print("Getting Corporate Actions\n")
    mc.get_CorporateActions()
    st.stock_adjust()
    
if today.strftime('%A') == 'Tuesday' and 15 <= today.day <= 21:
    mc.get_MCStockCodes()
    print("Getting Ratios\n")
    mc.get_MCRatios()
    mc.populate_ratios_table()
