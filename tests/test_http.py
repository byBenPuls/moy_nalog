import pytest

from moy_nalog.http import HttpConnection
from moy_nalog.types import Credentials


@pytest.fixture
def connection():
    return HttpConnection(Credentials("1", "2"))


@pytest.fixture
def sms_connection():
    return HttpConnection()


class TestHttp:
    @pytest.mark.asyncio
    async def test_connection(self, connection: HttpConnection):
        response = await connection.client.get("https://example.com")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sms_connection(self, sms_connection: HttpConnection):
        response = await sms_connection.client.get("https://example.com")
        assert response.status_code == 200
