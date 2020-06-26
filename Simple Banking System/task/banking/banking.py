import random
import sys


class SimpleBankingSystem:

    def __init__(self):
        self.login_menu_options = {1: 'Create an account', 2: 'Log into account', 0: 'Exit'}
        self.iin = 400000
        self.logged_in_menu_option = {1: 'Balance', 2: 'Logout', 0: 'Exit'}
        self.balance = 0
        self.card_pool = {}

    def display_option(self, options):
        for option in options:
            print('{key}. {value}'.format(key=option, value=options.get(option)))

    def fetch_user_option(self):
        return input()

    def create_new_card_number(self):
        while True:
            acc = str(random.randint(0, 999999999)).zfill(9)
            checksum = random.randint(0, 9)
            card_number = str(self.iin) + acc + str(checksum)
            if card_number not in self.card_pool:
                self.card_pool[card_number] = str(random.randint(0, 9999)).zfill(4)
                return card_number

    def create_an_account(self):
        print('\nYour card has been created')
        new_card_number = self.create_new_card_number()
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