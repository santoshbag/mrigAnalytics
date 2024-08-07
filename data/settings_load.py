# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:01:52 2017

@author: Santosh Bag

reads NSE bhavcopy file in zip format and puts into database
format is "cmDDMMMYYYYbhav.csv.zip"
"""
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime #import date, timedelta
import pandas as pd #import DataFrame
#from sqlalchemy import create_engine
import mrigutilities
import json

datadir = os.path.dirname(__file__)
settings_files_path = os.path.join(datadir, '..', ".settings.json")
now = datetime.datetime.now()

engine = mrigutilities.sql_engine()

def set_settings():
      settings = json.load(open(settings_files_path))
      settings = json.dumps(settings)
      sql = "insert into settings (setting_type,settings,load_time) values ('main',%s,%s) "\
            "    on conflict(setting_type) do update set settings = excluded.settings,load_time = excluded.load_time "
      engine.execute(sql,(settings,now))
      # print(settings['indices_for_mrig'][3])

def get_settings():
      sql = "select settings from settings where setting_type='main' limit 1"
      settings = engine.execute(sql).fetchone()[0]
      settings = json.loads(settings)
      return settings


if __name__ == '__main__':
      # print(get_settings())
      set_settings()