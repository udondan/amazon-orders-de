"""
An ``amazon-orders`` language package for amazon.de, which requests its pages in English. Enable it with
``language_package: amazon_orders_de`` and ``domain: amazon.de`` in the config.
"""

from amazon_orders_de.constants import Constants
from amazon_orders_de.order import Order
from amazon_orders_de.selectors import Selectors
from amazon_orders_de.transactions import TransactionsPage

__all__ = ["Constants", "Order", "Selectors", "TransactionsPage"]
