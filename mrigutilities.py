# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:13:11 2018

@author: Santosh Bag
"""
import csv
import pandas as pd
from collections import deque
from sqlalchemy import create_engine


def get_last_row(csv_filename,lines=1):
    with open(csv_filename,'r') as f:
        try:
            lastrow = deque(csv.reader(f), lines)
        except IndexError:  # empty file
            lastrow = None
        return lastrow
    

def clean_df_db_dups(df, tablename, engine, dup_cols=[],
                         filter_continuous_col=None, filter_categorical_col=None):
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
    date_handling = "to_char(\"Date\",'dd-Mon-YYYY') as \"Date\""
    args = args.replace("\"Date\"",date_handling)
    #print(args)
    args_contin_filter, args_cat_filter = None, None
    #print("santosh -->"+ args)     

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
       
    df.drop_duplicates(dup_cols, keep='last', inplace=True)
    #print(pd.read_sql(args, engine))
    df = pd.merge(df, pd.read_sql(args, engine), how='left', on=dup_cols, indicator=True,suffixes=['', '_in_db'])
    #print(df)
    df = df[df['_merge'] == 'left_only']
    #print(df)
    df.drop(['_merge'], axis=1, inplace=True)
    #print(df)
    return df

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
