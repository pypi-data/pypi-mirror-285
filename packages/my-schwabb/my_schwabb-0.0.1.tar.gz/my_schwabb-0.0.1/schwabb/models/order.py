from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from ..utils import camel_to_snake, parse_date
from ..enums import *

def binary_search(objects, target_id):
    # Extract ids from objects for the purpose of using bisect
    ids = [obj.order_id for obj in objects]
    index = bisect_left(ids, target_id)
    if index < len(objects) and objects[index].order_id == target_id:
        return objects[index]
    return None

class Order:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, camel_to_snake(key), value)

    def __repr__(self):
        return f"<Order: {self.order_id}>"

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)

    @classmethod
    def new(cls, symbol, *, qty, side, price=None, **kwargs):
        instrument = Instrument.new(
            symbol=symbol,
            asset_type=AssetType(kwargs.get('asset_type', 'equity')).name
        )

        order_leg_collection = [
            dict(
                instruction=Instruction(side).name,
                quantity=float(qty),
                instrument=instrument,
                quantityType=QuantityType(kwargs.get('quantity_type', 'shares')).name,
                divCapGains=DivCapGains(kwargs.get('div_cap_gains', 'payout')).name,
            )
        ]

        order = dict(
            session=Session(kwargs.get('session', 'normal')).name,
            duration=Duration(kwargs.get('duration', 'day')).name,
            orderType=OrderType(kwargs.get('order_type', 'limit')).name,
            orderStrategyType=OrderStrategyType(kwargs.get('order_strategy_type', 'single')).name,
            orderLegCollection=order_leg_collection,
        )

        if price is not None:
            order['price'] = float(price)

        if (value := kwargs.get('special_instruction', None)) is not None:
            order['specialInstruction'] = SpecialInstruction(value).name

        # Stop Limit Parameters
        # Stop price
        if (value := kwargs.get('stop_price')) is not None:
            order['stopPrice'] = float(value)

        # Stop Type
        if (value := kwargs.get('stop_type')) is not None:
            order['stopType'] = StopType(value).name


        # Stop Price Link Type
        if (value := kwargs.get('stop_price_link_type')) is not None:
            order['stopPriceLinkType'] = StopPriceLinkType(value).name

        # Stop Price Link Basis
        if (value := kwargs.get('stop_price_link_basis')) is not None:
            order['stopPriceLinkBasis'] = StopPriceLinkBasis(value).name

        # Price Link Type
        if (value := kwargs.get('price_link_type')) is not None:
            order['priceLinkType'] = PriceLinkType(value).name

        # Price Link Basis
        if (value := kwargs.get('price_link_basis')) is not None:
            order['priceLinkBasis'] = PriceLinkBasis(value).name

        # Activation Price
        if (value := kwargs.get('activation_price', None)) is not None:
            order['activation_price'] = float(value)

        return order


@dataclass(slots=True)
class Orders:
    _data: list[Order]

    def __post_init__(self):
        self._data.sort(key=lambda x: x.order_id)

    def __repr__(self):
        return f"<Orders: {len(self._data)} orders>"

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __add__(self, other):
        if not isinstance(other, (Order, Orders)):
            raise ValueError(f"Cannot add object of type {type(other)} to Orders")

        if isinstance(other, Orders):
            other = other._data

        self._data = sorted(set(self._data + other), key=lambda x: x.order_id)

        return self

    def __iadd__(self, other):
        if not isinstance(other, (Order, Orders)):
            raise ValueError(f"Cannot add object of type {type(other)} to Orders")

        if isinstance(other, Orders):
            other = other._data

        self._data = sorted(set(self._data), key=lambda x: x.order_id)

        return self

    def __getitem__(self, key):
        if isinstance(key, int) and key < len(self._data):
            return self._data[key]
        elif isinstance(key, int) and key > len(self._data):
            return self.find(key)
        elif isinstance(key, slice):
            return self._data[key]
        else:
            return self.filter(*key)

    def __setitem__(self, key, value):
        if not isinstance(value, Order):
            raise ValueError(f"Cannot add object of type {type(value)} to Orders")
        self._data = sorted(set(self._data + [value]), key=lambda x: x.order_id)

    @property
    def orders(self):
        return self._data

    def add(self, order):
        if not isinstance(order, Order):
            raise ValueError(f"Cannot add object of type {type(order)} to Orders")
        self._data = sorted(set(self._data + [order]), key=lambda x: x.order_id)

    def filter(self, key, value):
        return Orders([order for order in self._data if hasattr(order, key) and getattr(order, key) == value])

    def filter_iter(self, key, value):
        return (order for order in self._data if hasattr(order, key) and getattr(order, key) == value)

    def filter_date(self, from_date=None, to_date=None, how='open'):
        if (from_date := parse_date(from_date)) is None:
            from_date = datetime.now() - timedelta(days=365)
            from_date = parse_date(from_date.isoformat())

        if (to_date := parse_date(to_date)) is None:
            to_date = parse_date(datetime.now().isoformat())

        attr = 'entered_time' if how == 'open' else 'close_time'

        return Orders([order for order in self._data if from_date <= parse_date(getattr(order, attr).rstrip('+00:00')) <= to_date])

    def find(self, order_id: int):
        return binary_search(self._data, order_id)

    def get_order(self, order_id: int):
        return binary_search(self._data, order_id)

    def to_list(self):
        return self._data

    def tolist(self):
        return self._data

    def to_dataframe(self):
        from polars import DataFrame
        pass