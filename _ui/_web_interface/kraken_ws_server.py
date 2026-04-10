"""
WebSocket server for KrakenSDR real-time data broadcasting.

Clients connect to  ws://<host>:8080/ws/kraken  and receive newline-delimited
JSON messages.  Every message has a 'type' field as its first key so clients
can route messages without inspecting the full payload:

    { "type": "doa",      "timestamp": <epoch_ms>, ... }
    { "type": "spectrum", "timestamp": <epoch_ms>, ... }
    { "type": "settings", "timestamp": <epoch_ms>, ... }

Thread-safety
-------------
The Quart event loop runs in the main thread.  The signal processor and the
fetch_dsp_data timer both run in worker threads.  Use broadcast_from_thread()
from those contexts; it schedules the async coroutine onto the event loop via
asyncio.run_coroutine_threadsafe().
"""

import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# One asyncio.Queue per connected WebSocket client.
_ws_clients: set = set()

# Set by the before_serving hook in app.py once the Quart event loop is live.
_event_loop: Optional[asyncio.AbstractEventLoop] = None


async def broadcast_to_ws(payload: dict) -> None:
    """Coroutine: serialise payload and put it on every connected client's queue.

    Uses put_nowait() so that a slow or stalled client is never allowed to
    block the signal-processing pipeline.  If a client's queue is full the
    message is silently dropped for that client.
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
    """Thread-safe wrapper around broadcast_to_ws.

    Safe to call from any non-async thread (signal processor, Timer callbacks).
    Returns immediately; the actual send is scheduled on the Quart event loop.
    """
    loop = _event_loop
    if loop is None or loop.is_closed():
        return
    try:
        asyncio.run_coroutine_threadsafe(broadcast_to_ws(payload), loop)
    except RuntimeError:
        pass


def register_ws_route(quart_app) -> None:
    """Register the /ws/kraken WebSocket endpoint on the supplied Quart app.

    Call this from app.py *after* importing the Dash app but *before*
    app.run_server(), passing app.server (the underlying Quart instance).
    """
    from quart import websocket as ws_ctx  # imported here to avoid top-level dep

    @quart_app.websocket("/ws/kraken")
    async def ws_kraken():
        q: asyncio.Queue = asyncio.Queue(maxsize=20)
        _ws_clients.add(q)
        logger.info("WS client connected (%d total)", len(_ws_clients))
        try:
            while True:
                message = await q.get()
                await ws_ctx.send(message)
        except Exception:
            pass
        finally:
            _ws_clients.discard(q)
            logger.info("WS client disconnected (%d total)", len(_ws_clients))