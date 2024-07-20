from currency_quote.application.ports.inbound.controller import IController
from currency_quote.application.use_cases.get_last_currency_quote import (
    GetLastCurrencyQuoteUseCase,
)
from currency_quote.application.use_cases.get_history_currency_quote import (
    GetHistCurrencyQuoteUseCase,
)
from currency_quote.domain.entities.currency import CurrencyQuote


class ClientBuilder(IController):
    def __init__(self, currency_list: list):
        self.currency_list = currency_list
        self.currency_quote = CurrencyQuote(self.currency_list)

    def get_last_quote(self) -> dict:
        return GetLastCurrencyQuoteUseCase.execute(currency_quote=self.currency_quote)

    def get_history_quote(self, reference_date: int) -> dict:
        return GetHistCurrencyQuoteUseCase.execute(
            currency_quote=self.currency_quote,
            reference_date=reference_date,
        )
