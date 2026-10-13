# amazon-orders-de

A [language package](https://amazon-orders.readthedocs.io/language-packages.html) for
[amazon-orders](https://github.com/alexdlaird/amazon-orders) that adds support for amazon.de.

Rather than translating `amazon-orders` into German, it asks amazon.de for its pages in English and handles what's
different there:

- British English labels ("Postage & Packing", "Estimated VAT")
- Orders whose service was cancelled
- Recipient addresses rendered as a plain list
- The payment method of an Order paid with a Gift Card and a card
- The Transactions page, which embeds its first page as JSON and loads further pages from an API

## Installation

```sh
pip install amazon-orders-de
```

## Usage

Set `language_package` and `domain` in the `amazon-orders` config (`~/.config/amazon-orders/config.yml`):

```yaml
language_package: amazon_orders_de
domain: amazon.de
```

or pass them in Python:

```python
from amazonorders.conf import AmazonOrdersConfig
from amazonorders.orders import AmazonOrders
from amazonorders.session import AmazonSession

config = AmazonOrdersConfig(data={"language_package": "amazon_orders_de", "domain": "amazon.de"})
amazon_session = AmazonSession(config=config)
amazon_session.login()

orders = AmazonOrders(amazon_session).get_order_history(year=2026)
```

Everything else works as described in the [amazon-orders docs](https://amazon-orders.readthedocs.io).

## Development

```sh
python -m venv venv
venv/bin/pip install -e ".[dev]"
venv/bin/flake8 amazon_orders_de tests scripts
venv/bin/mypy
venv/bin/pytest
```

The unit tests parse real amazon.de pages in `tests/resources`. Before a page is added there, it's anonymized with
`scripts/anonymize-test-resources.py`, which removes personal and product details. The raw pages and the rules file
with the values to replace must never be committed.

The integration tests in `tests/integration` log in to amazon.de with `AMAZON_USERNAME`, `AMAZON_PASSWORD`, and
`AMAZON_OTP_SECRET_KEY`, and run nightly in CI.
