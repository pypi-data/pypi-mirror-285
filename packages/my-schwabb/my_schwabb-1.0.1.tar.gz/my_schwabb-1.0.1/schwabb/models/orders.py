# Standard library imports
from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, datetime, timedelta

# Third party imports
try:
    import polars as pl
    _has_polars = True
    _order_schema = {
        'symbol': pl.Utf8,
        'order_id': pl.UInt64,
        'account_number': pl.UInt32,
        'status': pl.Utf8,
        'order_type': pl.Utf8,
        'price': pl.Float64,
        'quantity': pl.Float64,
        'filled_quantity': pl.Float64,
        'remaining_quantity': pl.Float64,
        'entered_time': pl.Datetime,
        'close_time': pl.Datetime,
        'duration': pl.Utf8,
        'session': pl.Utf8,
        'tag': pl.Utf8,
    }
except ImportError:
    _has_polars = False


# Relative imports
from .meta import Mapping
from ..utils import binary_search, dict_to_snake, parse_date
from ..enums import *

# def binary_search(objects, target_id):
#     # Extract ids from objects for the purpose of using bisect
#     ids = [obj.order_id for obj in objects]
#     index = bisect_left(ids, target_id)
#     if index < len(objects) and objects[index].order_id == target_id:
#         return objects[index]
#     return None

@dataclass(slots=True, eq=False, kw_only=True)
class Order(Mapping):
    order_id: int
    account_number: int = None
    cancelable: bool = None
    close_time: datetime = None
    complex_order_strategy_type: str = None
    destination_link_name: str = None
    duration: str = None
    editable: bool = None
    entered_time: datetime = None
    filled_quantity: float = None
    order_activity_collection: list = None
    order_leg_collection: list[dict] = None
    order_strategy_type: str = None
    order_type: str = None
    price: float = None
    quantity: float = None
    remaining_quantity: float = None
    requested_destination: str = None
    session: str = None
    status: str = None
    status_description: str = None
    symbol: str = None
    tag: str = None

    def __post_init__(self):
        self.symbol = self.order_leg_collection[0]['instrument']['symbol']

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)

    @classmethod
    def build(cls, symbol, *, qty, side, price=None, **kwargs):
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
    _order_ids: set[int] = None

    @property
    def orders(self):
        return self._data

    def __post_init__(self):
        self._data = sorted((Order(**dict_to_snake(order)) if not isinstance(order, Order) else order for order in self._data), key=lambda x: x.order_id)
        self._order_ids = set(order.order_id for order in self._data)

    def __repr__(self):
        return f"<Orders: {len(self._data)} orders>"

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, value):
        if isinstance(value, Order):
            return value in self._data
        return value in self._order_ids

    def __len__(self):
        return len(self._data)

    def __add__(self, other):
        if not isinstance(other, (Order, Orders)):
            raise ValueError(f"Cannot add object of type {type(other)} to Orders")

        if isinstance(other, Orders):
            other = other._data

        self._data = sorted(set(self._data + other), key=lambda x: x.order_id)
        self._order_ids.add(other.order_id)
        return self

    def __iadd__(self, other):
        try:
            other = Orders(other._data)
        except:
            try:
                other = Order(**dict_to_snake(other))
            except Exception as e:
                print(f"Error creating order: {e}")
                raise ValueError(f"Cannot add object of type {type(other)} to Orders")

        if isinstance(other, Orders):
            other = other._data

        self._data = sorted(set(self._data), key=lambda x: x.order_id)
        self._order_ids.add(other.order_id)
        return self

    def __getitem__(self, key):
        if isinstance(key, int) and key < len(self._data):
            return self._data[key]
        elif isinstance(key, int) and key > len(self._data):
            return self.find(key)
        elif isinstance(key, slice):
            return self._data[key]
        elif isinstance(key, str):
            return tuple(getattr(order, key) for order in self._data if hasattr(order, key))
        else:
            return self.filter(*key)

    def __setitem__(self, key, value):
        try:
            value = Order(**dict_to_snake(value))
        except TypeError:
            raise ValueError(f"Cannot add object of type {type(value)} to Orders")
        self._data = sorted(set(self._data + [value]), key=lambda x: x.order_id)
        self._order_ids.add(value.order_id)

    def add(self, order):
        try:
            order = Order(**dict_to_snake(order))
        except TypeError:
            raise ValueError(f"Cannot add object of type {type(order)} to Orders")
        self._data = sorted(set(self._data + [order]), key=lambda x: x.order_id)
        self._order_ids.add(order.order_id)

    def filter(self, key, value):
        return Orders([order for order in self._data if hasattr(order, key) and getattr(order, key) == value])

    def filter_iter(self, key, value):
        return (order for order in self._data if hasattr(order, key) and getattr(order, key) == value)

    def filter_date(self, from_date=None, to_date=None, how='open'):
        if (from_date := parse_date(from_date)) is None:
            from_date = parse_date(
                (datetime.now() - timedelta(days=365)).isoformat()
            )

        if (to_date := parse_date(to_date)) is None:
            to_date = parse_date(datetime.now().isoformat())

        attr = 'entered_time' if how == 'open' else 'close_time'
        return Orders([order for order in self._data if from_date <= getattr(order, attr) <= to_date])

    def filter_by_date(self, *args, **kwargs):
        return self.filter_date(*args, **kwargs)

    def find(self, order_id: int):
        return binary_search(self._data, order_id, 'order_id')

    def get_order(self, order_id: int):
        return binary_search(self._data, order_id, 'order_id')

    def to_list(self):
        return self._data

    def tolist(self):
        return self._data

    def to_dataframe(self) -> pl.DataFrame:
        if not _has_polars:
            raise ImportError("polars is not installed. Please install it using 'pip install polars'")
        rows = [
            [
                row.symbol,
                row.order_id,
                row.account_number,
                row.status,
                row.order_type,
                row.price,
                row.quantity,
                row.filled_quantity,
                row.remaining_quantity,
                row.entered_time,
                row.close_time,
                row.duration,
                row.session,
                row.tag,
            ]
                for row in self.orders
        ]

        return pl.DataFrame(rows, schema=_order_schema)