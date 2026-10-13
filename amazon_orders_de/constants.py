from amazonorders import constants


class Constants(constants.Constants):
    """
    Constants for amazon.de, requested in English.
    """

    # Ask for the English version of the site, so its pages are parsed with the English words of ``amazon-orders``
    BASE_HEADERS = {**constants.Constants.BASE_HEADERS, "Accept-Language": "en-GB,en;q=0.9"}

    # amazon.de picks its language from this cookie rather than from ``Accept-Language``, and sets it again from the
    # account's language on every response
    REQUEST_COOKIES = {"lc-acbde": "en_GB"}

    #: The internal API that loads further pages of Transactions.
    TRANSACTION_HISTORY_API_ROUTE = "/payments-portal/data/iris/live/v1/data/manage/get-transactions"

    @property
    def TRANSACTION_HISTORY_API_URL(self) -> str:
        return f"{self.BASE_URL}{self.TRANSACTION_HISTORY_API_ROUTE}"
