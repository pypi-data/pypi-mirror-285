# Standard library imports
from dataclasses import dataclass

# Third party imports
try:
    import polars as pl
    _has_polars = True
    _positions_schema = {
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
from ..enums import *
from ..utils import dict_to_snake, binary_search
from .meta import Mapping, Filterable


@dataclass(slots=True, repr=False)
class Position(Mapping):
    average_price: float = None
    average_long_price: float = None
    average_short_price: float = None
    current_day_cost: float = None
    current_day_profit_loss: float = None
    current_day_profit_loss_percentage: float = None
    instrument: dict = None
    long_open_profit_loss: float = None
    long_quantity: float = None
    maintenance_requirement: float = None
    market_value: float = None
    previous_session_long_quantity: float = None
    previous_session_short_quantity: float = None
    settled_long_quantity: float = None
    settled_short_quantity: float = None
    short_open_profit_loss: float = None
    short_quantity: float = None
    tax_lot_average_long_price: float = None
    tax_lot_average_short_price: float = None
    symbol: str = None

    def __post_init__(self):
        self.symbol = self.instrument['symbol']

    def __hash__(self):
        return hash(self.symbol)

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


@dataclass(slots=True)
class Positions(Filterable):
    _data: list[Position]
    _symbols: set[str] = None

    @property
    def symbols(self):
        return self.get_symbols()

    def __post_init__(self):
        self._data = sorted([self._build_position(position) for position in self._data], key=lambda x: x.symbol)
        self._symbols = set(position.symbol for position in self._data)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, value):
        if isinstance(value, Position):
            return value in self._data
        return value in self._symbols

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[key]
        elif isinstance(key, str):
            key = key.upper()
            if (position := binary_search(self._data, key, 'symbol')) is not None:
                return position
            # for position in self._data:
            #     if position.symbol == key:
            #         return position
            else:
                raise KeyError(f"'{key}' was not found")
        else:
            raise KeyError('Key must be integer or symbol string')

    def _build_position(self, position):
        if isinstance(position, Position):
            return position
        return Position(**dict_to_snake(position))

    def get_symbols(self):
        return tuple(position.symbol for position in self._data)

    def get(self, symbol, default=None):
        symbol = symbol.upper()
        try:
            return self[symbol]
        except KeyError:
            return default



    def to_dataframe(self) -> pl.DataFrame:
        if not _has_polars:
            raise ImportError("polars is not installed. Please install it using 'pip install polars'")

        positions = (
            (
                position.symbol,
                position.long_quantity,
                position.short_quantity,
                position.market_value,
                sum([position.long_open_profit_loss if position.long_open_profit_loss is not None else 0, position.short_open_profit_loss if position.short_open_profit_loss is not None else 0]),
                position.average_long_price if position.average_long_price is not None else position.average_short_price,
            )
            for position in self._data
        )

        return pl.DataFrame(positions, schema=_positions_schema)