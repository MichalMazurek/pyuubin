import logging
import re
from base64 import b64decode
from pathlib import Path
from typing import Dict, Optional, Tuple

import bcrypt
from fastapi import FastAPI
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
    Response,
)
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from pyuubin.exceptions import Forbidden

log = logging.getLogger(__name__)

_basic_matcher = re.compile(r"^[bB]asic[ ]+(\w+)$")


class ForbiddenResponse(PlainTextResponse):
    def __init__(self):
        super().__init__("Forbidden.", status_code=401)


def load_user_db(htpasswd_file: str) -> Dict[str, str]:

    users = {}
    users.update(
        (
            line.strip().split(":", 1)
            for line in Path(htpasswd_file).read_text().splitlines()
        )
    )

    return users


def password_matches(plain_text_password, crypted_password) -> bool:

    try:
        return bcrypt.checkpw(
            plain_text_password.encode("utf8"), crypted_password.encode("utf8")
        )
    except ValueError:
        return False


def get_user_password(token: str) -> Tuple[str, str]:

    try:
        basic_token = re.search(_basic_matcher, token).group(1)
        username, password = (
            b64decode(basic_token).decode("utf8").split(":", 1)
        )
        return username, password

    except AttributeError:
        raise ValueError("Couldn't retrieve username and password.")


class BasicAuthMiddleware(BaseHTTPMiddleware):

    user_db: Dict[str, str]

    def __init__(self, *args, htpasswd_file: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_db = (
            load_user_db(htpasswd_file) if htpasswd_file is not None else {}
        )

    def verify_user(self, auth_header: str):

        try:
            user, password = get_user_password(auth_header)
            if not password_matches(password, self.user_db[user]):
                log.warn(
                    f"Password doesn't match the on on record for user {user}"
                )
                raise Forbidden()
        except KeyError:
            log.warn(f"Can't find {user} in user list.")
            raise Forbidden()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            auth_header = request.headers["Authorization"]
            self.verify_user(auth_header)
        except (Forbidden, KeyError):
            return ForbiddenResponse()

        response = await call_next(request)
        return response


def add_authentication(app: FastAPI, htpasswd_file: str):

    app.add_middleware(BasicAuthMiddleware, htpasswd_file=htpasswd_file)
