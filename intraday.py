#!/usr/bin/python3

import os
import sys
import time
from datetime import date
from datetime import datetime, timedelta
import wget
import requests
import zipfile
import pandas as pd
import yfinance as yf
from pandarallel import pandarallel
import multiprocessing
import concurrent.futures
import requests
import threading
import time
import shutil

manager = multiprocessing.Manager()
STOCK = manager.dict()

pandarallel.initialize()

NSECSV = ""

def dataHelper(r, filename, gtime):
    global NSECSV
    open('data/' + gtime + "/" + filename, 'wb').write(r.content)
    with zipfile.ZipFile("data/" + gtime + "/" + filename, 'r') as zip_ref:
        zip_ref.extractall("data/" + gtime)
        NSECSV = "data/" + gtime + "/" + filename.replace(".zip", "")
    print("Download complete.\n\nExecuting table creation...")

def generateURLAndFileAndDir(day):
    if day == "today":
        tDay = date.today()
        gTime = datetime.now()
    else:
        cday = 3 if datetime.now().weekday() == 0 else 1 
        tDay = date.today() - timedelta(days=cday)
        gTime = datetime.now() - timedelta(days=cday)

    year = tDay.strftime("%Y")
    month = tDay.strftime("%b").upper()
    day = tDay.strftime("%d")
    filename = "cm" + day + month + year+ "bhav.csv.zip"
    nseUrl = "https://archives.nseindia.com/content/historical/EQUITIES/" + year + "/" + month + "/" + filename
    return filename, nseUrl, gTime.strftime("%d-%b-%Y-%H-%M-%f")

def getNseData():
    global NSECSV
    filename, nseUrl, gtime = generateURLAndFileAndDir("today")
    os.mkdir("data/" + gtime)
    try:
        r = requests.get(nseUrl, timeout=10)
        dataHelper(r, filename, gtime)
    except requests.exceptions.Timeout as err: 
        print("NSE doesn't have that file. Will try with one day older ...")
        shutil.rmtree("data/" + gtime)
        filename, nseUrl, gtime = generateURLAndFileAndDir("yesterday")
        os.mkdir("data/" + gtime)
        r = requests.get(nseUrl, timeout=10)
        dataHelper(r, filename, gtime)

def getTop100Table():
    getNseData()
    df = pd.read_csv(NSECSV)
    sdf = df.sort_values(by=['TOTTRDVAL'], ascending=False)
    cdf = sdf.head(100)
    newdf = cdf[['SYMBOL']].copy()
    rdf = newdf.reset_index(drop=True)
    rdf['SYMBOL'] = rdf['SYMBOL'].astype(str) + '.NS'
    return rdf

def getStockHistory(stock):
    print("Fetching history for " + stock, end="\r")
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

def populateCMP(row):
    return STOCK[row[0]].get("price", -1)

def populateDMA10(row):
    return STOCK[row[0]]["dma10"]

def populateDMA30(row):
    return STOCK[row[0]]["dma30"]

def populateDMA60(row):
    return STOCK[row[0]]["dma60"]

def populateDMA90(row):
    return STOCK[row[0]]["dma90"]

def populateDMA120(row):
    return STOCK[row[0]]["dma120"]

def populateDMA200(row):
    return STOCK[row[0]]["dma200"]

def getIntradayTable():
    df100 = getTop100Table()
    pool = multiprocessing.Pool()
    processes = [pool.apply_async(getStockHistory, args=(df100['SYMBOL'][sym],)) for sym in df100.index]
    result = [p.get() for p in processes]
    df100['CMP'] = df100.parallel_apply(populateCMP, axis=1)
    df100 = df100.drop(index=[row for row in df100.index if -1 == df100.loc[row, 'CMP']])
    df100['10DMA'] = df100.parallel_apply(populateDMA10, axis=1)
    df100['30DMA'] = df100.parallel_apply(populateDMA30, axis=1)
    df100['60DMA'] = df100.parallel_apply(populateDMA60, axis=1)
    df100['90DMA'] = df100.parallel_apply(populateDMA90, axis=1)
    df100['120DMA'] = df100.parallel_apply(populateDMA120, axis=1)
    df100['200DMA'] = df100.parallel_apply(populateDMA200, axis=1)
    return df100

def predictStock(cmp, dma10, dma30, dma60, dma90, dma120, dma200):
    if cmp > dma10 and cmp > dma30 and cmp > dma60 and cmp > dma90 and cmp > dma120 and cmp < dma200:
        return "Best for buy above 200 DMA"
    elif cmp < dma10 and cmp < dma30 and cmp < dma60 and cmp < dma90 and cmp < dma120 and cmp > dma200:
        return "Best for sell below 200 DMA" 
    else:
        return "Avoid"

def intraStock(df):
    df["PREDICTION"] = df.apply(lambda row: predictStock(row["CMP"], row["10DMA"], row["30DMA"], row["60DMA"], row["90DMA"], row["120DMA"], row["200DMA"]), axis=1)
    pdf = df.drop(index=[row for row in df.index if "Avoid" in df.loc[row, 'PREDICTION']])
    print(pdf)
    
# The stock market begins
print("Welcome to Intraday Payal :)\n\n\nDownloading latest NSE data...")
idf = getIntradayTable()
intraStock(idf)
