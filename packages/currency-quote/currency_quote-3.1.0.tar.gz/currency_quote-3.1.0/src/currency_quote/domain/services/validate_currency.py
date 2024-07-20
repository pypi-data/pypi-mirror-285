# src/currency_quote/application/services/currency_validator_service.py
from typing import Type
from currency_quote.domain.entities.currency import CurrencyQuote
from currency_quote.application.ports.outbound.currency_validator_repository import (
    ICurrencyValidator,
)


class CurrencyValidatorService:
    def __init__(
        self, currency: CurrencyQuote, currency_validator: Type[ICurrencyValidator]
    ):
        self.currency_validator = currency_validator
        self.currency_quote = currency
        self.currency_list = currency.get_currency_list()

    def validate_currency_code(self) -> list:
        validated_list = self.currency_validator(
            self.currency_quote
        ).validate_currency_code()

        if len(validated_list) == 0:
            raise ValueError(f"All params: {self.currency_list} are invalid.")

        if len(validated_list) < len(self.currency_list):
            print(
                f"Invalid currency params: {set(self.currency_list) - set(validated_list)}"
            )

        return validated_list
