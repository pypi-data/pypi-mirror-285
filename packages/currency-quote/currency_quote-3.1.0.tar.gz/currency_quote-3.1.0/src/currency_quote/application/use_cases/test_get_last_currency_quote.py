import pytest
from currency_quote.application.use_cases.get_last_currency_quote import (
    GetLastCurrencyQuoteUseCase,
)
from currency_quote.domain.entities.currency import CurrencyQuote


def test_valid_currency():
    currency_list = ["USD-BRL", "EUR-BRL"]
    currency_quote = CurrencyQuote(currency_list)
    result = GetLastCurrencyQuoteUseCase.execute(currency_quote)
    assert isinstance(result, dict)
    assert len(result) == 2


def test_partial_valid_currency():
    currency_list = ["USD-BRL", "EUR-BRL", "param1"]
    currency_quote = CurrencyQuote(currency_list)
    result = GetLastCurrencyQuoteUseCase.execute(currency_quote)
    assert isinstance(result, dict)
    assert len(result) == 2


def test_invalid_currency():
    currency_list = ["param1", "param2"]
    currency_quote = CurrencyQuote(currency_list)
    with pytest.raises(ValueError):
        GetLastCurrencyQuoteUseCase.execute(currency_quote)
