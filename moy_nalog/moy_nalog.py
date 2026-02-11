from __future__ import annotations

from typing import Any, Optional, Union
from datetime import datetime, date

from moy_nalog.methods import (
    AddIncomeMethod,
    CancelIncomeMethod,
    UserMethod,
)
from moy_nalog.methods.api import BaseAPI
from moy_nalog.http import HttpConnection, AuthDetails
from moy_nalog.constants import CancelType
from moy_nalog.exceptions import AuthorizationError
from moy_nalog.types import Credentials, Income, CanceledIncome, User, SmsChallenge


class MoyNalog:
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> None:
        self.__login = login
        self.__password = password
        self.__phone = phone

        self._connection: HttpConnection = self._init_http()
        self._api: BaseAPI = self._init_api()

    @property
    def credentials(self) -> Optional[Credentials]:
        if self.__login and self.__password:
            return Credentials(self.__login, self.__password)
        return None

    @property
    def auth_details(self) -> Optional[AuthDetails]:
        return self._api.connection.auth.details

    def _init_http(self) -> HttpConnection:
        return HttpConnection(self.credentials)

    def _init_api(self) -> BaseAPI:
        return BaseAPI(self._connection)

    async def request_sms_code(self) -> SmsChallenge:
        if not self.__phone:
            raise AuthorizationError(
                "Phone number is required for SMS authentication"
            )
        return await self._connection.auth.request_sms_code(self.__phone)

    async def verify_sms_code(
        self, code: str, challenge_token: str
    ) -> AuthDetails:
        if not self.__phone:
            raise AuthorizationError(
                "Phone number is required for SMS authentication"
            )
        return await self._connection.auth.verify_sms_code(
            self.__phone, code, challenge_token
        )

    async def add_income(
        self,
        name: str,
        created_at: Union[datetime, date],
        quantity: int,
        amount: Union[int, float],
    ) -> Income:
        return await AddIncomeMethod(
            api=self._api,
            name=name,
            created_at=created_at,
            quantity=quantity,
            amount=amount,
        ).execute()

    async def cancel_income(
        self, receipt_uuid: str, comment_type: CancelType
    ) -> CanceledIncome:
        return await CancelIncomeMethod(
            api=self._api, comment_type=comment_type, receipt_uuid=receipt_uuid
        ).execute()

    async def get_user_info(self) -> User:
        return await UserMethod(api=self._api).execute()

    async def __aenter__(self) -> MoyNalog:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._connection.close()

    async def close(self) -> None:
        await self._connection.close()

    def __repr__(self) -> str:
        return "MoyNalog()"

    def __hash__(self) -> int:
        if self.__login and self.__password:
            return hash(f"{self.__login}:{self.__password}")
        return hash(self.__phone)

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, MoyNalog):
            return False
        return hash(self) == hash(value)
