#!/usr/bin/env python3

import numpy as np
import pandas as pd
import pystore

DATE        = 'date'
DEBIT       = 'debit'
CREDIT      = 'credit'
BALANCE     = 'balance'
ACCOUNT_NO  = 'account_no'
DESCRIPTION = 'description'

# rename data columns with desired names (map provided by user?)
name_map = {
    'Date'          : DATE,
    'Debit Amount'  : DEBIT,
    'Credit Amount' : CREDIT,
    'Balance'       : BALANCE,
    'Bank Account'  : ACCOUNT_NO,
    'Narrative'     : DESCRIPTION,
}

def update_store(filename='Data.csv', name_map=name_map, path='./db',
                 date_format='%d/%m/%Y', overwrite=False):
    pystore.set_path(path)
    accounts_store = pystore.store('accounts')
    with open('accounts.txt') as accounts:
        account_map = dict()
        for account in accounts:
            name, number = account.split(' ')
            account_map[name] = int(number)

    # read in new data
    data = pd.read_csv(filename)
    # rename columns to match internal representation
    data.rename(columns=name_map, inplace=True)
    columns = name_map.values()

    # change data strings into efficient numerical format
    data.loc[:, DATE] = pd.to_datetime(data.loc[:, DATE], format=date_format)
    data = data.loc[:, [*columns]] # use only desired columns
    data.fillna(0, inplace=True) # fill any NaN/blank values with 0
    # remove the debit column, if there is one
    if DEBIT in columns:
        # merge the debit column into the credit column and remove
        data.loc[:, CREDIT] -= data.loc[:, DEBIT]
        data.drop(columns=DEBIT, inplace=True)

    # finish processing and save data into separate accounts
    for name, number in account_map.items():
        # add as a collection if not already present, assign for convenience
        collection = accounts_store.collection(name)
        if not overwrite:
            if 'transactions' in collection.list_items():
                write = collection.append
            else:
                write = collection.write
        else:
            write = lambda *args, **kw : collection.write(*args, **kw,
                                                          overwrite=overwrite)
        if 'transactions' in collection.list_items():
            metadata = collection.item('transactions').metadata
        else:
            metadata = dict()
        metadata.update(number=number)
        # can we somehow mark the index as pre-sorted??
        write('transactions', data[data[ACCOUNT_NO] == account_map[name]]
                              .drop(columns=ACCOUNT_NO)
                              .set_index(DATE), metadata=metadata,
        )

    return accounts_store


if __name__ == '__main__':
    updating = False

    import matplotlib.pyplot as plt

    def plot_account(account, show=True):
        plt.plot(account.index, account['balance'])
        if show:
            plt.show()

    if updating:
        accounts_store = update_store(overwrite=True)
    else:
        pystore.set_path('./db')
        accounts_store = pystore.store('accounts')
    print('Current Stores:', pystore.list_stores())
    print('Current Accounts:', ', '.join(accounts_store.list_collections()))

    savings = (accounts_store.collection('savings')
                             .item('transactions')
                             .to_pandas())
    stocks = (accounts_store.collection('stocks')
                            .item('transactions')
                            .to_pandas())
    if updating:
        print('Savings Account:\n', savings)

    plot_account(savings, False)
    plot_account(stocks)
