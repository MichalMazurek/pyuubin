from pyuubin.templates import Templates

TEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta test>
</head>
<body>
    {{ body }}
</body>
</html>
"""

TEST_BODY = """<h1>some test title</h1>
<p>Test Paragraph and some content</p>"""

RENDERED_TEST_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <meta test>
</head>
<body>
    {TEST_BODY}
</body>
</html>"""


async def test_templates():

    templates = Templates({"test.template": TEST_TEMPLATE})
    assert RENDERED_TEST_TEMPLATE == await templates.render("test.template", {"body": TEST_BODY})


async def test_missing_template():

    templates = Templates({})
    rendered = await templates.render("test.template", {"body": TEST_BODY})

    assert "<dd>test.template</dd>" in rendered
    assert f"<dd>{TEST_BODY}</dd>" in rendered


async def test_template_render_endpoint(test_cli):

    response = await test_cli.post("/api/v1/template", json={"template_id": "my-template", "content": TEST_TEMPLATE})
    assert response.status == 201
    response = await test_cli.post("/api/v1/template/my-template/render", json={"body": TEST_BODY})
    assert response.status == 200
    assert RENDERED_TEST_TEMPLATE == await response.json()
    response = await test_cli.post("/api/v1/template/my-templates/delete")
    assert response.status == 204


async def test_template_testing_render_endpoint(test_cli):

    response = await test_cli.post(
        "/api/v1/template-render", json={"template": TEST_TEMPLATE, "parameters": {"body": TEST_BODY}}
    )
    assert response.status == 200
    assert RENDERED_TEST_TEMPLATE == await response.json()
