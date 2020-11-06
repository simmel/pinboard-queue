__version__ = "0.1.0"

import typing

import click


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str):
    """A Pinboard.in feed to Message Queue doer"""
    print("{!r} {!r}".format(amqp_url, pinboard_api_token))


main(auto_envvar_prefix="PINQUE")
