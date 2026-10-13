import json
import logging
import re
from typing import Any

from amazonorders import transactions, util
from amazonorders.entity.transaction import Transaction
from amazonorders.exception import AmazonOrdersEntityError, AmazonOrdersError
from amazonorders.session import AmazonSession
from bs4 import Tag

logger = logging.getLogger(__name__)

#: An Order number within a Transaction's Order description.
_ORDER_NUMBER_RE = re.compile(r"\b(\d{3}-\d{7}-\d{7}|D\d{2}-\d{7}-\d{7})\b")

_PageResult = tuple[list[Transaction], dict[str, Any] | None]


class TransactionsPage(transactions.TransactionsPage):
    """
    The Transactions page of amazon.de, a Next.js page that embeds its first page of Transactions as JSON and loads
    further pages from an internal API.
    """

    def get_page(
        self, amazon_session: AmazonSession, url: str, next_page_data: dict[str, Any] | None = None
    ) -> _PageResult:
        if not next_page_data or "request" not in next_page_data:
            return super().get_page(amazon_session, url, next_page_data)

        page_response = amazon_session.post(
            self.config.constants.TRANSACTION_HISTORY_API_URL,
            json=next_page_data["request"],
            headers={"x-amzn-upx-token": next_page_data["token"]},
        )
        amazon_session.check_response(page_response, meta=next_page_data)

        try:
            data = page_response.response.json()
        except ValueError as e:
            raise AmazonOrdersError(
                "Could not parse Transaction history. Check if Amazon changed the API.", meta=next_page_data
            ) from e

        return self._parse_api_response(data, next_page_data)

    def parse_page(self, parsed: Tag) -> _PageResult:
        next_data_tag = util.select_one(parsed, self.config.selectors.TRANSACTION_HISTORY_NEXT_DATA_SELECTOR)
        if next_data_tag:
            result = self._parse_next_data(next_data_tag)
            if result is not None:
                return result

        return super().parse_page(parsed)

    def _parse_next_data(self, next_data_tag: Tag) -> _PageResult | None:
        try:
            page_props = json.loads(next_data_tag.text)["props"]["pageProps"]
            state = page_props["state"]["transactionResponseState"]
            transaction_list = state["visibleTransactionResponse"]["transactionList"]
        except (ValueError, KeyError, TypeError):
            return None

        loaded_transactions = self._parse_transactions_data(transaction_list)

        # Further pages are loaded from an internal API, authorized by the token embedded in the page
        next_page_data = None
        if state.get("hasMore") and state.get("lastEvaluatedPageKey"):
            try:
                next_page_data = {
                    "token": page_props["token"],
                    "request": {
                        "type": "GetTransactions",
                        "locale": page_props["request"]["locale"],
                        "surfaceInfo": page_props["manageWalletRequest"]["requestContext"]["surfaceInfo"],
                        "transactionsViewRequest": {"filtersControls": {"includeFilters": True}},
                        "widgetName": "ViewTransactions",
                        "exclusiveStartKey": state["lastEvaluatedPageKey"],
                    },
                }
            except (KeyError, TypeError):
                logger.warning(
                    "Only the first page of Transactions could be loaded, as the data to load further "
                    "pages was not found."
                )

        return loaded_transactions, next_page_data

    def _parse_api_response(self, data: dict[str, Any], next_page_data: dict[str, Any]) -> _PageResult:
        try:
            display_response = data["displayResponse"]
            transaction_list = display_response["transactionsList"]
        except (KeyError, TypeError) as e:
            raise AmazonOrdersError(
                "Could not parse Transaction history. Check if Amazon changed the API.", meta=next_page_data
            ) from e

        loaded_transactions = self._parse_transactions_data(transaction_list)

        last_evaluated_key = display_response.get("lastEvaluatedKey")
        if not last_evaluated_key:
            return loaded_transactions, None

        return loaded_transactions, {
            "token": next_page_data["token"],
            "request": dict(next_page_data["request"], exclusiveStartKey=last_evaluated_key),
        }

    def _parse_transactions_data(self, transaction_list: list[dict[str, Any]]) -> list[Transaction]:
        config = self.config
        loaded_transactions = []
        for data in transaction_list:
            date_str = data.get("formattedDate")
            completed_date = config.constants.parse_date(date_str)
            if completed_date is None:
                err_msg = (
                    f"Transaction date {date_str!r} could not be parsed, but it's required. Check if "
                    f"Amazon changed the page"
                )
                if not config.warn_on_missing_required_field:
                    raise AmazonOrdersEntityError(f"{err_msg} or set warn_on_missing_required_field=True in config.")

                logger.warning(f"{err_msg}.")
                continue

            grand_total = config.constants.parse_currency(data.get("formattedAmount"))
            if grand_total is None:
                logger.warning(
                    f"Transaction amount {data.get('formattedAmount')!r} could not be parsed, so the "
                    f"Transaction was skipped."
                )
                continue

            payment_data = data.get("paymentMethodDisplayStringData") or {}
            payment_method_name = payment_data.get("paymentMethodName")
            last_digits = (payment_data.get("paymentMethodNumber") or {}).get("lastDigits")
            # When a Transaction covers more than one Order, only the first one is used
            order_data = (data.get("orderData") or [{}])[0]
            order_number_match = _ORDER_NUMBER_RE.search(order_data.get("orderDisplayString") or "")

            loaded_transactions.append(
                config.transaction_cls.from_fields(
                    config,
                    completed_date,
                    grand_total,
                    payment_method=f"{payment_method_name} ****{last_digits}"
                    if payment_method_name and last_digits
                    else payment_method_name,
                    payment_method_last_4=last_digits,
                    order_number=order_number_match.group(1) if order_number_match else None,
                    order_details_link=order_data.get("orderDetailsUrl"),
                    seller=data.get("statementDescriptor"),
                )
            )

        return loaded_transactions
