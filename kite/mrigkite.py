import logging
from kiteconnect import KiteConnect
import kiteconnect.exceptions
import mrigutilities as mu
import pandas as pd

# logging.basicConfig(level=logging.DEBUG)

class mrigkite:

    vendor = 'zerodha'
    username = 'sbag'
    api_key = None
    __api_secret = None
    __access_token = None
    logged_in = False
    kite = None
    login_url = None



    def __init__(self,vendor='zerodha',username='sbag'):
        self.vendor = vendor
        self.username = username
        engine = mu.sql_engine()
        pool = {
            "pool_connections": 10,
            "pool_maxsize": 10,
            "max_retries": 5,
            "pool_block": False
        }


        creds = engine.execute("select api_key, api_secret,access_token from auth where vendor=%s and username=%s",(self.vendor,self.username)).fetchall()
        if len(creds) > 0:
            self.api_key = creds[0][0]
            self.__api_secret = creds[0][1]
            self.__access_token = creds[0][2]
            self.kite = KiteConnect(api_key=self.api_key,pool=pool)
            try:
                self.kite.set_access_token(self.__access_token)
                quote = self.kite.quote('NSE:NIFTY 50')
                if len(quote) > 0:
                    self.logged_in = True
            except kiteconnect.exceptions.TokenException:
                pass
            self.login_url = self.kite.login_url()


    def set_credentials(self,cred_dict):
        if 'api_key' in cred_dict.keys():
            self.api_key = cred_dict['api_key']
        if 'api_secret' in cred_dict.keys():
            self.__api_secret = cred_dict['api_secret']
        # if 'access_token' in cred_dict.keys():
        #     self.access_token = cred_dict['access_token']

        engine = mu.sql_engine()

        if self.api_key is not None:
            engine.execute("update auth set api_key=%s where vendor=%s and username=%s",(self.api_key,self.vendor,self.username))
        if self.__api_secret is not None:
            engine.execute("update auth set api_secret=%s where vendor=%s and username=%s",(self.__api_secret,self.vendor,self.username))
        # if self.access_token is not None:
        #     engine.execute("update auth set access_token=%s where vendor=%s and username=%s",(self.access_token,self.vendor,self.username))
        #


    def kite_login(self,request_token):

        data = self.kite.generate_session(request_token, api_secret=self.__api_secret)
        self.kite.set_access_token(data["access_token"])
        quote = self.kite.quote('NSE:NIFTY 50')
        if len(quote) > 0:
            self.logged_in = True
            engine = mu.sql_engine()
            engine.execute("update auth set access_token=%s where vendor=%s and username=%s",(data["access_token"],self.vendor,self.username))


    def getStatus(self):
        return 1 if self.logged_in else 0

    def getKiteSession(self):
        return self.kite

    def getInstruments(self,exchange='ALL'):
        if exchange == 'ALL':
            instruments = self.kite.instruments()
        else:
            instruments = self.kite.instruments(exchange=exchange)
        return pd.DataFrame(instruments)

    def getPositions(self):
        positions = self.kite.positions()

        positions = pd.DataFrame(positions['net'])

        # print(positions.columns)
        # print(positions.head(1).to_string())
        return positions

    def getQuoteLive(self,scrip):
        sec = scrip
        if scrip == 'NIFTY':
            sec = 'NIFTY 50'
        elif scrip == 'BANKNIFTY':
            sec = 'NIFTY BANK'
        return pd.DataFrame(self.kite.quote('NSE:'+sec))['NSE:'+sec]

    def getHistorical(self,token,from_date,to_date,interval):
        data = self.kite.historical_data(token,from_date,to_date,interval)
        return pd.DataFrame(data)

