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
        self.conn = None
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
        self.commit_records()

    def commit_records(self):
        self.conn.commit()

    def get_card_details(self, conn, acc):
        c = conn.cursor()
        c.execute(''' SELECT number
                      FROM card
                      WHERE number = '{acc}' '''.format(acc=acc))
        card_detail = c.fetchone()
        print(card_detail[0])
        if not card_detail:
            return None
        return card_detail[0]

    def get_pin_details(self, conn, number):
        c = conn.cursor()
        c.execute(''' SELECT pin
                      FROM card
                      WHERE number = '{number}' '''.format(number=number))
        pin_detail = c.fetchone()
        print(pin_detail[0])
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

    def credit_balance(self, conn, number, amount):
        c = conn.cursor()
        c.execute(''' UPDATE card
                      SET balance = balance + {amount} 
                      WHERE number = '{number}' '''.format(number=number, amount=amount))
        self.commit_records()

    def debit_balance(self, conn, number, amount):
        c = conn.cursor()
        c.execute(''' UPDATE card
                      SET balance = balance - {amount} 
                      WHERE number = '{number}' '''.format(number=number, amount=amount))
        self.commit_records()

    def close_account(self, conn, number):
        c = conn.cursor()
        c.execute(''' DELETE 
                      FROM card
                      WHERE number = '{number}' '''.format(number=number))
        self.conn.commit()
        print('The account has been closed!')

    def verify_transfer_acc_no(self, transfer_acc_no):

        if transfer_acc_no[-1] != self.calculate_checksum(transfer_acc_no[6:15], transfer_acc_no[:6]):
            print('Probably you made mistake in the card number. Please try again!')
            return False

        card_number = self.verify_login_details_from_db(transfer_acc_no[6:15], transfer_acc_no[:6], 'transfer')
        if card_number is None:
            print('Such a card does not exist.')
            return False

        if card_number == transfer_acc_no:
            print("You can't transfer money to the same account!")
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
                self.debit_balance(self.conn, self.user_input_acc, int(transfer_amount))
                self.credit_balance(self.conn, transfer_acc_no, int(transfer_amount))
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

    def create_unique_pin_num(self):
        return str(random.randint(0, 9999)).zfill(4)

    def create_unique_acc_num(self):
        return str(random.randint(0, 999999999)).zfill(9)

    def create_new_card_number(self):
        while True:
            unique_acc = self.create_unique_acc_num()
            checksum = self.calculate_checksum(unique_acc, self.iin)
            card_number = self.iin + unique_acc + checksum
            # check in db
            check_number_db = self.get_card_details(self.conn, card_number)
            if check_number_db is None:
                return card_number, self.create_unique_pin_num()

    def create_an_account(self):
        print('\nYour card has been created')
        new_card_number, new_card_pin = self.create_new_card_number()

        with self.conn:
            self.insert_new_card_details(self.conn, new_card_number, new_card_pin)

        # to display
        print('Your card number:\n{}'.format(new_card_number))
        print('Your card PIN:\n{}'.format(new_card_pin))

    def verify_login_details_from_db(self, acc_number, iin, transaction_type):

        checksum = self.calculate_checksum(acc_number, iin)
        number = iin + acc_number + checksum
        # from db
        card_number = self.get_card_details(self.conn, number)
        card_pin = self.get_pin_details(self.conn, number)

        if transaction_type == 'login':
            return card_number, card_pin
        return card_number

    def verify_login_details(self, number, pin):
        acc_number = number[6:15]
        iin = number[:6]
        card_number, card_pin = self.verify_login_details_from_db(acc_number, iin, 'login')
        if number == card_number and pin == card_pin:
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
                amount = self.fetch_user_option('\nEnter income:')
                self.credit_balance(self.conn, self.user_input_acc, int(amount))
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
