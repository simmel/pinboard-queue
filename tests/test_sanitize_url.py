import pytest

from sanitize_url import sanitize_url


@pytest.mark.parametrize(
    "url,url_sanitized",
    [
        ("https://soy.se", "https://soy.se"),
        (
            "https://soy.se/?user=simmel&password=apa",
            "https://soy.se/?user=simmel&password=xxx",
        ),
        (
            "https://soy.se/?user=simmel&TOKEN=apa",
            "https://soy.se/?user=simmel&TOKEN=xxx",
        ),
        (
            "https://soy.se/?user=simmel&secret=apa",
            "https://soy.se/?user=simmel&secret=xxx",
        ),
        ("https://soy.se/?API_KEY=apa", "https://soy.se/?API_KEY=xxx"),
    ],
)
def test_eval(url, url_sanitized):
    assert sanitize_url(url) == url_sanitized
