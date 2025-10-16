from decimal import Decimal

class BankAccount:
    def __init__(self, account_number, balance=0.0):
        self.account_number = account_number
        # Convert balance to Decimal for safe money operations
        self.balance = Decimal(balance)

    def deposit(self, amount):
        amount = Decimal(amount)
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        amount = Decimal(amount)
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False


class SavingsAccount(BankAccount):
    def __init__(self, account_number, balance=0.0, interest_rate=0.02):
        super().__init__(account_number, balance)
        self.interest_rate = Decimal(interest_rate)

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest
