STABLECOINS = ['ousd','usdk','rsv','musd','vai','sbd','dgd','qc','cusd','susd','eurs','usdx','gusd','xsgd','tribe','lusd','frax','husd','fei','rsr','usdn','usdp','tusd','dai','ust','busd','usdc','usdt']

MODDAYS = 30 # get from website if files are older than moddays

import numpy as np
import pandas as pd
import datetime as dt
import json
import os
from urllib.error import HTTPError
import time

from pycoingecko import CoinGeckoAPI

def FullMergeDict(one, two):
  return { key:one.get(key,[])+two.get(key,[]) for key in set(list(one.keys())+list(two.keys())) }


def getCoinGeckoId(symbols, forceLower = True):
    # get CoinGeckoId from Coin symbol
    # set forceLower = False if don't want to get lower case of symbol

    ids = []
    if type (symbols)!=list:
        symbols = [symbols]
    for symbol in symbols:
        if forceLower:
            symbol = symbol.lower()
        try:
            id = dfCoinsList[dfCoinsList['symbol']==symbol]['id'].iloc[0]
            ids.append(id)
        except ValueError:
            ids.append(np.nan)
        except IndexError:
            ids.append(np.nan)
    return ids

def getCoinGeckoMarket (symbols, modDays = 30, forceLower = True):
    dfMarket = pd.DataFrame()
    ids = getCoinGeckoId(symbols, forceLower)
    direc = './data'
    if not os.path.isdir(direc):
        os.mkdir (direc)
    if os.path.isfile('./data/invalid-symbols.json'):
        with open('./data/invalid-symbols.json','r') as f:
            invalidSymbols=json.load(f)
    else:
        invalidSymbols={"Invalid_Symbols":[]}
        
    for i in range(len(ids)):
        if symbols[i] in invalidSymbols['Invalid_Symbols']:
            print (f'Skipping {symbols[i]}')
            continue
#         try:
#             data = cg.get_coin_market_chart_by_id(ids[i],'usd',1)
        file = './data/coingecko_coin_market_chart_by_ids_'+str(ids[i])+'.json'

        if os.path.isfile(file):
            modDate = os.path.getmtime(file)
            with open(file,'r') as f:
                data=json.load(f)
                print ('loading')
            if dt.datetime.now() - dt.datetime.fromtimestamp(modDate)>dt.timedelta(days=modDays):
                daysOld = (dt.datetime.now()-dt.datetime.fromtimestamp(data['prices'][-1][0]/1000)).days
                newData = cg.get_coin_market_chart_by_id(ids[i],'usd',daysOld,interval='daily')
                data = FullMergeDict(data,newData)
                for k, v in data.items(): # remove last item
                    v.pop()
                with open (file,'w') as f:
                    json.dump(data, f)
                    print ('appended file')
        else:
            try:
                print(f"trying {symbols[i]}")
                data = cg.get_coin_market_chart_by_id(ids[i],'usd',5000)
                for k,v in data.items():
                    v.pop()
                with open(file, 'w') as f:
                    json.dump(data, f)
                    print ('new file')
            except ValueError:
                print (f"Invalid symbol: {symbols[i]}")
                invalidSymbols['Invalid_Symbols'].append(symbols[i])
                continue



        df = pd.DataFrame(data['prices'],columns=['Date','Price'])
        df['Symbol']=symbols[i]
        df['Date']=pd.to_datetime(df['Date']*1000000)
        dfMktCap = pd.DataFrame(data['market_caps'], columns=['Date','Market_Cap'])
        df['Market_Cap']=dfMktCap['Market_Cap']
        dfTotVol = pd.DataFrame(data['total_volumes'], columns=['Date','Total_Volume'])
        df['Total_Volume'] = dfTotVol['Total_Volume']
        dfMarket=dfMarket.append(df,ignore_index=True)

    print (invalidSymbols)
    print (type(invalidSymbols))

    with open('./data/invalid-symbols.json','w') as f:
            json.dump(invalidSymbols,f)
    return dfMarket

def getExchangesList (modDays = 30):
    # get exchanges list (from website is json files is more than modDays old)
    direc = './data'
    file = './data/coingecko-exchanges-list.json'
    if not os.path.isdir(direc):
        os.mkdir (direc)
    if os.path.isfile(file):
        modDate = os.path.getmtime(file)
        if dt.datetime.now() - dt.datetime.fromtimestamp(modDate)<dt.timedelta(days=modDays):
            with open(file,'r') as f:
                data=json.load(f)
#                 print ('loading')
            return data
    data=cg.get_exchanges_list()
    with open(file, 'w') as f:
        json.dump(data, f)
#         print ('new file')
    return data

def getSupportedCurrencies (modDays = 30):
    # get supported vs currencies list (from website is json files is more than modDays old)
    direc = './data'
    file = './data/coingecko-supported-vs-currencies.json'
    if not os.path.isdir(direc):
        os.mkdir (direc)
    if os.path.isfile(file):
        modDate = os.path.getmtime(file)
        if dt.datetime.now() - dt.datetime.fromtimestamp(modDate)<dt.timedelta(days=modDays):
            with open(file,'r') as f:
                data=json.load(f)
#                 print ('loading')
            return data
    data=cg.get_supported_vs_currencies()
    with open(file, 'w') as f:
        json.dump(data, f)
#         print ('new file')
    return data   
    
def getCoinsList (modDays = 30):
    # get coins list list (from website is json files is more than modDays old)
    direc = './data'
    file = './data/coingecko-coins-list.json'
    if not os.path.isdir(direc):
        os.mkdir (direc)
    if os.path.isfile(file):
        modDate = os.path.getmtime(file)
        if dt.datetime.now() - dt.datetime.fromtimestamp(modDate)<dt.timedelta(days=modDays):
            with open(file,'r') as f:
                data=json.load(f)
#                 print ('loading')
            return data
    data=cg.get_coins_list()
    with open(file, 'w') as f:
        json.dump(data, f)
#         print ('new file')
    return data   

cg = CoinGeckoAPI()
coinsList = getCoinsList(MODDAYS)
dfCoinsList = pd.DataFrame(coinsList)