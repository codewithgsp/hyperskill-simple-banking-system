import random
import sys
import sqlite3
from sqlite3 import Error


class SimpleBankingSystem:

    def __init__(self):
        self.login_menu_options = {1: 'Create an account',
                                   2: 'Log into account',
                                   0: 'Exit'}
        self.iin = '400000'
        self.logged_in_menu_option = {1: 'Balance',
                                      2: 'Add income',
                                      3: 'Do transfer',
                                      4: 'Close account',
                                      5: 'Log out',
                                      0: 'Exit'}
        # self.balance = 0
        # self.card_pool = {}
        # self.acc_pool = set()
        self.conn = None
        # self.c = None
        self.user_input_acc = None
        self.user_input_pin = None

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

    def insert_new_card_details(self, conn, number, pin):
        c = conn.cursor()
        c.execute(''' INSERT INTO card(number, pin)
                           VALUES({number}, {pin}) '''.format(number=number, pin=pin))
        # self.commit_records()

    def commit_records(self):
        self.conn.commit()

    def get_card_details(self, conn, acc):
        c = conn.cursor()
        c.execute(''' SELECT substr(number, 7, 9)
                           FROM card
                           WHERE substr(number, 7, 9) = '{acc}' '''.format(acc=acc))
        card_detail = c.fetchone()
        if not card_detail:
            return None
        return card_detail[0]

    def get_pin_details(self, conn, number):
        c = conn.cursor()
        c.execute(''' SELECT pin
                           FROM card
                           WHERE substr(number, 7, 9) = '{number}' '''.format(number=number))
        pin_detail = c.fetchone()
        if not pin_detail:
            return None
        return pin_detail[0]

    def show_balance(self, conn, number):
        c = conn.cursor()
        c.execute(''' SELECT balance
                           FROM card
                           WHERE number = '{number}' '''.format(number=number))
        balance_detail = c.fetchone()
        return balance_detail[0]

    def update_balance(self, conn, number, amount):
        c = conn.cursor()
        c.execute(''' UPDATE card
                           SET balance = {amount} 
                           WHERE number = '{number}' '''.format(number=number, amount=amount))
        self.commit_records()

    def close_account(self, conn, number):
        c = conn.cursor()
        c.execute(''' DELETE FROM card
                           WHERE number = {number} '''.format(number=number))
        self.conn.commit()
        print('The account has been closed!')

    def verify_transfer_acc_no(self, transfer_acc_no):
        card_number, checksum = self.verify_login_details_from_db(transfer_acc_no[6:15], 'transfer')
        if card_number is None:
            print('Such a card does not exist.')
            return False
        elif self.iin + card_number == transfer_acc_no[:15] and checksum != transfer_acc_no[-1]:
            print('Probably you made mistake in the card number. Please try again!')
            return False
        return True

    def perform_transfer(self):
        transfer_acc_no = self.fetch_user_option('Transfer\nEnter card number:')
        if self.verify_transfer_acc_no(transfer_acc_no):
            transfer_amount = self.fetch_user_option('Enter how much money you want to transfer:')
            current_balance = self.show_balance(self.conn, self.user_input_acc)
            if int(transfer_amount) > current_balance:
                print('Not enough money!')
            else:
                self.update_balance(self.conn, self.user_input_acc, current_balance - int(transfer_amount))
                self.update_balance(self.conn, transfer_acc_no, self.show_balance(self.conn, transfer_acc_no)
                                    + int(transfer_amount))
                print('Success!')

    def display_option(self, options):
        for option in options:
            print('{key}. {value}'.format(key=option, value=options.get(option)))

    def fetch_user_option(self, string):
        return input(string)

    def calculate_checksum(self, acc, iin):
        unique_15_digit = list(map(int, iin + acc))
        for i, digit in enumerate(unique_15_digit):
            if (i + 1) % 2 == 1:
                unique_15_digit[i] = (digit * 2) - 9 if digit * 2 > 9 else digit * 2
        return str(10 - (sum(unique_15_digit) % 10)) if sum(unique_15_digit) % 10 != 0 else '0'

    def create_unique_acc_num(self):
        while True:
            acc = str(random.randint(0, 999999999)).zfill(9)
            acc_check_db = self.get_card_details(self.conn, acc)
            if acc_check_db is None:
                return acc

    def create_new_card_number(self):
        unique_acc = self.create_unique_acc_num()
        checksum = self.calculate_checksum(unique_acc, self.iin)
        card_number = self.iin + unique_acc + checksum
        return card_number, str(random.randint(0, 9999)).zfill(4)

    def create_an_account(self):
        print('\nYour card has been created')
        new_card_number, new_card_pin = self.create_new_card_number()

        with self.conn:
            self.insert_new_card_details(self.conn, new_card_number, new_card_pin)

        # to display
        print('Your card number:\n{}'.format(new_card_number))
        print('Your card PIN:\n{}'.format(new_card_pin))

    def verify_login_details_from_db(self, acc_number, transaction_type):
        card_number = self.get_card_details(self.conn, acc_number)
        card_pin = self.get_pin_details(self.conn, acc_number)
        checksum = self.calculate_checksum(acc_number, self.iin)
        if transaction_type == 'login':
            return card_number, card_pin, checksum
        return card_number, checksum

    def verify_login_details(self, number, pin):
        acc_number = number[6:15]
        card_number, card_pin, checksum = self.verify_login_details_from_db(acc_number, 'login')
        if acc_number == card_number and pin == card_pin and checksum == number[-1]:
            print('\nYou have successfully logged in!')
            return True
        print('\nWrong card number or PIN!')
        return False

    def perform_transactions(self):
        choice = '-1'
        while choice != '5':
            print()
            self.display_option(self.logged_in_menu_option)
            choice = self.fetch_user_option('')
            if choice == '1':
                print('\nBalance: {}'.format(self.show_balance(self.conn, self.user_input_acc)))
            elif choice == '2':
                current_balance = self.show_balance(self.conn, self.user_input_acc)
                amount = self.fetch_user_option('\nEnter income:')
                self.update_balance(self.conn, self.user_input_acc, current_balance + int(amount))
                print('Income was added!')
            elif choice == '3':
                self.perform_transfer()
            elif choice == '4':
                self.close_account(self.conn, self.user_input_acc)
                break
            elif choice == '0':
                sys.exit(0)
        else:
            print('\nYou have successfully logged out!')

    def log_into_account(self):
        self.user_input_acc = self.fetch_user_option('\nEnter your card number:')
        self.user_input_pin = self.fetch_user_option('Enter your PIN:')
        if self.verify_login_details(self.user_input_acc, self.user_input_pin):
            self.perform_transactions()

    def main_menu(self):
        # creating a database
        self.conn = self.create_connection(self.database_file_name())
        self.create_table(self.conn, self.sql_create_card_table())

        choice = -1
        while choice != '0':
            print()
            self.display_option(self.login_menu_options)
            choice = self.fetch_user_option('')
            if choice == '1':
                self.create_an_account()
            elif choice == '2':
                self.log_into_account()
        else:
            print('\nBye!')


simple_banking_system = SimpleBankingSystem()
simple_banking_system.main_menu()
