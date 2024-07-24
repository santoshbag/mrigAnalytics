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
import research.analytics as ra
import json
import mriggraphics as mg
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
            # print('SEC_ID  ', portfolio_df['sec_id'] )
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

def show_portfolio(name,user,portfolio=None):

    if portfolio is None:
        mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
        rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])

        portfolio = pd.read_sql(
            "select portfolio_name as Portfolio_Name,	position_date as Position_Date,SPLIT_PART(sec_id,'|',1) as Security,\
                security_type as Type,		quantity as Qty,	price as Cost from portfolio where account_id='" + user + "' \
                 and portfolio_name='" + name + "'",mrig_engine)
        # print(portfolio)
        port_analytics = pd.read_sql("select * from analytics where date = (select max(date) from analytics)",rb_engine)
        port_analytics.rename(columns={'date':'valuation_date_time','secid':'security'},inplace=True)
        port_analytics = pd.merge(portfolio,port_analytics,how='left',on='security')
    else:
        port_analytics = portfolio
    # print(port_analytics.columns)
    port_analytics['delta'] = port_analytics['delta'] * port_analytics['qty']
    port_analytics['gamma'] = port_analytics['gamma'] * port_analytics['qty']
    port_analytics['theta_per_day'] = port_analytics['theta_per_day'] * port_analytics['qty']
    # port_analytics.dropna(inplace=True)


    scenarios = ['SCENARIO_SPOT','SCENARIO_TIME']
    scenario_dfs = []
    scenario_dfs_multi = []
    for scenario in scenarios:
        # df = pd.DataFrame()
        df_multi = {}
        for sec, cost, qty in zip(list(port_analytics['security']), list(port_analytics['cost']), list(port_analytics['qty'])):
            # print(sec)
            scen_spot = json.loads(port_analytics[port_analytics['security'] == sec]['scenarios'].values[0])
            # print(scen_spot)
            if len(scen_spot[scenario]) > 5:
                scen_spot = pd.DataFrame(scen_spot[scenario], columns=['spot', sec])
                # scen_tmp = pd.DataFrame(scen_spot[scenario], columns=['spot', 'anltk']).set_index('spot')

                scen_spot.set_index('spot', inplace=True)
                scen_tmp = scen_spot.copy()
                scen_tmp.rename(columns={sec:'anltk'},inplace=True)
                # print(scen_spot)
                df1 = pd.DataFrame()
                for inx in scen_tmp.index:
                    # print(ss.loc[inx]['anltk'])
                    df2 = pd.DataFrame(scen_tmp.loc[inx]['anltk'], index=[inx])
                    df2['NPV'] = (df2['NPV'] - cost) * qty
                    # print(df2)
                    df1 = pd.concat([df1, df2])
                    # print(df)
                df_multi[sec] = df1

                # scen_tmp = scen_spot.copy()
                # print('scen_tmp before',scen_tmp)
                # scen_tmp[sec] = pd.DataFrame(scen_tmp[sec])
                # print('scen_tmp after',scen_tmp)
                scen_spot[sec] = scen_spot[sec].apply(lambda x: (x['NPV'] - cost) * qty)
                # print(scen_spot)
                # if df.empty:
                #     df = scen_spot
                # else:
                #     df = df.merge(scen_spot, left_index=True, right_index=True)

        if len(df_multi) > 0:
            df_multi = pd.concat(df_multi, axis=1)
            df_multi = df_multi.sum(level=1, axis=1)
            scenario_dfs_multi.append(df_multi)

        # print(df_multi.loc[:,(slice(None),'NPV')])
        # df = df.transpose()
        # df_multi = df_multi.transpose()

        # df.loc["Total"] = df.sum()
        # df_multi = df_multi.sum(level=1,axis=1)
        # print(type(df_multi))
        # print(df_multi.columns)
        # df_multi.loc["Total"] = df_multi.sum()
        # print('df_multi_SUM\n',df_multi)
        # df = df.loc["Total"]
        # df_multi = df_multi.loc["Total"]
        # df = df.reset_index()
        # print(df)

        # scenario_dfs.append(df)
        # scenario_dfs_multi.append(df_multi)
        # print(scenario_dfs_multi[0])
    # print(df)

    from plotly.offline import plot
    import plotly.graph_objs as go
    import plotly.subplots as subplt

    greeks = ['NPV','delta','gamma','theta_per_day','vega','rho']
    # fig = subplt.make_subplots(rows=len(scenario_dfs),
    #                            cols=1,
    #                            shared_yaxes=False,
    #                            vertical_spacing=0.2,
    #                            subplot_titles=scenarios)
    # i = 0
    # for scenario_df,scenario in zip(scenario_dfs,scenarios):
    #     i = i + 1
    #     fig.add_trace(go.Scatter(x=scenario_df['spot'],
    #                              y=scenario_df['Total'],
    #                              line=dict(color='blue',
    #                                        width=1,
    #                                        shape='spline'), showlegend=False,name=scenario), row=i, col=1)
    npv = scenario_dfs_multi[scenarios.index('SCENARIO_SPOT')]
    # print('SCENARIO_DF_MULTI \n\n',npv)
    NPV_graph = mg.plotly_line_graph(x=npv.index,
                          y_list=[npv['NPV']],
                          y_names=["NPV"],
                          fig_title=port_analytics['portfolio_name'].head(1).values[0] + '( PnL vs Spot )',
                          y_title='PnL',
                          x_title='Spot')
    NPV_graph = plot(NPV_graph, output_type='div')

    fig = subplt.make_subplots(rows=int(len(greeks)/2),
                               cols=2,
                               shared_yaxes=False,
                               vertical_spacing=0.2,
                               subplot_titles=[str(g).upper() for g in greeks])

    scenario_graphs = []
    for scenario_df,scenario in zip(scenario_dfs_multi,scenarios):
        # print('Insode ',scenario_df)
        fig = subplt.make_subplots(rows=int(len(greeks)/2),
                                   cols=2,
                                   shared_yaxes=False,
                                   shared_xaxes=True,
                                   vertical_spacing=0.2,subplot_titles=[str(g).upper() for g in greeks])
        i = 0
        for tuple in greeks:
            # print(tuple[0])
            fig.add_trace(go.Scatter(x=scenario_df.index,
                                     y=scenario_df[tuple],
                                     line=dict(color='blue',
                                               width=1,
                                               shape='spline'), showlegend=False), row=int(i%3)+1, col=int(i%2)+1)
            i = i + 1
            # fig.add_trace(go.Scatter(x=scenario_df.index,
            #                          y=scenario_df[tuple],
            #                          line=dict(color='blue',
            #                                    width=1,
            #                                    shape='spline'), showlegend=False), row=i, col=2)

    # fig.show()
        fig.update_xaxes(showticklabels=True)
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes({'zerolinecolor': 'darkslateblue'})
        fig.update_yaxes({'zerolinecolor': 'darkslateblue'})
        fig.update_annotations(font_size=10)
        fig.update_layout(width=900, height=700)
        fig.update_layout(title_text=scenario,title_x=0.5)
        scenario_graphs.append(plot(fig, output_type='div'))
    port_analytics_all = port_analytics
    port_analytics = port_analytics[['portfolio_name','valuation_date_time',  'position_date', 'security', 'type', 'qty', 'cost',
       'price', 'delta', 'gamma', 'theta_per_day', 'vega', 'rho',       'analytic_value']]

    return [port_analytics,scenario_graphs,NPV_graph,port_analytics_all]
    # return [port_analytics,scenario_graph]


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





def run_portfolio_analytics(portfolio=None,spot_scenario_scale=0.05):
    '''
    :param portfolio:  Dataframe with symbol,security_type,underlying,strike,option_type,expiry_date as columns
    :return: Analytics Dataframe
    '''
    ssn = mu.getKiteSession()

    if portfolio is None:
        mrig_engine = mu.sql_engine(dbname=mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
        rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])

        # kite_object = ka.kite_account()

        symbols = mrig_engine.execute("select distinct split_part(sec_id,'|',1) as symbol from portfolio").fetchall()
        symbols = str([s[0] for s in symbols]).replace('[', '(').replace(']', ')')
        # print(symbols)
        sec_m = pd.read_sql(
            " select symbol,security_type,underlying,strike,option_type,expiry_date from security_master where symbol in " + symbols,
            rb_engine)
    else:
        sec_m = portfolio
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
    sec_m['date'] = datetime.datetime.now()


    # Make portfolio list
    portfolio_list = [(x[0],sec_m[sec_m['symbol'] == x[0]]['obj'].values[0]) for x in sec_m[sec_m['expiry_date'] >= datetime.date.today()][['symbol']].values]
    scen_spot = ra.scenario_analysis(portfolio_list,scenario=['SPOT'],scale=spot_scenario_scale)
    scen_time = ra.scenario_analysis(portfolio_list,scenario=['TIME'])
    sec_m = sec_m.merge(scen_spot,on='symbol',how='left')
    sec_m = sec_m.merge(scen_time,on='symbol',how='left')
    sec_m.fillna('None', inplace=True)
    # print(sec_m)
    return sec_m


def populate_portfolio_analytics(analytics_db,db=True):
    rb_engine = mu.sql_engine(dbname=mrigstatics.RB_WAREHOUSE[mrigstatics.ENVIRONMENT])
    df = pd.DataFrame()
    # df_all = pd.DataFrame()
    analytics_map = {
        'symbol': 'secid',
        'cmp': 'price',
        'NPV': 'analytic_value'
    }
    symbols = analytics_db['symbol']
    for sym in symbols:
        analytics = analytics_db[analytics_db['symbol'] == sym]
        result = analytics['analytics'].values[0] if len(analytics['analytics'].values) > 0 else None
        result1 = {}
        result1['SCENARIO_SPOT'] = analytics['SCENARIO_SPOT'].values[0]
        result1['SCENARIO_TIME'] = analytics['SCENARIO_TIME'].values[0]
        analytics['others'] = json.dumps(result)
        analytics['scenarios'] = json.dumps(result1)
        # result.pop('SCENARIO_SPOT')
        # result.pop('SCENARIO_TIME')

        for key, val in result.items():
            analytics[key] = val
        analytics.rename(columns=analytics_map, inplace=True)
        # analytics_all = analytics.copy()
        analytics = analytics[
            ['date', 'secid', 'price', 'delta', 'gamma', 'theta_per_day', 'vega', 'rho', 'others', 'analytic_value',
             'scenarios']]
        df = pd.concat([df, analytics])
        # df_all = pd.concat([df_all, analytics_all])
        # print(analytics)
    if db:
        df.to_sql('analytics', rb_engine, index=False, if_exists='append')
    # print(df_all)
    return df

if __name__ == '__main__':
    adb = run_portfolio_analytics()
    populate_portfolio_analytics(adb)

