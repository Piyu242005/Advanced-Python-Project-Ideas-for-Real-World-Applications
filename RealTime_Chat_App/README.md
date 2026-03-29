# 💬 Real-Time Chat Application

## Purpose
A multi-room WebSocket chat server where multiple users can connect, send messages, change names, and switch rooms — all in real time.

## Use Case
Learning WebSocket-based system design, building the backbone of a chat app, or prototyping any real-time event-driven feature.

## Tech Used
| Library | Role |
|:---|:---|
| `websockets` | Async WebSocket server handling client connections |
| `asyncio` | Concurrent handling of multiple users without threads |
| `json` | Message protocol (event, text, room, timestamp) |

## Run
```bash
pip install -r requirements.txt

# Start server (connects on ws://localhost:8765)
python main.py

# Demo mode — simulates a conversation without a browser
python main.py --demo
```
