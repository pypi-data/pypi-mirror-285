from typing import Type
from currency_quote.application.ports.outbound.currency_repository import (
    ICurrencyRepository,
)
from currency_quote.application.use_cases.validate_currency import (
    ValidateCurrencyUseCase,
)
from currency_quote.domain.entities.currency import CurrencyQuote


class GetCurrencyQuoteService:
    def __init__(
        self, currency: CurrencyQuote, currency_repository: Type[ICurrencyRepository]
    ):
        self.currency = currency
        self.currency_repository = currency_repository

    def last(self) -> dict:
        return self.currency_repository(self.validate_currency_code()).get_last_quote()

    def history(self, reference_date: int) -> dict:
        return self.currency_repository(
            self.validate_currency_code()
        ).get_history_quote(reference_date=reference_date)

    def validate_currency_code(self) -> str:
        valid_list = ValidateCurrencyUseCase.execute(self.currency)
        return ",".join(valid_list)
