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
logging.getLogger("pika").setLevel(logging.ERROR)

recent_posts: Dict = {
    "date": "2021-04-30T17:58:10Z",
    "user": "simmel",
    "posts": [
        {
            "href": "https:\/\/tech.olx.com\/improving-jvm-warm-up-on-kubernetes-1b27dd8ecd58",
            "description": "Improving JVM Warm-up on Kubernetes | by Vikas Kumar | OLX Group Engineering",
            "extended": "",
            "meta": "a02c6543c7d09f071de533c9d6137c0e",
            "hash": "452bb67270c2ff6225ac7b0ad61f8b2e",
            "time": "2021-04-30T17:58:10Z",
            "shared": "no",
            "toread": "no",
            "tags": "jvm containers",
        },
        {
            "href": "https:\/\/faun.pub\/java-application-optimization-on-kubernetes-on-the-example-of-a-spring-boot-microservice-cf3737a2219c",
            "description": "Java Application Optimization on Kubernetes on the Example of a Spring Boot Microservice | by Stephan Hartmann | FAUN",
            "extended": "",
            "meta": "30c519cba8250139723f88e9befee80e",
            "hash": "95c991eaf4d02c62b84ae4dbd03d53dc",
            "time": "2021-04-30T17:52:31Z",
            "shared": "no",
            "toread": "no",
            "tags": "jvm containers",
        },
        {
            "href": "https:\/\/github.com\/adobe\/OSAS",
            "description": "adobe\/OSAS: One Stop Anomaly Shop: Anomaly detection using two-phase approach: (a) pre-labeling using statistics, Natural Language Processing and static rules; (b) anomaly scoring using supervised and unsupervised machine learning.",
            "extended": "",
            "meta": "144064c04382758980a7cde1b6d6505c",
            "hash": "e03789871a1605355c9518d3db2c9001",
            "time": "2021-04-28T19:34:17Z",
            "shared": "no",
            "toread": "no",
            "tags": "logging security",
        },
        {
            "href": "https:\/\/github.com\/marcelovicentegc\/octosync",
            "description": "marcelovicentegc\/octosync: An open-source solution to keep Github and Jira issues in sync. An alternative to Exalate and Unito.",
            "extended": "",
            "meta": "a83add6ba7554e2a1da7740c94d73387",
            "hash": "4460dc06d4dde9de0263d7025c1eb56e",
            "time": "2021-04-25T13:30:08Z",
            "shared": "no",
            "toread": "no",
            "tags": "issue tracking work",
        },
        {
            "href": "https:\/\/www.linkedin.com\/pulse\/improving-team-productivity-reducing-context-karen-casella\/",
            "description": "Improving Team Productivity by Reducing Context Switching",
            "extended": "<blockquote>A challenge that many engineering teams face is project and task fragmentation.\u00a0Engineers often work on multiple projects in parallel and can be severely interrupt-driven by operational issues and partner support requests.<\/blockquote>",
            "meta": "a45093aceb3c5c194720b98ff5d07df7",
            "hash": "ec9fa7a4d02910b50fb99c5b9fb16b3e",
            "time": "2021-04-24T17:53:49Z",
            "shared": "no",
            "toread": "no",
            "tags": "work meetings productivity",
        },
        {
            "href": "https:\/\/status.auth0.com\/incidents\/zvjzyc7912g5",
            "description": "Increased errors in Auth0 \u2022 Auth0 Status Page",
            "extended": "",
            "meta": "1cdf58acfddc8a6117fa2150b6388965",
            "hash": "40097882887c054722bd5f2b1ef05544",
            "time": "2021-04-21T18:21:08Z",
            "shared": "no",
            "toread": "no",
            "tags": "iam aas",
        },
        {
            "href": "https:\/\/www.alchemists.io\/articles\/docker_multi-platform_images\/",
            "description": "Docker Multi-Platform Images | Alchemists",
            "extended": "",
            "meta": "c2bf7f9a536d8c96efdc0c778a8af40f",
            "hash": "e54950ba55fc1922371e5d02e2ad4715",
            "time": "2021-04-21T18:18:08Z",
            "shared": "no",
            "toread": "no",
            "tags": "containers",
        },
        {
            "href": "https:\/\/medium.com\/young-coder\/ageism-in-tech-fatal-barrier-or-outdated-myth-fdf872130f1c",
            "description": "Ageism in Tech: Fatal Barrier or Outdated Myth? | Young Coder | Matthew MacDonald | Young Coder",
            "extended": "",
            "meta": "f727e7bf22af1a9e4b89bcfe8bac937c",
            "hash": "ed878c39384d0e3f37f19dc48c6c851c",
            "time": "2021-04-17T13:35:17Z",
            "shared": "no",
            "toread": "no",
            "tags": "career",
        },
        {
            "href": "https:\/\/access.redhat.com\/articles\/4409591#audit-record-types-2",
            "description": "RHEL Audit System Reference - Red Hat Customer Portal",
            "extended": "",
            "meta": "5703d9b92e95d6fb05b6181f1c10984c",
            "hash": "2b27c3ee06251a202b146a1a02ad39e2",
            "time": "2021-04-17T06:45:01Z",
            "shared": "no",
            "toread": "no",
            "tags": "security hids auditd",
        },
        {
            "href": "https:\/\/www.opencti.io\/en\/",
            "description": "OpenCTI - Open platform for cyber threat intelligence",
            "extended": "",
            "meta": "39bfe218ffc691f572c9c98e2ee7325c",
            "hash": "50574ad292e7606199ae19a0fa053cb6",
            "time": "2021-04-16T18:32:17Z",
            "shared": "no",
            "toread": "no",
            "tags": "esb security",
        },
        {
            "href": "https:\/\/github.com\/certtools\/intelmq",
            "description": "certtools\/intelmq: IntelMQ is a solution for IT security teams for collecting and processing security feeds using a message queuing protocol.",
            "extended": "",
            "meta": "6c80d3f72ebe61c39dd206a99a122b34",
            "hash": "768371527f4c129c52a0743d090fb369",
            "time": "2021-04-16T18:30:30Z",
            "shared": "no",
            "toread": "no",
            "tags": "security esb",
        },
        {
            "href": "https:\/\/reflectoring.io\/create-analyze-heapdump\/",
            "description": "Creating and Analyzing Java Heap Dumps",
            "extended": "",
            "meta": "cd4153d5215a3070abd63e1e436e5a83",
            "hash": "87d6832e532bf211272341c27934568c",
            "time": "2021-04-16T16:22:59Z",
            "shared": "no",
            "toread": "no",
            "tags": "jvm debug memory",
        },
        {
            "href": "https:\/\/yannesposito.com\/Scratch\/en\/blog\/Learn-Vim-Progressively\/",
            "description": "YBlog - Learn Vim Progressively",
            "extended": "",
            "meta": "9225b626033fc6630f494543acd10dae",
            "hash": "458dd2213c5ec07ee783d9fc1915da56",
            "time": "2021-04-15T18:07:21Z",
            "shared": "no",
            "toread": "no",
            "tags": "",
        },
        {
            "href": "https:\/\/github.com\/authorizon\/opal",
            "description": "authorizon\/opal: Policy and data administration, distribution, and real-time update* Connection #0 to host api.pinboard.in left intacts on top of Open Policy Agent",
            "extended": "",
            "meta": "a22c3d3c7c704f22f306a27bf8f2cccb",
            "hash": "064b69a3934032e2b4371b9bb6cd3524",
            "time": "2021-04-15T17:53:07Z",
            "shared": "no",
            "toread": "no",
            "tags": "authz spocp",
        },
        {
            "href": "https:\/\/pythonspeed.com\/articles\/speeding-up-docker-ci\/",
            "description": "Speeding up Dockerbuilds in CI with BuildKit",
            "extended": "",
            "meta": "577ad53b36bc16856c19b1c7de577a0e",
            "hash": "f379fff2d214b433b8fa59d99e85bb68",
            "time": "2021-04-15T15:03:56Z",
            "shared": "no",
            "toread": "no",
            "tags": "containers",
        },
    ],
}


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
    post = pinboard_post.PinboardPost.new_message(**recent_post).to_bytes()
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.confirm_delivery()
    channel.exchange_declare(exchange="pinboard", exchange_type="topic")
    channel.basic_publish(
        exchange="pinboard",
        routing_key="pinboard.recent",
        body=post,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    log.info(
        "Message sent",
        extra={k: v for k, v in recent_post.items() if k in ["meta", "time"]},
    )
    log.debug("Message sent", extra={"post": post})
    connection.close()


main(auto_envvar_prefix="PINQUE")
