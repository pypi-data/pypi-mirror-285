from enum import Enum

class Command(Enum):
    LOGIN = 'login'
    SUBS = 'subs'
    ADD = 'add'
    UNSUBS = 'unsubs'
    VIEW = 'view'
    LOGOUT = 'logout'

class Service(Enum):
    ADMIN = 'admin'
    LEVELONE_EQUITIES = 'equities'
    LEVELONE_OPTIONS = 'options'
    LEVELONE_FUTURES = 'futures'
    LEVELONE_FUTURES_OPTIONS = 'futures_options'
    LEVELONE_FOREX = 'forex'
    NYSE_BOOK = 'nyse_book'
    NASDAQ_BOOK = 'nasdaq_book'
    OPTIONS_BOOK = 'options_book'
    CHART_EQUITY = 'chart_equity'
    CHART_FUTURES = 'chart_futures'
    SCREENER_EQUITY = 'screener_equity'
    SCREENER_OPTION = 'screener_option'
    ACCT_ACTIVITY = 'account_activity'

class EquityOptions(Enum):
    symbol = 0
    bid_price = 1
    ask_price = 2
    last_price = 3
    bid_size = 4
    ask_size = 5
    ask_id = 6
    bid_id = 7
    total_volume = 8
    last_size = 9
    high_price = 10
    low_price = 11
    close_price = 12
    exchange_id = 13
    marginable = 14
    description = 15
    last_id = 16
    open_price = 17
    net_change = 18
    year_high = 19
    year_low = 20
    pe_ratio = 21
    annual_dividend_amount = 22
    dividend_yield = 23
    nav = 24
    exchange_name = 25
    dividend = 26
    regular_market_quote = 27
    regular_market_trade = 28
    regular_market_last_price = 29
    regular_market_last_size = 30
    regular_market_net_change = 31
    security_status = 32
    mark_price = 33
    quote = 34
    trade = 35
    regular_market_trade_time_in_long = 36
    bid = 37
    ask = 38
    net_percent_change = 42
    regular_market_percent_change = 43
    mark_price_net_change = 44
    mark_price_percent_change = 45
    hard_to_borrow_quantity = 46
    hard_to_borrow_rate = 47
    hard_to_borrow = 48
    post_market_net_change = 50
    post_market_percent_change = 51
