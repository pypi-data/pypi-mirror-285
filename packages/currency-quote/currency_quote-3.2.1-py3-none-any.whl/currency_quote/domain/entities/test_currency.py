import pytest
from currency_quote.domain.entities.currency import CurrencyQuote


def test_currency():
    client = CurrencyQuote(currency_list=[])
    with pytest.raises(ValueError):
        client.get_currency_list()
