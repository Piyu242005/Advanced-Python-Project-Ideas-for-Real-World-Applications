"""
IoT Home Automation Simulator
Demonstrates MQTT-style publish/subscribe flows for sensors and
smart devices using Python's asyncio — no broker or hardware required.

For real deployment replace the InMemoryBroker with paho-mqtt:
    pip install paho-mqtt
"""

import asyncio
import random
import time
from collections import defaultdict
from datetime import datetime


# ── In-memory async pub/sub broker ──────────────────────────────────────────

class InMemoryBroker:
    """Lightweight asyncio pub/sub bus that mimics MQTT semantics."""

    def __init__(self):
        self._subscribers: dict[str, list] = defaultdict(list)

    def subscribe(self, topic: str, callback):
        self._subscribers[topic].append(callback)

    async def publish(self, topic: str, payload: dict):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] 📡 PUBLISH  {topic:35s} → {payload}")
        for cb in self._subscribers.get(topic, []):
            await cb(topic, payload)


broker = InMemoryBroker()


# ── Sensor publishers ────────────────────────────────────────────────────────

async def temperature_sensor(room: str, cycles: int = 5):
    """Simulates a temperature & humidity sensor."""
    for _ in range(cycles):
        payload = {
            "room": room,
            "temp_c": round(random.uniform(18.0, 30.0), 1),
            "humidity": round(random.uniform(30.0, 70.0), 1),
        }
        await broker.publish(f"home/{room}/temperature", payload)
        await asyncio.sleep(1)


async def motion_sensor(room: str, cycles: int = 3):
    """Simulates a PIR motion sensor."""
    for _ in range(cycles):
        detected = random.choice([True, False])
        await broker.publish(f"home/{room}/motion", {"detected": detected, "room": room})
        await asyncio.sleep(1.5)


async def door_sensor(door: str, cycles: int = 3):
    """Simulates a magnetic door/window sensor."""
    for _ in range(cycles):
        state = random.choice(["open", "closed"])
        await broker.publish(f"home/security/{door}", {"state": state, "door": door})
        await asyncio.sleep(2)


# ── Smart device subscribers (automation rules) ──────────────────────────────

async def thermostat_controller(topic: str, payload: dict):
    """Auto-adjusts HVAC based on temperature readings."""
    temp = payload["temp_c"]
    room = payload["room"]
    if temp > 26:
        action = "🔵 COOLING ON"
    elif temp < 20:
        action = "🔴 HEATING ON"
    else:
        action = "✅ HVAC IDLE"
    print(f"           🌡️  Thermostat [{room}]: {temp}°C → {action}")


async def smart_light_controller(topic: str, payload: dict):
    """Turns lights on/off based on motion detection."""
    room = payload["room"]
    if payload["detected"]:
        print(f"           💡 Smart Light [{room}]: Motion detected → LIGHTS ON")
    else:
        print(f"           💡 Smart Light [{room}]: No motion → LIGHTS OFF (30s delay)")


async def security_alert(topic: str, payload: dict):
    """Sends an alert when a door opens unexpectedly."""
    if payload["state"] == "open":
        print(f"           🚨 SECURITY ALERT: {payload['door']} opened!")
    else:
        print(f"           🔒 Security: {payload['door']} is closed — all clear.")


# ── Wire up subscriptions ────────────────────────────────────────────────────

def setup_automations():
    for room in ["living_room", "bedroom", "kitchen"]:
        broker.subscribe(f"home/{room}/temperature", thermostat_controller)
        broker.subscribe(f"home/{room}/motion", smart_light_controller)
    for door in ["front_door", "back_door"]:
        broker.subscribe(f"home/security/{door}", security_alert)


# ── Main runner ──────────────────────────────────────────────────────────────

async def run_simulation():
    print("\n" + "═" * 60)
    print("  🏠  IoT Home Automation Simulation")
    print("  Pub/Sub flows for sensors & smart devices")
    print("═" * 60)
    print()

    setup_automations()

    await asyncio.gather(
        temperature_sensor("living_room", cycles=4),
        temperature_sensor("bedroom", cycles=3),
        motion_sensor("living_room", cycles=4),
        motion_sensor("kitchen", cycles=3),
        door_sensor("front_door", cycles=3),
        door_sensor("back_door", cycles=2),
    )

    print("\n" + "═" * 60)
    print("  ✅  Simulation complete")
    print("═" * 60)


def main():
    asyncio.run(run_simulation())


if __name__ == "__main__":
    main()
