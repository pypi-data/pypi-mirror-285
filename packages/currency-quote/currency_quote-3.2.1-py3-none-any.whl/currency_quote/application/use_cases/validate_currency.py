# src/currency_quote/application/use_cases/validate_currency.py
from currency_quote.domain.services.validate_currency import CurrencyValidatorService
from currency_quote.adapters.outbound.currency_validator_api import CurrencyValidatorAPI
from currency_quote.domain.entities.currency import CurrencyQuote


class ValidateCurrencyUseCase:
    @staticmethod
    def execute(currency_quote: CurrencyQuote) -> list:
        validator_service = CurrencyValidatorService(
            currency=currency_quote, currency_validator=CurrencyValidatorAPI
        )
        return validator_service.validate_currency_code()
