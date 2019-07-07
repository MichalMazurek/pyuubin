from dataclasses import dataclass

from sanic import Blueprint
from sanic.request import Request
from sanic_transmute import add_route, describe
from schematics import Model
from schematics.types import IntType, StringType, DictType, UnionType, NumberType
from transmute_core import ResponseShapeComplex, TransmuteContext

from pyuubin.models import Mail, Template
from pyuubin.templates import Templates
from pyuubin.db import redisdb
from typing import Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel

blueprint = Blueprint("v1", url_prefix="/api/v1")

app = FastAPI()


class APIOK(BaseModel):
    message: str


@app.post("/send", response_model=APIOK)
async def send_email(mail: Mail) -> APIOK:

    await redisdb.add_mail(mail)
    return APIOK(message="OK")


class Stats(BaseModel):
    mail_queue_size: int


@app.get("/stats", response_model=Stats)
async def stats(request: Request) -> Stats:

    return Stats(mail_queue_size=await request.app.db.mail_queue_size())


@app.post("/template", status_code=201, response_model=APIOK)
async def add_template(request: Request, template: Template) -> APIOK:
    await redisdb.add_template(template)
    return APIOK({"message": "ok"})


@describe(paths="/template/{template_id}/delete", methods="POST", success_code=204)
@app.post("/template/{template_id}/delete", status_code=204, response_model=APIOK)
async def remove_template(request: Request, template_id: str) -> APIOK:

    await request.app.db.remove_template(template_id)
    return APIOK({"message": "OK"})


@describe(paths="/template/{template_id}/render", methods="POST", body_parameters="parameters")
async def render_template(request: Request, template_id: str, parameters: Dict[str, Any]) -> str:

    templates = Templates(await request.app.db.load_templates())
    return await templates.render(template_id, parameters)


add_route(blueprint, render_template)


class TestingTemplate(Model):

    template: str = StringType(required=True)
    parameters: Dict[str, Any] = DictType(UnionType(types=[StringType, NumberType]), required=True)


@describe(paths="/template-render", methods="POST", body_parameters="testing_template")
async def render_template(request: Request, testing_template: TestingTemplate) -> str:

    templates = Templates({"_test": testing_template.template})
    return await templates.render("_test", testing_template.parameters)


add_route(blueprint, render_template)
