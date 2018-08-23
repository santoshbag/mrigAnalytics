# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
import pandas as pd
from collections import deque
from sqlalchemy import create_engine
from dateutil import relativedelta
import datetime,nsepy
import mrigstatics
import QuantLib as ql
import datetime


def get_last_row(csv_filename,lines=1):
    with open(csv_filename,'r') as f:
        try:
            lastrow = deque(csv.reader(f), lines)
        except IndexError:  # empty file
            lastrow = None
        return lastrow
    

def clean_df_db_dups(df, tablename, engine, dup_cols=[],
                         filter_continuous_col=None, 
                         filter_categorical_col=None,
                         date_handling=None,
                         leftIdx=False):
    """
    Remove rows from a dataframe that already exist in a database
    Required:
        df : dataframe to remove duplicate rows from
        engine: SQLAlchemy engine object
        tablename: tablename to check duplicates in
        dup_cols: list or tuple of column names to check for duplicate row values
    Optional:
        filter_continuous_col: the name of the continuous data column for BETWEEEN min/max filter
                               can be either a datetime, int, or float data type
                               useful for restricting the database table size to check
        filter_categorical_col : the name of the categorical data column for Where = value check
                                 Creates an "IN ()" check on the unique values in this column
    Returns
        Unique list of values from dataframe compared to database table
    """
    args = 'SELECT %s FROM %s' %(', '.join(['"{0}"'.format(col) for col in dup_cols]), tablename)
    if date_handling is not None:
        args = args.replace("\"Date\"",date_handling)
    #print(args)
    args_contin_filter, args_cat_filter = None, None
    #print("santosh -->"+ args)     
    existing_security = ""
    if filter_continuous_col is not None:
        if df[filter_continuous_col].dtype == 'datetime64[ns]':
            args_contin_filter = """ "%s" BETWEEN Convert(datetime, '%s')
                                          AND Convert(datetime, '%s')""" %(filter_continuous_col,
                              df[filter_continuous_col].min(), df[filter_continuous_col].max())


    if filter_categorical_col is not None:
        args_cat_filter = ' "%s" in(%s)' %(filter_categorical_col,
                          ', '.join(["'{0}'".format(value) for value in df[filter_categorical_col].unique()]))

    if args_contin_filter and args_cat_filter:
        args += ' Where ' + args_contin_filter + ' AND' + args_cat_filter
    elif args_contin_filter:
        args += ' Where ' + args_contin_filter
    elif args_cat_filter:
        args += ' Where ' + args_cat_filter
       
    try:
        df.drop_duplicates(dup_cols, keep='last', inplace=True)
    except:
        pass
    #print(pd.read_sql(args, engine))
    #print(df)
    df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, left_index=leftIdx, indicator=True,suffixes=['', '_in_db'])
    #print(df)
    existing_security = str(df[df['_merge'] == 'both'])
    df = df[df['_merge'] == 'left_only']
    #print(df)
    df.drop(['_merge'], axis=1, inplace=True)
    #print(df)
    return [df,existing_security]

def sql_engine():
    DB_TYPE = 'postgresql'
    DB_DRIVER = 'psycopg2'
    DB_USER = 'postgres'
    DB_PASS = 'xanto007'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'RB_WAREHOUSE'
    POOL_SIZE = 50
    
    SQLALCHEMY_DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER,
                                                          DB_PASS, DB_HOST, DB_PORT, DB_NAME)
    ENGINE = create_engine(
        SQLALCHEMY_DATABASE_URI, pool_size=POOL_SIZE, max_overflow=0)

    return ENGINE

def last_thursday_of_month(date):
    date = date + relativedelta.relativedelta(day=31,weekday=relativedelta.TH(-1))
    return date

def get_futures_expiry(startdate,enddate):
    expiryDateList = []
    if startdate > enddate:
        expiryDateList = None
    for yr in range(startdate.year,enddate.year+1):
        for mon in range(1,13):
            dt = datetime.date(yr,mon,20)
            if(dt < enddate + relativedelta.relativedelta(months=3)):
                expiryDateList.append(last_thursday_of_month(dt))
    return expiryDateList

def test_df():
    nifty_fut = nsepy.get_history(symbol="NIFTY", 
			start=datetime.date(2015,1,1), 
			end=datetime.date(2015,1,10),
			index=True,
			futures=True, 
          expiry_date=datetime.date(2015,1,29))
    return nifty_fut

def get_Quandl():
    QUANDL_API_KEY = 'C33qTjnTYtCkx7UZ6H3R'
    
    return QUANDL_API_KEY

def get_finalColumns(cols=None):
    if cols is not None:
        for i in range(0,len(cols)):
            if cols[i] in mrigstatics.COLUMN_MAPPINGS.keys():
                cols[i] = mrigstatics.COLUMN_MAPPINGS[cols[i]]
    return cols

def get_date_vector(date_from_db):
    dateList = []
    """
    Takes a list [[curvedate(s)][tenor(s)]] and returns a 
    date vector [curvedate + tenor]
    
    """
    for i in range(0,len(date_from_db[0])):
        if date_from_db[1][i].split(" ")[1] == 'months':
            dateList.append(date_from_db[0][i] + relativedelta.relativedelta(months=int(date_from_db[1][i].split(" ")[0])))
        if date_from_db[1][i].split(" ")[1] in ('years','year'):
            dateList.append(date_from_db[0][i] + relativedelta.relativedelta(years=int(date_from_db[1][i].split(" ")[0])))
    dateList = [ql.Date(dt.day,dt.month,dt.year) for dt in dateList]
    return dateList

def args_inspector(args):
    """
    Does checks if the arguments are valid.
    """
    check = True
    wrong_arg = ""
    for arg_name in args:
        if args[arg_name] == "":
            check = False
            wrong_arg = wrong_arg + "|"+arg_name+"-"+args[arg_name]
    return [check,wrong_arg]

def python_dates(qldates):
    return datetime.date(qldates.year(),qldates.month(),qldates.dayOfMonth())
            
def getStockData(symbol,start_date,end_date):
    
    sql = "select * from stock_history where date >='"+ start_date.strftime('%Y-%m-%d') \
        + "' and date <'"+ end_date.strftime('%Y-%m-%d') \
        + "' and symbol='" \
        + symbol + "'"
        
    engine = sql_engine()
    stock_df = pd.read_sql(sql,engine)
    if not stock_df.empty:
        for i in range(0,len(stock_df['date'])-1):
            stock_df.iloc[i]['date'] = datetime.datetime.combine(stock_df.iloc[i]['date'],datetime.time())
        stock_df.date = pd.DatetimeIndex(stock_df.date)
        stock_df.set_index('date',inplace=True)
        #for i in range(0,len(stock_df.index)-1):
         #   stock_df.index[i] = datetime.datetime.combine(stock_df.index[i], datetime.time())

#    nav_df = [list(nav_df.loc[ind]) for ind in nav_df.index]
    return stock_df
 
def getMFNAV(reference_date, isinlist=None):
    
    sql = "select * from mf_nav_history where \"Date\">='"+ reference_date.strftime('%Y-%m-%d') +"' and \"ISIN Div Payout/ ISIN Growth\" in ("
    engine = sql_engine()
    for isin in isinlist:
        sql = sql +"'"+ isin + "',"
    sql = sql[:-1] + ")"
    nav_df = pd.read_sql(sql,engine)
    nav_df.set_index('Date',inplace=True)
    return nav_df

def getTransactionCosts():
    cost = mrigstatics.TR_CHARGES['BROK']\
            +mrigstatics.TR_CHARGES['STT/CTT']\
            +mrigstatics.TR_CHARGES['EXCH']\
            +mrigstatics.TR_CHARGES['GST']*(mrigstatics.TR_CHARGES['BROK']+mrigstatics.TR_CHARGES['EXCH'])
            
    return cost
