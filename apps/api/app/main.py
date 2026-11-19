"""Local-first IoT demo API. Replace the in-memory registry with persistent storage for production."""
from __future__ import annotations

import asyncio
import json
import math
import os
import random
import threading
import copy
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    import paho.mqtt.client as mqtt
except ImportError:  # Keep the API usable without MQTT in the PC-only demo.
    mqtt = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DEVICES: dict[str, dict[str, Any]] = {
    "quarto-sensor": {"id": "quarto-sensor", "name": "Sensor do quarto", "room": "Quarto", "kind": "sensor", "protocol": "simulator", "online": True, "temperature_c": 24.0, "humidity_pct": 55.0, "power_w": 0.0},
    "sala-lamp": {"id": "sala-lamp", "name": "Lâmpada da sala", "room": "Sala", "kind": "light", "protocol": "simulator", "online": True, "on": True, "power_w": 8.5},
    "cozinha-plug": {"id": "cozinha-plug", "name": "Tomada da cozinha", "room": "Cozinha", "kind": "plug", "protocol": "simulator", "online": True, "on": True, "power_w": 74.0},
    "grow-sensor": {"id": "grow-sensor", "name": "Cultivo", "room": "Horta", "kind": "sensor", "protocol": "simulator", "online": True, "temperature_c": 26.5, "humidity_pct": 68.0, "soil_pct": 61.0, "power_w": 0.0},
}
HISTORY: list[dict[str, Any]] = []
MQTT_CLIENT: Any = None
REGISTRY_LOCK = threading.RLock()


class DeviceCommand(BaseModel):
    action: str = Field(pattern="^(set_power)$")
    value: bool


def mqtt_publish(topic: str, payload: dict[str, Any]) -> None:
    if MQTT_CLIENT and MQTT_CLIENT.is_connected():
        MQTT_CLIENT.publish(topic, json.dumps(payload), qos=1, retain=not topic.startswith("home/command/"))


def ingest_mqtt(topic: str, raw_payload: bytes) -> None:
    """Normalize ESP32/bridge telemetry published to home/telemetry/<id>."""
    if not topic.startswith("home/telemetry/"):
        return
    device_id = topic.rsplit("/", 1)[-1]
    if not device_id or "/" in topic[len("home/telemetry/"):]:
        return
    try:
        data = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    with REGISTRY_LOCK:
        _ingest_device(device_id, data)


def _ingest_device(device_id: str, data: dict[str, Any]) -> None:
    # Simulator messages must not reclassify virtual devices as physical devices.
    if DEVICES.get(device_id, {}).get("protocol") == "simulator":
        return
    device = DEVICES.setdefault(device_id, {
        "id": device_id, "name": device_id.replace("-", " ").title(),
        "room": "Sem cômodo", "kind": "sensor", "protocol": "mqtt", "online": True,
    })
    for field in ("temperature_c", "humidity_pct", "soil_pct", "power_w", "on"):
        value = data.get(field)
        if field == "on" and isinstance(value, bool):
            device[field] = value
        elif field != "on" and type(value) in (int, float) and math.isfinite(value):
            if field in ("humidity_pct", "soil_pct") and not 0 <= value <= 100:
                continue
            if field == "power_w" and value < 0:
                continue
            device[field] = value
    device["protocol"] = "mqtt"
    device["online"] = True
    device["updated_at"] = now_iso()
    HISTORY.append(copy.deepcopy(device))
    del HISTORY[:-500]


def configure_mqtt() -> Any:
    global MQTT_CLIENT
    if mqtt is None or not os.getenv("MQTT_HOST"):
        return None
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-smarthome-api")
    client.on_connect = lambda connected, userdata, flags, reason_code, properties: connected.subscribe("home/telemetry/+")
    client.on_message = lambda client, userdata, message: ingest_mqtt(message.topic, message.payload)
    if os.getenv("MQTT_USERNAME"):
        client.username_pw_set(os.environ["MQTT_USERNAME"], os.getenv("MQTT_PASSWORD"))
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect_async(os.getenv("MQTT_HOST", "localhost"), int(os.getenv("MQTT_PORT", "1883")), 60)
    client.loop_start()
    MQTT_CLIENT = client
    return client


async def simulate() -> None:
    """Generate believable demo values and publish them to MQTT when configured."""
    tick = 0
    while True:
        tick += 1
        # Paho invokes ingestion from another thread: take a stable snapshot.
        with REGISTRY_LOCK:
            simulated = [d for d in DEVICES.values() if d.get("protocol") == "simulator"]
        for device in simulated:
            if device["kind"] == "sensor":
                device["temperature_c"] = round(device["temperature_c"] + random.uniform(-0.15, 0.15), 1)
                device["humidity_pct"] = round(min(90, max(30, device["humidity_pct"] + random.uniform(-0.7, 0.7))), 1)
                if "soil_pct" in device:
                    device["soil_pct"] = round(min(100, max(0, device["soil_pct"] + random.uniform(-0.1, 0.1))), 1)
            elif device["kind"] in {"light", "plug"}:
                base = 8.5 if device["kind"] == "light" else 74.0
                device["power_w"] = round((base + math.sin(tick / 5) * base * 0.08) if device["on"] else 0, 1)
            device["updated_at"] = now_iso()
            snapshot = {**device, "ts": now_iso()}
            HISTORY.append(snapshot)
            mqtt_publish(f"home/state/{device['id']}", snapshot)
        if len(HISTORY) > 500:
            del HISTORY[:-500]
        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(_: FastAPI):
    simulator_enabled = os.getenv("SIMULATOR_ENABLED", "true").lower() == "true"
    task = asyncio.create_task(simulate()) if simulator_enabled else None
    try:
        configure_mqtt()
    except Exception as exc:  # MQTT is optional; surface the reason in health output.
        app.state.mqtt_error = str(exc)
    yield
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    if MQTT_CLIENT:
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()


app = FastAPI(title="IoT Smarthome API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.state.mqtt_error = None


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "mqtt_connected": bool(MQTT_CLIENT and MQTT_CLIENT.is_connected()), "mqtt_error": app.state.mqtt_error, "simulator": os.getenv("SIMULATOR_ENABLED", "true").lower() == "true"}


@app.get("/api/devices")
def list_devices() -> list[dict[str, Any]]:
    with REGISTRY_LOCK:
        return copy.deepcopy(list(DEVICES.values()))


@app.get("/api/summary")
def summary() -> dict[str, Any]:
    devices = list_devices()
    sensors = [item for item in devices if item["kind"] == "sensor"]
    total = round(sum(item.get("power_w", 0) for item in devices), 1)
    rooms = sorted({d["room"] for d in devices})
    return {"device_count": len(devices), "online_count": sum(bool(d["online"]) for d in devices), "power_w": total, "power_by_room_w": {room: round(sum(d.get("power_w", 0) for d in devices if d["room"] == room), 1) for room in rooms}, "rooms": rooms, "sensors": sensors, "updated_at": now_iso()}


@app.get("/api/history")
def history(limit: int = 100) -> list[dict[str, Any]]:
    return HISTORY[-max(1, min(limit, 500)):]


@app.post("/api/devices/{device_id}/command")
def command(device_id: str, command_data: DeviceCommand) -> dict[str, Any]:
    device = DEVICES.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    if device["kind"] not in {"light", "plug", "switch"}:
        raise HTTPException(status_code=422, detail="Dispositivo não suporta set_power")
    if device.get("protocol") != "simulator":
        if not MQTT_CLIENT or not MQTT_CLIENT.is_connected():
            raise HTTPException(status_code=503, detail="Broker MQTT indisponível")
        mqtt_publish(f"home/command/{device_id}", command_data.model_dump())
        return {**device, "command_status": "pending"}
    device["on"] = command_data.value
    if not device["on"]:
        device["power_w"] = 0.0
    device["updated_at"] = now_iso()
    payload = {"device_id": device_id, **command_data.model_dump(), "ts": now_iso()}
    mqtt_publish(f"home/command/{device_id}", payload)
    mqtt_publish(f"home/state/{device_id}", {**device, "ts": now_iso()})
    return device

