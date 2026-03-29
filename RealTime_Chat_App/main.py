"""
Real-Time Chat Application
WebSocket-based multi-room chat server with asyncio.

Dependencies:
    pip install websockets

Usage:
    # Start server (connects on ws://localhost:8765)
    python main.py

    # Self-contained demo (no external client needed)
    python main.py --demo
"""

import asyncio
import sys
import json
from datetime import datetime

try:
    import websockets
    WS_AVAILABLE = True
    serve = websockets.serve   # top-level, non-deprecated API
except ImportError:
    WS_AVAILABLE = False
    serve = None


# ── Server state ─────────────────────────────────────────────────────────────
connected_clients: dict = {}   # websocket → {"name": str, "room": str}
rooms: dict = {}               # room → set of websockets


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def build_msg(event: str, **kwargs) -> str:
    return json.dumps({"event": event, "ts": ts(), **kwargs})


# ── Broadcast helpers ─────────────────────────────────────────────────────────

async def broadcast_room(room: str, message: str, exclude=None):
    if room not in rooms:
        return
    targets = [ws for ws in rooms[room] if ws is not exclude]
    if targets:
        await asyncio.gather(*[ws.send(message) for ws in targets], return_exceptions=True)


async def broadcast_all(message: str):
    if connected_clients:
        await asyncio.gather(
            *[ws.send(message) for ws in connected_clients], return_exceptions=True
        )


# ── Connection handler ────────────────────────────────────────────────────────

async def handle_client(websocket):
    name = f"User_{id(websocket) % 1000}"
    room = "general"

    connected_clients[websocket] = {"name": name, "room": room}
    rooms.setdefault(room, set()).add(websocket)

    await websocket.send(build_msg("welcome", name=name, room=room,
                                   message=f"Welcome, {name}! You joined #{room}"))
    await broadcast_room(room, build_msg("join", name=name, room=room,
                                         message=f"{name} joined #{room}"), exclude=websocket)

    print(f"  [{ts()}] + {name} connected  (total: {len(connected_clients)})")

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"type": "chat", "text": raw}

            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                text = data.get("text", "").strip()
                if not text:
                    continue
                print(f"  [{ts()}] [{room}] {name}: {text}")
                out = build_msg("chat", name=name, room=room, text=text)
                await broadcast_room(room, out)        # including sender
                await websocket.send(out)              # echo to sender if not in room

            elif msg_type == "join":
                new_room = data.get("room", "general").strip()
                # Leave old room
                rooms[room].discard(websocket)
                await broadcast_room(room, build_msg("leave", name=name, room=room,
                                                     message=f"{name} left #{room}"))
                # Join new room
                room = new_room
                connected_clients[websocket]["room"] = room
                rooms.setdefault(room, set()).add(websocket)
                await websocket.send(build_msg("joined", room=room,
                                               message=f"You joined #{room}"))
                await broadcast_room(room, build_msg("join", name=name, room=room,
                                                     message=f"{name} joined #{room}"),
                                     exclude=websocket)

            elif msg_type == "rename":
                old = name
                name = data.get("name", name).strip() or name
                connected_clients[websocket]["name"] = name
                await broadcast_room(room, build_msg("rename", old=old, name=name,
                                                     message=f"{old} is now {name}"))

    except websockets.exceptions.ConnectionClosedOK:
        pass
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        rooms.get(room, set()).discard(websocket)
        del connected_clients[websocket]
        await broadcast_room(room, build_msg("leave", name=name, room=room,
                                             message=f"{name} disconnected"))
        print(f"  [{ts()}] - {name} disconnected (total: {len(connected_clients)})")


# ── Demo mode (no external client needed) ────────────────────────────────────

async def demo_conversation():
    """Simulate a chat conversation locally without a browser client."""
    HOST, PORT = "localhost", 8765

    # Start server in background
    server_task = asyncio.create_task(run_server(HOST, PORT, silent=True))
    await asyncio.sleep(0.3)   # let server start

    print("\n" + "═" * 55)
    print("  💬  REAL-TIME CHAT APP — Demo Mode")
    print("  Simulating a WebSocket multi-user conversation")
    print("═" * 55)

    uri = f"ws://{HOST}:{PORT}"
    msgs_alice = [
        {"type": "chat", "text": "Hey everyone! 👋"},
        {"type": "chat", "text": "Anyone working on ML projects?"},
        {"type": "chat", "text": "Just finished a TF-IDF resume screener!"},
    ]
    msgs_bob = [
        {"type": "chat", "text": "Hi Piyush! 🤗"},
        {"type": "chat", "text": "That sounds awesome — share the repo?"},
    ]

    async def user_session(name: str, messages: list):
        async with websockets.connect(uri) as ws:
            # Rename
            await ws.send(json.dumps({"type": "rename", "name": name}))
            await asyncio.sleep(0.1)
            for msg in messages:
                await ws.send(json.dumps(msg))
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(raw)
                    if data.get("event") == "chat":
                        print(f"  [{data['ts']}] #{data['room']} | {data['name']}: {data['text']}")
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.5)

    await asyncio.gather(
        user_session("Piyush", msgs_piyush),
        user_session("Tippsy", msgs_tippsy),
    )

    print("\n  ✅  Demo conversation complete")
    print("═" * 55)
    server_task.cancel()


async def run_server(host: str = "localhost", port: int = 8765, silent: bool = False):
    async with serve(handle_client, host, port):
        if not silent:
            print("\n" + "═" * 50)
            print(f"  💬  Chat server running on ws://{host}:{port}")
            print("  Press Ctrl+C to stop")
            print("═" * 50)
        await asyncio.Future()   # run forever


def main():
    if not WS_AVAILABLE:
        print("❌  websockets not installed. Run: pip install websockets")
        sys.exit(1)

    if "--demo" in sys.argv:
        asyncio.run(demo_conversation())
    else:
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            print("\n  Server stopped.")


if __name__ == "__main__":
    main()
