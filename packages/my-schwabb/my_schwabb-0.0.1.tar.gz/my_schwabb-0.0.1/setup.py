from setuptools import setup, find_packages

setup(
    name="schwabb",
    version="1.0.1",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        'requests',
        'redis',
        'orjson',
        'websockets',

    ],
    extras_require={
        'redis': ['redis'],
        'mysql': ['pymysql'],
        'websocket': ['websockets'],
    }
)