# currency.py


class CurrencyQuote:
    def __init__(self, currency_list: list):
        self.currency_list = currency_list

    def get_currency_list(self) -> list:
        if len(self.currency_list) == 0:
            raise ValueError("Currency list is empty")

        return self.currency_list
