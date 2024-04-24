# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag

Generates the Correlation data based on returns/prices and populates the database
for the purpose of historical analysis
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime #import date, timedelta
import logging
import mrigutilities

# date_range = pd.bdate_range(start='02/23/2024', end = '02/24/2024',
#                          freq='C', holidays = holidays(2024,12))


datadir = os.path.dirname(__file__)
today = datetime.date.today()
log_file_name = 'mriglog_'+today.strftime('%Y%m%d')+'.txt'
log_file_path = os.path.join(datadir, '..', '..', 'logs', log_file_name)

input_dir = os.path.join(datadir, '..', '..', 'data', 'input')
processed_dir = os.path.join(datadir, '..', '..', 'data', 'processed')

# Create and configure logger
logging.basicConfig(filename=log_file_path,
                    format='%(asctime)s %(message)s',
                    filemode='a')

def nifty_corr_data():
    # create logger
    logger = logging.getLogger('correlations.py > nifty_corr_data()')
    logger.setLevel(logging.DEBUG)

    sql = '''
    delete from return_correlations;
    
    
    insert into return_correlations
    (select date, stock, daily_log_returns, 
    corr(daily_log_returns,nifty) over (partition by stock order by date rows between 19 preceding and current row) as nifty_20_corr,
    corr(daily_log_returns,nifty) over (partition by stock order by date rows between 49 preceding and current row) as nifty_50_corr,
    corr(daily_log_returns,nifty) over (partition by stock order by date rows between 149 preceding and current row) as nifty_150_corr,
    corr(daily_log_returns,nifty) over (partition by stock order by date rows between 249 preceding and current row) as nifty_250_corr
    
    from
    (select sh.date as date, sh.symbol as stock, sh.daily_log_returns as daily_log_returns , sh1.daily_log_returns as nifty 
    from daily_returns sh
    inner join daily_returns sh1 on sh.date = sh1.date
    where sh1.symbol='NIFTY 50'
    order by sh.symbol, sh.date asc) as dat)
    '''

    engine = mrigutilities.sql_engine()
    try:
        engine.execute(sql)
        logger.info('Correlation Generated')
    except Exception as e:
        logger.error("%s", str(e))


if __name__ == '__main__':
    nifty_corr_data()