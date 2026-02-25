import argparse
import threading
import webbrowser
from pathlib import Path

from aiohttp import web

from flexus_client_kit.builder import bot_registry_app


def _resolve_registry_path(registry_arg: str) -> Path:
    try:
        p = Path(registry_arg)
        if p.is_absolute():
            return p.resolve()
        return (Path(__file__).resolve().parent / p).resolve()
    except OSError as e:
        raise RuntimeError(f"Cannot resolve registry path: {registry_arg}") from e


def _open_browser_after_start(url: str, delay_sec: float) -> None:
    try:
        if delay_sec <= 0:
            return
        timer = threading.Timer(delay_sec, lambda: webbrowser.open(url))
        timer.daemon = True
        timer.start()
    except Exception as e:
        raise RuntimeError(f"Cannot schedule browser open for {url}: {e}") from e


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            description="Run Bot Registry UI with a beginner-friendly root entrypoint",
        )
        parser.add_argument(
            "--registry",
            default="flexus_simple_bots/generated/bots_registry.json",
            help="Path to bots registry json (absolute or relative to repo root)",
        )
        parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
        parser.add_argument("--port", type=int, default=8777, help="Port to bind")
        parser.add_argument(
            "--no-browser",
            action="store_true",
            help="Do not auto-open browser",
        )
        parser.add_argument(
            "--open-delay-sec",
            type=float,
            default=0.8,
            help="Delay before opening browser (seconds)",
        )
        args = parser.parse_args()

        registry_path = _resolve_registry_path(args.registry)
        if not registry_path.exists():
            raise RuntimeError(f"Registry file not found: {registry_path}")

        app = web.Application()
        app["registry_path"] = registry_path
        app.router.add_get("/", bot_registry_app.index_handler)
        app.router.add_get("/bot/{bot_id}", bot_registry_app.bot_page_handler)
        app.router.add_post("/bot/{bot_id}/save", bot_registry_app.save_bot_handler)
        app.router.add_post("/build", bot_registry_app.build_handler)
        app.router.add_get("/control-plane", bot_registry_app.control_plane_handler)
        app.router.add_get("/integrations", bot_registry_app.integrations_handler)
        app.router.add_get("/integrations/{integration_key}", bot_registry_app.integration_detail_handler)
        app.router.add_get("/tools", bot_registry_app.tools_handler)
        app.router.add_get("/tools/{tool_name}", bot_registry_app.tool_detail_handler)
        app.router.add_get("/bots", bot_registry_app.bots_handler)
        app.router.add_get("/bots/{bot_id}", bot_registry_app.bot_detail_handler)

        url = f"http://{args.host}:{args.port}/"
        if not args.no_browser:
            _open_browser_after_start(url, args.open_delay_sec)

        print(f"Bot Registry UI: {url}")
        print(f"Registry: {registry_path}")
        web.run_app(app, host=args.host, port=args.port)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
