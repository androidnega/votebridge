"""
Helpers for building Django ALLOWED_HOSTS from environment values.

In development (DEBUG=True), Cloudflare Quick Tunnel hostnames are permitted
via leading-dot suffix entries (e.g. ``.trycloudflare.com``).
"""

from __future__ import annotations

LOCAL_DEV_HOSTS: tuple[str, ...] = ("localhost", "127.0.0.1", "[::1]")

# Django treats a leading dot as "this domain and all subdomains".
CLOUDFLARE_QUICK_TUNNEL_SUFFIXES: tuple[str, ...] = (".trycloudflare.com",)


def normalize_host_entry(host: str) -> str:
    """Normalize env host entries; map ``*.example.com`` to ``.example.com``."""
    host = host.strip()
    if not host:
        return host
    if host.startswith("*."):
        return host[1:]
    return host


def parse_allowed_hosts(
    raw_hosts: list[str] | tuple[str, ...] | None,
    *,
    debug: bool = False,
    include_local_defaults: bool = False,
) -> list[str]:
    """
    Build a deduplicated ALLOWED_HOSTS list.

    When ``debug`` is True, Cloudflare Quick Tunnel suffixes are appended so
    ephemeral ``*.trycloudflare.com`` hostnames work during local development.
    Production must pass ``debug=False`` and rely on explicit host entries only.
    """
    hosts: list[str] = []
    seen: set[str] = set()

    def add(host: str) -> None:
        normalized = normalize_host_entry(host)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        hosts.append(normalized)

    for host in raw_hosts or []:
        add(host)

    if include_local_defaults:
        for host in LOCAL_DEV_HOSTS:
            add(host)

    if debug:
        for suffix in CLOUDFLARE_QUICK_TUNNEL_SUFFIXES:
            add(suffix)

    return hosts
