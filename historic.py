#!/usr/bin/python3

import os
import sys
import time
from datetime import date
from datetime import datetime
import wget
import requests
import zipfile
import pandas as pd

from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp

api_key = 'Ljmy6PY3'
clientId = 'P259336'
pwd = '2095'
smartApi = SmartConnect(api_key)
token = "YD6S2P7ULVQOWY2L6WJ46LZYBY"
totp=pyotp.TOTP(token).now()
correlation_id = "abc123"

data = smartApi.generateSession(clientId, pwd, totp)

authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']

# fetch the feedtoken
feedToken = smartApi.getfeedToken()

# fetch User Profile
res = smartApi.getProfile(refreshToken)
smartApi.generateToken(refreshToken)
res=res['data']['exchanges']

try:
    historicParam={
    "exchange": "NSE",
    "symboltoken": 2885,
    "interval": "ONE_MINUTE",
    "fromdate": "2023-02-26 10:15", 
    "todate": "2023-02-26 10:16"
    }
    print(smartApi.getCandleData(historicParam))
except Exception as e:
    print("Historic Api failed: {}".format(e.message))

