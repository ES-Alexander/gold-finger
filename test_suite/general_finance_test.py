#!/usr/bin/env python3

from testrun.TestRun import TestRun, TestGroup, Redirect
import sys
sys.path.append('..')
from general_finance import *
from datetime import date

class AccountTests(TestRun):
    ''' A test-suite for the Account class. '''
    def __init__(self):
        ''' Create the test suite with relevant variables. '''
        super().__init__()
        self.number = 0
        self.name = 'test'
        self.finder = 'test_find'
        self.balance = 500
        self.balance_history = []
        self.time_history = []
        self.props = ['number', 'name', 'finder', 'balance']

    def property_test(self, props, obj):
        ''' Test the specified properties (props) of obj against self. '''
        for prop in props:
            assert obj.__dict__[prop] == self.__dict__[prop], \
                    'Account {!s} {!r} does not match input {!r}'.format(
                        prop, obj.__dict__[prop], self.__dict__[prop])

    def test_init_default(self):
        ''' Test an Account with the default balance. '''
        test_account = Account(self.number, self.name, self.finder)
        self.property_test(self.props[:-1], test_account)

    def test_init_balance(self):
        ''' Test an Account with a specified balance. '''
        test_account = Account(self.number, self.name, self.finder,
                               self.balance)
        self.property_test(self.props, test_account)

    def test_change_balance(self):
        ''' Test the change_balance method. '''
        test_account = Account(self.number, self.name, self.finder,
                               self.balance)
        old_balance = self.balance
        old_balance_history = list(self.balance_history)
        old_time_history = list(self.time_history)

        try:
            for amount, day in zip([10, 20, -30], [date(2000,1,10),
                                   date(2000,1,10), date(2020,1,20)]):
                test_account.change_balance(amount, day)
                self.balance += amount
                self.balance_history.append(self.balance)
                self.time_history.append(day)
                self.property_test(['balance', 'balance_history',
                                    'time_history'], test_account)
        finally: # ensure values are restored
            self.balance = old_balance
            self.balance_history = old_balance_history
            self.time_history = old_time_history

class TransactionTests(TestRun):
    ''' A test-suite for the Transaction class. '''
    pass

if __name__ == '__main__':
    account_tests = AccountTests()
    transaction_tests = TransactionTests()
    tests = TestGroup(account_tests, transaction_tests)
    tests.run_tests()
