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
    def __init__(self, sender, receiver, date, amount, reason=None, tags=None,
                 unit='$'):
        ''' A Transaction instance.

        'sender' and 'receiver' should be Account instances or a string for
            un-tracked accounts
        'date' should be a datetime.date or datetime.datetime instance
            representing the time of the Transaction.
        'amount' should be the Transaction amount in the 'unit' specified.
        'reason' is an optional string reason for the transaction.
        'tags' is an optional list of string tags for the transaction.
        'unit' is a string representing the amount unit (default $).

        Constructor:
            Transaction(Account, Account, date, float, *str, *list[str])

        '''
        self.sender = sender
        self.receiver = receiver
        self.date = date
        self.amount = amount
        self.reason = reason
        self.tags = tags

        self.perform_transaction()

    def perform_transaction(self):
        ''' '''
        try:
            self.sender.change_balance(-self.amount, self.date)
        except: pass
        try:
            self.receiver.change_balance(self.amount, self.date)
        except: pass

    def __str__(self):
        ''' A human-readable string representation of this Transaction. '''
        print('Transaction:\n\t {!s}{!s} from {!s} to {!s} on {!s}'.format(
            self.unit, self.amount, self.sender, self.receiver))
        if reason:
            print('Reason: "{!s}"'.format(reason))
        if tags:
            print('Tags: {!s}'.format(', '.format(tags)))

    def __repr__(self):
        ''' A formal representation of this Transaction. '''
        print('Transaction(sender={!r}, receiver={!r}, date={!r}, amount={!r},'
              'reason={!r}, tags={!r}, unit={!r})'.format(
                  self.sender, self.receiver, self.date, self.amount,
                  self.reason, self.tags, self.unit))
