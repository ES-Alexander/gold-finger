#!/usr/bin/env python3
import datetime

class Account(object):
    '''A class for bank accounts.'''
    def __init__(self, number, name, find_str, current_bal=0):
        ''' A bank account instance that is findable in data.
        
            Number is the account number, which must be either an intiger 
            or a string. Name is the reference name of the account (e.g. 
            'spending'), as a string. Find_str is the unique string that 
            appears in the data file identifying this account. Current_bal 
            is the current balance in dollars, set to zero by default.
            
            Constructor: Account(int/str, str, str, float) --> Account
        '''

        self.num = str(number)
        self.name = name
        self.finder = find_str
        self.balance = current_bal
        self.balance_hist = []
        self.time_hist = []

    def change_balance(self, change, date):
        ''' Modify the balance of the account by the amount given.

            Change is the value of the debit or credit, negative for 
            debits, given as a float. Date is the date and/or time of 
            the transaction, given as a datetime instance.

            Account.change_bal(float, datetime) --> None
        '''

        self.balance += change
        self.balance_hist.append(self.balance)
        self.time_hist.append(date)


class Transaction(object):
    ''' '''
    def __init__(sender, receiver, date, amount, reason=None, tags=None):
        ''' '''
        pass
