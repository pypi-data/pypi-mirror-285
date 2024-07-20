# Standard library imports
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UserPreferences:
    ws_url: str
    client_customer_id: str
    client_correl_id: str
    client_channel: str
    client_function_id: str