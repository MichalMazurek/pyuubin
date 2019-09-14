from base64 import b64encode

import pytest
from click.testing import CliRunner
from hypothesis import given
from hypothesis.strategies import text
from starlette.testclient import TestClient

from pyuubin.api.app import get_app
from pyuubin.auth import (
    add_authentication,
    get_user_password,
    load_user_db,
    password_matches,
)

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

    assert not password_matches(
        passwd, "$2y$05$./BIQMqWvesvVNo5RFiQ1.277hZ9WRIr6h2t3VDRrunc8XAwdKphK"
    )


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
def test_auth_cli(mock_aioredis):
    mock_aioredis.monkeypatch_module()
    with CliRunner().isolated_filesystem():
        with open("./test_htpasswd", "w") as f:
            f.write(TEST_HTPASSWD)
        app = get_app()
        add_authentication(app, "./test_htpasswd")

        with TestClient(app) as client:
            yield client


def test_auth_failure(test_auth_cli):

    response = test_auth_cli.get("/api/v1/stats")
    assert response.status_code == 401


def test_auth_success(test_auth_cli):

    working_auth = b64encode("test:test".encode("utf8")).decode("utf8")

    response = test_auth_cli.get(
        "/api/v1/stats", headers={"Authorization": f"Basic {working_auth}"}
    )
    assert response.status_code == 200
