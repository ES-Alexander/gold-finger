#!/usr/bin/env python3

import numpy as np
import pandas as pd
import pystore
pystore.set_path('./db') # set the storage location

# initialise (or get) an accounts store, and populate from settings
accounts_store = pystore.store('accounts')
with open('accounts.txt') as accounts:
    account_map = dict()
    for account in accounts:
        name, id_ = account.split(' ')
        account_map[name] = int(id_)
        accounts_store.delete_collection(name) # remove for this test
        accounts_store.collection(name)

# read in some data
data = pd.read_csv('Data.csv')

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
data.rename(columns=name_map, inplace=True)

# change date strings into efficient numerical format
data.loc[:, DATE] = pd.to_datetime(data.loc[:, DATE])
data = data.loc[:, [*name_map.values()]] # use only the desired columns
data.fillna(0, inplace=True) # fill any NaN/blank values with 0
# remove the debit column, if there is one
if DEBIT in name_map.values():
    # merge the debit column into the credit column and remove
    data.loc[:,CREDIT] -= data.loc[:,DEBIT]
    data.drop(columns=DEBIT, inplace=True)

# finish processing and save data into separate accounts
for name in account_map:
    # can we somehow mark the index as pre-sorted??
    accounts_store.collection(name).write('transactions',
            data[data[ACCOUNT_NO] == account_map[name]]
            .drop(columns=ACCOUNT_NO)
            .set_index(DATE)
    )

print('Current Stores:', pystore.list_stores())
print('Current Accounts:', ', '.join(accounts_store.list_collections()))

savings = accounts_store.collection('savings').item('transactions').to_pandas()
print('Savings Account:\n', savings)
