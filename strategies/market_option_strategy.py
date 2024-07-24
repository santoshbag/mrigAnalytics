
"""
Created on Wed Jul  4 17:37:47 2018

@author: Santosh Bag
Copyright (c) 2024.
"""
import sys,os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mrigutilities as mu
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import strategies.strategy as st
import statsmodels.api as sm
import research.math as rm
import research.analytics as ra
import json
import mrigstatics
import strategies.option_strategies as op_s
from mrigweb.mrigwebapp.myhtml import myhtml
# import mrigwebapp.forms as fm

import kite.mrigkite as zkite
from itertools import permutations
import portfolios.portfolio_manager as pm

engine = mu.sql_engine()
datadir = os.path.dirname(__file__)

def load_option_strategies(strategy=['bps','']):
    starttime = time.monotonic()
    print("Loading Option Strategies Started")
    json_file_path = os.path.join(datadir, 'option_strategies.json')
    f = open(json_file_path)

    f = json.load(f)
    strategy_map = pd.DataFrame.from_dict(f['strategy_map'])
    stratlist = strategy_map[(strategy_map['implementation'] == 'True')].index.to_list()

    index = 'NIFTY 50'
    stocklist = engine.execute("select index_members from stock_history where symbol=%s and \
    index_members is not NULL order by date desc limit 1",(index)).fetchall()[0][0]
    stocklist = stocklist.replace('[','(').replace(']',')')
    # stocklist = [x[1:-1] for x in stocklist]

    df = pd.read_sql("select * from technicals where symbol in "+stocklist+" and date = (select max(date) from technicals)", engine)
    # df.set_index('symbol',inplace=True)
    df['ta'] = df['ta'].apply(lambda x: json.loads(x))
    df1 = pd.json_normalize(df['ta'])
    df = df.join(df1)
    bullish_stocks = df[(df['MACD_12_26_9'] > 0) & (df['SUPERTd_7_3.0'] == 1)]['symbol'].to_list()
    print('bullish_stocks -->',bullish_stocks)
    bearish_stocks = df[(df['MACD_12_26_9'] < 0) & (df['SUPERTd_7_3.0'] == -1)]['symbol'].to_list()
    print('bearish_stocks -->', bearish_stocks)
    loaddate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for strat in stratlist:
        print('Running strat --',strat)
        trend = strategy_map.loc[strat]['trend']
        strjson = json.dumps(f[strat])
        bps = op_s.OptionStrategy(strat)
        bps.set_strategy_json(strjson)
        if trend == 'bullish':
            bps.set_symbols(bullish_stocks)
        if trend == 'bearish':
            bps.set_symbols(bearish_stocks)

        bps.run_strategy()

        strategy = 'BPS'
        strategy_desc = 'Bull Put Spread'

        mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])

        strategy_basket = bps.strategy_basket  # ['TATAMOTORS'][0][3]
        strategy_body = []
        for sym, strategylist in strategy_basket.items():
            for s in strategylist:
                s[3].drop(['obj', 'yld'], axis=1, inplace=True)
                id = s[3]['strategy_id'].head(1).values[0]
                s[3]['valuation_date_time'] = s[3]['valuation_date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                s[3]['position_date'] = s[3]['position_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                s[3]['date'] = s[3]['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

                s[3]['expiry_date'] = s[3]['expiry_date'].astype(str)
                s[3][['max_risk', 'max_profit', 'breakeven']] = s[3][
                    ['max_risk', 'max_profit', 'breakeven']].applymap(mu.shortenlength)
                s[3]['Yield'] = s[3]['Yield'].apply(lambda x: '{:.2%}'.format(x))
                # s[3][['max_risk','max_profit','breakeven','Yield']] = s[3][['max_risk','max_profit','breakeven','Yield']].astype(

                # s[3]['max_risk'] = pd.to_numeric(s[3]['max_risk'], errors='coerce')

                # s[3]['max_profit'] = pd.to_numeric(s[3]['max_profit'], errors='coerce')
                # s[3]['breakeven'] = pd.to_numeric(s[3]['breakeven'], errors='coerce')
                # s[3]['Yield'] = pd.to_numeric(s[3]['Yield'], errors='coerce')

                sql = "insert into os_page (strategy_id, strategy_obj,load_date, strategy_table, strategy_name) values (%s,%s,%s,'','')"
                mrig_engine.execute(sql, (id, json.dumps([s[3].to_dict(), s[1], s[2]]), loaddate))
    print("Loading Option Strategies Ended")
    elapsed = time.monotonic() - starttime
    print("--------Time Taken for load_option_strategies %s hrs %s mins %s sec------------" %("{0:5.2f}".format(elapsed//3600),"{0:3.2f}".format(elapsed%3600//60),"{0:3.2f}".format(elapsed%3600%60)))


if __name__ == '__main__':
    load_option_strategies()
