import click

from pyuubin.settings import print_env_variables


@click.command("pyuubin")
@click.option(
    "-e",
    "--print-environment-variables",
    help="print environment variables to be put in .env file for configuration",
    type=bool,
    flag_value=True,
)
def main(print_environment_variables: bool = False):
    """Modules to be run:

    - pyuubin.worker
    - pyuubin.api

    """
    if print_environment_variables:
        print_env_variables()
        return


if __name__ == "__main__":
    main()
    pass
