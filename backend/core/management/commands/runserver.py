"""Development ASGI runserver — REST + WebSockets via uvicorn."""

from __future__ import annotations

import os
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start the development ASGI server (HTTP + WebSockets) with auto-reload."

    default_addr = "127.0.0.1"
    default_port = "8000"

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            help="Optional port number or ipaddr:port (default 127.0.0.1:8000).",
        )
        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Disable auto-reload.",
        )
        parser.set_defaults(use_reloader=True)

    def handle(self, *args, **options):
        addrport = options.get("addrport") or f"{self.default_addr}:{self.default_port}"
        if ":" in addrport:
            host, port = addrport.rsplit(":", 1)
        else:
            host, port = self.default_addr, addrport

        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development"),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting VoteBridge ASGI server at http://{host}:{port}/ (WebSockets enabled)"
            )
        )

        import uvicorn

        backend_root = Path(__file__).resolve().parents[3]
        uvicorn.run(
            "config.asgi:application",
            host=host,
            port=int(port),
            reload=options["use_reloader"],
            reload_dirs=[str(backend_root)],
            log_level="info",
        )
