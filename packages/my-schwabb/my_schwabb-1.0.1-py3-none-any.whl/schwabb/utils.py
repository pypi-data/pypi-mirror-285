from datetime import date, datetime, timedelta
from functools import wraps
from re import compile as re_compile, sub as re_sub
import time

from dateutil.parser import parse as parse_dt

_camel_to_snake_regex = re_compile('([a-z0-9])([A-Z])')

def from_isoformat(value):
    if len(value) == 10:
        return date.fromisoformat(value)
    else:
        value = value[:19]
        return datetime.fromisoformat(value)

def snake_to_camel(name):
    items = name.split('_')
    return f"{items[0]}{''.join(i.title() for i in items[1:])}"

def camel_to_snake(name):
    s1 = re_sub(_camel_to_snake_regex, r'\1_\2', name)
    return s1.lower()

def dict_to_snake(value):
    if isinstance(value, dict):
        new_dict = {}
        for key, val in value.items():
            new_key = camel_to_snake(key)
            if 'date' in new_key or 'time' in new_key and isinstance(val, str):
                new_val = from_isoformat(val)
            else:
                new_val = dict_to_snake(val)
            new_dict[new_key] = new_val
        return new_dict
    elif isinstance(value, list):
        new_list = []
        for item in value:
            new_item = dict_to_snake(item)
            new_list.append(new_item)
        return new_list
    else:
        return value

def binary_search(objs, target, attr=None):
    low = 0
    high = len(objs) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_item = objs[mid]
        if attr is not None:
            mid_item = getattr(mid_item, attr)

        if mid_item == target:
            return objs[mid]  # Found the target, return it
        elif mid_item < target:
            low = mid + 1  # Target is in the upper half
        else:
            high = mid - 1  # Target is in the lower half

    return None  # Target not found

def ts_to_milliseconds(value):
    return value * 1000

def parse_date(value):
    if value is None or isinstance(value, (date, datetime)):
        return value
    return parse_dt(value)

def parse_lookback(value, format=datetime):
    if value is None:
        return value

    elif isinstance(value, int):
        value = datetime
    elif isinstance(value, str):
        value = value.lower()
        if value[-1].isalpha():
            if value[-1] == 'y':
                value = int(value[:-1]) * 365
            elif value[-1] == 'm':
                value = int(value[:-1]) * 30
            elif value[-1] == 'w':
                value = int(value[:-1]) * 7
            elif value[-1] == 'd':
                value = int(value[:-1])
        else:
            value = int(value)
    return value

class ratelimit:
    def __init__(self, capacity, window_size):
        self.capacity = capacity
        self.window_size = window_size
        self.requests = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            self.requests = [req for req in self.requests if req > current_time - self.window_size]

            if len(self.requests) < self.capacity:
                result = func(*args, **kwargs)
                # self.requests.append(time.time())
                self.requests.append(current_time)
                print(f"Request allowed: {len(self.requests)}")
                return result
            else:
                time.sleep(0.05)
                return wrapper(*args, **kwargs)
        return wrapper

    def allow_request(self):
        current_time = time.time()
        self.requests = [req for req in self.requests if req > current_time - self.window_size]

        if len(self.requests) < self.capacity:
            self.requests.append(current_time)
            return True
        else:
            return False