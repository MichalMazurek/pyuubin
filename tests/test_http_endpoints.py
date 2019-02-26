import yuubin.settings as settings
import pytest
from yuubin.db import unpack, _t_id
from yuubin.models import Mail
from yuubin.health import update_health


async def test_send(test_cli, mock_aioredis):

    response = await test_cli.post(
        "/api/v1/send", json={"to": ["test@example.com"], "cc": [], "subject": "Test Email", "text": "Some text"}
    )

    assert response.status == 200, await response.json()

    mail = Mail(**unpack(await mock_aioredis.rpop(settings.REDIS_MAIL_QUEUE)))

    assert mail.to[0] == "test@example.com"


async def test_health(test_cli):

    update_health("test.smth", "test")

    response = await test_cli.get("/health")
    assert response.status == 200
    status = await response.json()

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


async def test_adding_templates(test_cli, mock_aioredis):

    response = await test_cli.post("/api/v1/template/", json={"template_id": "template1", "content": TEST_TEMPLATE})
    response_json = await response.json()
    assert response.status == 201

    template: bytes = await mock_aioredis.get(_t_id("template1"))

    assert template.decode("utf8") == TEST_TEMPLATE


async def test_remove_templates(test_cli, mock_aioredis):

    response = await test_cli.post("/api/v1/template/", json={"template_id": "template1", "content": TEST_TEMPLATE})
    response_json = await response.json()
    assert response.status == 201

    response = await test_cli.post("/api/v1/template/template1/delete", json="")

    response_json = await response.json()
    assert response.status == 204

    template: bytes = await mock_aioredis.get(_t_id("template1"))
    assert template is None
