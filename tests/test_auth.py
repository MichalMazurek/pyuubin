from pyuubin.auth import load_user_db, password_matches, get_user_password, add_authentication

from hypothesis import given
from hypothesis.strategies import text
from click.testing import CliRunner
import pytest
from sanic.websocket import WebSocketProtocol
from base64 import b64encode

TEST_HTPASSWD = """test:$2y$05$./BIQMqWvesvVNo5RFiQ1.277hZ9WRIr6h2t3VDRrunc8XAwdKphK
"""


def test_loading_user_db():

    with CliRunner().isolated_filesystem():

        with open("./test_htpasswd", "w") as f:
            f.write(TEST_HTPASSWD)

        users = load_user_db("./test_htpasswd")
        assert "test" in users

        assert password_matches("test", users["test"])


@given(text())
def test_weird_password(passwd):

    assert not password_matches(passwd, "$2y$05$./BIQMqWvesvVNo5RFiQ1.277hZ9WRIr6h2t3VDRrunc8XAwdKphK")


@given(text())
def test_weird_tokens(token: str):

    with pytest.raises(ValueError):
        get_user_password(f"Basic {token}")


@given(text())
def test_weird_tokens_encoded(random_token: str):

    b_random_token = b64encode(random_token.encode("utf8")).decode("utf8")
    token = f"smth:{b_random_token}"
    with pytest.raises(ValueError):
        get_user_password(f"Basic {token}")


@pytest.fixture
def test_auth_cli(loop, app, test_client):

    with CliRunner().isolated_filesystem():
        with open("./test_htpasswd", "w") as f:
            f.write(TEST_HTPASSWD)

        add_authentication(app, "./test_htpasswd")
        yield loop.run_until_complete(test_client(app, protocol=WebSocketProtocol))


async def test_auth_failure(test_auth_cli):

    response = await test_auth_cli.get("/api/v1/")
    assert response.status == 403


async def test_auth_success(test_auth_cli):

    working_auth = b64encode("test:test".encode("utf8")).decode("utf8")

    response = await test_auth_cli.get("/api/v1/", headers={"Authorization": f"Basic {working_auth}"})
    assert response.status == 200
