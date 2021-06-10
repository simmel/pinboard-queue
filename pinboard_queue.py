__version__ = "0.1.0"

import logging
import os
from typing import Dict

import capnp  # type: ignore
import click
import pika  # type: ignore

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# pika is too verbose
logging.getLogger("pika").setLevel(logging.INFO)


def boolify_post(post: Dict):
    for k in ["shared", "toread"]:
        post[k] = True if post[k].lower() == "on" else False
    return post


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str):
    """A Pinboard.in feed to Message Queue doer"""
    recent_post = recent_posts["posts"][0]
    recent_post = boolify_post(recent_post)
    pinboard_post_schema = os.path.dirname(__file__) + "/pinboard_post.capnp"
    pinboard_post = capnp.load(pinboard_post_schema)
    post = pinboard_post.PinboardPost.new_message(**recent_post)
    post_bytes = post.to_bytes()
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.confirm_delivery()
    channel.exchange_declare(exchange="pinboard", exchange_type="topic")
    channel.basic_publish(
        exchange="pinboard",
        routing_key="pinboard.recent",
        body=post_bytes,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            message_id=post.meta,
        ),
    )
    log.info(
        "Message sent",
        extra={k: v for k, v in recent_post.items() if k in ["meta", "time"]},
    )
    log.debug("Message sent", extra={"post": post})
    connection.close()


main(auto_envvar_prefix="PINQUE")
