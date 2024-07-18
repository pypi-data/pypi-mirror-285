from .base import Provider

class SQLiteProvider(Provider):
    def __init__(self):
        print("SQLite provider initialized")