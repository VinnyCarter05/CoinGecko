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


def getCoinGeckoId(symbols, forceUpper = False):
    # get CoinGeckoId from Coin symbol
    # set forceLower = False if don't want to get lower case of symbol
    file = './data/coingecko-valid-symbol-id.json'
    if os.path.isfile(file):
        with open (file,'r') as f:
            symbolId = json.load(f)
    else:
        symbolId = {}
    calls = 0
    ids = {}
    if type (symbols)!=list:
        symbols = [symbols]
    for symbol in symbols:
        if forceUpper:
            symbol = symbol.upper()
#         try:
#             id = dfCoinsList[dfCoinsList['symbol']==symbol]['id'].iloc[0]
#            print ('length: ', symbol,len(dfCoinsList[dfCoinsList['symbol']==symbol]['id']))
        if symbol in symbolId.keys():
            ids[symbol]=symbolId[symbol]
            print (f"loading {symbol}:{ids[symbol]}")
            continue
        allIds = dfCoinsList[dfCoinsList['symbol']==symbol]['id']
        id = {symbol:""}
        if len(allIds)>1:
            highestMktCap = 0
            for i in range(len(allIds)):
#                 print (symbol,allIds.iloc[i])
                try:
                    data = cg.get_coin_market_chart_by_id(allIds.iloc[i],'usd',1,interval='daily')
                    calls += 1
#                     print (calls)
                    if calls >= 40:
                        time.sleep(60)
                        calls = 0
                    if data['market_caps'][0][1]>highestMktCap:
#                         print (allIds.iloc[i])
                        id[symbol] = allIds.iloc[i]
#                         id["symbol"] = symbol
                except ValueError:
                    print ('ValueError')
#                     print (allIds.iloc[i])
        elif len(allIds)==1:
            try:
                data = cg.get_coin_market_chart_by_id(allIds.iloc[0],'usd',1,interval='daily')
                calls += 1
#                 print (calls)
                id[symbol] = allIds.iloc[0]
#                 id["symbol"] = symbol
            except ValueError:
                print (allIds.iloc[0], "doesn't exist")
        if id[symbol] != "":
            ids[symbol]=id[symbol]
            print (symbol,':', ids[symbol])
#         except ValueError:
#             ids.append(np.nan)
#         except IndexError:
#             ids.append(np.nan)
    with open (file,'w') as f:
        json.dump(ids,f) 
    return ids

def getCoinGeckoMarket (symbols, modDays = 30, forceUpper = True):
    dfMarket = pd.DataFrame()
    ids = getCoinGeckoId(symbols, forceUpper)
    direc = './data'
    if not os.path.isdir(direc):
        os.mkdir (direc)
    if os.path.isfile('./data/coingecko-invalid-symbols.json'):
        with open('./data/coingecko-invalid-symbols.json','r') as f:
            invalidSymbols=json.load(f)
    else:
        invalidSymbols={"Invalid_Symbols":[]}
        
    for symbol in ids.keys():
        if symbol in invalidSymbols['Invalid_Symbols']:
            print (f'Skipping {symbols[i]}')
            continue
#         try:
#             data = cg.get_coin_market_chart_by_id(ids[i],'usd',1)
        file = './data/coingecko_coin_market_chart_by_ids_'+str(ids[symbol])+'.json'

        if os.path.isfile(file):
            modDate = os.path.getmtime(file)
            with open(file,'r') as f:
                data=json.load(f)
                print ('loading', symbol)
            if dt.datetime.now() - dt.datetime.fromtimestamp(modDate)>dt.timedelta(days=modDays):
                daysOld = (dt.datetime.now()-dt.datetime.fromtimestamp(data['prices'][-1][0]/1000)).days
                newData = cg.get_coin_market_chart_by_id(ids[symbol],'usd',daysOld,interval='daily')
                data = FullMergeDict(data,newData)
                for k, v in data.items(): # remove last item
                    v.pop()
                with open (file,'w') as f:
                    json.dump(data, f)
                    print ('appended file')
        else:
            try:
                print(f"trying {symbol}")
                data = cg.get_coin_market_chart_by_id(ids[symbol],'usd',5000)
                for k,v in data.items():
                    v.pop()
                with open(file, 'w') as f:
                    json.dump(data, f)
                    print ('new file')
            except ValueError:
                print (f"Invalid symbol: {symbol}")
                invalidSymbols['Invalid_Symbols'].append(symbol)
                continue



        df = pd.DataFrame(data['prices'],columns=['Date','Price'])
        df['Symbol']=symbol
        df['Date']=pd.to_datetime(df['Date']*1000000).dt.floor(freq='d')
        dfMktCap = pd.DataFrame(data['market_caps'], columns=['Date','Market_Cap'])
        df['Market_Cap']=dfMktCap['Market_Cap']
        dfTotVol = pd.DataFrame(data['total_volumes'], columns=['Date','Total_Volume'])
        df['Total_Volume'] = dfTotVol['Total_Volume']
        dfMarket=dfMarket.append(df,ignore_index=True)

    print (invalidSymbols)
    print (type(invalidSymbols))

    with open('./data/coingecko-invalid-symbols.json','w') as f:
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
    for i in range(len(data)):
        data[i]['symbol']=data[i]['symbol'].upper()
    with open(file, 'w') as f:
        json.dump(data, f)
#         print ('new file')
    return data   

cg = CoinGeckoAPI()
coinsList = getCoinsList(MODDAYS)
dfCoinsList = pd.DataFrame(coinsList)