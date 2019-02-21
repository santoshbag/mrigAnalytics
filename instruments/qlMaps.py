# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 18:37:46 2018

@author: Santosh Bag

Mapping module for Quantlib classes and constants
"""

import QuantLib as ql

CURRENCY  = {'INR' : ql.INRCurrency(),
             'USD' : ql.USDCurrency(),
             'EUR' : ql.EURCurrency(),
             'GBP' : ql.GBPCurrency()}

CALENDAR = {'India' : ql.India(),
            'US' : ql.UnitedStates(),
            'Euro' : ql.TARGET(),
            'UK' : ql.UnitedKingdom(),
            'TARGET' : ql.TARGET()}

DAYCOUNT = {'30-360' : ql.Thirty360(),
            'Actual-Actual' : ql.ActualActual(),
            'Actual-360' : ql.Actual360(),
            'Actual-365Fixed' : ql.Actual365Fixed()}

COMPOUNDING = {'Compounded' : ql.Compounded,
             'Continuous': ql.Continuous}

FREQUENCY = {'Annual' : ql.Annual,
             'Semiannual': ql.Semiannual,
             'Quarterly' : ql.Quarterly,
             'Monthly' : ql.Monthly,
             'Weekly' : ql.Weekly,
             'Daily' : ql.Daily}

BUSINESS_CONVENTION = {'Following' : ql.Following,
                       'ModifiedFollowing': ql.ModifiedFollowing,
                       'Preceding' : ql.Preceding,
                       'ModifiedPreceding' : ql.ModifiedPreceding,
                       'Unadjusted' : ql.Unadjusted,
                       'HalfMonthModifiedFollowing' : ql.HalfMonthModifiedFollowing}

DATE_GENERATION = {'Backward' : ql.DateGeneration.Backward,
                   'Forward' : ql.DateGeneration.Forward,
                   'Zero' : ql.DateGeneration.Zero,
                   'ThirdWednesday' : ql.DateGeneration.ThirdWednesday,
                   'TwentiethIMM' : ql.DateGeneration.TwentiethIMM,
                   'OldCDS' : ql.DateGeneration.OldCDS,
                   'CDS' : ql.DateGeneration.CDS,
                   'CDS2015' : ql.DateGeneration.CDS2015}


INTERPOLATION = {'Linear' : ql.Linear()}

OPTION = {'Call' : ql.Option.Call,
          'Put' : ql.Option.Put}

QL = {**CURRENCY, **CALENDAR, **DAYCOUNT}
QL = CURRENCY
QL.update(CALENDAR)
QL.update(DAYCOUNT)
QL.update(COMPOUNDING)
QL.update(FREQUENCY)
QL.update(BUSINESS_CONVENTION)
QL.update(DATE_GENERATION)
QL.update(INTERPOLATION)
QL.update(OPTION)



def period(period):
    map = {'D' : ql.Days,
           'W' : ql.Weeks,
           'M' : ql.Months,
           'Y' : ql.Years}
    
    return ql.Period(int(period[:-1]),map[period[-1]])

def qlDates(date):
    return ql.Date(date.day,
                   date.month,
                   date.year)

def quote(quote):
    return ql.QuoteHandle(ql.SimpleQuote(quote))
    
    

                                