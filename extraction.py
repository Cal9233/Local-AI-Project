"""Rules applied to extracted quotes: code does the arithmetic, not the model."""

from decimal import Decimal

from model import PriceBasis, Quote

CENTS = Decimal("0.01")


def unit_price(quote: Quote) -> Decimal:
    """Return the per-unit price of a validated quote, quantized to cents.

    A LOT price is divided by quantity. The Quote schema guarantees quantity > 0,
    so no zero check is needed here.
    """
    if quote.price_basis == PriceBasis.PER_UNIT:
        return quote.price.quantize(CENTS)
    return (quote.price / quote.quantity).quantize(CENTS)
