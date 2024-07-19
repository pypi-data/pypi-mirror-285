import urllib.request
import urllib.parse

from .runtime import ctx


def make_get_request(url: str, headers: dict[str, str] = {}):

    if not ctx.can_read():
        ctx.add_cmd(f"make_get_request {url} {headers}")

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        charset = response.headers.get_content_charset()
        if not charset:
            charset = "utf-8"
        response_str = response.read().decode(charset)
    return response_str
