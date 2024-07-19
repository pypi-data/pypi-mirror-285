"""Payment init request package."""

from base64 import b64encode
from enum import Enum
from typing import Optional

from ..base import BaseRequest
from ..dttm import get_payment_expiry
from .cart import Cart, CartItem
from .currency import Currency
from .customer import CustomerData
from .order import OrderData
from .payment import PaymentMethod, PaymentOperation
from .webpage import WebPageAppearanceConfig


class ReturnMethod(Enum):
    """Return method."""

    POST = "POST"
    GET = "GET"


def _pack_merchant_data(data: bytes) -> str:
    encoded = b64encode(data).decode("UTF-8")

    if len(encoded) > 255:
        raise ValueError(
            "Merchant data length encoded to BASE64 is over 255 chars"
        )

    return encoded


class PaymentInitRequest(BaseRequest):
    """Payment init request."""

    def __init__(
        self,
        merchant_id: str,
        private_key: str,
        order_no: str,
        total_amount: int,
        return_url: str,
        return_method: ReturnMethod = ReturnMethod.POST,
        payment_operation: PaymentOperation = PaymentOperation.PAYMENT,
        payment_method: PaymentMethod = PaymentMethod.CARD,
        currency: Currency = Currency.CZK,
        close_payment: bool = True,
        ttl_sec: int = 600,
        cart: Optional[Cart] = None,
        customer: Optional[CustomerData] = None,
        order: Optional[OrderData] = None,
        merchant_data: Optional[bytes] = None,
        customer_id: Optional[str] = None,
        payment_expiry: Optional[int] = None,
        page_appearance: WebPageAppearanceConfig = WebPageAppearanceConfig(),
    ) -> None:
        # pylint:disable=too-many-locals
        super().__init__("payment/init", merchant_id, private_key)

        if not 300 <= ttl_sec <= 1800:
            raise ValueError('"ttl_sec" must be in [300, 1800]')
        if len(order_no) > 10:
            raise ValueError('"order_no" must be up to 10 chars')
        if len(return_url) > 300:
            raise ValueError('"return_url" must be up to 300 chars')
        if customer_id and len(customer_id) > 50:
            raise ValueError('"customer_id" must be up to 50 chars')
        if total_amount <= 0:
            raise ValueError('"total_amount" must be > 0')

        cart = cart or Cart([CartItem("Payment", 1, total_amount)])

        if cart.total_amount != total_amount:
            raise ValueError(
                "Cart's total amount does not match the requested total amount"
            )

        self.order_no = order_no
        self.total_amount = total_amount
        self.return_url = return_url
        self.return_method = return_method
        self.payment_operation = payment_operation
        self.payment_method = payment_method
        self.currency = currency
        self.close_payment = close_payment
        self.ttl_sec = ttl_sec
        self.cart = cart
        self.customer = customer
        self.order = order
        self.merchant_data = (
            _pack_merchant_data(merchant_data) if merchant_data else None
        )
        self.customer_id = customer_id
        self.payment_expiry = get_payment_expiry(payment_expiry)
        self.page_appearance = page_appearance

    def _get_params_sequence(self) -> tuple:
        return (
            self.merchant_id,
            self.order_no,
            self.dttm,
            self.payment_operation.value,
            self.payment_method.value,
            self.total_amount,
            self.currency.value,
            self.close_payment,
            self.return_url,
            self.return_method.value,
            self.cart.to_sign_text(),
            self.customer.to_sign_text() if self.customer else None,
            self.order.to_sign_text() if self.order else None,
            self.merchant_data,
            self.customer_id,
            self.page_appearance.language.value,
            self.ttl_sec,
            self.page_appearance.logo_version,
            self.page_appearance.color_scheme_version,
            self.payment_expiry,
        )

    def _as_json(self) -> dict:
        return {
            "orderNo": self.order_no,
            "totalAmount": self.total_amount,
            "returnUrl": self.return_url,
            "returnMethod": self.return_method.value,
            "payOperation": self.payment_operation.value,
            "payMethod": self.payment_method.value,
            "closePayment": self.close_payment,
            "currency": self.currency.value,
            "ttlSec": self.ttl_sec,
            "cart": self.cart.as_json(),
            "customer": self.customer.as_json() if self.customer else None,
            "order": self.order.as_json() if self.order else None,
            "merchantData": self.merchant_data,
            "customerId": self.customer_id,
            "language": self.page_appearance.language.value,
            "logoVersion": self.page_appearance.logo_version,
            "colorSchemeVersion": self.page_appearance.color_scheme_version,
            "customExpiry": self.payment_expiry,
        }
