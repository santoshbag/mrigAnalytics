# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 05:02:07 2016

@author: sbag
"""
import pandas as pd

"""


"""
import datetime
import csv 
import mrigutilities as mu

class UPortfolio:
    """
    ######################################################################################################################
    # Portfolio Class 
    #
    # Description : This class represents the business idea of a Portfolio. A portfolio is composed of a set of Positions.
    # It is the class which would typically be the starting point for any implementation of the Project VRC.
    #
    # The idea is to enable all facilities for a portfolio manager. There are functions defined for setting up portfolio,
    # adding positions and displaying and exporting the portfolio details.
    #
    #######################################################################################################################
    """
    
    #Class begins here-----------------
    def __init__(self,username,name=None,currency="INR"):
        if name:
            self.portfolio_name = name
        else:
            self.portfolio_name = username+'_portfolio_'+ str(datetime.datetime.timestamp())
        self.position_date = datetime.date.today()
        self.portfolio_currency = currency
        self.position_list = []


    @classmethod
    def create(self,user_id,portfolio_name):
        engine = mu.sql_engine()
        query = """
            INSERT INTO portfolio.portfolios (user_id, portfolio_name)
            VALUES (%s, %s) RETURNING portfolio_id;
        """

        result = engine.execute(query, (user_id, portfolio_name)).fetchall()
        print('CREATE RESULT -->',result)
        if len(result) > 0 :
            return result[0][0]
        else:
            return []
    @classmethod
    def getPortfolios(self,user_id):
        engine = mu.sql_engine()
        query = """
            SELECT portfolio_id, portfolio_name
                    FROM portfolio.portfolios
                    WHERE user_id = %s
        """

        result = engine.execute(query, (user_id)).fetchall()
        print('FETCH RESULT -->',result)
        if len(result) > 0 :
            print('RESULT -->', result[0][0])
            return result
        else:
            return []

    @classmethod
    def verify(self,user_id,portfolio_id):
        engine = mu.sql_engine()
        query = """
            SELECT portfolio_id
                    FROM portfolio.portfolios
                    WHERE user_id = %s and portfolio_id = %s limit 1
        """

        result = engine.execute(query, (user_id,portfolio_id))
        return result[0][0]

    # @classmethod
    # def getItems(self,portfolio_id):
    #     engine = mu.sql_engine()
    #
    #     query = """
    #      SELECT item_id,item_type,item_symbol,quantity,purchase_price from portfolio.portfolio_items where portfolio_id = %s
    #      """
    #     result = engine.execute(query, (portfolio_id)).fetchall()
    #     print('FETCH ITEM RESULT -->',result)
    #
    #     return result

    @classmethod
    def getItems(self,portfolio_id):
        engine = mu.sql_engine()

        query = """
            SELECT
                item_type,item_symbol,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) AS net_quantity,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE 0 END) /
                NULLIF(SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE 0 END), 0) AS average_buy_price,
                (select close from stock_history where symbol = item_symbol order by date desc limit 1) as current_price,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) * 
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE 0 END) /
                NULLIF(SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE 0 END), 0)) AS investment,
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) * 
                (select close from stock_history where symbol = item_symbol order by date desc limit 1)) -
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE -quantity * transaction_price END)) AS profit_loss                
            FROM portfolio.transactions        
            where portfolio_id = %s
            GROUP BY item_type, item_symbol
         """
        result = engine.execute(query, (portfolio_id)).fetchall()
        print('FETCH ITEM RESULT -->',result)

        return result

    @classmethod
    def getPortfolioValueSeries(self, portfolio_id):
        engine = mu.sql_engine()

        query = """
            WITH first_transaction_date AS (
                SELECT MIN(transaction_date::date) AS start_date
                FROM portfolio.transactions 
                WHERE portfolio_id = %s
            ),
            cumulative_transactions AS (
                SELECT 
                    t.transaction_date::date,
                    t.item_symbol as symbol,
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'BUY' THEN t.quantity
                            WHEN t.transaction_type = 'SELL' THEN -t.quantity
                            ELSE 0 
                        END
                    ) OVER (PARTITION BY t.item_symbol ORDER BY t.transaction_date ROWS UNBOUNDED PRECEDING) AS cumulative_qty,
                    COALESCE(m.close, t.transaction_price) AS price_at_date, -- use market price or transaction price
                    t.quantity,
                    CASE 
                        WHEN t.transaction_type = 'SELL' THEN t.quantity * t.transaction_price
                        ELSE 0
                    END AS sell_cash
                FROM 
                    portfolio.transactions t
                LEFT JOIN 
                    stock_history m 
                    ON t.item_symbol = m.symbol AND t.transaction_date::date = m.date
                    where t.portfolio_id = %s
            ),
            symbol_daily_value AS (
                SELECT 
                    m.date,
                    m.symbol,
                    COALESCE(ct.cumulative_qty, 0) * m.close AS symbol_value,
                    SUM(ct.sell_cash) OVER (PARTITION BY m.date ORDER BY m.date) AS cumulative_sell_cash
                FROM 
                    stock_history m
                LEFT JOIN 
                    cumulative_transactions ct
                    ON m.symbol = ct.symbol AND m.date >= ct.transaction_date
             WHERE 
                    m.date >= (SELECT start_date FROM first_transaction_date)
                
            )
            SELECT 
                date,
                SUM(symbol_value) + MAX(cumulative_sell_cash) AS portfolio_value
            FROM 
                symbol_daily_value
            GROUP BY 
                date
            ORDER BY 
                date asc
          """
        # result = engine.execute(query, (portfolio_id)).fetchall()
        result = pd.read_sql(query % (portfolio_id,portfolio_id),engine)

        print('FETCH ITEM RESULT -->', result)

        return result

    @classmethod
    def getPortfolioXIRRSeries(self, portfolio_id):
        engine = mu.sql_engine()

        query = """
            WITH date_series AS (
                -- Generate a series of dates from the earliest transaction to today
                SELECT 
                    generate_series(
                        (SELECT MIN(transaction_date::date) FROM portfolio.transactions where portfolio_id = %s), 
                        CURRENT_DATE, 
                        '1 day'::interval
                    )::date AS date
            ),
            base_transactions AS (
                SELECT
                    t.transaction_date,
                    t.item_symbol,
                    t.transaction_type,
                    t.quantity,
                    t.transaction_price,
                    -- Calculate cash flow for each transaction
                    CASE 
                        WHEN t.transaction_type = 'BUY' THEN -t.quantity * t.transaction_price
                        WHEN t.transaction_type = 'SELL' THEN t.quantity * t.transaction_price
                        ELSE 0
                    END AS cashflow
                FROM portfolio.transactions t
                where t.portfolio_id = %s  
            ),
            daily_cashflow AS (
                -- Aggregate cashflows for each date and symbol
                SELECT
                    ds.date,
                    bt.item_symbol,
                    COALESCE(SUM(bt.cashflow) FILTER (WHERE bt.transaction_date::date = ds.date), 0) AS daily_cashflow
                FROM date_series ds
                LEFT JOIN base_transactions bt 
                    ON bt.transaction_date::date = ds.date
                GROUP BY ds.date, bt.item_symbol
            ),
            cumulative_qty AS (
                -- Compute cumulative quantity for each date and symbol
                SELECT
                    bt.item_symbol,
                    ds.date,
                    -- Calculate cumulative quantity by summing up transactions until the current date
                    COALESCE(SUM(
                        CASE 
                            WHEN bt.transaction_type = 'BUY' THEN bt.quantity
                            WHEN bt.transaction_type = 'SELL' THEN -bt.quantity
                            ELSE 0
                        END
                    ) FILTER (WHERE bt.transaction_date::date <= ds.date), 0) AS cumulative_qty
                FROM date_series ds
                LEFT JOIN base_transactions bt 
                    ON bt.transaction_date::date <= ds.date
                GROUP BY ds.date, bt.item_symbol
            ),
            daily_portfolio AS (
                -- Calculate daily portfolio holding value
                SELECT
                    ds.date,
                    cq.item_symbol,
                    cq.cumulative_qty,
                    COALESCE(m.close, 0) AS market_price,
                    dc.daily_cashflow,
                    -- Calculate holding value as cumulative_qty * market_price
                    cq.cumulative_qty * COALESCE(m.close, 0) AS holding_value
                FROM date_series ds
                LEFT JOIN cumulative_qty cq
                    ON cq.date = ds.date
                LEFT JOIN daily_cashflow dc
                    ON dc.date = ds.date AND cq.item_symbol = dc.item_symbol
                LEFT JOIN stock_history m
                    ON cq.item_symbol = m.symbol AND ds.date = m.date
            ),
            portfolio_summary AS (
                -- Summarize portfolio value and cashflows
                SELECT
                    date,
                    SUM(daily_cashflow) AS total_cashflow,
                    SUM(holding_value) AS total_portfolio_value
                FROM daily_portfolio
                GROUP BY date
            )
            SELECT 
                date,
                total_cashflow,
                total_portfolio_value,
                (total_cashflow + total_portfolio_value) AS total_value_on_date
            FROM portfolio_summary
            WHERE total_portfolio_value > 0  -- Exclude dates with no portfolio value
            ORDER BY date asc;
          """
        # result = engine.execute(query, (portfolio_id)).fetchall()
        result = pd.read_sql(query % (portfolio_id,portfolio_id),engine)
        result = result.fillna(0)
        print('FETCH ITEM RESULT -->', result)
        result["date"] = pd.to_datetime(result["date"])

        # Calculate Running XIRR
        cashflows = []
        dates = []
        running_xirr = []

        for _, row in result.iterrows():
            # cashflows.append(row["total_value_on_date"])
            if len(cashflows) > 0 :
                cashflows = cashflows[:-1]
                cashflows.append(row["total_cashflow"])
                cashflows.append(row["total_portfolio_value"])
                dates = dates[:-1]
                dates.append(row["date"])
                dates.append(row["date"]+datetime.timedelta(days=1))
            else:
                cashflows.append(row["total_cashflow"])
                cashflows.append(row["total_portfolio_value"])
                dates.append(row["date"])
                dates.append(row["date"]+datetime.timedelta(days=1))

            try:
                print('cashflows',cashflows)
                print('dates',dates)
                irr = mu.xirr(cashflows, dates)  # XIRR Calculation
                running_xirr.append(round(irr * 100, 2))  # XIRR as percentage
            except:
                running_xirr.append(None)  # Skip if insufficient data

        result["running_xirr"] = running_xirr
        return result[['date','running_xirr']]

    @classmethod
    def getPortfolioComp(self,portfolio_id):
        engine = mu.sql_engine()

        query = """
            SELECT
                item_type,item_symbol,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) AS net_quantity,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE 0 END) /
                NULLIF(SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE 0 END), 0) AS average_buy_price,
                (select close from stock_history where symbol = item_symbol order by date desc limit 1) * SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) as current_value,
                SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) * 
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE 0 END) /
                NULLIF(SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE 0 END), 0)) AS investment,
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) * 
                (select close from stock_history where symbol = item_symbol order by date desc limit 1)) -
                (SUM(CASE WHEN transaction_type = 'BUY' THEN quantity * transaction_price ELSE -quantity * transaction_price END)) AS profit_loss,
                (select country from security_master where symbol = item_symbol limit 1) as country,
                (select industry from security_master where symbol = item_symbol limit 1) as industry,
                (select sub_industry from security_master where symbol = item_symbol limit 1) as sub_industry
            FROM portfolio.transactions        
            where portfolio_id = %s
            GROUP BY item_type, item_symbol
         """
        result = engine.execute(query, (portfolio_id)).fetchall()
        print('FETCH ITEM RESULT -->',result)

        return result



    @classmethod
    def addItem(self,portfolio_id, item_type, item_symbol, quantity, purchase_price):
        engine = mu.sql_engine()

        query = """
         INSERT INTO portfolio.portfolio_items (portfolio_id, item_type, item_symbol, quantity, purchase_price)
         VALUES (%s, %s, %s, %s, %s) RETURNING item_id, item_type, item_symbol, quantity::float, purchase_price::float
         """
        result = engine.execute(query, (portfolio_id, item_type, item_symbol, quantity, purchase_price)).fetchall()
        print('ADD ITEM RESULT -->',result)

        return result

    @classmethod
    def addTransaction(self,portfolio_id, item_type, item_symbol, b_s,quantity, b_s_price,b_s_date):
        engine = mu.sql_engine()

        query = """
         INSERT INTO portfolio.transactions (portfolio_id, item_type, item_symbol, transaction_type,quantity, transaction_price,transaction_date)
         VALUES (%s, %s, %s, %s, %s,%s,%s) RETURNING transaction_id, item_type, item_symbol,transaction_type, quantity::float, transaction_price::float,transaction_date
         """
        print(query, (portfolio_id, item_type, item_symbol, b_s, quantity, b_s_price,b_s_date))
        result = engine.execute(query, (portfolio_id, item_type, item_symbol, b_s, quantity, b_s_price,b_s_date)).fetchall()
        print('ADD ITEM RESULT -->',result)

        return result

    @classmethod
    def deleteItem_old(self,portfolio_id, item_id):
        engine = mu.sql_engine()

        query = """
         DELETE FROM portfolio.portfolio_items WHERE portfolio_id = %s and item_id = %s
         """
        result = engine.execute(query, (portfolio_id, item_id))
        print('DELETE DONE', result)
        return result

    @classmethod
    def deleteItem(self,portfolio_id, item_name):
        engine = mu.sql_engine()

        query = """
         DELETE FROM portfolio.transactions WHERE portfolio_id = %s and item_symbol = %s
         """
        result = engine.execute(query, (portfolio_id, item_name))
        print('DELETE DONE', result)
        return result


    @classmethod
    def deletePortfolio(self,portfolio_id):
        engine = mu.sql_engine()

        query1 = """
         DELETE FROM portfolio.portfolio_items WHERE portfolio_id = %s
         """
        query2 = """
         DELETE FROM portfolio.portfolios WHERE portfolio_id = %s
         """
        result = engine.execute(query1, (portfolio_id))
        result = engine.execute(query2, (portfolio_id))
        return result

    @classmethod
    def getTransactions(self,portfolio_id,from_date,to_date,search_text=None):
        engine = mu.sql_engine()

        query = """
        SELECT *
        FROM portfolio.transactions
        WHERE portfolio_id = %s
        """

        # Add filters for date range
        if from_date:
            query += (" AND transaction_date >= '%s'" % from_date)
        if to_date:
            query += (" AND transaction_date <= '%s'" % to_date)

        # Add filter for search text
        if search_text:
            query += (" AND (LOWER(item_symbol) LIKE '%s' OR LOWER(transaction_type) LIKE '%s')" %(search_text,search_text))

        query += " ORDER BY transaction_date DESC"
        print('TRAN QUERY',query)
        result = engine.execute(query, (portfolio_id)).fetchall()
        return result

    def getPortfolioDetails(self,fields=[],export='n'):
        
        header_list = ['portfolio_id',
                       'portfolio_name',
                       'position_date', 
                       'portfolio_currency',
                       'product_type',
                       'product_quantity',
                       'product_price',
                       'marketValue',
                       'product_cost',
                       'product_currency',
                       'product_mult']

        
        if fields != []:
            header_list = fields

        portfolioDetails = {'portfolio_name': self.portfolio_name, 
        'position_date': self.position_date, 
        'portfolio_currency': self.portfolio_currency}
        
        port_out = self.portfolio_name + ", "+ str(self.position_date)+ ", "+self.portfolio_currency
        out = ""

        for positions in self.position_list:
            
            posdetail = positions.getPositionDetails()
            out = out + port_out 
            #out = out + ", " + positions.product_type + ", " + str(positions.product_quantity) + ", " \
            #+ str(positions.product_price) + ", " + str(positions.product_cost) + ", " + str(positions.product_currency)
            for poskeys in posdetail:
                out = out +", "+ str(posdetail[poskeys])
            out = out + "\n"
            
        print(out)
        
        if export=='y':
            csvfilename = str(self.portfolio_name) + ".csv"
            with open(csvfilename,'w',newline='') as csvfile:
                csvwriter = csv.DictWriter(csvfile,header_list,extrasaction='ignore')
                csvwriter.writeheader()
                for positions in self.position_list:
                    posdetail = positions.getPositionDetails()
                    posdetail.update(portfolioDetails)
                    csvwriter.writerow(posdetail)
        
        return portfolioDetails
        
    def addPosition(self,position_list):
        """ Adds a position or list of positions to the portfolio
        
        Arguments: 
        position_list  -- A list of objects of type Position. Single positions too must be passed as a list

        """
        for position in position_list:
            self.position_list.append(position)
        #return self.portfolio_list.count()


class Portfolio:
    """
    ######################################################################################################################
    # Portfolio Class
    #
    # Description : This class represents the business idea of a Portfolio. A portfolio is composed of a set of Positions.
    # It is the class which would typically be the starting point for any implementation of the Project VRC.
    #
    # The idea is to enable all facilities for a portfolio manager. There are functions defined for setting up portfolio,
    # adding positions and displaying and exporting the portfolio details.
    #
    #######################################################################################################################
    """

    # Class begins here-----------------
    def __init__(self, name="Portfolio1", currency="INR"):
        self.portfolio_name = name
        self.position_date = datetime.date.today()
        self.portfolio_currency = currency
        self.position_list = []

    def getPortfolioDetails(self, fields=[], export='n'):

        header_list = ['portfolio_id',
                       'portfolio_name',
                       'position_date',
                       'portfolio_currency',
                       'product_type',
                       'product_quantity',
                       'product_price',
                       'marketValue',
                       'product_cost',
                       'product_currency',
                       'product_mult']

        if fields != []:
            header_list = fields

        portfolioDetails = {'portfolio_name': self.portfolio_name,
                            'position_date': self.position_date,
                            'portfolio_currency': self.portfolio_currency}

        port_out = self.portfolio_name + ", " + str(self.position_date) + ", " + self.portfolio_currency
        out = ""

        for positions in self.position_list:

            posdetail = positions.getPositionDetails()
            out = out + port_out
            # out = out + ", " + positions.product_type + ", " + str(positions.product_quantity) + ", " \
            # + str(positions.product_price) + ", " + str(positions.product_cost) + ", " + str(positions.product_currency)
            for poskeys in posdetail:
                out = out + ", " + str(posdetail[poskeys])
            out = out + "\n"

        print(out)

        if export == 'y':
            csvfilename = str(self.portfolio_name) + ".csv"
            with open(csvfilename, 'w', newline='') as csvfile:
                csvwriter = csv.DictWriter(csvfile, header_list, extrasaction='ignore')
                csvwriter.writeheader()
                for positions in self.position_list:
                    posdetail = positions.getPositionDetails()
                    posdetail.update(portfolioDetails)
                    csvwriter.writerow(posdetail)

        return portfolioDetails

    def addPosition(self, position_list):
        """ Adds a position or list of positions to the portfolio

        Arguments:
        position_list  -- A list of objects of type Position. Single positions too must be passed as a list

        """
        for position in position_list:
            self.position_list.append(position)
        # return self.portfolio_list.count()

    
class Position:

    """
    ######################################################################################################################
    # Position Class 
    #
    # Description : This class represents the business idea of a Position in a particular asset or product type.
    # The position has the quantity, price and other information in a certain asset type like bonds, options, equity.
    # After instantiating a portfolio, this class will be used to populate the portfolio.
    # 
    # This class will be used to consolidate the position value and its other risk parameters which would again 
    # be aggregated at the portfolio level in the Portfolio Class.
    # 
    #######################################################################################################################
    """

    def __init__(self,setupparams):
        self.resultSet = {}
        self.metadataSet = {}
        self.positionDetail = {}
        self.product = setupparams['product']
        self.product_type = setupparams['product_type']
        self.product_quantity = setupparams['product_quantity']
        self.product_price = setupparams['product_price']
        self.product_cost = setupparams['product_cost']
        self.product_currency = setupparams['product_currency']
        self.product_mult = setupparams['product_mult']
        self.positionDetail = setupparams
        self.positionDetail.pop('product')        
        
    def getResults(self):

        """ Gets the Result set

        Argument : none
        Return Type : Dictionary of Dictionaries
        
        The results returned are 

        1)Marketvalue
        2)Yields : Yield to Maturity, Yield to Worst, Yield to First Call, Yield to Second Call etc
        3)Spreads : Z Spread to Maturity, Z Spread to Worst, Z Spread to First Call, OAS etc
        4)Durations : Spread Duration, Effective Duration etc
        5)Sensitivities : Option Greeks i.e Delta, Gamma, Theta etc

        """
        self.resultSet['marketValue'] = self.product_price*self.product_quantity*self.product_mult
        self.resultSet['yields'] = self.product.getYields()
        self.resultSet['spreads'] = self.product.getSpreads()
        self.resultSet['durations'] = self.product.getDurations()
        self.resultSet['sensitivities'] = self.product.getSensitivities()
        return self.resultSet

    def getMetadata(self):
        
        """ Gets the Product specific data 

        Argument : none
        Return Type : Dictionary

        Function description:
        The data returned is
        Issuer Name, Issuer country, Ratings, Issue Date, Maturity Date, Currency, Call Dates, Cashflow Dates,
        Coupon, Daycount, Coupon Spread, Cap/Floor, Reference Rate, Strike, Option Type, Exercise Type etc
         
        """

        self.metadataSet = self.product.getProductMetadata()
        return self.metadataSet


    def getPositionDetails(self):

        """ Consolidates all the position details

        Argument : none
        Return Type : Dictionary

        Function description:
        The gathers all the position information about the metadata, risk calculation results and merges in a
        dictionary type for retrieval.

        """
        res = self.getResults()
        meta = self.getMetadata()

        self.positionDetail.update(res)
        self.positionDetail.update(meta)

        return self.positionDetail

class Product:
    """
    ######################################################################################################################
    # Product Class 
    #
    # Description : This class acts as a parent class for all instruments or asset types
    # 
    # Any meaningful implementation of an asset type needs to be done by extending this class.
    # This class has some interface functions to extract the risk parameters but the actual implementation would depend on
    # the product type and hence when extending the class they need to be redefined to provide for actual calculation
    # 
    #######################################################################################################################
    """

    #Super class Member Data variables

    def __init__(self,productType):
        self.productType = productType
        self.productMetadataSet = {}
        self.value = None
#        self.yields = {}
#        self.sensitivities = {}
#        self.spreads = {}
#        self.durations = {}
        self.resultSet = {}
        
    #interface functions for the Product class which needs to be implemented properly in the subclasses
    def getProductMetadata(self):
        return self.productMetadataSet

    def getValue(self):
        return self.value
    
    def getResultSet(self):
        return self.resultSet   

# Code below is for testing 
if __name__ == '__main__':
    CS = Portfolio('Credit Suisse')
    bondpos = Product('fixedbond')
    position_params1 = {'product': bondpos, 
                       'product_type' : 'Bond',
                       'product_quantity' : 1000000,
                       'product_cost' : 97,
                       'product_price' : 98.2,
                       'product_mult' : 0.01,
                       'product_currency' : 'USD'}
    position_params2 = {'product': bondpos, 
                       'product_type' : 'Bond',
                       'product_quantity' : 10000000,
                       'product_cost' : 95,
                       'product_price' : 96.7,
                       'product_mult' : 0.01,
                       'product_currency' : 'USD'}

    CSPos1 = Position(position_params1)
    CSPos2 = Position(position_params2)
    poslist = []
    poslist.append(CSPos1)
    poslist.append(CSPos2)
    CS.addPosition(poslist)
    print("Printing Portfolio\n")
    portDet = CS.getPortfolioDetails(export='y')





    

        
    
    
