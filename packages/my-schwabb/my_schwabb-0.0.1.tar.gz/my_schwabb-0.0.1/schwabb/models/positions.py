from dataclasses import dataclass, field
from ..enums import *
from ..utils import camel_to_snake
from .meta import Indexable


@dataclass(slots=True)
class Positions:
    _data: list

    def __post_init__(self):
        self._data = [self._build_position(position) for position in self._data]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[key]
        elif isinstance(key, str):
            key = key.upper()
            for position in self._data:
                if position.symbol == key:
                    return position
            else:
                raise KeyError(f"'{key}' was not found")
        else:
            raise KeyError('Key must be integer or symbol string')

    def __iter__(self):
        return iter(self._data)

    def _build_position(self, position):
        return Position(
            average_price=position.get('averagePrice'),
            average_long_price=position.get('averageLongPrice'),
            average_short_price=position.get('averageShortPrice'),
            current_day_cost=position.get('currentDayCost'),
            current_day_profit_loss=position.get('currentDayProfitLoss'),
            current_day_profit_loss_percentage=position.get('currentDayProfitLossPercentage'),
            instrument=position.get('instrument'),
            long_open_profit_loss=position.get('longOpenProfitLoss'),
            long_quantity=position.get('longQuantity'),
            maintenance_requirement=position.get('maintenaceRequirement'),
            market_value=position.get('marketValue'),
            previous_session_long_quantity=position.get('previousSessionLongQuantity'),
            previous_session_short_quantity=position.get('previousSessionShortQuantity'),
            settled_long_quantity=position.get('settledLongQuantity'),
            settled_short_quantity=position.get('settledShortQuantity'),
            short_open_profit_loss=position.get('shortOpenProfitLoss'),
            short_quantity=position.get('shortQuantity'),
            tax_lot_average_long_price=position.get('taxLotAverageLongPrice'),
            tax_lot_average_short_price=position.get('taxLotAverageShortPrice'),
        )

    @property
    def symbols(self):
        return self.get_symbols()

    def get_symbols(self):
        return tuple(position.symbol for position in self._data)

    def get(self, symbol, default=None):
        symbol = symbol.upper()
        try:
            return self[symbol]
        except KeyError:
            return default


@dataclass(slots=True, repr=False)
class Position(Indexable):
    average_price: float
    average_long_price: float
    average_short_price: float
    current_day_cost: float
    current_day_profit_loss: float
    current_day_profit_loss_percentage: float
    instrument: dict
    long_open_profit_loss: float
    long_quantity: float
    maintenance_requirement: float
    market_value: float
    previous_session_long_quantity: float
    previous_session_short_quantity: float
    settled_long_quantity: float
    settled_short_quantity: float
    short_open_profit_loss: float
    short_quantity: float
    tax_lot_average_long_price: float
    tax_lot_average_short_price: float
    symbol: str = None
    _data: tuple = field(default_factory=tuple)

    def __post_init__(self):
        self.symbol = self.instrument['symbol']
        self._data = tuple(getattr(self, name) for name in self.__dataclass_fields__.keys() if not name.startswith('_'))

    def __repr__(self):
        value = f"{self.symbol}(\n"
        values = [
            f"    {name}: {getattr(self, name)},\n"
            for name in self.__dataclass_fields__.keys()
            if name != 'symbol'
        ]
        values.insert(0, value)
        values.append(')')
        return ''.join(values)

    def __str__(self):
        return self.symbol

class Quotes:
    pass

@dataclass(slots=True)
class QuoteData(Indexable):
    asset_main_type: str
    quote_type: str
    realtime: bool
    ssid: int
    symbol: str
    quote: dict
    fundamental: dict = None
    reference: dict = None
    regular: dict = None
    asset_sub_type: str = None


    def __post_init__(self):
        self.symbol = self.symbol.upper()
        self.quote = self._build_quote()

    def __repr__(self):
        value = f"{self.symbol}(\n"
        values = [
            f"    {name}: {getattr(self, name)},\n"
            for name in self.__dataclass_fields__.keys()
            if name != 'symbol'
        ]
        values.insert(0, value)
        values.append(')')
        return ''.join(values)

    def __str__(self):
        return self.symbol

    def _build_quote(self):
        return Quote(
            hard_to_borrow=self.reference.get('isHardToBorrow', None),
            shortable=self.reference.get('isShortable', None),
            exchange=self.reference.get('exchange', None),
            **self.quote
        )

    @classmethod
    def new(cls, symbol, data):
        quote = {camel_to_snake(key): value for key, value in data.items()}
        quote['quote'] = {camel_to_snake(key): value for key, value in quote['quote'].items()}
        quote['quote']['year_high'] = quote['quote'].pop('52_week_high')
        quote['quote']['year_low'] = quote['quote'].pop('52_week_low')
        return cls(**quote)

@dataclass(slots=True)
class Quote(Indexable):
    year_high: float
    year_low: float
    ask_price: float
    ask_size: int
    ask_time: int
    bid_price: float
    bid_size: int
    bid_time: int
    close_price: float
    high_price: float
    last_price: float
    last_size: int
    low_price: float
    mark: float
    mark_change: float
    mark_percent_change: float
    net_change: float
    net_percent_change: float
    open_price: float
    post_market_change: float
    post_market_percent_change: float
    quote_time: int
    security_status: str
    total_volume: int
    trade_time: int
    last_micid: str = None
    bid_micid: str = None
    ask_micid: str = None
    hard_to_borrow: bool = None
    shortable: bool = None
    exchange: str = None