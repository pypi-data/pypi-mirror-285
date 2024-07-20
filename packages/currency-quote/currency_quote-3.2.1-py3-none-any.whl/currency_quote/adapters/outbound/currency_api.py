from datetime import datetime

from api_to_dataframe import ClientBuilder, RetryStrategies

from currency_quote.application.ports.outbound.currency_repository import (
    ICurrencyRepository,
)
from currency_quote.config.endpoints import API


class CurrencyAPI(ICurrencyRepository):
    def __init__(self, currency_codes: str):
        self.currency_codes = currency_codes

    def get_last_quote(self) -> dict:
        url = f"{API.ENDPOINT_LAST_COTATION}{self.currency_codes}"
        client = ClientBuilder(
            endpoint=url, retry_strategy=RetryStrategies.EXPONENTIAL_RETRY_STRATEGY
        )

        response = client.get_api_data()

        return response

    def get_history_quote(self, reference_date: int) -> dict:
        today = int(datetime.today().strftime("%Y%m%d"))

        if reference_date > today or reference_date == today:
            print(f"[currency-quote] Invalid reference date: {reference_date}")
        else:
            url = (
                f"{API.ENDPOINT_HISTORY_COTATION}{self.currency_codes}"
                f"?start_date={reference_date}&end_date={reference_date}"
            )

            client = ClientBuilder(
                endpoint=url, retry_strategy=RetryStrategies.EXPONENTIAL_RETRY_STRATEGY
            )

            response = client.get_api_data()

            if len(response) == 0:
                print(f"[currency-quote] Response returned 0 results: {response}")
            else:
                return response

        return {}
