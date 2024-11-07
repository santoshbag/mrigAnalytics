# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import pandas as pd
import numpy as np
#from pandas.compat import StringIO
from io import StringIO
from collections import deque
from sqlalchemy import create_engine
from dateutil import relativedelta
import datetime, nsepy, nsetools
import mrigstatics
import QuantLib as ql
from urllib.parse import quote
import requests, socket, time
from bs4 import BeautifulSoup
from random import choice
import string
import json
from pandas import json_normalize
import interface.web.webdashboard as wdb

import math
import yfinance
# from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import yfinance as yf

# import kite.kite_trade as zkite
import kite.mrigkite as zkite

import scipy.stats as si
from scipy import optimize
from sqlalchemy.dialects.postgresql import insert
import sympy as sp

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def top_stocks(universe='NIFTY 500'):
    api_key = "your_api_key"
    access_token = "your_access_token"

    # kite = KiteConnect(api_key=api_key)
    # kite.set_access_token(access_token)

    kite = mu.getKiteSession()
    # Fetch the list of NSE stocks to monitor
    instruments = kite.instruments("NSE")
    instruments_df = pd.DataFrame(instruments)
    nifty_500 = json.loads(mu.getIndexMembers(universe).replace("'", "\""))
    instruments_df = instruments_df.loc[instruments_df['tradingsymbol'].isin(nifty_500)]
    # print(instruments_df.columns)

    # Select a subset of instruments (for demonstration, taking the top 100 by default)
    top_instruments = instruments_df.head(100)
    instrument_tokens = top_instruments['instrument_token'].tolist()

    # Function to fetch live market prices
    def fetch_ltp():
        # Retrieve last traded prices (LTP) for the selected instruments
        try:
            ltp_data = kite.ltp(instrument_tokens)
        except Exception as e:
            print(f"Error fetching LTP data: {e}")
            return {}

        # Extract LTP data with instrument_token as key
        # ltp_prices = {
        #     int(token.split(":")[1]): data['last_price']
        #     for token, data in ltp_data.items()
        # }
        # ltp_prices = {
        #     int(data['instrument_token']): data['last_price']
        #     for token, data in ltp_data.items()
        # }
        ltp_prices = {}
        for token, data in ltp_data.items():
            if (data['last_price'] > 0):
                ltp_prices[instruments_df[instruments_df['instrument_token'] == data['instrument_token']]['tradingsymbol'].values[0]] = data['last_price']

        # print('ltp_prices',ltp_prices)
        return ltp_prices

    def fetch_open():
        # Retrieve last traded prices (LTP) for the selected instruments
        try:
            open_data = kite.ohlc(instrument_tokens)
        except Exception as e:
            print(f"Error fetching LTP data: {e}")
            return {}

        # Extract LTP data with instrument_token as key
        # ltp_prices = {
        #     int(token.split(":")[1]): data['last_price']
        #     for token, data in ltp_data.items()
        # }

        # open_prices = {
        #     int(data['instrument_token']): data['ohlc']['open']
        #     for token, data in open_data.items()
        # }

        open_prices = {}
        for token, data in open_data.items():
            if (data['ohlc']['open'] > 0):
                open_prices[instruments_df[instruments_df['instrument_token'] == data['instrument_token']]['tradingsymbol'].values[0]] = data['ohlc']['open']

        # print('open_prices',open_prices)

        return open_prices

    # Function to calculate top winners and losers based on LTP changes
    def get_top_movers(ltp_prices, open_prices):
        # Calculate percentage change
        changes = {
            token: round(((ltp_prices[token] - open_price) / open_price) * 100,2)
            for token, open_price in open_prices.items() if token in ltp_prices
        }

        # Sort by percentage change to find top gainers and losers
        sorted_changes = sorted(changes.items(), key=lambda x: x[1], reverse=True)
        top_winners = sorted_changes[:10]
        top_losers = sorted_changes[-10:]
        # print(top_losers)
        return top_winners, top_losers

    # Initial fetch of opening prices (assuming open prices are the first LTPs)
    open_prices = fetch_open()
    # time.sleep(1)  # Delay to prevent API rate limit issues

    # Main loop to fetch LTP and calculate movers
    # while True:
    # Fetch current LTP
    ltp_prices = fetch_ltp()
    # print(ltp_prices)
    # Calculate and display top movers
    top_winners, top_losers = get_top_movers(ltp_prices, open_prices)

    print("Top 10 Winners:")
    for token, change in top_winners:
        print(f"Token: {token}, Change: {change:.2f}%")

    print("\nTop 10 Losers:")
    for token, change in top_losers:
        print(f"Token: {token}, Change: {change:.2f}%")

    # Refresh data every 60 seconds
    # time.sleep(60)
    return[top_winners,top_losers]

def rates(currency='INR',params=None):
    szyc = wdb.mrigweb_szc_rates(curve_currency=currency,params=params)[0]
    ffyc = wdb.mrigweb_ff_rates()
    rates = {}
    start = szyc.getReferenceDate()
    forwardstart = start + datetime.timedelta(days=180)
    dates = [start + datetime.timedelta(days=180 * i) for i in range(0, 80)]
    tenors = [datetime.timedelta(days=180 * i) / datetime.timedelta(days=360) for i in range(0, 80)]
    discounts = szyc.getDiscountFactor(dates)
    #        print(discounts)
    # baseforwards = [basecurve.getForwardRate(start,start+datetime.timedelta(days=180*i)) for i in range(0,20)]
    forwards = [szyc.getForwardRate(forwardstart, forwardstart + datetime.timedelta(days=180 * i)) for i in
                range(0, 80)]
    zeroes = [szyc.getZeroRate(start + datetime.timedelta(days=180 * i)) for i in range(0, 80)]

    rates['tenors'] = tenors[1:]
    rates['zeroes'] = zeroes[1:]
    rates['forwards'] = forwards[1:]
    rates['discounts'] = discounts[1:]

    return rates

def bonds(params=None):

    objectmap = {}
    objectmap['None'] = None
    objectmap['SZYC_INR'] = wdb.mrigweb_szc_rates()
    objectmap['SZYC_USD'] = wdb.mrigweb_szc_rates('USD')
    objectmap['SZYC_GBP'] = wdb.mrigweb_szc_rates('GBP')
    objectmap['LIBOR_3M_INR'] = wdb.mrigweb_Libor('LIBOR_3M_INR', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_6M_INR'] = wdb.mrigweb_Libor('LIBOR_6M_INR', tenor='6M', yieldcurvehandle=objectmap['SZYC_INR'][0])
    objectmap['LIBOR_3M_USD'] = wdb.mrigweb_Libor('LIBOR_3M_USD', curve_currency='USD',
                                                  yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_6M_USD'] = wdb.mrigweb_Libor('LIBOR_6M_USD', curve_currency='USD', tenor='6M',
                                                  yieldcurvehandle=objectmap['SZYC_USD'][0])
    objectmap['LIBOR_3M_GBP'] = wdb.mrigweb_Libor('LIBOR_3M_GBP', curve_currency='GBP', tenor='3M',
                                                  yieldcurvehandle=objectmap['SZYC_GBP'][0])
    objectmap['LIBOR_6M_GBP'] = wdb.mrigweb_Libor('LIBOR_6M_GBP', curve_currency='GBP', tenor='6M',
                                                  yieldcurvehandle=objectmap['SZYC_GBP'][0])

    resultset = ""
    face_value = 100
    day_count = '30-360'
    calendar = 'India'
    business_convention = 'Following'
    month_end = 'True'
    settlement_days = 3
    date_generation = 'Backward'
    coupon_frequency = 'Semiannual'
    fixed_coupon_rate = None
    floating_coupon_index = 'LIBOR_3M_INR'
    floating_coupon_spread = 0
    inArrears = True
    cap = None
    floor = None
    fixing = None
    conversionRatio = None
    conversionPrice = None
    credit_spread = None
    call_date_1 = None
    call_date_2 = None
    call_date_3 = None
    call_date_4 = None
    call_date_5 = None
    put_date_1 = None
    put_date_2 = None
    put_date_3 = None
    put_date_4 = None
    put_date_5 = None

    call_schedule = None
    call_schedule_date = []
    call_schedule_price = []
    put_schedule = None
    put_schedule_date = []
    put_schedule_price = []
    dividend_schedule = None
    discount_curve = 'SZYC_INR'
    volatility_curve = 0
    dividend_curve = 0
    underlying_spot = 0
    mean_reversion = 0.03
    shortrate_vol = 0.12
    hwgrid_pts = 40


    reference_date = datetime.date.today()

    if len(params) > 0:
        issue_name = params['bond_name']
        issue_date = params['issue_date']
        issue_date = datetime.datetime.strptime(issue_date, '%Y-%m-%d').date()
        maturity_date = params['maturity_date']
        maturity_date = datetime.datetime.strptime(maturity_date, '%Y-%m-%d').date()
        day_count = params['day_count']
        calendar = params['calendar']
        currency = params['currency']
        business_convention = params['business_convention']
        month_end = bool(params['month_end'])
        date_generation = params['date_generation']
        coupon_frequency = params['coupon_frequency']
        floating_coupon_index = params['floating_coupon_index']
        try:
            face_value = float(params['facevalue'])
        except:
            pass
        try:
            settlement_days = float(params['settlement_days'])
        except:
            pass
        try:
            fixed_coupon_rate = float(params['fixed_coupon_rate'])
        except:
            pass

        try:
            floating_coupon_spread = float(params['floating_coupon_spread'])
        except:
            pass
        inArrears = bool(params['inArrears'])
        try:
            cap = float(params['cap'])
        except:
            pass
        try:
            floor = float(params['floor'])
        except:
            pass
        try:
            fixing = float(params['last_libor'])
        except:
            pass
        try:
            conversionRatio = float(params['conversion_ratio'])
        except:
            pass
        try:
            conversionPrice = float(params['conversion_price'])
        except:
            pass
        try:
            credit_spread = float(params['credit_spread'])
        except:
            pass
        # call_date_1 = params['call_date_1']
        # call_price_1 = params['call_price_1']
        # try:
        #     call_date_1 = datetime.datetime.strptime(call_date_1, '%Y-%m-%d').date()
        #     call_schedule_date.append(call_date_1)
        #     call_schedule_price.append(float(call_price_1))
        # except:
        #     pass
        # call_date_2 = params['call_date_2']
        # call_price_2 = params['call_price_2']
        # try:
        #     call_date_2 = datetime.datetime.strptime(call_date_2, '%Y-%m-%d').date()
        #     call_schedule_date.append(call_date_2)
        #     call_schedule_price.append(float(call_price_2))
        # except:
        #     pass
        # call_date_3 = params['call_date_3']
        # call_price_3 = params['call_price_3']
        # try:
        #     call_date_3 = datetime.datetime.strptime(call_date_3, '%Y-%m-%d').date()
        #     call_schedule_date.append(call_date_3)
        #     call_schedule_price.append(float(call_price_3))
        # except:
        #     pass
        # call_date_4 = params['call_date_4']
        # call_price_4 = params['call_price_4']
        # try:
        #     call_date_4 = datetime.datetime.strptime(call_date_4, '%Y-%m-%d').date()
        #     call_schedule_date.append(call_date_4)
        #     call_schedule_price.append(float(call_price_4))
        # except:
        #     pass
        # call_date_5 = params['call_date_5']
        # call_price_5 = params['call_price_5']
        # try:
        #     call_date_5 = datetime.datetime.strptime(call_date_5, '%Y-%m-%d').date()
        #     call_schedule_date.append(call_date_5)
        #     call_schedule_price.append(float(call_price_5))
        # except:
        #     pass
        #
        # if len(call_schedule_date) > 0:
        #     call_schedule = [call_schedule_date, call_schedule_price]
        #
        # put_date_1 = params['put_date_1']
        # put_price_1 = params['put_price_1']
        # try:
        #     put_date_1 = datetime.datetime.strptime(put_date_1, '%Y-%m-%d').date()
        #     put_schedule_date.append(put_date_1)
        #     put_schedule_price.append(float(put_price_1))
        # except:
        #     pass
        # put_date_2 = params['put_date_2']
        # put_price_2 = params['put_price_2']
        # try:
        #     put_date_2 = datetime.datetime.strptime(put_date_2, '%Y-%m-%d').date()
        #     put_schedule_date.append(put_date_2)
        #     put_schedule_price.append(float(put_price_2))
        # except:
        #     pass
        # put_date_3 = params['put_date_3']
        # put_price_3 = params['put_price_3']
        # try:
        #     put_date_3 = datetime.datetime.strptime(put_date_3, '%Y-%m-%d').date()
        #     put_schedule_date.append(put_date_3)
        #     put_schedule_price.append(float(put_price_3))
        # except:
        #     pass
        # put_date_4 = params['put_date_4']
        # put_price_4 = params['put_price_4']
        # try:
        #     put_date_4 = datetime.datetime.strptime(put_date_4, '%Y-%m-%d').date()
        #     put_schedule_date.append(put_date_4)
        #     put_schedule_price.append(float(put_price_4))
        # except:
        #     pass
        # put_date_5 = params['put_date_5']
        # put_price_5 = params['put_price_5']
        # try:
        #     put_date_5 = datetime.datetime.strptime(put_date_5, '%Y-%m-%d').date()
        #     put_schedule_date.append(put_date_5)
        #     put_schedule_price.append(float(put_price_5))
        # except:
        #     pass
        #
        # if len(put_schedule_date) > 0:
        #     put_schedule = [put_schedule_date, put_schedule_price]

        # Valuation Parameters
        discount_curve = params['discount_curve']
        try:
            volatility_curve = float(params['volatility_curve'])
        except:
            pass
        try:
            volatility_curve = float(params['volatility_curve'])
        except:
            pass
        try:
            dividend_curve = float(params['dividend_curve'])
        except:
            pass
        try:
            underlying_spot = float(params['underlying_spot'])
        except:
            pass
        try:
            mean_reversion = float(params['mean_reversion'])
        except:
            pass
        try:
            shortrate_vol = float(params['shortrate_vol'])
        except:
            pass
        try:
            hwgrid_pts = float(params['hwgrid_pts'])
        except:
            pass

    discount_curve = objectmap[discount_curve][0]
    floating_coupon_index = objectmap[floating_coupon_index]
    volatility_curve = wdb.mrigweb_ConstantVolatilityCurve(volatility_curve)
    dividend_curve = wdb.mrigweb_FlatDividendYieldCurve(reference_date, flat_rate=dividend_curve)

    print(issue_date)
    print(call_schedule)
    print(put_schedule)
    print(conversionRatio)


    bond = wdb.mrigweb_Bond(issue_name, issue_date, maturity_date,
                            face_value, day_count, calendar, business_convention,
                            month_end, settlement_days, date_generation, coupon_frequency,
                            fixed_coupon_rate, floating_coupon_index, floating_coupon_spread,
                            inArrears, cap, floor, fixing, conversionRatio, conversionPrice,
                            credit_spread, call_schedule, put_schedule, dividend_schedule)

    valuation_args = {'Underlying Spot': underlying_spot,
                      'Discount Curve': discount_curve,
                      'Volatility Curve': volatility_curve,
                      'Dividend Curve': dividend_curve,
                      'Mean Reversion': mean_reversion,
                      'Short Rate Vol': shortrate_vol,
                      'Hull White Grid Pts': hwgrid_pts}

    resultset = wdb.mrigweb_Analytics(bond, valuation_args,cf_format=True)
    print(resultset)

    def yield_scenario():
        scenario = {'yield' : [],'price' : []}
        curr_yield = float(resultset['Yield'])
        yield_range = [min(0.01/100,0.5*curr_yield),max(0.2,1.5*curr_yield)] if curr_yield > 0 else [0.01/100,0.2]
        yield_params = {
        'curvename' : 'Flat_Forward_1',
        'day_count' : params['day_count'],
        'calendar' : params['calendar'],
        'flat_rate' : '0.02',
        'compounding' : 'Compounded',
        'compounding_frequency' : params['coupon_frequency'],
        'shiftparameter' : '0'
        }
        yld = yield_range[0]
        while yld <= yield_range[1]:
            yield_params['flat_rate'] = str(yld)
            ff = wdb.mrigweb_ff_rates(params=yield_params)[0]
            valuation_args['Discount Curve'] = ff
            rs = wdb.mrigweb_Analytics(bond, valuation_args, cf_format=True)
            scenario['yield'].append(yld)
            scenario['price'].append(rs['NPV'])
            yld = yld + 1/1000
        return scenario
    scenario = yield_scenario()
    return [resultset,scenario]

if __name__ == '__main__':
    print(pd.__version__)
    top_stocks()
