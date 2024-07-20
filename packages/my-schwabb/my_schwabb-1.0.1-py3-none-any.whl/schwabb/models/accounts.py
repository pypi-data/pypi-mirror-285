from dataclasses import dataclass

# Relative imports
from .meta import Mapping

@dataclass(slots=True)
class Account(Mapping):
    number: int
    hash: str

    def __post_init__(self):
        self.number = int(self.number)

    def __str__(self):
        return self.hash

@dataclass(slots=True, repr=False)
class Accounts:
    data: tuple[Account]
    primary: int = None

    def __post_init__(self):
        self.data = tuple(account if isinstance(account, Account) else Account(account['accountNumber'], account['hashValue']) for account in self.data)
        if len(self.data) == 1:
            self.set_primary(self.data[0].number)

    def __repr__(self):
        value = 'Accounts(\n'
        for account in self.data:
            if len(self.data) == 1 or account.number == self.primary:
                value += f"    *{repr(account)},\n"
            else:
                value += f"    {repr(account)},\n"
        value += ')'
        return value

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]

        key = int(key)
        for account in self.data:
            if key == account.number or key == account.hash:
                return account
        else:
            raise KeyError(f"'{key}' is not a valid account.")

    @property
    def primary_account(self):
        return self.primary

    def get(self, number):
        number = int(number)

        for account in self.data:
            if account.number == number:
                return account

    def set_primary(self, number):
        number = int(number)
        self.primary = self.get(number)