from amazonorders import selectors
from amazonorders.selectors import Selector


class Selectors(selectors.Selectors):
    """
    Selectors for amazon.de, requested in English, which uses British English labels.
    """

    # Rendered as "Postage & Packing"
    FIELD_ORDER_SHIPPING_TOTAL_LABELS = [*selectors.Selectors.FIELD_ORDER_SHIPPING_TOTAL_LABELS, "postage"]
    # Rendered as "Estimated VAT"
    FIELD_ORDER_ESTIMATED_TAX_LABELS = [*selectors.Selectors.FIELD_ORDER_ESTIMATED_TAX_LABELS, "estimated vat"]

    ORDER_SKIP_TOTALS = [
        *selectors.Selectors.ORDER_SKIP_TOTALS,
        # Identifies an Order of a cancelled service (e.g. a cancelled installation) on the history page
        Selector("div.yohtmlc-shipment-status-primaryText", "Service cancelled"),
    ]

    #: The payment instruments an Order was paid with, and each one's name and masked number.
    FIELD_ORDER_PAYMENT_INSTRUMENT_SELECTOR = "[data-testid='payment-instrument']"
    FIELD_ORDER_PAYMENT_INSTRUMENT_NAME_SELECTOR = "[data-testid='payment-instrument-name']"
    FIELD_ORDER_PAYMENT_INSTRUMENT_NUMBER_SELECTOR = "[data-testid='payment-instrument-number']"

    #: The address lines that follow the Recipient's name in an unclassed list.
    FIELD_RECIPIENT_ADDRESS_LINES_SELECTOR = "ul > li:not(:first-child)"

    #: The Transactions, embedded as JSON in the Next.js page.
    TRANSACTION_HISTORY_NEXT_DATA_SELECTOR = "script#__NEXT_DATA__"
