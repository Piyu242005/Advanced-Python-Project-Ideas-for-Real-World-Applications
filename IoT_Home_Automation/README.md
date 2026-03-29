# 🏠 IoT Home Automation

## Purpose
Simulate a smart home system where sensors publish events and devices respond automatically — all using Python's built-in async tools.

## Use Case
Learning and prototyping IoT pub/sub flows (MQTT-style) without needing real hardware or a broker.

## Tech Used
| Tool | Role |
|:---|:---|
| `asyncio` | Async event loop powering the pub/sub broker |
| `MQTT pattern` | Publish/subscribe topic routing (simulated in-memory) |
| Python stdlib only | No external packages required |

## Run
```bash
python main.py
```

> Sensors fire every 1–2 seconds. Smart lights, thermostat, and security alerts respond in real time.
