# src/currency_quote/application/ports/outbound/currency_validator_port.py
from abc import ABC, abstractmethod


class ICurrencyRepository(ABC):
    @abstractmethod
    def __init__(self, currency_codes: str):
        pass

    @abstractmethod
    def get_last_quote(self) -> dict:
        pass

    @abstractmethod
    def get_history_quote(self, reference_date: int) -> dict:
        pass
