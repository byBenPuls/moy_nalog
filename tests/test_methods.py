import pytest

from moy_nalog import MoyNalog
from moy_nalog.exceptions import AuthorizationError


@pytest.mark.asyncio
async def test_user_method() -> None:
    nalog = MoyNalog("12345678", "strong-password")
    try:
        await nalog.get_user_info()
    except Exception as ex:
        assert isinstance(ex, AuthorizationError)


class TestSmsAuthMethods:
    @pytest.mark.asyncio
    async def test_request_sms_without_phone_raises(self):
        nalog = MoyNalog(login="123", password="456")
        with pytest.raises(AuthorizationError, match="Phone number is required"):
            await nalog.request_sms_code()

    @pytest.mark.asyncio
    async def test_verify_sms_without_phone_raises(self):
        nalog = MoyNalog(login="123", password="456")
        with pytest.raises(AuthorizationError, match="Phone number is required"):
            await nalog.verify_sms_code(code="123456", challenge_token="token")

    @pytest.mark.asyncio
    async def test_api_call_without_sms_verification_raises(self):
        nalog = MoyNalog(phone="79990001122")
        with pytest.raises(AuthorizationError, match="verify_sms_code"):
            await nalog.get_user_info()

    @pytest.mark.asyncio
    async def test_request_sms_code_invalid_phone(self):
        nalog = MoyNalog(phone="0000000000")
        with pytest.raises(AuthorizationError):
            await nalog.request_sms_code()

    @pytest.mark.asyncio
    async def test_verify_sms_code_invalid(self):
        nalog = MoyNalog(phone="0000000000")
        with pytest.raises(AuthorizationError):
            await nalog.verify_sms_code(code="000000", challenge_token="invalid")
