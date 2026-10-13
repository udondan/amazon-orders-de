import re
from typing import List, Optional

from amazonorders import util
from amazonorders.entity import order, recipient


class Recipient(recipient.Recipient):
    """
    A Recipient whose address is rendered as an unclassed list, one or more lines per list item.
    """

    def _parse_address(self) -> Optional[str]:
        return self._parse_address_lines() or super()._parse_address()

    def _parse_address_lines(self) -> Optional[str]:
        lines: List[str] = []
        for tag in util.select(self.parsed, self.config.selectors.FIELD_RECIPIENT_ADDRESS_LINES_SELECTOR):
            # A list item may hold several lines separated by <br> or, when Amazon renders the address inline,
            # by commas
            lines.extend(line.strip() for line in re.split(r"[\n,]", tag.get_text("\n")) if line.strip())

        return "\n".join(lines) or None


class Order(order.Order):
    """
    An Order on amazon.de.
    """

    def _parse_payment_method(self) -> Optional[str]:
        # When a Gift Card was used alongside a card, prefer the card (the instrument with a number), like its last
        # digits are
        selectors = self.config.selectors
        for instrument in util.select(self.parsed, selectors.FIELD_ORDER_PAYMENT_INSTRUMENT_SELECTOR):
            name_tag = util.select_one(instrument, selectors.FIELD_ORDER_PAYMENT_INSTRUMENT_NAME_SELECTOR)
            if name_tag and util.select_one(instrument, selectors.FIELD_ORDER_PAYMENT_INSTRUMENT_NUMBER_SELECTOR):
                return name_tag.text.strip() or None

        return super()._parse_payment_method()

    def _parse_recipient(self) -> Optional[recipient.Recipient]:
        value = super()._parse_recipient()
        if value is None:
            return None

        return Recipient(value.parsed, self.config)
