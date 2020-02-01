#!/usr/bin/env python3

class Account(object):
    ''' '''
    def __init__(number, name, find_str):
        ''' '''
        pass

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
