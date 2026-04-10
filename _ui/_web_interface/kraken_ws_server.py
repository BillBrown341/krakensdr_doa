"""
KrakenSDR WebSocket broadcast server.

Runs in its own background daemon thread with a dedicated asyncio event loop,
completely independent of the dash_devices / Quart server on port 8080.
This means clients can connect and receive data immediately at application
startup — no browser needs to be open.

Endpoint
--------
    ws://<host>:<WS_PORT>/ws/kraken          (default port 8082)

Every message is a JSON object whose first key is 'type':

    { "type": "doa",      "timestamp": <epoch_ms>, ... }
    { "type": "spectrum", "timestamp": <epoch_ms>, ... }
    { "type": "settings", "timestamp": <epoch_ms>, ... }

On connect the client immediately receives the last-known settings snapshot
so it always has the current device configuration without waiting for a change.

Thread-safety
-------------
Signal-processor and fetch_dsp_data timer threads call broadcast_from_thread()
which is a non-blocking, thread-safe fire-and-forget that schedules the
async send onto the WS server's own event loop.
"""

import asyncio
import json
import logging
import threading
from typing import Optional

from quart import Quart
from quart import websocket as ws_ctx

logger = logging.getLogger(__name__)

# ── shared state ──────────────────────────────────────────────────────────────

# One asyncio.Queue per connected client.
_ws_clients: set = set()

# The event loop running inside the WS server thread.  Set by start_server()
# before the serve loop begins; None until then.
_event_loop: Optional[asyncio.AbstractEventLoop] = None

# Last settings payload as a serialised JSON string.  Written synchronously by
# cache_settings() so it is available even before the server starts.
_last_settings: Optional[str] = None

# ── internal Quart app ────────────────────────────────────────────────────────

_ws_app = Quart(__name__)
_ws_app.logger.setLevel(logging.WARNING)


@_ws_app.websocket("/ws/kraken")
async def _ws_kraken():
    q: asyncio.Queue = asyncio.Queue(maxsize=20)
    _ws_clients.add(q)
    logger.info("WS client connected (%d total)", len(_ws_clients))
    try:
        # Send cached settings snapshot immediately so the client has current
        # device configuration without waiting for a settings-change event.
        if _last_settings is not None:
            await ws_ctx.send(_last_settings)
        while True:
            message = await q.get()
            await ws_ctx.send(message)
    except Exception:
        pass
    finally:
        _ws_clients.discard(q)
        logger.info("WS client disconnected (%d total)", len(_ws_clients))


# ── public API ────────────────────────────────────────────────────────────────

def cache_settings(payload: dict) -> None:
    """Synchronously cache the settings payload.

    Called by save_configuration() *before* broadcast_from_thread() so the
    snapshot is always current — even at startup before the event loop exists.
    """
    global _last_settings
    _last_settings = json.dumps(payload)


async def broadcast_to_ws(payload: dict) -> None:
    """Coroutine: put a JSON message on every connected client's queue.

    Uses put_nowait() so a slow client never blocks the pipeline.
    """
    message = json.dumps(payload)
    slow_clients: set = set()
    for q in list(_ws_clients):
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            slow_clients.add(q)
        except Exception:
            slow_clients.add(q)
    _ws_clients.difference_update(slow_clients)


def broadcast_from_thread(payload: dict) -> None:
    """Thread-safe, non-blocking broadcast.

    Safe to call from any worker thread (signal processor, Timer callbacks).
    Schedules broadcast_to_ws onto the WS server's event loop and returns
    immediately.
    """
    loop = _event_loop
    if loop is None or loop.is_closed():
        return
    try:
        asyncio.run_coroutine_threadsafe(broadcast_to_ws(payload), loop)
    except RuntimeError:
        pass


def start_server(host: str = "0.0.0.0", port: int = 8082) -> None:
    """Start the WebSocket server in a background daemon thread.

    Uses hypercorn (Quart's bundled ASGI server) with a fresh asyncio event
    loop, entirely separate from the dash_devices server on port 8080.
    Returns immediately; the server runs until the process exits.
    """
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    def _run() -> None:
        global _event_loop

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _event_loop = loop

        config = Config()
        config.bind = [f"{host}:{port}"]
        config.loglevel = "WARNING"

        logger.info(
            "KrakenSDR WebSocket server listening on ws://%s:%d/ws/kraken",
            host, port,
        )
        try:
            loop.run_until_complete(serve(_ws_app, config))
        except Exception:
            logger.exception("WebSocket server stopped unexpectedly")

    t = threading.Thread(target=_run, daemon=True, name="kraken-ws-server")
    t.start()


def register_ws_route(_quart_app) -> None:
    """No-op — kept so existing call sites don't break during transition."""
    pass