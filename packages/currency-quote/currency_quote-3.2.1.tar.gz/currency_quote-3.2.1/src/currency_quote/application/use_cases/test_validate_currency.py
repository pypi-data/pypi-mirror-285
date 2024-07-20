import pytest
from currency_quote.application.use_cases.validate_currency import (
    ValidateCurrencyUseCase,
)
from currency_quote.domain.entities.currency import CurrencyQuote


def test_valid_currency():
    currency_list = ["USD-BRL", "USD-BRLT"]
    currency_quote = CurrencyQuote(currency_list)
    result = ValidateCurrencyUseCase.execute(currency_quote=currency_quote)
    assert result == currency_list


def test_partial_valid_currency():
    currency_list = ["USD-BRL", "USD-BRLT", "param1"]
    currency_quote = CurrencyQuote(currency_list)
    expected_result = ["USD-BRL", "USD-BRLT"]
    result = ValidateCurrencyUseCase.execute(currency_quote=currency_quote)
    assert result == expected_result


def test_invalid_currency():
    currency_list = ["param1", "param2"]
    currency_quote = CurrencyQuote(currency_list)
    with pytest.raises(ValueError):
        ValidateCurrencyUseCase.execute(currency_quote=currency_quote)
