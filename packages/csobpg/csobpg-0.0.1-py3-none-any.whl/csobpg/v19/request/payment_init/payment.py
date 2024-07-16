"""Payment models."""

from enum import Enum


class PaymentOperation(Enum):
    """Payment operation."""

    PAYMENT = "payment"
    ONE_CLICK_PAYMENT = "oneclickPayment"
    CUSTOM_PAYMENT = "customPayment"


class PaymentMethod(Enum):
    """Payment method."""

    CARD = "card"
    CARD_LVP = "card#LVP"
