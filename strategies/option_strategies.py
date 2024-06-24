# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:37:47 2018

@author: Santosh Bag
"""
import sys,os
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
import kite.mrigkite as zkite
from itertools import permutations
import portfolios.portfolio_manager as pm

class OptionStrategy(st.Strategy):
    def __init__(self,strategy_name):
        self.name = strategy_name
        self.strategy_json = None
        self.basket = None
        self.symbols = None
        self.strategy_basket = None
        ''' Structure of strategy_basket:
            {stock_symbol1 : [[stock_symbol1_analytics_1],[stock_symbol1_analytics_2],[stock_symbol1_analytics_3]]
            [stock_symbol1_analytics_1] : [portfolio_df,scenario_graph_list,fig,portfolio_df_all]
        '''

    def get_strategy_json(self):
        return self.strategy_json

    def set_strategy_json(self,strategy):
        self.strategy_json = strategy

    def set_symbols(self,symbols):
        self.symbols = symbols

    def get_symbols(self):
        return self.symbols

    def option_strategy(self):

        os = json.loads(self.strategy_json)
        kite_object = zkite.mrigkite()

        underlying = os['symbol']

        # session = mu.getKiteSession()
        underlying_price = kite_object.getQuoteLive(underlying)['last_price']
        print(underlying,'  ATM ------->', underlying_price)
        oc = mu.kite_OC_new([underlying])
        if oc is None:
            return []
        if len(oc) == 0:
            return []
        expiry_date = min(oc['expiry'].values)
        # print(expiry_date)
        # print(oc.columns)
        assets = os['assets']
        rules = os['rules']
        metric = os['metric']

        for key, a in assets.items():
            a['id'] = key
        # a1 = bps['assets']['a1']
        # a1['id'] = 'a1'
        # a2 = bps['assets']['a2']
        # a2['id'] = 'a2'
        # a1_defined  = True if a1['strike'] is not None else False
        # a2_defined  = True if a2['strike'] is not None else False
        m1 = metric['m1']

        for key, m in metric.items():
            if 'atm' == m['name']:
                m['body'] = underlying_price
            if 'max_options' == m['name']:
                max_options = m['body']
            else:
                max_options = 5

        # if 'atm' == m1['name']:
        # m1['body'] = underlying_price
        # max_options = m3['max_options'] if 'max_options' in m3.keys() else 5
        oc_up_strikes = sorted(
            set(list(oc[(oc['strike'] >= underlying_price) & (oc['expiry'] == expiry_date)]['strike'].values)))
        # print('oc_up_strikes\n',oc_up_strikes[0:max_options])
        oc_down_strikes = sorted(
            set(list(oc[(oc['strike'] < underlying_price) & (oc['expiry'] == expiry_date)]['strike'].values)))
        # print('oc_down_strikes\n',oc_down_strikes[-max_options:])
        # strikes = oc_up_strikes+oc_down_strikes
        strikes = sorted(set(oc_up_strikes + oc_down_strikes))
        # print('strikes\n',strikes)
        strikes = sorted(set(oc_up_strikes[0:max_options] + oc_down_strikes[-max_options:]))

        # print('strikes\n',strikes)

        # def get_ltp(name,strike,expiry,type):
        #     # get the instrument token
        #     ltp = oc[(oc['name'] == name) &
        #                (oc['strike'] == strike) &
        #                (oc['expiry'] == expiry) &
        #                (oc['instrument_type'] == type)]['ltp'].values
        strikes = permutations(strikes, len(assets))

        valid_basket = []
        for strike in list(strikes):
            # print (strike[0],strike[1])
            try:
                asset_dict = {}
                asset_tmp = []
                i = 0
                for key, a in assets.items():
                    a['strike'] = strike[i]
                    a['expiry'] = expiry_date.strftime('%y%m%d')
                    a['ltp'] = oc[(oc['name'] == underlying) &
                                  (oc['strike'] == strike[i]) &
                                  (oc['expiry'] == expiry_date) &
                                  (oc['instrument_type'] == a['type'])]['last_price'].values[0]
                    a['tradingsymbol'] = oc[(oc['name'] == underlying) &
                                            (oc['strike'] == strike[i]) &
                                            (oc['expiry'] == expiry_date) &
                                            (oc['instrument_type'] == a['type'])]['tradingsymbol'].values[0]
                    a['lot_size'] = oc[(oc['name'] == underlying) &
                                            (oc['strike'] == strike[i]) &
                                            (oc['expiry'] == expiry_date) &
                                            (oc['instrument_type'] == a['type'])]['lot_size'].values[0]
                    asset_tmp.append(dict(a))

                    for k in a.keys():
                        asset_dict[str(a['id']) + '_' + str(k)] = a[k]
                    i = i + 1

                # for a in asset_tmp:
                #     for key in a.keys():
                #         asset_dict[str(a['id'])+'_'+str(key)] = a[key]
                for key, m in metric.items():
                    res = mu.evaluate_expression(m['body'], asset_dict)
                    asset_dict[m['name']] = res
                    asset_tmp.append({m['name']: res})
                    # print(asset_dict)
                rule_value = True
                for key, r in rules.items():
                    expression = r['body']
                    # print(expression)
                    result = mu.evaluate_expression(expression, asset_dict)
                    # print(r['name']+'\n',result)
                    rule_value = rule_value & result
                    # print('rule_value -> '+str(rule_value))
                if rule_value:
                    # print('rule_value -> '+str(rule_value))
                    # print(asset_tmp)
                    # print(asset_dict)
                    asset_tmp.append({'Yield': asset_dict['yld']})
                    asset_tmp.append({'Strategy': os['strategy']})
                    valid_basket.append(asset_tmp)
            except:
                pass

        # print(valid_basket)
        return valid_basket


    def option_strategy_analytics(self):
        col_map = {'symbol': 'underlying', 'instrument': 'security_type', 'type': 'option_type', 'expiry': 'expiry_date',
                   'tradingsymbol': 'symbol'}
        sec_map = {'option': 'OPT', 'futures': 'FUT'}
        return_basket = {}

        for key, strategy_list in self.basket.items():
            return_strategy_list = []
            for strategy in strategy_list:
                portfolio = pd.DataFrame(strategy)
                portfolio.rename(columns=col_map, inplace=True)
                portfolio['security_type'] = portfolio['security_type'].map(sec_map)
                # portfolio['Yield'] = portfolio[portfolio['underlying'].isnull()]['Yield'].head(1).values[0]
                portfolio['Yield'] = portfolio[portfolio['Yield'].notnull()]['Yield'].head(1).values[0]

                # print('AFTER YIELD',portfolio)

                portfolio['Strategy'] = portfolio[portfolio['Strategy'].notnull()]['Strategy'].head(1).values[0]
                # print('AFTER STRATEGY',portfolio)
                portfolio['max_profit'] = portfolio[portfolio['max_profit'].notnull()]['max_profit'].head(1).values[0]
                portfolio['max_risk'] = portfolio[portfolio['max_risk'].notnull()]['max_risk'].head(1).values[0]
                portfolio['breakeven'] = portfolio[portfolio['breakeven'].notnull()]['breakeven'].head(1).values[0]

                portfolio = portfolio[portfolio['underlying'].notnull()]
                portfolio['expiry_date'] = portfolio['expiry_date'].apply(
                    lambda x: datetime.datetime.strptime(x, '%y%m%d').date())
                # print('AFTER FINAL',portfolio)

                portfolio = pm.run_portfolio_analytics(portfolio, spot_scenario_scale=0.1)
                return_strategy_list.append(portfolio)
            return_basket[key] = return_strategy_list

        return return_basket

    def set_symbol_in_strategy(self,symbol):
        os = json.loads(self.strategy_json)
        os['symbol'] = symbol
        for key,a in os['assets'].items():
            a['symbol'] = symbol
        self.strategy_json = json.dumps(os)

    def run_strategy(self):
        self.basket = {}
        for s in self.symbols:
        # for s in ['TATAMOTORS']:
        #     print(s)
            # try:
            self.set_symbol_in_strategy(s)
            a = self.option_strategy()
            self.basket[s] = a
            # except:
            # pass
        self.basket = self.option_strategy_analytics()

        analytic_basket = {}
        for s in self.symbols:
            sym_basket = self.basket[s]
            sym_basket_analytics = []
            for adb in sym_basket:
            # adb
                adb_a = pm.populate_portfolio_analytics(adb, db=False)
                # adb_a
                adb['qty'] = adb['direction'].apply(lambda x: 1 if x == 'long' else -1)
                adb['qty'] = adb['qty']*adb['lot_size']
                adb['max_profit'] = adb['lot_size'] * adb['max_profit']
                adb['max_risk'] = adb['lot_size'] * adb['max_risk']
            # adb
                adb_a.rename(columns={'date': 'valuation_date_time', 'secid': 'security'}, inplace=True)
                # adb_a
                adb.rename(columns={'ltp': 'cost', 'security_type': 'type', 'symbol': 'security'}, inplace=True)
                # adb
                adb_a = pd.merge(adb, adb_a, how='left', on='security')
                # adb_a
                adb_a['portfolio_name'] = adb_a['underlying'] + '_' + adb_a['Strategy'].str.upper()
                # adb_a['strategy_id'] = adb_a['portfolio_name'] + '_' + str(list(adb_a['strike'])) + '_' + str(list(adb_a['expiry_date']))
                adb_a['strategy_id'] = mu.generatekey()

                adb_a['position_date'] = adb_a['date']
                # adb_a
                port = pm.show_portfolio('any', 'any', portfolio=adb_a)
                sym_basket_analytics.append(port)
            analytic_basket[s] = sym_basket_analytics
        self.strategy_basket = analytic_basket
        # print('Final basket\n\n', self.strategy_basket)


if __name__ == '__main__':
    sd = datetime.date(2017,5,31)
    ed = datetime.date(2018,11,18)
    # trades1 = MovingCrossover('HDFCBANK',60,90)
    # trades1.backtest(sd,ed)
    # trades2 = MovingCrossover('MARUTI',60,90)
    # #trades2.backtest(sd,ed)
    #
    # rm.isNormal(np.array(list(trades2.portfolio['returns'])))
    #rm.linreg(trades1.portfolio['returns'][1:519].values,trades2.portfolio['returns'][1:519].values)


    