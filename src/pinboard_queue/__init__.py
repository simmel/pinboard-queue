__version__ = "0.1.0"

import logging
import typing

import click
import uamqp  # type: ignore
from uamqp import authentication

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str):
    """A Pinboard.in feed to Message Queue doer"""
    url = uamqp.compat.urlparse(amqp_url)
    plain_auth = authentication.SASLPlain(
        hostname=url.hostname,
        username=url.username,
        password=url.password,
        encoding="UTF-8",
    )
    target = "queue://{}/".format(url.path)
    send_client = uamqp.SendClient(target, auth=plain_auth, debug=False)
    header = uamqp.message.MessageHeader()
    header.durable = True
    msg_content = b"hello world"
    message = uamqp.Message(
        msg_content,
        header=header,
    )
    send_client.queue_message(message)
    results = send_client.send_all_messages()
    print("Message sent: {!r}".format(results))


main(auto_envvar_prefix="PINQUE")
