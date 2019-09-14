from typing import Any, Dict

from fastapi import Body, FastAPI
from pydantic import BaseModel

from pyuubin.db import redisdb
from pyuubin.health import get_health
from pyuubin.models import Mail, Template
from pyuubin.templates import Templates

app = FastAPI(title="Pyuubin - Mailing System", openapi_prefix="/api/v1/")


class APIOK(BaseModel):
    message: str


@app.post("/send", response_model=APIOK)
async def send_email(mail: Mail = Body(...)) -> APIOK:

    await redisdb.add_mail(mail)
    return APIOK(message="OK")


class Stats(BaseModel):
    mail_queue_size: int


@app.get("/stats", response_model=Stats)
async def stats() -> Stats:
    return Stats(mail_queue_size=await redisdb.mail_queue_size())


@app.post("/template", status_code=201, response_model=APIOK)
async def add_template(template: Template) -> APIOK:
    await redisdb.add_template(template)
    return APIOK(message="ok")


@app.post(
    "/template/{template_id}/delete", status_code=204, response_model=APIOK
)
async def remove_template(template_id: str) -> APIOK:

    await redisdb.remove_template(template_id)
    return APIOK(message="ok")


@app.post("/template/{template_id}/render")
async def render_template(template_id: str, parameters: Dict[str, Any]) -> str:

    templates = Templates(await redisdb.load_templates())
    return await templates.render(template_id, parameters)


@app.post("/template/test-render")
async def render_test_template(
    template: str = Body(...), parameters: Dict[str, Any] = Body(...)
) -> str:

    templates = Templates({"test-template": template})
    return await templates.render("test-template", parameters)


@app.get("/health")
async def health_endpoint() -> Dict[str, Any]:
    return get_health()
