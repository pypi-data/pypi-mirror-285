# Standard library imports
from dataclasses import dataclass

# Third party imports
try:
    import polars as pl
    _has_polars = True
    _quotes_schema = {
        'symbol': pl.Utf8,
        'long_quantity': pl.Float64,
        'short_quantity': pl.Float64,
        'market_value': pl.Float64,
        'gl': pl.Float64,
        'average_price': pl.Float64,
    }
except ImportError:
    print("Error occurred while importing polars")
    _has_polars = False

# Relative imports
from ..utils import dict_to_snake
from .meta import Mapping





@dataclass(slots=True, kw_only=True)
class QuoteData(Mapping):
    symbol: str
    asset_main_type: str = None
    quote_type: str = None
    realtime: bool = None
    ssid: int = None
    quote: dict = None
    extended: dict = None
    fundamental: dict = None
    reference: dict = None
    regular: dict = None
    asset_sub_type: str = None

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        self.quote = self._build_quote(self.symbol, self.quote, self.reference)

    # def __repr__(self):
    #     value = f"{self.symbol}(\n"
    #     values = [
    #         f"    {name}: {getattr(self, name)},\n"
    #         for name in self.__dataclass_fields__.keys()
    #         if name != 'symbol'
    #     ]
    #     values.insert(0, value)
    #     values.append(')')
    #     return ''.join(values)

    def __str__(self):
        return self.symbol

    @classmethod
    def _build_quote(cls, symbol, quote, reference=None):
        reference = reference or {}
        return Quote(
            symbol=symbol,
            hard_to_borrow=reference.get('isHardToBorrow'),
            shortable=reference.get('isShortable'),
            exchange=reference.get('exchange'),
            **quote
        )

    @classmethod
    def new(cls, symbol, data, fields):
        fields = tuple(fields)
        data = dict_to_snake(data)

        if 'invalid_symbols' in data.keys():
            return InvalidQuote(symbol)

        data['quote']['year_high'] = data['quote'].pop('52_week_high')
        data['quote']['year_low'] = data['quote'].pop('52_week_low')
        if fields == ('quote', 'reference') or fields == ('quote',):
            return cls._build_quote(data['symbol'], data['quote'], data.get('reference'))
        return cls(**data)

@dataclass(slots=True)
class InvalidQuote(Mapping):
    symbol: str
    last_price: float = 0

@dataclass(slots=True, eq=False, kw_only=True)
class Quote(Mapping):
    symbol: str
    year_high: float = None
    year_low: float = None
    ask_price: float = None
    ask_size: int = None
    ask_time: int = None
    bid_price: float = None
    bid_size: int = None
    bid_time: int = None
    close_price: float = None
    high_price: float = None
    last_price: float = None
    last_size: int = None
    low_price: float = None
    mark: float = None
    mark_change: float = None
    mark_percent_change: float = None
    net_change: float = None
    net_percent_change: float = None
    open_price: float = None
    quote_time: int = None
    security_status: str = None
    total_volume: int = None
    trade_time: int = None
    post_market_change: float = None
    post_market_percent_change: float = None
    last_micid: str = None
    bid_micid: str = None
    ask_micid: str = None
    hard_to_borrow: bool = None
    shortable: bool = None
    exchange: str = None

    # def __repr__(self):
    #     value = f"{self.symbol}(\n"
    #     values = [
    #         f"    {name}: {getattr(self, name)},\n"
    #         for name in self.__dataclass_fields__.keys()
    #         if name != 'symbol'
    #     ]
    #     values.insert(0, value)
    #     values.append(')')
    #     return ''.join(values)

    def __eq__(self, other):
        if isinstance(other, Quote):
            return self.symbol == other.symbol and self.last_price == other.last_price
        elif isinstance(other, dict):
            return self.symbol == other.get('symbol') and self.last_price == other.get('last_price')
        return False


@dataclass(slots=True)
class Quotes:
    _data: list[QuoteData|Quote]

    def __post_init__(self):
        pass

    def to_dataframe(self):
        if not _has_polars:
            raise ImportError("polars is not installed. Please install it using 'pip install polars'")
