# -*- coding: utf-8 -*-
"""
Created on Wed May 23 19:31:48 2018

@author: Santosh Bag
"""
import sys

test = open("CHECK.txt","a+")

arg1 = sys.argv[1]
arg2 = sys.argv[2]


test.write("Argument 1 is "+arg1+"\n")
test.write("argument 2 is "+arg2+"\n")

test.close()
print("Batch Works")
