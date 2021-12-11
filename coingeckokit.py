STABLECOINS = ['ousd','usdk','rsv','musd','vai','sbd','dgd','qc','cusd','susd','eurs','usdx','gusd','xsgd','tribe','lusd','frax','husd','fei','rsr','usdn','usdp','tusd','dai','ust','busd','usdc','usdt']

import numpy as np
import pandas as pd

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
coinsList = cg.get_coins_list()
dfCoinsList = pd.DataFrame(coinsList)


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

def getCoinGeckoMarket (symbols, forceLower = True):
    dfMarket = pd.DataFrame()
    ids = getCoinGeckoId(symbols, forceLower)
    for i in range(len(ids)):
        try:
            data = cg.get_coin_market_chart_by_id(ids[i],'usd',5000)
            df = pd.DataFrame(data['prices'],columns=['date','price'])
            df['symbol']=symbols[i]
            df['date']=pd.to_datetime(df['date']*1000000)
            dfMktCap = pd.DataFrame(data['market_caps'], columns=['date','market_cap'])
            df['market_cap']=dfMktCap['market_cap']
            dfTotVol = pd.DataFrame(data['total_volumes'], columns=['date','total_volume'])
            df['total_volume'] = dfTotVol['total_volume']
            dfMarket=dfMarket.append(df,ignore_index=True)
        except ValueError:
            print (f"Invalid symbol: {symbols[i]}")
    return dfMarket

    
    