#!/usr/bin/env python3

'''
Pystore.path
-> users (stores)
    -> accounts (collections)
        -> transactions/stocks (items)
'''

import pystore
import requests
import numpy as np
import pandas as pd
url_query = lambda url, *a, **kw: requests.get('https://www.'+url, *a, **kw)

class Account(object):
    ''' An account for tracking one (or more) values over time. '''
    # define accessor strings for stored data
    DATE         = 'date'
    DEBIT        = 'debit'
    CREDIT       = 'credit'
    NUMBER       = 'number'
    BALANCE      = 'balance'
    ACCOUNT_NO   = 'account_no'
    DESCRIPTION  = 'description'
    TRANSACTIONS = 'transactions'

    def __init__(self, store, name=None, number=None, data=None, save=True,
                 **metadata):
        ''' Initialise an account with the specified parameters.

        If the account is already stored in store (by name or number),
        populates the account with available metadata.

        Successful initialisation must include at least a name or number
        currently stored in store, or both name and number if not currently
        tracked.

        Constructor: Account(pystore.store, *str, *int, *pd.DataFrame, *bool,
                             **metadata)

        '''
        new_account = False
        if name and not number:
            # attempt to extract metadata from known collection 'name'
            self._metadata = (store.collection(name)
                                   .item(self.TRANSACTIONS)
                                   .metadata)
            self.number = self._metadata[self.NUMBER]
            self.name = name
        elif number and not name:
            # attempt to find which store has the specified number
            found = False
            for name in store.list_collections():
                self._metadata = (store.collection(name)
                                       .item(self.TRANSACTIONS)
                                       .metadata)
                if number == self._metadata[self.NUMBER]:
                    self.name = name
                    self.number = number
                    found = True
                    break
            if not found:
                raise Exception('No existing accounts with number {}'
                                .format(number))
        elif name and number:
            # assume new account
            self.name = name
            self.number = number
            # ensure number included in metadata
            metadata.update({self.NUMBER: number})
            self._data = data
            new_account = True
        else:
            raise Exception('Accounts must be initialised with at least a name'
                            ' or number.')

        # account successfully found, get data/make a collection for it
        self._collection = store.collection(self.name)
        self._metadata.update(metadata)
        if not new_account:
            self._data = self._collection.item(self.TRANSACTIONS).to_pandas()
        if save:
            self.save()

    def add_data(self, new_data, item=None):
        ''' Add data to the current data-store.

        'new_data' must have the same column format as the existing data.

        If 'item' is left as None, defaults to the transactions item, else
            updates the specified item in this account.

        self.add_data(pd.DataFrame, *None/str) -> None

        '''
        if not item:
            item = self.TRANSACTIONS
        self._collection.append(item, new_data)

    def overwrite_data(self, new_data, metadata=None, item=None):
        ''' Overwrite the data, and optionally metadata of an item.

        'new_data' must have the same column format as the existing data.

        'item' specifies the item being overwritten.
            If left as None, defaults to the transactions item, else overwrites
                the specified item in this account.

        'metadata' specifies the metadata to save with the given item.
            If left as None and 'item' is None, uses the current transactions
                metadata.
            If left as None and 'item' is not None, does not specify metadata
                for the item being written.

        self.overwrite_data(pd.DataFrame, *None/dict, *None/str) -> None

        '''
        if not item:
            item = self.TRANSACTIONS
            # update internal variables as relevant
            self._data = new_data
            if metadata:
                self._metadata = metadata
            else:
                metadata = self._metadata # TODO why is this here?
            self.save()
        else:
            if not metadata:
                self._collection.write(item, new_data, overwrite=True)
            else:
                self._collection.write(item, new_data, metadata=metadata,
                                       overwrite=True)

    def get_balance(self, date='latest'):
        ''' '''
        return self._data.tail(1)[self.BALANCE]

    def save(self):
        ''' Save the account with updated data and/or metadata. '''
        self._collection.write(self.TRANSACTIONS, self._data,
                               metadata=self._metadata, overwrite=True)

    def plot(self):
        ''' '''
        import matplotlib.pyplot as plt
        plt.plot(self._data.index, self._data['balance'])
        plt.show()

    def __str__(self):
        ''' Returns a user-readable string of this Account. '''
        balance = self.get_balance()
        balance_str = 'Balance = ${} ({})'.format(balance[0],
                                                  balance.index.date[0])
        tracked_from = 'Tracked from {}'.format(
            self._data.head(1).index.date[0])
        return 'Account({} - {}):\n\t{}\n\t{}'.format(
            self.name, self.number, '\n\t'.join((balance_str, tracked_from)),
            '\n\t'.join([key + ' = ' + value \
                         for (key, value) in self._metadata.items()
                         if key != self.NUMBER]))


class Stock(object):
    ''' '''
    # accessor strings
    DIVIDENDS = 'dividends'
    PURCHASES = 'purchases'
    BROKERAGE = 'total_brokerage'
    QUANTITY  = 'owned_quantity'
    NAME      = 'name'

    # internal classes for convenience of presentation of metadata
    class Dividend(dict):
        ''' A single dividend installment. '''
        # stock dividend types
        DEPOSIT      = 'deposit'
        REINVESTMENT = 'reinvestment'

        def __init__(self, type_, amount, date, balance=0.0):
            ''' Store a dividend of type_ self.DEPOSIT or self.REINVESTMENT.

            'balance' is available for reinvestments where some balance remains
                uninvested due to being insufficient for a full share.

            '''
            date = str(date)
            super().__init__(type_=type_, amount=amount, date=date,
                             balance=balance)
            self.date    = date
            self.type    = type_
            self.amount  = amount
            self.balance = balance

        def __repr__(self):
            ''' A string representation of this Dividend. '''
            ret_val = 'Dividend('
            if self.type == self.DEPOSIT:
                ret_val += str(amount) + ' shares'
            else:
                ret_val += '${:.2f}'.format(amount)
            ret_val += ' ({self.date})'.format(self)
            if balance:
                ret_val += ' + ${self.balance} balance'.format(self)
            return ret_val + ')'

    class Purchase(dict):
        ''' A single purchase/sale of this stock. '''
        def __init__(self, quantity, date, unit_cost, brokerage):
            ''' Store the information in a stock purchase/sale.

            A Sale is a Purchase with a negative quantity.

            '''
            date = str(date)
            super().__init__(quantity=quantity, date=date,
                             unit_cost=unit_cost, brokerage=brokerage)
            self.date      = date
            self.quantity  = quantity
            self.unit_cost = unit_cost
            self.brokerage = brokerage

        def get_cost(self, brokerage=False):
            ''' Returns the total amount paid, optionally with brokerage. '''
            value = self.unit_cost * self.quantity
            if brokerage:
                value += self.brokerage
            return value

        def __repr__(self):
            ''' '''
            quantity = self.quantity
            if quantity < 0:
                quantity *= -1
                type_ = 'Sale'
            else:
                type_ = 'Purchase'

            return '{}: ${:.2f} ({}x${:.2f}) + ${} brokerage on {}'\
                    .format(type_, self.get_cost(), quantity, self.unit_cost,
                            self.brokerage, self.date)

    def __init__(self, collection, symbol, apikey, name='', quantity=None,
                 purchase_date=None, unit_cost=None, brokerage=None,
                 **metadata):
        ''' Tracks a stock. If the stock is not already tracked, records the
            specified purchase information for a new purchase of the stock.

        '''
        # TODO add option to ignore apikey and only display latest saved values
        #   (e.g. for offline usage)
        self._collection = collection
        self.symbol = symbol
        if symbol not in collection.list_items():
            # stock is new, populate and add user specified metadata
            self._data = self.get_data(symbol, np.datetime64(purchase_date),
                                       apikey)
            self._metadata = {
                self.PURCHASES: [],
                self.DIVIDENDS: [],
                self.BROKERAGE: 0.0, # updated in add_quantity call
                self.QUANTITY:  0,
                self.NAME:      name,
            }
            self._metadata.update(metadata)
            purchase_data = (quantity, purchase_date, unit_cost, brokerage)
            if None in purchase_data:
                raise Exception("quantity, purchase_date, unit_cost and "
                                "brokerage must be specified for a purchase")
            self.add_quantity(*purchase_data)
        else:
            # existing stock, get stored metadata, ignore inputs
            item = collection.item(symbol)
            self._metadata = item.metadata

            # update with latest stock values (if appropriate)
            latest_date = item.to_pandas().index[-1]
            if latest_date < np.datetime64('today'):
                collection.append(symbol,
                                  self.get_data(symbol, latest_date, apikey))

            # retrieve updated data
            self._data = collection.item(symbol).to_pandas()

    @property
    def name(self):
        return self._metadata[self.NAME]

    @property
    def quantity(self):
        ''' The current owned quantity of the stock. '''
        return self._metadata[self.QUANTITY] # TODO 'as at date' option

    @property
    def brokerage(self):
        ''' The total brokerage paid for the stock. '''
        return self._metadata[self.BROKERAGE] # TODO function w/ date range

    def get_purchase_history(self):
        return [purchase if isinstance(purchase, self.Purchase) else
                self.Purchase(**purchase) # must be dict of purchase data
                for kwargs in self._metadata[self.PURCHASES]]

    def get_dividend_history(self):
        return [dividend if isinstance(dividend, self.Dividend) else
                self.Dividend(**dividend) # must be dict of dividend data
                for dividend in self._metadata[self.DIVIDENDS]]

    def get_value(self, unit=False):
        ''' Returns the latest stored unit/full value of this stock. '''
        # TODO 'as at date' option
        unit_val = self._data.tail(1)[0]
        if not unit:
            return unit_val * self.quantity
        return unit_val

    def get_profit(self, stored_balance=True, brokerage=False, relative=False):
        ''' Returns absolute ($) or relative (%) profit for this stock.

        Includes dividend shares in valuation, and optionally includes
            brokerage costs, and dividends paid as balance.

        Setting 'relative' to True returns a percentage increase of the
            current valuation over the total costs from all tracked purchases
            of this stock.

        '''
        # TODO add optional start and end dates to calculate profit since
        #   or up to given date, or over specified time bracket
        value = self.get_value()
        purchases = self.get_purchase_history()
        cost = sum([purchase.get_cost(brokerage) for purchase in purchases])

        if stored_balance:
            value += self.get_dividend_history()[-1].balance

        if relative:
            return value / cost - 1
        return value - cost

    def add_dividend(self, type_, amount, date, balance=0.0):
        '''

        'type_' should be one of Stock.Dividend.REINVESTMENT or
            Stock.Dividend.DEPOSIT

        '''
        dividend = self.Dividend(type_, amount, date, balance)
        self._metadata[self.DIVIDENDS].append(dividend)
        if type_ == dividend.REINVESTMENT:
            self._metadata[self.QUANTITY] += dividend.amount
        self.save()

    def add_quantity(self, quantity, date, unit_cost, brokerage):
        ''' '''
        purchase = self.Purchase(quantity, date, unit_cost, brokerage)
        self._metadata[self.QUANTITY]  += quantity
        self._metadata[self.BROKERAGE] += brokerage
        self._metadata[self.PURCHASES].append(purchase)
        self.save()

    def save(self):
        ''' Save the current state of this stock. '''
        self._collection.write(self.symbol, self._data,
                               metadata=self._metadata, overwrite=True)

    def __str__(self):
        ''' '''
        return 'Stock:\n\t' + '\n\t'.join('{}={}'.format(key, value) for
                                          key, value in self._metadata.items())

    def __repr__(self):
        ''' '''
        return str(self)

    @classmethod
    def get_data(cls, symbol, start_date, apikey,
                 function='TIME_SERIES_DAILY', **params):
        ''' Returns close data for 'symbol' stock since 'start_date'.

        Requires an AlphaVantage API key.

        Parameters are as defined by the AlphaVantage API.

        'start_date' should be of datetime64[ns] format.

        '''
        # update parameters
        params.update(dict(symbol=symbol, apikey=apikey, function=function))

        query_minute = np.datetime64('now').tolist().minute

        # If extra functionality is needed, probably best to transfer to using
        #   the open-source alpha_vantage library (pip-installable), but for
        #   now that would just add excess overhead
        with url_query('alphavantage.co/query?', params=params) as query:
            data = query.json()

        # parse and format data
        try:
            data.pop('Meta Data')
        except KeyError:
            error = data.get('Error Message', None)
            if error:

                raise IOError(error)
            else:
                # too many calls for API plan (for free key, >5/min or >500)
                print(data['Note'])
                print('Auto-retrying on new minute.')
                while np.datetime64('now').tolist().minute == query_minute:
                    pass # wait until next minute
                return cls.get_data(symbol, start_date, apikey, function,
                                    **params)

        # only data item remaining, get it and create a DataFrame
        data = pd.DataFrame(list(data.values())[0]).transpose()
        data.index = data.index.astype('datetime64[ns]')

        # check if retrieved data is sufficient
        if data.index[0] > start_date and \
                params.get('outputsize', None) != 'full':
            # doesnt't go far enough back, get more data
            params['outputsize'] = 'full'
            try:
                return cls.get_data(start_date=start_date, **params)
            except IOError as e:
                print(e)

        # only get market close values (removes open, high, low, and volume)
        data = data['4. close'].to_frame(name='Daily Close')
        data.name = symbol
        return data.astype(float)[data.index >= start_date].sort_index()


class StocksAccount(Account):
    ''' '''
    def __init__(self, store, name=None, number=None, data=None, save=True,
                 apikey=None, **metadata):
        super().__init__(store, name, number, data, save, **metadata)
        self.__sqolru = apikey
        self._load_stocks()

    def _load_stocks(self):
        ''' Load existing stocks from the collection. '''
        self._stocks  = dict()
        self._names   = dict()

        # initialise previously stored stocks from storage
        for symbol in self._collection.list_items():
            if symbol == self.TRANSACTIONS: continue
            # otherwise assume to be a valid stock symbol
            stock = Stock(self._collection, symbol, self.__sqolru)
            self._stocks[symbol] = stock
            self._names[stock.name] = symbol

    def add_stock(self, symbol, name, quantity, purchase_date, unit_cost,
                  brokerage, **metadata):
        ''' Add a new stock to the account - must occur as a purchase. '''
        self._stocks[symbol] = Stock(self._collection, symbol, self.__sqolru,
                                     name, quantity, purchase_date, unit_cost,
                                     brokerage, **metadata)
        self._names[name] = symbol

    def delete_stock(self, symbol):
        ''' Delete a stock (permanently) by name/symbol. '''
        stock  = self.get_stock(symbol)
        symbol = stock.symbol
        self._stocks.pop(symbol)
        self._names.pop(stock.name)
        self._collection.delete_item(symbol)

    def add_quantity(symbol, quantity, date, unit_cost, brokerage):
        ''' Make an additional purchase of an existing stock by name/symbol '''
        return self.get_stock(symbol) \
                   .add_quantity(quantity, date, unit_cost, brokerage)

    def add_dividend(symbol, type_, amount, date, balance):
        ''' Add a dividend to an existing stock by name/symbol. '''
        return self.get_stock(symbol) \
                   .add_dividend(type_, amount, date, balance)

    def get_stock(self, name):
        ''' get by symbol or name '''
        stock = self._stocks.get(name, None)
        if not stock:
            stock = self._stocks[self._names[name]]
        return stock

    def __str__(self):
        ''' '''
        return 'Stocks' + super().__str__() + '\n\tStocks:\n\n\t' + \
                '\n\n\n\t'.join('{}\n\t{!s}'.format(symbol, stock) for \
                                symbol, stock in self._stocks.items())


if __name__ == '__main__':
    pystore.set_path('./db')
    store = pystore.store('accounts')
    savings = Account(store, 'savings')
    with open('API_KEY.txt') as magical_key:
        apikey = magical_key.readline()
    stocks = StocksAccount(store, 'stocks', apikey=apikey)
    print(savings)
    print(stocks)

    # TODO ADD DIVIDENDS 
