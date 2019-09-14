import click
from hypercorn.run import run

from pyuubin.api.app import get_app


@click.command()
@click.option("--host", "-h", default="0.0.0.0")
@click.option("--port", "-p", default=8000)
def main(host: str, port: int):

    app = get_app()

    run(app)


if __name__ == "__main__":
    main()
