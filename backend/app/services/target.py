import ipaddress
import re
from urllib.parse import urlparse

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
)


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        raise ValueError("Target bo'sh bo'lishi mumkin emas.")

    parsed = urlparse(target if "://" in target else f"//{target}")
    host = parsed.hostname or target
    host = host.strip().lower().rstrip(".")

    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass

    if not DOMAIN_RE.match(host) or "." not in host:
        raise ValueError("Domain, URL yoki IPv4 formatini to'g'ri kiriting.")

    return host


def http_url_for_target(target: str, prefer_https: bool = True) -> str:
    scheme = "https" if prefer_https else "http"
    return f"{scheme}://{target}"

