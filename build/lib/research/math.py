# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 11:29:17 2018

@author: Santosh Bag
"""
import numpy as np
from statsmodels import regression
import statsmodels.api as sm
import matplotlib.pyplot as plt
import math
from statsmodels.stats.stattools import jarque_bera

def isNormal(X):
    _, pvalue, _, _ = jarque_bera(X)

    if pvalue > 0.05:
        print('The values are likely normal.')
        return True
    else:
        print('The values are likely not normal.')
        return False
    
def linreg(X,Y):
    # Running the linear regression
    X = sm.add_constant(X)
    model = regression.linear_model.OLS(Y, X).fit()
    a = model.params[0]
    b = model.params[1]
    X = X[:,1]
    
    # Return summary of the regression and plot results
    X2 = np.linspace(X.min(), X.max(), 100)
    Y_hat = X2 * b + a
    plt.scatter(X, Y, alpha=0.3) # Plot the raw data
    plt.plot(X2, Y_hat, 'r', alpha=0.9);  # Add the regression line, colored in red
    plt.xlabel('X Value')
    plt.ylabel('Y Value')
    print(model.summary())
    return model.summary()
    