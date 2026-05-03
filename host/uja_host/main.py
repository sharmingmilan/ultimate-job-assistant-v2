"""FastAPI app + uvicorn entrypoint for the UJA local web host.

Usage:
    python -m uja_host.main [--project-root PATH] [--bind HOST] [--port PORT]

Defaults: 127.0.0.1:0 (random ephemeral port). Project root is read from
~/.uja/config.json if not passed; if neither exists, the server starts but
endpoints that need a root return 409 until /api/config/project-root is set.
"""

from __future__ import annotations

import argparse
import logging
import sys
import webbrowser

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uja_host import __version__, config as host_config
from uja_host.api import auth, chat, changes, config as config_api, conversations, files as files_api, questions


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ultimate Job Assistant — local host",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
    )

    # Localhost-only frontends in dev (Vite dev server typically on :5173).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(config_api.router)
    app.include_router(auth.router)
    app.include_router(conversations.router)
    app.include_router(chat.router)
    app.include_router(files_api.router)
    app.include_router(changes.router)        # Phase 17.5: change-set approve/reject
    app.include_router(questions.router)      # Phase 17.5: pending-question answer

    @app.get("/api/health", tags=["meta"])
    def health():
        cfg = host_config.load_config()
        return {
            "ok": True,
            "version": __version__,
            "project_root_configured": cfg.project_root is not None,
        }


    # ----- Frontend static files (Phase 17) -----
    # In production, FastAPI serves the Vite-built SPA from host/frontend/dist/.
    # In dev, Vite runs on :5173 with /api proxied here, so this mount is absent.
    from pathlib import Path as _Path
    from fastapi.staticfiles import StaticFiles as _StaticFiles
    _here = _Path(__file__).resolve().parent
    _dist = (_here.parent / "frontend" / "dist").resolve()
    if _dist.is_dir():
        # html=True makes StaticFiles serve index.html for missing routes
        # (SPA history mode). API routes still match first because FastAPI
        # checks them before falling through to mounted static files.
        app.mount("/", _StaticFiles(directory=str(_dist), html=True), name="frontend")

    return app


app = create_app()


def _parse_args(argv):
    p = argparse.ArgumentParser(prog="uja-host")
    p.add_argument("--project-root", type=str, default=None,
                   help="Set project root before launching (overrides ~/.uja/config.json)")
    p.add_argument("--bind", type=str, default="127.0.0.1",
                   help="Bind address. Default 127.0.0.1 (recommended). "
                        "0.0.0.0 exposes to LAN; only set this if you know what you're doing.")
    p.add_argument("--port", type=int, default=0, help="Port. 0 = random ephemeral.")
    p.add_argument("--no-browser", action="store_true", help="Do not auto-open browser.")
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if args.project_root:
        try:
            host_config.set_project_root(args.project_root)
        except ValueError as e:
            print("ERROR: " + str(e), file=sys.stderr)
            sys.exit(2)

    cfg = host_config.load_config()
    if cfg.project_root is None:
        print("WARNING: no project_root set. Open the web UI to configure, "
              "or relaunch with --project-root /path/to/folder.", file=sys.stderr)

    print()
    print("  Ultimate Job Assistant host (v" + __version__ + ")")
    port_label = str(args.port) if args.port else "<random>"
    print("  -> binding " + args.bind + ":" + port_label)
    if cfg.project_root:
        print("  -> project root: " + cfg.project_root)
    print()

    if not args.no_browser and args.port:
        url = "http://" + args.bind + ":" + str(args.port)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    config = uvicorn.Config(app, host=args.bind, port=args.port, log_level="info")
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
