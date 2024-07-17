"""Response wrapper for payment/status."""

from typing import Optional

from ..signature import SignedModel
from .base import PaymentStatus, Response, get_payment_status


class Endpoint(SignedModel):
    """Browser init."""

    def __init__(
        self,
        url: str,
        method: Optional[str] = None,
        vars: Optional[dict] = None,  # pylint:disable=redefined-builtin
    ) -> None:
        self.url = url
        self.method = method
        self.vars = vars

    @classmethod
    def from_json(cls, response: dict) -> "Endpoint":
        """Return browser init result from JSON."""
        return cls(
            response["url"], response.get("method"), response.get("vars")
        )

    def _get_params_sequence(self) -> tuple:
        return (self.url, self.method, self.vars)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"url='{self.url}', "
            f"method={self.method}, "
            f"vars={self.vars}"
            ")"
        )


class SDKInit(SignedModel):
    """SDK init."""

    def __init__(
        self, directory_server_id: str, scheme_id: str, message_version: str
    ) -> None:
        self.directory_server_id = directory_server_id
        self.scheme_id = scheme_id
        self.message_version = message_version

    @classmethod
    def from_json(cls, response: dict) -> "SDKInit":
        """Return SDK init result from JSON."""
        return cls(
            response["directory_server_id"],
            response["scheme_id"],
            response["message_version"],
        )

    def _get_params_sequence(self) -> tuple:
        return (
            self.directory_server_id,
            self.scheme_id,
            self.message_version,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"directory_server_id='{self.directory_server_id}', "
            f"scheme_id='{self.scheme_id}', "
            f"message_version='{self.message_version}'"
            ")"
        )


class SDKChallenge(SignedModel):
    """SDK challenge."""

    def __init__(
        self,
        three_dsserver_trans_id: str,
        acs_reference_number: str,
        acs_trans_id: str,
        acs_signed_content: str,
    ) -> None:
        self.three_dsserver_trans_id = three_dsserver_trans_id
        self.acs_reference_number = acs_reference_number
        self.acs_trans_id = acs_trans_id
        self.acs_signed_content = acs_signed_content

    @classmethod
    def from_json(cls, response: dict) -> "SDKChallenge":
        """Return SDK challenge result from JSON."""
        return cls(
            response["three_dsserver_trans_id"],
            response["acs_reference_number"],
            response["acs_trans_id"],
            response["acs_signed_content"],
        )

    def _get_params_sequence(self) -> tuple:
        return (
            self.three_dsserver_trans_id,
            self.acs_reference_number,
            self.acs_trans_id,
            self.acs_signed_content,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"three_dsserver_trans_id='{self.three_dsserver_trans_id}', "
            f"acs_reference_number='{self.acs_reference_number}', "
            f"acs_trans_id='{self.acs_trans_id}', "
            f"acs_signed_content='{self.acs_signed_content}'"
            ")"
        )


class Fingerprint(SignedModel):
    """Fingerprint."""

    def __init__(
        self,
        browser_init: Optional[Endpoint] = None,
        sdk_init: Optional[SDKInit] = None,
    ) -> None:
        self.browser_init = browser_init
        self.sdk_init = sdk_init

    @classmethod
    def from_json(cls, response: dict) -> "Fingerprint":
        """Return fingerprint result from JSON."""
        return cls(
            (
                Endpoint.from_json(response["browserInit"])
                if response.get("browserInit")
                else None
            ),
            (
                SDKInit.from_json(response["sdkInit"])
                if response.get("sdkInit")
                else None
            ),
        )

    def _get_params_sequence(self) -> tuple:
        return (
            self.browser_init.to_sign_text() if self.browser_init else None,
            self.sdk_init.to_sign_text() if self.sdk_init else None,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"browser_init={self.browser_init}, "
            f"sdk_init={self.sdk_init}"
            ")"
        )


class Authenticate(SignedModel):
    """Authenticate."""

    def __init__(
        self,
        browser_challenge: Optional[Endpoint] = None,
        sdk_challenge: Optional[SDKChallenge] = None,
    ) -> None:
        self.browser_challenge = browser_challenge
        self.sdk_challenge = sdk_challenge

    @classmethod
    def from_json(cls, response: dict) -> "Authenticate":
        """Return authenticate result from JSON."""
        return cls(
            (
                Endpoint.from_json(response["browserChallenge"])
                if response.get("browserChallenge")
                else None
            ),
            (
                SDKChallenge.from_json(response["sdkChallenge"])
                if response.get("sdkChallenge")
                else None
            ),
        )

    def _get_params_sequence(self) -> tuple:
        return (
            (
                self.browser_challenge.to_sign_text()
                if self.browser_challenge
                else None
            ),
            self.sdk_challenge.to_sign_text() if self.sdk_challenge else None,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"browser_challenge={self.browser_challenge}, "
            f"sdk_challenge={self.sdk_challenge}"
            ")"
        )


class Actions(SignedModel):
    """Actions."""

    def __init__(
        self,
        fingerprint: Optional[Fingerprint] = None,
        authenticate: Optional[Authenticate] = None,
    ) -> None:
        self.fingerprint = fingerprint
        self.authenticate = authenticate

    @classmethod
    def from_json(cls, response: dict) -> "Actions":
        """Return actions result from JSON."""
        return cls(
            (
                Fingerprint.from_json(response["fingerprint"])
                if response.get("fingerprint")
                else None
            ),
            (
                Authenticate.from_json(response["authenticate"])
                if response.get("authenticate")
                else None
            ),
        )

    def _get_params_sequence(self) -> tuple:
        return (
            self.fingerprint.to_sign_text() if self.fingerprint else None,
            self.authenticate.to_sign_text() if self.authenticate else None,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"fingerprint={self.fingerprint}, "
            f"authenticate={self.authenticate}"
            ")"
        )


class PaymentStatusResponse(Response):
    """Payment status response."""

    def __init__(
        self,
        pay_id: str,
        dttm: str,
        result_code: int,
        result_message: str,
        payment_status: Optional[PaymentStatus] = None,
        auth_code: Optional[str] = None,
        status_detail: Optional[str] = None,
        actions: Optional[Actions] = None,
    ):
        super().__init__(dttm, result_code, result_message)
        self.pay_id = pay_id
        self.payment_status = payment_status
        self.auth_code = auth_code
        self.status_detail = status_detail
        self.actions = actions

    @classmethod
    def _from_json(
        cls, response: dict, dttm: str, result_code: int, result_message: str
    ) -> "PaymentStatusResponse":
        """Return payment status result from JSON."""
        return cls(
            response["payId"],
            dttm,
            result_code,
            result_message,
            (
                get_payment_status(response["paymentStatus"])
                if response.get("paymentStatus")
                else None
            ),
            response.get("authCode"),
            response.get("statusDetail"),
            (
                Actions.from_json(response["actions"])
                if response.get("actions")
                else None
            ),
        )

    def _get_params_sequence(self) -> tuple:
        return (
            self.pay_id,
            self.dttm,
            self.result_code,
            self.result_message,
            self.payment_status.value if self.payment_status else None,
            self.auth_code,
            self.status_detail,
            self.actions.to_sign_text() if self.actions else None,
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"pay_id='{self.pay_id}', "
            f"dttm='{self.dttm}', "
            f"result_code={self.result_code}, "
            f"result_message='{self.result_message}', "
            f"payment_status={self.payment_status}, "
            f"auth_code={self.auth_code}, "
            f"status_detail={self.status_detail}, "
            f"actions={self.actions}"
            ")"
        )
