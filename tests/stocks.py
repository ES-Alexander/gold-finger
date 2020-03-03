#!/usr/bin/env python3
import json
import urllib.request as www
from sys import stdout

#with www.urlopen('https://www.asx.com.au/asx/1/share/AEF') as site:
#    data = json.load(site)

#json.dump(data, stdout, indent=4)

def alpha_vantage(apikey=open('API_KEY.txt').readline(),
                  function='TIME_SERIES_DAILY', **kwargs):
    kwargs['apikey'] = apikey
    kwargs['function'] = function
    with www.urlopen('https://www.alphavantage.co/query?' + \
                     '&'.join(str(key) + '=' + str(kwargs[key]) \
                              for key in kwargs)) as query:
        return json.load(query)

if __name__ == '__main__':
    #json.dump(alpha_vantage(symbol='AEF.AX'), stdout, indent=4)
    #json.dump(alpha_vantage(symbol='ASX:RBTZ'), stdout, indent=4)
    json.dump(alpha_vantage(symbol='ASX:GBND'), stdout, indent=4)
