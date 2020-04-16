#!/usr/bin/env python3
#import json
from sys import stdout
import pandas as pd
import requests
www = lambda url, *a, **kw: requests.get('https://www.'+url, *a, **kw)

#with www.urlopen('https://www.asx.com.au/asx/1/share/AEF') as site:
#    data = json.load(site)

#json.dump(data, stdout, indent=4)

def alpha_vantage(apikey=open('API_KEY.txt').readline(),
                  function='TIME_SERIES_DAILY', **params):
    params.update(dict(apikey=apikey, function=function))
    with www('alphavantage.co/query?', params=params) as query:
        data = query.json()
        print(query.url)

    try:
        data.pop('Meta Data')
    except KeyError:
        raise Exception(data['Error Message'])

    # only data item remaining, get it and create a DataFrame
    #  -> only get the close of business value 
    #       (removes 1. open, 2. high, 3. low, 5. volume)
    data = pd.DataFrame(list(data.values())[0]).transpose()['4. close']
    data.index = data.index.astype('datetime64[ns]')
    data.name = params['symbol']
    return data.astype(float)

if __name__ == '__main__':
    #json.dump(alpha_vantage(symbol='AEF.AX'), stdout, indent=4)
    #json.dump(alpha_vantage(symbol='ASX:RBTZ'), stdout, indent=4)
    #json.dump(alpha_vantage(symbol='ASX:GBND'), stdout, indent=4)
    data = alpha_vantage(symbol='ASX:AEF', outputsize='full')
    print(data)
