"""Customer data."""

from typing import Optional

from ....signature import SignedModel
from ...fields import _StrField
from .account import AccountData
from .login import LoginData


class PhoneNumber:
    """Phone number."""

    def __init__(self, prefix: str, subscriber: str) -> None:
        """Phone number in format <prefix>.<subscriber>."""
        self.prefix = prefix
        self.subscriber = subscriber

    def __str__(self) -> str:
        return f"{self.prefix}.{self.subscriber}"


class CustomerData(SignedModel):
    """Customer information."""

    name = _StrField(max_length=45)
    email = _StrField(max_length=100)

    def __init__(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        home_phone: Optional[PhoneNumber] = None,
        work_phone: Optional[PhoneNumber] = None,
        mobile_phone: Optional[PhoneNumber] = None,
        account: Optional[AccountData] = None,
        login: Optional[LoginData] = None,
    ) -> None:
        self.name = name
        self.email = email
        self.home_phone = home_phone
        self.work_phone = work_phone
        self.mobile_phone = mobile_phone
        self.account = account
        self.login = login

    def as_json(self) -> dict:
        """Return customer data as JSON."""
        result = {}
        if self.name:
            result["name"] = self.name
        if self.email:
            result["email"] = self.email
        if self.home_phone:
            result["homePhone"] = str(self.home_phone)
        if self.work_phone:
            result["workPhone"] = str(self.work_phone)
        if self.mobile_phone:
            result["mobilePhone"] = str(self.mobile_phone)
        if self.account:
            result["account"] = self.account.as_json()
        if self.login:
            result["login"] = self.login.as_json()
        return result

    def _get_params_sequence(self) -> tuple:
        return (
            self.name,
            self.email,
            self.home_phone,
            self.work_phone,
            self.mobile_phone,
            self.account,
            self.login,
        )
