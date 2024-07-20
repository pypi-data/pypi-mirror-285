# Schwabb

## About

The `my-schwabb` API client is a Python package that provides a convenient way to interact with the Schwabb API. It allows you to access your Schwabb account information, fetch account details, place orders, and retrieve order history. With this client, you can easily integrate Schwabb functionality into your Python applications and automate trading strategies. It provides a simple and intuitive interface, making it easy to get started with the Schwabb API. Start using the `my-schwabb` API client today and take control of your Schwabb account programmatically.

## Installation

You can install the `my-schwabb` package using pip. Open your terminal and type:

```bash
pip install my-schwabb
```


```python
from schwabb import Client

# fetch will fetch your current account and positions
client = Client(fetch=True)

client.place_order('AAPL', qty=1, order_type='limit', side='buy')
orders = client.get_orders()

transactions = client.get_transactions()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.