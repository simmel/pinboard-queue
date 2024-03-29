try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

import io
import logging
import os
import sys
from typing import Dict, Union

import capnp  # type: ignore
import click
import pika  # type: ignore
import requests
import requests.adapters
import urllib3.util.retry  # type: ignore

import sanitize_url

sanitize_url.infect()

package_name = __spec__.name  # type: ignore
# When we no longer support <3.8 this can be removed
# mypy: no-warn-unused-ignores
__metadata__ = importlib_metadata.metadata(package_name)  # type: ignore
__version__ = __metadata__["Version"]

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__metadata__["Name"])

# pika is too verbose
logging.getLogger("pika").setLevel(logging.INFO)

BEGINNING_OF_TIME = "1970-01-01T00:00:00Z"


def boolify_post(post: Dict[str, str]) -> Dict[str, Union[bool, str]]:
    return_post: Dict[str, Union[bool, str]] = {**post}
    for k in ["shared", "toread"]:
        return_post[k] = True if post[k].lower() == "on" else False
    return return_post


def create_session(auth_token: str) -> requests.sessions.Session:
    session = requests.Session()
    # <3 https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    session.hooks["response"].append(
        lambda response, *args, **kwargs: response.raise_for_status()
    )

    class TimeoutHTTPAdapter(requests.adapters.HTTPAdapter):
        DEFAULT_TIMEOUT = 2

        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            self.timeout = self.DEFAULT_TIMEOUT
            if "timeout" in kwargs:
                self.timeout = kwargs["timeout"]
                del kwargs["timeout"]
            super().__init__(*args, **kwargs)

        def send(self, request, **kwargs):  # type: ignore[no-untyped-def]
            if not kwargs.get("timeout"):
                kwargs["timeout"] = self.timeout
            return super().send(request, **kwargs)

    retries = 3
    retry = urllib3.util.retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=60,
    )
    adapter = TimeoutHTTPAdapter(timeout=10, max_retries=retry)  # type: ignore[no-untyped-call]
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    params = {
        "auth_token": auth_token,
        "format": "json",
    }
    session.params = params
    headers = {
        "User-Agent": "{}/{} (+{})".format(
            __metadata__["Name"],
            __version__,
            __metadata__["Home-page"],
        )
    }
    session.headers.update(headers)
    return session


@click.command()
@click.option("--amqp-url", required=True, show_envvar=True, help="URL to AMQP server")
@click.option(
    "--pinboard-api-token", required=True, show_envvar=True, help="Pinboard API token"
)
def main(*, amqp_url: str, pinboard_api_token: str) -> None:
    """A Pinboard.in feed to Message Queue doer"""
    update_time = BEGINNING_OF_TIME
    sleep_for = 300

    pinboard_post_schema = os.path.dirname(__file__) + "/pinboard_post.capnp"
    pinboard_post = capnp.load(pinboard_post_schema)

    session = create_session(auth_token=pinboard_api_token)

    parameters = pika.URLParameters(amqp_url)
    parameters._set_url_heartbeat(120)
    parameters._set_url_blocked_connection_timeout(10)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.confirm_delivery()
    channel.exchange_declare(exchange="pinboard", exchange_type="topic", durable=True)

    while True:

        # Sleep at the beginning of the endless loop so we can return when
        # /posts/update says there isn't any new posts.
        if update_time is not BEGINNING_OF_TIME:
            # https://pinboard.in/api/#limits
            log.info("Sleeping for %ss", sleep_for)
            connection.sleep(sleep_for)

        try:
            response = session.get(
                "https://api.pinboard.in/v1/posts/update",
            )
        except requests.exceptions.ReadTimeout as e:
            log.exception(e)
            continue

        response_posts_update = response.json()
        posts_update = response_posts_update["update_time"]
        if posts_update <= update_time:
            log.info(
                "No new updates, returning",
                extra={
                    "stored_update_time": update_time,
                    "response_update_time": posts_update,
                },
            )
            continue

        try:
            response = session.get(
                "https://api.pinboard.in/v1/posts/recent",
                params={"count": 100},
            )
        except requests.exceptions.ReadTimeout as e:
            log.exception(e)
            continue
        recent_posts = response.json()

        for recent_post in sorted(
            recent_posts["posts"], key=lambda p: p["time"]  # type: ignore[no-any-return]
        ):
            log.debug("Looping over %r", recent_post["meta"])
            if recent_post["time"] > update_time:
                log.info("Found new post %r", recent_post["meta"])
                recent_post = boolify_post(recent_post)

                post = pinboard_post.PinboardPost.new_message(**recent_post)
                post_bytes = post.to_bytes()

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
                    extra={
                        k: v for k, v in recent_post.items() if k in ["meta", "time"]
                    },
                )
                log.debug("Message sent", extra={"post": post})
                update_time = post.time
        # posts_update is when posts changed. update_time is now the time the
        # latest post was added. If we delete something e.g. posts_update is
        # newer than update_time.
        if update_time < posts_update:
            log.debug(
                "Setting update_time = posts_update",
                extra={"update_time": update_time, "posts_update": posts_update},
            )
            update_time = posts_update
    connection.close()


def cli() -> None:
    # Make stdout unbuffered https://stackoverflow.com/a/181654
    sys.stdout = io.TextIOWrapper(
        open(sys.stdout.fileno(), "wb", 0), write_through=True
    )

    main(  # pylint: disable=unexpected-keyword-arg,missing-kwoa
        auto_envvar_prefix="PINQUE"
    )


if __name__ == "__main__":
    cli()
