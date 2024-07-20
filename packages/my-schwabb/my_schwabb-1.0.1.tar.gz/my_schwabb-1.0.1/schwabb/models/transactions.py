# Standard library imports
from dataclasses import dataclass
from datetime import date, datetime, timedelta

# Relative imports
from .meta import Mapping
from ..utils import dict_to_snake, parse_date
from ..enums import *

_FIELDS = {
    'account_number',
    'activity_id',
    'position_id',
    'order_id',
    'type',
    'net_amount',
    'time',
    'status',
    'sub_account',
    'trade_date',
    'symbol',
    'fee',
    'value',
    'quantity',
    'position_effect',
    'price'
}

@dataclass(slots=True, kw_only=True, repr=False)
class Transaction(Mapping):
    account_number: int
    transfer_items: list[dict]
    activity_id: int = None
    position_id: int = None
    order_id: int = None
    type: str = None
    net_amount: float = None
    time: datetime
    status: str = None
    sub_account: str = None
    trade_date: datetime = None
    symbol: str = None
    fee: float = None
    value: float = None
    quantity: float = None
    position_effect: str = None
    price: float = None

    def __post_init__(self):
        self.account_number = int(self.account_number)
        self.symbol = self.transfer_items[-1]['instrument']['symbol']

        fee = 0
        for item in self.transfer_items[:-1]:
            fee += item['amount']
        self.fee = round(fee, 2)

        self.quantity = self.transfer_items[-1]['amount']
        self.value = abs(self.transfer_items[-1]['cost'])
        self.price = self.transfer_items[-1]['price']
        self.position_effect = self.transfer_items[-1]['position_effect']
        del self.transfer_items

    def __repr__(self):
        fields = sorted(self.__dataclass_fields__.keys())
        fields.remove('transfer_items')

        values = [f"{name}={getattr(self, name)}" for name in fields]

        return f"Transaction({', '.join(values)})"

@dataclass(slots=True, repr=False)
class Transactions:
    _data: list[Transaction]

    @property
    def transactions(self):
        return self._data

    def __post_init__(self):
        self._data = sorted([self._build_transaction(transaction) for transaction in self._data], key=lambda x: x.trade_date)

    def __repr__(self):
        return f"<Transactions: {len(self._data)} transactions>"

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, value):
        if isinstance(value, Transaction):
            return value in self._data
        try:
            value = Transaction(**dict_to_snake(value))
        except TypeError:
            return False
        return value in self._data

    def __getitem__(self, value):
        if isinstance(value, int):
            return self._data[value]

    def _build_transaction(cls, transaction):
        if isinstance(transaction, Transaction):
            return transaction
        return Transaction(**dict_to_snake(transaction))

    def filter(self, value, by='trade_date'):
        if by not in _FIELDS:
            raise ValueError(f"'{by}' is not a valid field. Valid fields are: {_FIELDS}")
        return Transactions([transaction for transaction in self._data if getattr(transaction, by) == value])

    # TODO: Fix from_date and to_date
    def filter_by_date(self, from_date=None, to_date=None) -> "Transactions":
        date = parse_date(date)
        return Transactions([transaction for transaction in self._data if transaction.trade_date == date])

    def filter_by_symbol(self, symbol) -> "Transactions":
        return Transactions([transaction for transaction in self._data if transaction.symbol == symbol])
