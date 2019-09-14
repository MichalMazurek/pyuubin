import click

from pyuubin.api.app import get_app
from pyuubin.settings import REDIS_URL


@click.command()
@click.option("--host", "-h", default="0.0.0.0")
@click.option("--port", "-p", default=8000)
def main(host: str, port: int):

    app = get_app(REDIS_URL)
    app.run(host, port)


if __name__ == "__main__":
    main()
