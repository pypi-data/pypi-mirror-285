import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schwabb import Client

client = Client(fetch=True, host='192.168.1.154', key='some_key', encrypt=True)