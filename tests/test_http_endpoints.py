import pytest

import pyuubin.settings as settings
from pyuubin.db import _t_id, unpack
from pyuubin.health import update_health
from pyuubin.models import Mail


def test_send(test_cli, mock_aioredis):

    response = test_cli.post(
        "/api/v1/send",
        json={
            "to": ["test@example.com"],
            "cc": [],
            "subject": "Test Email",
            "text": "Some text",
        },
    )

    assert response.status_code == 200, response.text

    mail = Mail(**unpack(mock_aioredis.me[settings.REDIS_MAIL_QUEUE].pop()))
    assert mail.to[0] == "test@example.com"


def test_health(test_cli):

    update_health("test.smth", "test")

    response = test_cli.get("/health")
    assert response.status_code == 200
    status = response.json()

    assert status["test"]["smth"] == "test"


TEST_TEMPLATE = """
<html>
    <body>
        <p>Hi {{ name }} {{ __to }}</p>
        <ul>
            {% for line in lines %}
            <li>{{ line }}</li>
        </ul>
    </body>
</html>
"""


def test_adding_templates(test_cli, mock_aioredis):
    response = test_cli.post(
        "/api/v1/template",
        json={"template_id": "template1", "content": TEST_TEMPLATE},
    )
    assert response.status_code == 201

    template: bytes = mock_aioredis.me[_t_id("template1")]

    assert template.decode("utf8") == TEST_TEMPLATE


def test_remove_templates(test_cli, mock_aioredis):

    response = test_cli.post(
        "/api/v1/template",
        json={"template_id": "template2", "content": TEST_TEMPLATE},
    )
    assert response.json()
    assert response.status_code == 201

    response = test_cli.post("/api/v1/template/template2/delete", json="")

    assert response.json()
    assert response.status_code == 204

    with pytest.raises(KeyError):
        assert mock_aioredis.me[_t_id("template2")]
