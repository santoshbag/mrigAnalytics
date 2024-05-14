#  Copyright (c) 2024.


# from portfolio import Portfolio
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import mrigutilities as mu
import mrigstatics
import pandas as pd
import kite.kite_account as ka
import strategies.market_instruments as mo
import datetime
import json
'''
Manager module for Class Portfolio 
Add/Delete portfolio, Import/Export portfolio 
Generate Reports,
'''

def add_portfolio(portfolio_df):
    if portfolio_df is not None:
        if len(portfolio_df) > 0:
            # print('TEST  ',(portfolio_df['isin'] if ('isin' in portfolio_df.columns) else 'None'))
            portfolio_df['isin'] = portfolio_df['isin'] if ('isin' in portfolio_df.columns) else 'None'
            portfolio_df['sec_id'] = portfolio_df['symbol'].astype(str) + '|' \
                                     + portfolio_df['isin'].astype(str)  + '|'\
                                     + portfolio_df['underlying'].astype(str) + '|' \
                                     + portfolio_df['security_type'].astype(str) + '|' \
                                     + portfolio_df['strike'].astype(str) + '|' \
                                     + portfolio_df['option_type'].astype(str) + '|' \
                                     + portfolio_df['expiry_date'].astype(str)
            print('SEC_ID  ', portfolio_df['sec_id'] )
            sec_df = portfolio_df[['symbol','sec_id','isin', 'underlying','security_type','strike','option_type','expiry_date']]
            sec_df.set_index('symbol',inplace=True)
            mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
            rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])

            sec_df.to_sql('security_master',rb_engine,if_exists='append',method=mu.insert_on_conflict_nothing)
            portfolio_df['portfolio_id'] = portfolio_df['portfolio_name']
            portfolio_df = portfolio_df[['portfolio_id','sec_id','account_id', 'portfolio_currency','portfolio_name','position_date','security_type','price','quantity']]

            portfolio_df.to_sql('portfolio',mrig_engine,if_exists='append',index=False)


    return portfolio_df

def portfolio_list(user=None):
    if user == None:
        return []
    else:
        mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
        port_list = mrig_engine.execute(
            "select distinct portfolio_name from portfolio where account_id='" + user + "'").fetchall()
        port_list = [n[0] for n in port_list]
        return port_list

def show_portfolio(name,user):
    mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])

    portfolio = pd.read_sql(
        "select portfolio_name as Portfolio_Name,	position_date as Position_Date,SPLIT_PART(sec_id,'|',1) as Security,	security_type as Type,		quantity as Qty,	price as Cost from portfolio where account_id='" + user + "' and portfolio_name='" + name + "'",mrig_engine)
    print(portfolio)
    port_analytics = pd.read_sql("select * from analytics where date = (select max(date) from analytics)",rb_engine)
    port_analytics.rename(columns={'date':'valuation_date_time','secid':'security'},inplace=True)
    port_analytics = pd.merge(portfolio,port_analytics,how='left',on='security')
    port_analytics['delta'] = port_analytics['delta'] * port_analytics['qty']
    port_analytics['gamma'] = port_analytics['gamma'] * port_analytics['qty']
    port_analytics['theta_per_day'] = port_analytics['theta_per_day'] * port_analytics['qty']
    # port_analytics.dropna(inplace=True)
    port_analytics = port_analytics[['portfolio_name','valuation_date_time',  'position_date', 'security', 'type', 'qty', 'cost',
       'price', 'delta', 'gamma', 'theta_per_day', 'vega', 'rho',       'analytic_value']]

    return port_analytics


'''
Analytics for portfolio
Algorithm

1. Get the list of all symbols in portfolios
2. Create objects out of those 
3. Run Analytics on each
4. Store Analytics in database
5. Aggregate analytics at portfolio level
6. Display Analytics as table or as graphs  

'''





def run_portfolio_analtyics():
    mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
    rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])

    kite_object = ka.kite_account()
    ssn = kite_object.session

    symbols = mrig_engine.execute("select distinct split_part(sec_id,'|',1) as symbol from portfolio").fetchall()
    symbols = str([s[0] for s in symbols]).replace('[', '(').replace(']', ')')
    print(symbols)
    sec_m = pd.read_sql(
        " select symbol,security_type,underlying,strike,option_type,expiry_date from security_master where symbol in " + symbols,
        rb_engine)
    sec_m['underlying_price'] = sec_m['underlying'].apply(lambda x: mu.price(x))
    sec_m['cmp'] = sec_m[['symbol', 'expiry_date']].apply(
        lambda x: ssn.quote('NFO:' + x['symbol'])['NFO:' + x['symbol']]['last_price'] if (
                    x['expiry_date'] >= datetime.date.today()) else -1, axis=1)

    sec_m['obj'] = sec_m[['symbol','expiry_date','security_type','strike','option_type','cmp','underlying']] \
    .apply(lambda x : (mo.MarketOptions(x['underlying'], float(x['strike']), x['expiry_date'],  x['option_type']) \
                       if x['security_type'] == 'OPT' else mo.MarketFutures(x['underlying'], float(x['cmp']), x['expiry_date'])) \
                       if (x['expiry_date'] >= datetime.date.today()) else None, axis=1)
    sec_m['analytics'] = sec_m[['cmp','obj','expiry_date']] \
    .apply(lambda x : x['obj'].valuation(x['cmp']) if (x['expiry_date'] >= datetime.date.today()) else {'NPV': 0, 'delta': 0, \
                     'gamma': 0, 'theta': 0, 'theta_per_day': 0,'rho': 0, 'vega': 0, 'strike_sensitivity': 0, 'dividendRho': 0, \
                     'volatility': 0}, axis=1)
    sec_m['date'] = datetime.date.today()

    # print(sec_m)
    return sec_m


def populate_portfolio_analytics(analytics_db):
    rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    df = pd.DataFrame()
    analytics_map = {
        'symbol': 'secid',
        'cmp': 'price',
        'NPV': 'analytic_value'
    }
    symbols = analytics_db['symbol']
    for sym in symbols:
        analytics = analytics_db[analytics_db['symbol'] == sym]
        result = analytics['analytics'].values[0] if len(analytics['analytics'].values) > 0 else None
        analytics['others'] = json.dumps(result)
        for key, val in result.items():
            analytics[key] = val
        analytics.rename(columns=analytics_map, inplace=True)
        analytics = analytics[
            ['date', 'secid', 'price', 'delta', 'gamma', 'theta_per_day', 'vega', 'rho', 'others', 'analytic_value']]
        df = pd.concat([df, analytics])
        # print(analytics)
    df.to_sql('analytics', rb_engine, index=False, if_exists='append')
    print(df)

if __name__ == '__main__':
    adb = run_portfolio_analtyics()
    populate_portfolio_analytics(adb)

