from httpx import AsyncClient, HTTPStatusError
import pytest

from moy_nalog.http import HttpAuth, BASE_URL
from moy_nalog.types import Credentials
from moy_nalog.exceptions import AuthorizationError

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def auth_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("hello", "world"),
    )


@pytest.fixture
def sms_auth_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
    )


@pytest.fixture
def incorrect_inn_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("1234567890", "world"),
    )


@pytest.fixture
def incorrect_inn_or_password_instance():
    return HttpAuth(
        AsyncClient(base_url=BASE_URL),
        credentials=Credentials("3664069397", "super-strong-password"),
    )


class TestAuth:
    def test_bearer_auth(self, auth_instance: HttpAuth):
        auth = auth_instance
        assert auth._create_bearer_auth_header("123") == {"authorization": "Bearer 123"}

    @pytest.mark.asyncio
    async def test_request(self, auth_instance: HttpAuth):
        try:
            await auth_instance.make_request("/token", {"hello": "world"})
        except Exception as ex:
            assert isinstance(ex, HTTPStatusError)

    @pytest.mark.asyncio
    async def test_refresh_token(self, auth_instance: HttpAuth):
        try:
            await auth_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)

    def test_properties(self, auth_instance: HttpAuth):
        assert not auth_instance.access_token_is_active
        assert not auth_instance.is_authed

    def test_len_of_device_id(self, auth_instance: HttpAuth):
        assert len(auth_instance._create_device_id()) in (21, 22)
        # 10.12.24 on lknpd.nalog.ru length of device id is 21


class TestSmsAuth:
    def test_sms_auth_instance_not_authed(self, sms_auth_instance: HttpAuth):
        assert not sms_auth_instance.is_authed
        assert not sms_auth_instance.access_token_is_active

    @pytest.mark.asyncio
    async def test_bearer_header_without_credentials_raises(
        self, sms_auth_instance: HttpAuth
    ):
        with pytest.raises(AuthorizationError, match="verify_sms_code"):
            await sms_auth_instance.get_bearer_auth_header()

    @pytest.mark.asyncio
    async def test_request_sms_code_invalid_phone(self, sms_auth_instance: HttpAuth):
        with pytest.raises(AuthorizationError):
            await sms_auth_instance.request_sms_code("0000000000")

    @pytest.mark.asyncio
    async def test_verify_sms_code_invalid(self, sms_auth_instance: HttpAuth):
        with pytest.raises(AuthorizationError):
            await sms_auth_instance.verify_sms_code(
                "0000000000", "000000", "invalid-token"
            )


class TestServerResponseMessages:
    @pytest.mark.asyncio
    async def test_incorrect_inn(self, incorrect_inn_instance: HttpAuth):
        try:
            await incorrect_inn_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)
            assert str(ex) == "Указанный Вами ИНН некорректен"

    @pytest.mark.asyncio
    async def test_incorrect_inn_or_password(
        self, incorrect_inn_or_password_instance: HttpAuth
    ) -> None:
        try:
            await incorrect_inn_or_password_instance.get_bearer_auth_header()
        except Exception as ex:
            assert isinstance(ex, AuthorizationError)
            print(ex)
            assert str(ex) == "Неверный логин или пароль"
