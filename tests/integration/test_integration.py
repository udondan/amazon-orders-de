import os
import unittest

from amazonorders.conf import AmazonOrdersConfig
from amazonorders.orders import AmazonOrders
from amazonorders.session import AmazonSession
from amazonorders.transactions import AmazonTransactions

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), os.pardir, ".integration-output")


@unittest.skipUnless(
    os.environ.get("AMAZON_USERNAME") and os.environ.get("AMAZON_PASSWORD"),
    "AMAZON_USERNAME and AMAZON_PASSWORD must be set to run the integration tests.",
)
class TestIntegration(unittest.TestCase):
    """
    Log in to amazon.de and parse the live Order history and Transactions with the language package. Credentials are
    read from the environment by ``amazon-orders`` (``AMAZON_USERNAME``, ``AMAZON_PASSWORD``, and
    ``AMAZON_OTP_SECRET_KEY``).
    """

    amazon_session: AmazonSession

    @classmethod
    def setUpClass(cls):
        config = AmazonOrdersConfig(
            data={
                "language_package": "amazon_orders_de",
                "domain": "amazon.de",
                "output_dir": OUTPUT_DIR,
                "cookie_jar_path": os.path.join(OUTPUT_DIR, "cookies.json"),
            }
        )
        cls.amazon_session = AmazonSession(config=config, debug=os.environ.get("DEBUG") == "True")
        cls.amazon_session.login()

    @classmethod
    def tearDownClass(cls):
        cls.amazon_session.logout()

    def test_order_history(self):
        # WHEN
        orders = AmazonOrders(self.amazon_session).get_order_history(time_filter="months-3", full_details=True)

        # THEN
        for order in orders:
            self.assertIsNotNone(order.order_number)
            self.assertIsNotNone(order.order_placed_date)
            if not order.cancelled:
                self.assertIsNotNone(order.grand_total, order.order_number)
                self.assertIsNotNone(order.subtotal, order.order_number)

    def test_transactions(self):
        # WHEN
        transactions = AmazonTransactions(self.amazon_session).get_transactions(days=90)

        # THEN
        for transaction in transactions:
            self.assertIsNotNone(transaction.completed_date)
            self.assertIsNotNone(transaction.grand_total)
