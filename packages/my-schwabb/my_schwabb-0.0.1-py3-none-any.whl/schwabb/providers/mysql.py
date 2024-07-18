from .base import Provider

try:
    from pymysql import connect as connect_mysql
except ImportError:
    raise ImportError("MySQL provider requires pymysql")

class MySQLProvider(Provider):
    __slots__ = ('_conn', '_cursor')

    def __init__(self, *args, **kwargs):
        print("MySQL provider initialized")
        self._conn = connect_mysql(
            host='localhost',
            user='root',
            password='password',
        )
        self._cursor = self.conn.cursor()

    def close(self):
        self._cursor.close()
        self._conn.close()

    def retrieve(self):
        self._cursor.execute("SELECT * FROM schwabb")
        data = self._cursor.fetchall()
        if data:
            return data[0]
        return ()

    def store(self, data=None, **kwargs):
        print(f"Storing data: {data}")
        if data is None:
            raise ValueError('Data must be provided')
        self._cursor.execute("INSERT INTO oauth VALUES ()", data)
        self._conn.commit()