__version__ = "0.1.0"

import logging
import typing

import click

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str):
    """A Pinboard.in feed to Message Queue doer"""
    print(amqp_url)


main(auto_envvar_prefix="PINQUE")
