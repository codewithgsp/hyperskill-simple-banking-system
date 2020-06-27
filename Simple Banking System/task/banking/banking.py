import random
import sys
import sqlite3
from sqlite3 import Error


class SimpleBankingSystem:

    def __init__(self):
        self.login_menu_options = {1: 'Create an account', 2: 'Log into account', 0: 'Exit'}
        self.iin = '400000'
        self.logged_in_menu_option = {1: 'Balance', 2: 'Logout', 0: 'Exit'}
        self.balance = 0
        self.card_pool = {}
        self.acc_pool = set()
        self.conn = None

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def create_table(self, conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def database_file_name(self):
        return 'card.s3db'

    def sql_create_card_table(self):
        return """CREATE TABLE IF NOT EXISTS card(
                    id INTEGER PRIMARY KEY,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0 
                  );"""

    def display_option(self, options):
        for option in options:
            print('{key}. {value}'.format(key=option, value=options.get(option)))

    def fetch_user_option(self):
        return input()

    def calculate_checksum(self, acc, iin):
        unique_15_digit = list(map(int, iin + acc))
        for i, digit in enumerate(unique_15_digit):
            if (i + 1) % 2 == 1:
                unique_15_digit[i] = (digit * 2) - 9 if digit * 2 > 9 else digit * 2
        return str(10 - (sum(unique_15_digit) % 10)) if sum(unique_15_digit) % 10 != 0 else '0'

    def create_unique_acc_num(self):
        while True:
            acc = str(random.randint(0, 999999999)).zfill(9)
            if acc not in self.acc_pool:
                self.acc_pool.add(acc)
                return acc

    def create_new_card_number(self):
        unique_acc = self.create_unique_acc_num()
        checksum = self.calculate_checksum(unique_acc, self.iin)
        card_number = self.iin + unique_acc + checksum
        if card_number not in self.card_pool:
            self.card_pool[card_number] = str(random.randint(0, 9999)).zfill(4)
            return card_number

    def insert_new_card_details(self, conn, card):
        sql = ''' INSERT INTO card(number, pin)
                  VALUES(?,?);'''
        c = conn.cursor()
        c.execute(sql, card)

    def create_an_account(self):
        print('\nYour card has been created')
        new_card_number = self.create_new_card_number()

        with self.conn:
            card = (new_card_number, self.card_pool.get(new_card_number))
            self.insert_new_card_details(self.conn, card)

        # to display
        print('Your card number:\n{}'.format(new_card_number))
        print('Your card PIN:\n{}'.format(self.card_pool.get(new_card_number)))

    def verify_login_details(self, acc, pin):
        if acc in self.card_pool and pin == self.card_pool.get(acc):
            print('\nYou have successfully logged in!')
            return True
        print('\nWrong card number or PIN!')
        return False

    def show_balance(self):
        return self.balance

    def perform_transactions(self):
        choice = '-1'
        while choice != '2':
            print()
            self.display_option(self.logged_in_menu_option)
            choice = input()
            if choice == '1':
                print('\nBalance: {}'.format(self.show_balance()))
            if choice == '0':
                sys.exit(0)
        else:
            print('\nYou have successfully logged out!')

    def log_into_account(self):
        user_input_acc = input('\nEnter your card number:')
        user_input_pin = input('Enter your PIN:')
        if self.verify_login_details(user_input_acc, user_input_pin):
            self.perform_transactions()

    def main_menu(self):
        # creating a database
        self.conn = self.create_connection(self.database_file_name())
        self.create_table(self.conn, self.sql_create_card_table())

        choice = -1
        while choice != '0':
            print()
            self.display_option(self.login_menu_options)
            choice = input()
            if choice == '1':
                self.create_an_account()
            elif choice == '2':
                self.log_into_account()
        else:
            print('\nBye!')


simple_banking_system = SimpleBankingSystem()
simple_banking_system.main_menu()
