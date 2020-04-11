import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import requests, zipfile, os, io, pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import mrigutilities, mrigstatics


def bhavcopy_download():
    datadir = os.path.dirname(__file__)
    base = os.path.join(datadir, '..', '..', 'data')  # ''F:\\Mrig Analytics\\Development\\data\\'
    print(base)
    t = datetime.today().date()
    dmonth = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
              '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}

    # Before running this script , create a file called log.txt and write the date from which you want to download EOD data
    # Opening file named log.txt , which keeps track of the last downloaded date.
    ltdl = open(os.path.join(base, 'log.txt'), 'r')
    lastdt = ltdl.read(10)
    ltdl.close()
    lastdt = datetime.strptime(lastdt, '%Y-%m-%d')
    diff, wr = t - lastdt.date(), ''
    engine = mrigutilities.sql_engine()
    disable_sql = "alter table stock_history disable trigger return_trigger"
    enable_sql = "alter table stock_history enable trigger return_trigger"
    engine.execute(disable_sql)

    csv_header_map = {'SYMBOL': 'symbol',
                      'SERIES': 'series',
                      'OPEN': 'open',
                      'HIGH': 'high',
                      'LOW': 'low',
                      'CLOSE': 'close',
                      'LAST': 'last',
                      'PREVCLOSE': 'prev_close',
                      'TOTTRDQTY': 'volume',
                      'TOTTRDVAL': 'turnover',
                      'TIMESTAMP': 'date',
                      'TOTALTRADES': 'trades',
                      'DELIVERABLE': 'deliverable_volume'}

    for i in range(1, diff.days + 1):
        nextdt = lastdt + relativedelta(days=i)
        d, m, y = '%02d' % nextdt.day, '%02d' % nextdt.month, '%02d' % nextdt.year
        if not os.path.isdir(base + "/" + y):
            os.mkdir(base + "/" + y)
            os.mkdir(base + "/" + y + '/Index')
            os.mkdir(base + "/" + y + '/Futures')
        zpath = base + "/" + y + '/' + d + '.zip'

        for i in range(7):
            while True:
                try:
                    url = 'https://www1.nseindia.com/content/historical/EQUITIES/' + y + '/' + dmonth[m] + '/cm' + d + \
                          dmonth[m] + y + 'bhav.csv.zip'
                    print(url)
                    a = requests.get(
                        'https://www1.nseindia.com/content/historical/EQUITIES/' + y + '/' + dmonth[m] + '/cm' + d +
                        dmonth[m] + y + 'bhav.csv.zip')
                except requests.ConnectionError:
                    print('No connection, retrying')
                break

        if a.status_code == 200:
            dload = open(zpath, 'wb')
            dload.write(a.content)
            dload.close()
            z = zipfile.ZipFile(zpath, 'r')
            z.extractall(base + "/" + y + '/')
            z.close()
            os.remove(zpath)
            f, deldict = pd.read_csv(
                base + "/" + y + '/cm' + d + dmonth[m] + y + 'bhav.csv'), {}  # reading the raw dl-ed bhav file
            f = f[f['SERIES'] == 'EQ']  # retaining only EQ rows and leaving out bonds,options etc
            deliverable = requests.get(
                'https://www1.nseindia.com/archives/equities/mto/MTO_' + d + m + y + '.DAT').text.splitlines()
            del deliverable[:4]

            for i in deliverable:
                c = i.split(',')
                if c[3] == 'EQ':
                    deldict[c[2]] = c[5]  # building delivarables dict

            dfdel = pd.DataFrame(list(deldict.items()), columns=['SYMBOL', 'DELIVERABLE'])
            f = f.merge(dfdel, on='SYMBOL', how='left')  # left merge of delivarables here

            indices = requests.get(
                'https://www1.nseindia.com/content/indices/ind_close_all_' + d + m + y + '.csv').content

            if len(indices) > 300:  # sometimes nse doesnt give the index file, so the if condition
                indx = pd.read_csv(io.StringIO(
                    indices.decode('utf-8')))  # reading content of indices csv and storing in DataFrame using io module
                indx.to_csv(base + "/" + y + '/Index/Indices' + str(nextdt.date()) + '.csv', index=False)
                indx = indx[['Index Name', 'Index Date', 'Open Index Value', 'High Index Value', 'Low Index Value',
                      'Closing Index Value', 'Volume','Turnover (Rs. Cr.)','P/E','P/B','Div Yield']]
                indx = indx.rename(
                    columns={'Index Name': 'SYMBOL', 'Index Date': 'TIMESTAMP', 'Open Index Value': 'OPEN',
                             'High Index Value': 'HIGH', 'Low Index Value': 'LOW', 'Closing Index Value': 'CLOSE',
                             'Volume': 'TOTTRDQTY','Turnover (Rs. Cr.)':'TOTTRDVAL','P/E':'pe','P/B':'pb','Div Yield':'div_yield'})
                indx['TIMESTAMP'] = pd.Series(str(nextdt.date().strftime('%Y%m%d')) for _ in range(len(indx)))            
                indx['SERIES'] = 'IN'
                indx = indx.rename(columns=csv_header_map)
                indx['symbol'] = indx['symbol'].apply(lambda x:x.upper())
                indx = indx.replace('-', 0)
                indx['turnover'] = pd.to_numeric(indx['turnover'], errors='coerce')
                indx['turnover'] = indx['turnover'].apply(lambda x:x*10000000)
                indx.set_index('date', inplace=True)
                indx.to_sql('stock_history', engine, if_exists='append', index=True)    
#                f = f.append(indx, ignore_index=True)

            f['TIMESTAMP'] = pd.Series(str(nextdt.date().strftime('%Y%m%d')) for _ in range(len(f)))
            f['SERIES'] = 'EQ'
            f = f[['SYMBOL', 'SERIES', 'TIMESTAMP', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'LAST', 'PREVCLOSE', 'TOTTRDQTY',
                   'TOTTRDVAL', 'TOTALTRADES', 'DELIVERABLE']]
            f.to_csv(base + "/" + y + '/' + str(nextdt.date()) + '.csv', index=False)
            f = f.rename(columns=csv_header_map)
            f = f.replace('-', 0)
            # f['turnover'] = f['turnover'] * 10000000
            f.set_index('date', inplace=True)
            #        print(f)
#            f.to_sql('stock_history', engine, if_exists='append', index=True)

            os.remove(base + "/" + y + '/cm' + d + dmonth[m] + y + 'bhav.csv')
            futures = requests.get(
                'https://www1.nseindia.com/content/historical/DERIVATIVES/' + y + '/' + dmonth[m] + '/fo' + d + dmonth[
                    m] + y + 'bhav.csv.zip')
            fo = open(zpath, 'wb')
            fo.write(futures.content)
            fo.close()
            z, wr = zipfile.ZipFile(zpath, 'r'), nextdt.date()
            z.extractall(base + "/" + y + '/Futures')
            z.close()
            os.remove(zpath)
    engine.execute(enable_sql)
    # writing the last downloaded date to log.txt
    if not isinstance(wr, str):
        ltdl = open(base + "/" + 'log.txt', 'w')
        ltdl.write(str(wr))
        ltdl.close()


if __name__ == '__main__':
    bhavcopy_download()
