import time
import random
import string
from typing import Optional
from datetime import datetime
from json import JSONDecodeError
from functools import wraps

from httpx import AsyncClient, HTTPStatusError, Timeout

from moy_nalog.types import Credentials, Token, AuthDetails, SmsChallenge
from moy_nalog.exceptions import AuthorizationError, AccessTokenNotFoundError

BASE_URL = "https://lknpd.nalog.ru/api/v1"
BASE_URL_V2 = "https://lknpd.nalog.ru/api/v2"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
}


class HttpAuth:
    def __init__(
        self,
        async_client: AsyncClient,
        credentials: Optional[Credentials] = None,
    ) -> None:
        """
        This class helps to get accessToken for Bearer auth
        """
        self._async_client: AsyncClient = async_client
        self._device_id: str = self._create_device_id()
        self.__credentials: Optional[Credentials] = credentials

        self.__auth_data: Optional[AuthDetails] = None

    def handle_auth_exception(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except HTTPStatusError as ex:
                raise AuthorizationError(
                    f"{ex.response.json().get("message") or  "Success" + ex}"
                )
            except JSONDecodeError:
                raise AuthorizationError("Cannot decode auth JSON")
            except (KeyError, UnboundLocalError):
                raise AuthorizationError("Cannot find auth data in JSON response")

        return wrapper

    def _create_device_id(self) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=22))

    def _get_body(self) -> dict:
        return {
            "deviceInfo": {
                "sourceDeviceId": self._device_id,
                "sourceType": "WEB",
                "appVersion": "1.0.0",
                "metaDetails": {
                    "userAgent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        " AppleWebKit/537.36 (KHTML, like Gecko)"
                        " Chrome/131.0.0.0 Safari/537.36"
                    )
                },
            }
        }

    def _get_auth_params(self) -> dict:
        return {
            "username": self.__credentials.username,
            "password": self.__credentials.password,
        }

    def create_json_body(self, **kwargs) -> dict:
        return {**kwargs, **self._get_body()}

    def _create_bearer_auth_header(self, token: str) -> dict:
        return {"authorization": f"Bearer {token}"}

    async def make_request(self, handle: str, body: dict) -> dict:
        response = await self._async_client.post(handle, json=body)
        response.raise_for_status()
        return response.json()

    @handle_auth_exception
    async def get_token(self) -> AuthDetails:
        response = await self.make_request(
            "/auth/lkfl", self.create_json_body(**self._get_auth_params())
        )
        return AuthDetails(
            inn=response["profile"]["inn"],
            token=Token(
                value=response["token"],
                expire_in=datetime.fromisoformat(
                    response["tokenExpireIn"].replace("Z", "+00:00")
                ),
                refresh_value=response["refreshToken"],
            ),
        )

    @handle_auth_exception
    async def request_sms_code(self, phone: str) -> SmsChallenge:
        response = await self._async_client.post(
            f"{BASE_URL_V2}/auth/challenge/sms/start",
            json={
                "phone": phone,
                "requireTpToBeActive": True,
                "deviceData": {"sourceType": "WEB"},
            },
        )
        response.raise_for_status()
        data = response.json()
        return SmsChallenge(
            challenge_token=data["challengeToken"],
            expire_date=data["expireDate"],
            expire_in=data["expireIn"],
        )

    @handle_auth_exception
    async def verify_sms_code(
        self, phone: str, code: str, challenge_token: str
    ) -> AuthDetails:
        body = self.create_json_body(
            phone=phone,
            code=code,
            challengeToken=challenge_token,
        )
        response = await self.make_request("/auth/challenge/sms/verify", body)
        self.__auth_data = AuthDetails(
            inn=response["profile"]["inn"],
            token=Token(
                value=response["token"],
                expire_in=datetime.fromisoformat(
                    response["tokenExpireIn"].replace("Z", "+00:00")
                ),
                refresh_value=response["refreshToken"],
            ),
        )
        return self.__auth_data

    @handle_auth_exception
    async def update_access_token(self) -> str:
        response = await self.make_request(
            "/auth/token/",
            json=self.create_json_body(
                **{"refreshToken": self.__auth_data.token.refresh_value}
            ),
        )
        access_token = response.json().get("token")
        if access_token:
            return access_token
        raise AccessTokenNotFoundError

    @property
    def details(self) -> Optional[AuthDetails]:
        return self.__auth_data

    @property
    def is_authed(self) -> bool:
        return self.__auth_data is not None

    @property
    def access_token_is_active(self) -> bool:
        if not self.is_authed:
            return False
        if not (access_token_expired_in := self.__auth_data.token.expire_in):
            raise AccessTokenNotFoundError
        if (
            access_token_expired_in.timestamp() * 1000
            > int(time.time() * 1000) + 60 * 1000
        ):
            return True
        return False

    async def get_bearer_auth_header(self) -> dict:
        if not self.is_authed:
            if self.__credentials:
                self.__auth_data = await self.get_token()
            else:
                raise AuthorizationError(
                    "Not authenticated. Call verify_sms_code() first "
                    "or provide login/password credentials."
                )
        if not self.access_token_is_active:
            self.__auth_data.token.value = await self.update_access_token()
        return self._create_bearer_auth_header(self.__auth_data.token.value)


class HttpConnection:
    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        timeout: float = 5.0,
        read_timeout: float = 5.0,
        write_timeout: float = 5.0,
        connect_timeout: float = 5.0,
    ) -> None:
        self.__credentials: Optional[Credentials] = credentials
        self._timeout = timeout
        self._read_timeout = read_timeout
        self._write_timeout = write_timeout
        self._connect_timeout = connect_timeout

        self._async_client: AsyncClient = self._init_async_client()
        self._http_auth: HttpAuth = self._init_auth()

    def _init_async_client(self) -> AsyncClient:
        return AsyncClient(
            base_url=BASE_URL,
            headers=HEADERS,
            timeout=Timeout(
                timeout=self._timeout,
                connect=self._connect_timeout,
                read=self._read_timeout,
                write=self._write_timeout,
            ),
        )

    def _init_auth(self) -> HttpAuth:
        return HttpAuth(async_client=self._async_client, credentials=self.__credentials)

    @property
    def client(self) -> AsyncClient:
        return self._async_client

    @property
    def auth(self) -> HttpAuth:
        return self._http_auth

    async def close(self) -> None:
        await self._async_client.aclose()
