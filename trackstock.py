#!/usr/bin/python3


import time
from datetime import date
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
import time
import argparse


STOCK = {}
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--stock", help = "Stock name", type=str)
args = parser.parse_args()

def getStockHistory(stock):
    global STOCK
    try:
        stk = yf.Ticker(stock)
        price = stk.info.get('currentPrice', -1)
        hist = stk.history(period="200d")
        data = {}
        data["price"] = price
        data["dma10"] = hist["Close"].head(10).mean()
        data["dma30"] = hist["Close"].head(30).mean()
        data["dma60"] = hist["Close"].head(60).mean()
        data["dma90"] = hist["Close"].head(90).mean()
        data["dma120"] = hist["Close"].head(120).mean()
        data["dma200"] = hist["Close"].head(200).mean()
        STOCK[stock] = data
    except:
        return

def trackStock(stock):
    while(True):
        getStockHistory(stock)
        print(STOCK)
        time.sleep(10)
     
# The stock market begins
print("Welcome to Intraday Payal :)\n\n\nTracking the stock: ")
trackStock(args.stock)