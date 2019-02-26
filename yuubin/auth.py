import asyncio
import re
from base64 import b64decode
from pathlib import Path
from typing import Dict, Tuple

import bcrypt
from sanic import Sanic
from sanic.exceptions import Forbidden

_basic_matcher = re.compile(r"^[bB]asic[ ]+(\w+)$")


def load_user_db(htpasswd_file: str) -> Dict[str, str]:

    users = {}
    users.update((line.strip().split(":", 1) for line in Path(htpasswd_file).read_text().splitlines()))

    return users


def password_matches(plain_text_password, crypted_password) -> bool:

    try:
        return bcrypt.checkpw(plain_text_password.encode("utf8"), crypted_password.encode("utf8"))
    except ValueError:
        return False


def get_user_password(token: str) -> Tuple[str, str]:

    try:
        basic_token = re.search(_basic_matcher, token).group(1)
        username, password = b64decode(basic_token).decode("utf8").split(":", 1)
        return username, password

    except AttributeError:
        raise ValueError("Couldn't retrieve username and password.")


def add_authentication(app: Sanic, htpasswd_file: str):

    user_db = load_user_db(htpasswd_file)

    async def basic_auth_middleware(request):

        authorization = request.headers.get("Authorization", "")
        try:
            username, password = get_user_password(authorization)
            if not password_matches(password, user_db[username]):
                await asyncio.sleep(1)
                raise Forbidden()

        except (ValueError, KeyError):
            await asyncio.sleep(1)
            raise Forbidden("Not Authorised.")

    app.register_middleware(basic_auth_middleware, "request")
