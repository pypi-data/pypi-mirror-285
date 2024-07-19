"""API client."""

import logging
from typing import Optional, Union

from csobpg.http import HTTPClient
from csobpg.http.urllib_client import UrllibHTTPClient

from .key import FileRSAKey, RAMRSAKey, RSAKey
from .request import EchoRequest as _EchoRequest
from .request import PaymentCloseRequest as _PaymentCloseRequest
from .request import PaymentInitRequest as _PaymentInitRequest
from .request import PaymentProcessRequest as _PaymentProcessRequest
from .request import PaymentRefundRequest as _PaymentRefundRequest
from .request import PaymentReverseRequest as _PaymentReverseRequest
from .request import PaymentStatusRequest as _PaymentStatusRequest
from .request import payment_init as _payment_init
from .response import (
    PaymentCloseResponse,
    PaymentInitResponse,
    PaymentProcessResponse,
    PaymentRefundResponse,
    PaymentReverseResponse,
    PaymentStatusResponse,
)


class APIClient:
    """API client."""

    def __init__(
        self,
        merchant_id: str,
        private_key: Union[str, RSAKey],
        public_key: Union[str, RSAKey],
        base_url: str = "https://api.platebnibrana.csob.cz/api/v1.9",
        http_client: HTTPClient = UrllibHTTPClient(),
    ) -> None:
        # pylint:disable=too-many-arguments
        self.merchant_id = merchant_id
        self.base_url = base_url.rstrip("/")

        if isinstance(private_key, str):
            self.private_key = FileRSAKey(private_key)
        else:
            self.private_key = private_key

        if isinstance(public_key, str):
            self.public_key = RAMRSAKey(public_key)
        else:
            self.public_key = public_key

        self._http_client = http_client

        self._log = logging.getLogger(__name__)

    def init_payment(
        self,
        order_no: str,
        total_amount: int,
        return_url: str,
        return_method: _payment_init.ReturnMethod = _payment_init.ReturnMethod.POST,
        payment_operation: _payment_init.PaymentOperation = _payment_init.PaymentOperation.PAYMENT,
        payment_method: _payment_init.PaymentMethod = _payment_init.PaymentMethod.CARD,
        currency: _payment_init.Currency = _payment_init.Currency.CZK,
        close_payment: bool = True,
        ttl_sec: int = 600,
        cart: Optional[_payment_init.Cart] = None,
        customer: Optional[_payment_init.CustomerData] = None,
        order: Optional[_payment_init.OrderData] = None,
        merchant_data: Optional[bytes] = None,
        customer_id: Optional[str] = None,
        payment_expiry: Optional[int] = None,
        # pylint:disable=line-too-long, too-many-locals
        page_appearance: _payment_init.WebPageAppearanceConfig = _payment_init.WebPageAppearanceConfig(),
    ) -> PaymentInitResponse:
        """Init payment."""
        self._log.info(
            'Initializing payment: order_no="%s", total_amount=%s, '
            'return_url="%s", return_method=%s, payment_operation=%s, '
            "payment_method=%s, currency=%s, close_payment=%s, ttl_sec=%s, "
            "cart=%s, customer=%s, order=%s, customer_id=%s, "
            "payment_expiry=%s",
            order_no,
            total_amount,
            return_url,
            return_method,
            payment_operation,
            payment_method,
            currency,
            close_payment,
            ttl_sec,
            cart,
            customer,
            order,
            customer_id,
            payment_expiry,
        )
        request = _PaymentInitRequest(
            self.merchant_id,
            str(self.private_key),
            order_no=order_no,
            total_amount=total_amount,
            return_url=return_url,
            return_method=return_method,
            payment_operation=payment_operation,
            payment_method=payment_method,
            currency=currency,
            close_payment=close_payment,
            ttl_sec=ttl_sec,
            cart=cart,
            customer=customer,
            order=order,
            merchant_data=merchant_data,
            customer_id=customer_id,
            payment_expiry=payment_expiry,
            page_appearance=page_appearance,
        )
        return PaymentInitResponse.from_json(
            self._call_api(
                "post",
                self._build_url(request.endpoint),
                json=request.to_json(),
            ),
            str(self.public_key),
        )

    def get_payment_status(self, pay_id: str) -> PaymentStatusResponse:
        """Request payment status information."""
        self._log.info("Requesting payment status for pay_id=%s", pay_id)
        request = _PaymentStatusRequest(
            self.merchant_id, str(self.private_key), pay_id
        )
        return PaymentStatusResponse.from_json(
            self._call_api("get", url=self._build_url(request.endpoint)),
            str(self.public_key),
        )

    def reverse_payment(self, pay_id: str) -> PaymentReverseResponse:
        """Reverse payment.

        :param pay_id: payment ID
        """
        self._log.info("Reversing payment for pay_id=%s", pay_id)
        request = _PaymentReverseRequest(
            self.merchant_id, str(self.private_key), pay_id
        )
        return PaymentReverseResponse.from_json(
            self._call_api(
                "put", self._build_url(request.endpoint), request.to_json()
            ),
            str(self.public_key),
        )

    def close_payment(
        self, pay_id: str, total_amount: Optional[int] = None
    ) -> PaymentCloseResponse:
        """Close payment (move to settlement).

        :param total_amount: close the payment with this amount. It must be
          less or equal to the original amount and provided in hundredths of
          the base currency
        """
        self._log.info(
            "Closing payment for pay_id=%s, total_amount=%s",
            pay_id,
            total_amount,
        )
        request = _PaymentCloseRequest(
            self.merchant_id, str(self.private_key), pay_id, total_amount
        )
        return PaymentCloseResponse.from_json(
            self._call_api(
                "put",
                self._build_url(request.endpoint),
                json=request.to_json(),
            ),
            str(self.public_key),
        )

    def refund_payment(
        self, pay_id: str, amount: Optional[int] = None
    ) -> PaymentRefundResponse:
        """Refund payment.

        :param pay_id: payment ID
        :param amount: amount to refund. It must be less or equal to the
          original amount and provided in hundredths of the base currency.
          If not provided, the full amount will be refunded.
        """
        self._log.info(
            "Refunding payment for pay_id=%s, amount=%s", pay_id, amount
        )
        request = _PaymentRefundRequest(
            self.merchant_id, str(self.private_key), pay_id, amount
        )
        return PaymentRefundResponse.from_json(
            self._call_api(
                "put", self._build_url(request.endpoint), request.to_json()
            ),
            str(self.public_key),
        )

    def get_payment_process_url(self, pay_id: str) -> str:
        """Build payment URL.

        :param pay_id: pay_id obtained from `payment_init`
        :return: url to process payment
        """
        self._log.info("Building payment URL for pay_id=%s", pay_id)
        return self._build_url(
            _PaymentProcessRequest(
                self.merchant_id, str(self.private_key), pay_id
            ).endpoint
        )

    def echo(self) -> None:
        """Make an echo request."""
        self._log.info("Making echo request")
        request = _EchoRequest(self.merchant_id, str(self.private_key))
        self._call_api(
            "post", self._build_url(request.endpoint), request.to_json()
        )

    def process_gateway_return(self, datadict: dict) -> PaymentProcessResponse:
        """Process gateway return."""
        self._log.info("Processing gateway return %s", datadict)
        data = {}

        for key in datadict:
            data[key] = (
                int(datadict[key])
                if key in ("resultCode", "paymentStatus")
                else datadict[key]
            )

        return PaymentProcessResponse.from_json(data, str(self.public_key))

    def _call_api(
        self, method: str, url: str, json: Optional[dict] = None
    ) -> dict:
        http_response = self._http_client.request(method, url, json)
        return http_response.json or {}

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.strip('/')}/"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(merchant_id='{self.merchant_id}')"
