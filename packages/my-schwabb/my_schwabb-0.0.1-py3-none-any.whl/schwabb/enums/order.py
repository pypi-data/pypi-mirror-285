from enum import Enum

class Session(Enum):
    NORMAL = 'normal'
    AM = 'am'
    PM = 'pm'
    SEAMLESS = 'seamless'

class Duration(Enum):
    DAY = 'day'
    GOOD_TILL_CANCEL = 'good_till_cancel'
    FILL_OR_KILL = 'fill_or_kill'
    IMMEDIATE_OR_CANCEL = 'immediate_or_cancel'
    END_OF_WEEK = 'end_of_week'
    END_OF_MONTH = 'end_of_month'
    NEXT_END_OF_MONTH = 'next_end_of_month'
    UNKNOWN = 'unknown'

class OrderType(Enum):
    MARKET = 'market'
    MARKET_ON_CLOSE = 'market_on_close'
    LIMIT = 'limit'
    LIMIT_ON_CLOSE = 'limit_on_close'
    STOP = 'stop'
    STOP_LIMIT = 'stop_limit'
    TRAILING_STOP = 'trailing_stop'
    TRAILING_STOP_LIMIT = 'trailing_stop_limit'
    CABINET = 'cabinet'
    NON_MARKETABLE = 'non_marketable'
    EXERCISE = 'exercise'
    NET_DEBIT = 'net_debit'
    NET_CREDIT = 'net_credit'
    NET_ZERO = 'net_zero'
    UNKNOWN = 'unknown'

class ComplexOrderStrategy(Enum):
    NONE = None
    COVERED = 'covered'
    VERTICAL = 'vertical'
    BACK_RATIO = 'back_ratio'
    CALENDAR = 'calendar'
    DIAGONAL = 'diagonal'
    STRADDLE = 'straddle'
    STRANGLE = 'strangle'
    COLLAR_SYNTHETIC = 'collar_synthetic'
    BUTTERFLY = 'butterfly'
    CONDOR = 'condor'
    IRON_CONDOR = 'iron_condor'
    VERTICAL_ROLL = 'vertical_roll'
    COLLAR_WITH_STOCK = 'collar_with_stock'
    DOUBLE_DIAGONAL = 'double_diagonal'
    UNBALANCED_BUTTERFLY = 'unbalanced_butterfly'
    UNBALANCED_CONDOR = 'unbalanced_condor'
    UNBALANCED_IRON_CONDOR = 'unbalanced_iron_condor'
    UNBALANCED_VERTICAL_ROLL = 'unbalanced_vertical_roll'
    MUTUAL_FUND_SWAP = 'mutual_fund_swap'
    CUSTOM = 'custom'

class OrderStrategyType(Enum):
    SINGLE = 'single'
    CANCEL = 'cancel'
    RECALL = 'recall'
    PAIR = 'pair'
    FLATTEN = 'flatten'
    TWO_DAY_SWAP = 'two_day_swap'
    BLAST_ALL = 'blast_all'
    OCO = 'oco'
    TRIGGER = 'trigger'

class StopPriceLinkBasis(Enum):
    MANUAL = 'manual'
    BASE = 'base'
    TRIGGER = 'trigger'
    LAST = 'last'
    BID = 'bid'
    ASK = 'ask'
    ASK_BID = 'ask_bid'
    MARK = 'mark'
    AVERAGE = 'average'

class StopPriceLinkType(Enum):
    VALUE = 'value'
    PERCENT = 'percent'
    TICK = 'tick'

class StopType(Enum):
    STANDARD = 'standard'
    BID = 'bid'
    ASK = 'ask'
    LAST = 'last'
    MARK = 'mark'

class PriceLinkBasis(Enum):
    MANUAL = 'manual'
    BASE = 'base'
    TRIGGER = 'trigger'
    LAST = 'last'
    BID = 'bid'
    ASK = 'ask'
    ASK_BID = 'ask_bid'
    MARK = 'mark'
    AVERAGE = 'average'

class PriceLinkType(Enum):
    VALUE = 'value'
    PERCENT = 'percent'
    TICK = 'tick'

class Instruction(Enum):
    BUY = 'buy'
    SELL = 'sell'
    BUY_TO_COVER = 'buy_to_cover'
    SELL_SHORT = 'sell_short'
    BUY_TO_OPEN = 'buy_to_open'
    BUY_TO_CLOSE = 'buy_to_close'
    SELL_TO_OPEN = 'sell_to_open'
    SELL_TO_CLOSE = 'sell_to_close'
    EXCHANGE = 'exchange'
    SELL_SHORT_EXEMPT = 'sell_short_exempt'

class SpecialInstruction(Enum):
    ALL_OR_NONE = 'all_or_none'
    DO_NOT_REDUCE = 'do_not_reduce'
    ALL_OR_NONE_DO_NOT_REDUCE = 'all_or_none_do_not_reduce'

class AssetType(Enum):
    EQUITY = 'equity'
    OPTION = 'option'
    INDEX = 'index'
    MUTUAL_FUND = 'mutual_fund'
    CASH_EQUIVALENT = 'cash_equivalent'
    FIXED_INCOME = 'fixed_income'
    CURRENCY = 'currency'
    COLLECTIVE_INVESTMENT = 'collective_investment'


class QuantityType(Enum):
    ALL_SHARES = 'all_shares'
    DOLLARS = 'dollars'
    SHARES = 'shares'


class TaxLotMethod(Enum):
    FIFO = 'fifo'
    LIFO = 'lifo'
    HIGH_COST = 'high_cost'
    LOW_COST = 'low_cost'
    AVERAGE_COST = 'average_cost'
    SPECIFIC_LOT = 'specific_lot'
    LOSS_HARVESTER = 'loss_harvester'

class DivCapGains(Enum):
    REINVEST = 'reinvest'
    PAYOUT = 'payout'


class Instrument:
    @classmethod
    def new(cls, symbol, asset_type, cusip=None, description=None, instrument_id=None, net_change=None, type=None, maturity_date=None, variable_rate=None, factor=None, option_deliverables=None, put_call=None, option_multiplier=None, underlying_symbol=None):
        instrument = dict(
            symbol=symbol,
            assetType=asset_type
        )

        if cusip is not None:
            instrument['cusip'] = cusip

        if description is not None:
            instrument['description'] = description

        if instrument_id is not None:
            instrument['instrumentId'] = instrument_id

        if net_change is not None:
            instrument['netChange'] = net_change

        if type is not None:
            instrument['type'] = type

        if maturity_date is not None:
            instrument['maturityDate'] = maturity_date

        if variable_rate is not None:
            instrument['variableRate'] = variable_rate

        if factor is not None:
            instrument['factor'] = factor

        if option_deliverables is not None:
            instrument['optionDeliverables'] = option_deliverables

        if put_call is not None:
            instrument['putCall'] = put_call

        if option_multiplier is not None:
            instrument['optionMultiplier'] = option_multiplier

        if underlying_symbol is not None:
            instrument['underlyingSymbol'] = underlying_symbol

        return instrument