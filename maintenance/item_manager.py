import datetime

import mrigutilities as mu
import mrigstatics
import pandas as pd
'''
market_graphs = None
n50_ta_screen = None
sector_graph = None
'''

items= None

engine = mu.sql_engine(mrigstatics.MRIGWEB[mrigstatics.ENVIRONMENT])
def get_item(names):
    sql = '''
    select item,data from webpages where item in {} order by load_date desc
    '''

    item_names = str(names).replace('[','(').replace(']',')')
    items = pd.read_sql(sql.format(item_names),engine)
    if not items.empty:
        items.set_index('item',inplace=True)
        items = items.to_dict()
    else:
        items = {}
    return items

def set_items(item_value_dict):
    date = datetime.date.today().strftime('%Y%m%d')
    sql = '''
    insert into webpages (item, data, load_date) 
    values (%s,%s,%s)
    on conflict(item)
    do update set
    data = excluded.data,
    load_date = excluded.load_date,
    data_prev = excluded.data
    '''
    for key, value in item_value_dict.items():
        # try:
        # print(sql.format(key,value,date))
        engine.execute(sql,(key,value,date))
        # except:
        #     pass
def update_items(item_value_dict):
    date = datetime.date.today().strftime('%Y%m%d')
    sql = '''
    update webpages 
    set data_prev = data,
        data = %s,
        load_date = %s
    where item = %s 
    '''
    for key, value in item_value_dict.items():
        engine.execute(sql,(value,date,key))


if __name__ == '__main__':
    items = {'mg':'data5',
             'sg':'data2'}
    update_items(items)
    item = get_item(['mg','sg'])
    print(item)