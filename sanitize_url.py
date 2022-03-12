import urllib.parse

import urllib3.exceptions  # type: ignore
import wrapt  # type: ignore


def sanitize_url(url: str) -> str:
    url_parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(url_parsed.query)
    for q in qs:
        for s in ["password", "token", "secret", "key"]:
            if s in q.lower():
                qs[q] = "xxx"  # type: ignore[assignment] # We are replacing a List with a string
    url_parsed = url_parsed._replace(query=urllib.parse.urlencode(qs, doseq=True))
    return urllib.parse.urlunparse(url_parsed)


def infect() -> None:
    @wrapt.patch_function_wrapper(urllib3.exceptions.MaxRetryError, "__init__")
    def maxretryerror(wrapped, instance, args, kwargs):  # type: ignore
        pool, url, reason = args
        instance.reason = reason
        url = sanitize_url(url)
        message = "Max retries exceeded with url: %s (Caused by %r)" % (url, reason)
        urllib3.exceptions.RequestError.__init__(instance, pool, url, message)
