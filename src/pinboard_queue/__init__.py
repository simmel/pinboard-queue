__version__ = "0.1.0"

import logging
import typing

import click
import pika  # type: ignore

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str):
    """A Pinboard.in feed to Message Queue doer"""
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.confirm_delivery()
    channel.exchange_declare(exchange="pinboard", exchange_type="topic")
    channel.basic_publish(
        exchange="pinboard",
        routing_key="pinboard.recent",
        body="Hello World!",
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    print(" [x] Sent 'Hello World!'")
    connection.close()


main(auto_envvar_prefix="PINQUE")
