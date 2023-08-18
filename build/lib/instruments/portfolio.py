# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 05:02:07 2016

@author: sbag
"""
"""


"""
import datetime
import csv 

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
    
    #Class begins here-----------------
    def __init__(self,name="Portfolio1",currency="USD"):
        self.portfolio_name = name
        self.position_date = datetime.date.today()
        self.portfolio_currency = currency
        self.position_list = []
        
    def getPortfolioDetails(self,fields=[],export='n'):
        
        header_list = ['portfolio_name',
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
    # the product type and hence when extending the class they need to be redifned to provide for actual calculation
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





    

        
    
    
