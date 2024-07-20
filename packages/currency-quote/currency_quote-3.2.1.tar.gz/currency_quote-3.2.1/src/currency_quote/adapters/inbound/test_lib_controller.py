import pytest
from currency_quote import ClientBuilder


@pytest.fixture(scope="session")
def setup_client():
    return ClientBuilder(currency_list=["USD-BRL"])


def test_client_builder(setup_client):  # pylint: disable=redefined-outer-name
    assert isinstance(setup_client, ClientBuilder)


def test_get_last_quote(setup_client):  # pylint: disable=redefined-outer-name
    last_quote = setup_client.get_last_quote()
    assert isinstance(last_quote, dict)


def test_get_hist_quote(setup_client):  # pylint: disable=redefined-outer-name
    hist_quote = setup_client.get_history_quote(reference_date=20240621)
    assert isinstance(hist_quote, list)
