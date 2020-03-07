#!/usr/bin/env python3

import numpy as np
import pandas as pd
import pystore

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
                metadata = self._metadata
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

    def __str__(self):
        ''' Returns a user-readable string of this Account. '''
        balance = self.get_balance()
        balance_str = 'Balance = ${} ({})'.format(balance[0],
                                                  balance.index.date[0])
        tracked_from = 'Tracked from ({})'.format(
            self._data.head(1).index.date[0])
        return 'Account({self.name} - {self.number}):\n\t{}\n\t{}'.format(
            self, '\n\t'.join(balance_str, tracked_from),
            '\n\t'.join(key + ' = ' + self._metadata[key]
                    for key in self._metadata if key != self.NUMBER))


class Stock(object):
    ''' '''
    # accessor strings
    DIVIDENDS = 'dividends'
    PURCHASED = 'purchased'
    BROKERAGE = 'brokerage'
    QUANTITY  = 'quantity'
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
        ''' A single purchase of this stock. '''
        def __init__(self, quantity, date, unit_cost=0.0, brokerage=0.0):
            ''' Store the information in a stock purchase. '''
            super().__init__(quantity=quantity, date=date,
                             unit_cost=unit_cost, brokerage=brokerage)
            self.date      = date
            self.quantity  = quantity
            self.unit_cost = unit_cost
            self.brokerage = brokerage

        def get_value(self, brokerage=False):
            value = self.unit_cost * self.quantity
            if brokerage:
                value += self.brokerage
            return value

         def __repr__(self):
            ''' '''
            total = self.quantity * self.unit_cost
            return 'Purchase: ${:.2f} ({}x${:.2f}) + ${} brokerage on {}'\
                    .format(total, self.quantity, self.unit_cost,
                            self.brokerage, self.date)


    def __init__(self, collection, symbol, name=None, purchase_date=None,
                 brokerage=0.0, quantity=None, **metadata):
        ''' '''
        self._collection = collection
        self.symbol
        if symbol not in collection.list_items():
            # stock is new, populate and add user specified metadata
            self._data = self.update_data(symbol, purchase_date)
            self._metadata = metadata
            self._metadata.update({
                self.PURCHASED: [],
                self.DIVIDENDS: [],
                self.BROKERAGE: 0.0,
                self.QUANTITY:  quantity,
                self.NAME:      name,
            })
            self.add_quantity(quantity, brokerage, purchase_date)
        else:
            # existing stock, get stored metadata, ignore inputs
            item = collection.item(symbol)
            self._metadata = item.metadata
            self._data = item.to_pandas()

    @property
    def name(self):
        return self._metadata[self.NAME]

    @property
    def quantity(self):
        return self._metadata[self.QUANTITY]

    @property
    def brokerage(self):
        return self._metadata[self.BROKERAGE]

    def get_purchase_history(self):
        return [self.Purchase(**kwargs) \
                for kwargs in self._metadata[self.PURCHASED]]

    @property
    def get_dividend_history(self):
        return [self.Dividend(**kwargs) \
                for kwargs in self._metadata[self.DIVIDENDS]]

    def add_dividend(self, type_, amount, date, balance=0.0):
        ''' '''
        dividend = self.Dividend(type_, amount, date, balance)
        self._metadata[self.DIVIDENDS].append(dividend)
        if type_ == dividend.REINVESTMENT:
            self._metadata[self.QUANTITY] += dividend.amount
        self.save()

    def add_quantity(self, quantity, date, unit_cost=0.0, brokerage=0.0):
        ''' '''
        purchase = self.Purchase(quantity, unit_cost, brokerage, date)
        self._metadata[self.QUANTITY]  += quantity
        self._metadata[self.BROKERAGE] += brokerage
        self._metadata[self.PURCHASED].append(purchase)
        self.save()

    def get_value(self, unit=False):
        ''' Returns the latest stored unit/full value of this stock. '''
        unit_val = self._data.tail(1)[0]
        if not unit:
            return unit_val * self._quantity
        return unit_val

    def get_profit(self, stored_balance=True, brokerage=False, relative=False):
        ''' Returns absolute ($) or relative (%) profit for this stock. '''
        value = self.get_value()
        purchases = self.get_purchase_history()
        cost = sum([purchase.get_value(brokerage) for purchase in purchases])

        if stored_balance:
            value += self.get_dividend_history()[-1].balance

        if relative:
            return value / cost - 1
        return value - cost

    def save(self):
        ''' Save the current state of this stock. '''
        self._collection.write(self.symbol, self._data,
                               metadata=self._metadata, overwrite=True)

    def __str__(self):
        ''' '''
        return 'Stock:\n\t' # TODO

class StocksAccount(Account):
    ''' '''
    def __init__(self, store, name=None, number=None, data=None, save=True,
                 **metadata):
        super().__init__(store, name, number, data, save, **metadata)

    def add_stock(self, name, symbol, purchase_date, purchase_price,
                  brokerage):
        ''' '''
        pass

    def get_stock(self, name):
        ''' symbol or name '''
        return self._stocks.get(name, self._stocks[self._names[name]])

    def __str__(self):
        ''' '''
        pass



if __name__ == '__main__':
    print('boop')
