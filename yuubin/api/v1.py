from dataclasses import dataclass

from sanic import Blueprint
from sanic.request import Request
from sanic_transmute import add_route, describe
from schematics import Model
from schematics.types import IntType, StringType, DictType, UnionType, NumberType
from transmute_core import ResponseShapeComplex, TransmuteContext

from yuubin.models import Mail, Template
from yuubin.templates import Templates
from typing import Any, Dict

blueprint = Blueprint("v1", url_prefix="/api/v1")


@dataclass(init=False)
class APIOK(Model):
    message: str = StringType()


@describe(paths="/send", methods=["POST"], body_parameters="mail")
async def send_email(request: Request, mail: Mail) -> APIOK:

    await request.app.db.add_mail(mail)
    return {"message": "ok"}


add_route(blueprint, send_email)


@dataclass
class Stats(Model):
    mail_queue_size: int = IntType()


@describe(paths="/stats", methods="GET")
async def stats(request: Request) -> Stats:

    return {"mail_queue_size": await request.app.db.mail_queue_size()}


add_route(blueprint, stats)


@describe(paths="/template", methods="POST", body_parameters="template", success_code=201)
async def add_template(request: Request, template: Template) -> APIOK:

    await request.app.db.add_template(template)
    return APIOK({"message": "ok"})


context = TransmuteContext(response_shape=ResponseShapeComplex)
add_route(blueprint, add_template, context=context)


@describe(paths="/template/{template_id}/delete", methods="POST", success_code=204)
async def remove_template(request: Request, template_id: str) -> APIOK:

    await request.app.db.remove_template(template_id)
    return APIOK({"message": "OK"})


add_route(blueprint, remove_template)


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
