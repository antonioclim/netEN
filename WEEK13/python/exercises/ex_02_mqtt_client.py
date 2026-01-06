#!/usr/bin/env python3
"""Week 13 - MQTT client (plaintext and TLS).

This script is used in demos and exercises to illustrate:
- MQTT publish and subscribe flows
- plaintext vs TLS transport
- optional username and password authentication

It is intentionally minimal and suitable for a laboratory environment.

Examples
--------
Plaintext publish:
  python3 ex_02_mqtt_client.py --broker 127.0.0.1 --port 1883 \
    --mode publish --topic iot/sensors/temperature \
    --message '{"sensor":"temp","value":24.3}' --count 3

TLS publish (server authentication):
  python3 ex_02_mqtt_client.py --broker 127.0.0.1 --port 8883 \
    --mode publish --topic iot/sensors/temperature \
    --message '{"sensor":"temp","value":24.3}' --count 3 \
    --tls --cafile configs/certs/ca.crt

Subscribe with a timeout:
  python3 ex_02_mqtt_client.py --broker 127.0.0.1 --port 1883 \
    --mode subscribe --topic iot/sensors/# --timeout 20
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import paho.mqtt.client as mqtt


@dataclass
class MqttConfig:
    broker: str
    port: int
    mode: str  # publish or subscribe
    topic: str
    message: str
    count: int
    qos: int
    username: Optional[str]
    password: Optional[str]
    tls: bool
    cafile: Optional[str]
    insecure: bool
    timeout: int


def _format_message_for_print(msg: str) -> str:
    msg = msg.strip()
    if not msg:
        return msg
    try:
        obj = json.loads(msg)
        return json.dumps(obj, indent=2, sort_keys=True)
    except Exception:
        return msg


def _ensure_cafile(cafile: Optional[str]) -> str:
    if not cafile:
        raise ValueError("TLS is enabled but --cafile was not provided.")
    if not os.path.exists(cafile):
        raise FileNotFoundError(f"CA file not found: {cafile}")
    return cafile


def build_client(cfg: MqttConfig) -> mqtt.Client:
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    if cfg.username is not None:
        client.username_pw_set(cfg.username, cfg.password)

    if cfg.tls:
        cafile = _ensure_cafile(cfg.cafile)
        client.tls_set(ca_certs=cafile)
        client.tls_insecure_set(cfg.insecure)

    return client


def run_publish(cfg: MqttConfig) -> int:
    client = build_client(cfg)

    connected = False
    connection_rc: Optional[int] = None

    def on_connect(_client, _userdata, _flags, rc):
        nonlocal connected, connection_rc
        connection_rc = rc
        connected = True

    def on_publish(_client, _userdata, mid):
        print(f"[PUBLISH] ack mid={mid}")

    client.on_connect = on_connect
    client.on_publish = on_publish

    print("=" * 72)
    print("Week 13 - MQTT publish")
    print("=" * 72)
    print(f"Broker: {cfg.broker}:{cfg.port}")
    print(f"TLS: {cfg.tls}")
    if cfg.tls:
        print(f"CA file: {cfg.cafile}")
        print(f"TLS insecure: {cfg.insecure}")
    if cfg.username:
        print(f"Auth: username={cfg.username!r}")
    else:
        print("Auth: none")
    print(f"Topic: {cfg.topic}")
    print(f"QoS: {cfg.qos}")
    print(f"Count: {cfg.count}")
    print("Message:")
    print(_format_message_for_print(cfg.message))
    print()

    try:
        client.connect(cfg.broker, cfg.port, keepalive=30)
    except Exception as exc:
        print(f"[ERROR] Connect failed: {exc}")
        return 1

    client.loop_start()

    # Wait briefly for connection callback
    deadline = time.time() + 5
    while not connected and time.time() < deadline:
        time.sleep(0.05)

    if not connected:
        print("[ERROR] Connection timed out (no CONNACK).")
        client.loop_stop()
        return 1

    if connection_rc != 0:
        print(f"[ERROR] Connection rejected, rc={connection_rc}")
        client.loop_stop()
        return 1

    for i in range(cfg.count):
        payload = cfg.message
        info = client.publish(cfg.topic, payload=payload, qos=cfg.qos, retain=False)
        print(f"[PUBLISH] sent {i+1}/{cfg.count} mid={info.mid}")
        time.sleep(0.5)

    time.sleep(1.0)
    client.disconnect()
    client.loop_stop()
    return 0


def run_subscribe(cfg: MqttConfig) -> int:
    client = build_client(cfg)

    received = 0
    connected = False
    connection_rc: Optional[int] = None

    def on_connect(_client, _userdata, _flags, rc):
        nonlocal connected, connection_rc
        connection_rc = rc
        connected = True
        if rc == 0:
            _client.subscribe(cfg.topic, qos=cfg.qos)

    def on_message(_client, _userdata, msg):
        nonlocal received
        received += 1
        payload = msg.payload.decode(errors="replace")
        print(f"[MESSAGE] topic={msg.topic} qos={msg.qos} retained={msg.retain}")
        print(_format_message_for_print(payload))
        print("-" * 40)

    client.on_connect = on_connect
    client.on_message = on_message

    print("=" * 72)
    print("Week 13 - MQTT subscribe")
    print("=" * 72)
    print(f"Broker: {cfg.broker}:{cfg.port}")
    print(f"TLS: {cfg.tls}")
    if cfg.tls:
        print(f"CA file: {cfg.cafile}")
        print(f"TLS insecure: {cfg.insecure}")
    if cfg.username:
        print(f"Auth: username={cfg.username!r}")
    else:
        print("Auth: none")
    print(f"Topic filter: {cfg.topic}")
    print(f"QoS: {cfg.qos}")
    print(f"Timeout: {cfg.timeout}s")
    print()

    try:
        client.connect(cfg.broker, cfg.port, keepalive=30)
    except Exception as exc:
        print(f"[ERROR] Connect failed: {exc}")
        return 1

    client.loop_start()

    deadline = time.time() + 5
    while not connected and time.time() < deadline:
        time.sleep(0.05)

    if not connected:
        print("[ERROR] Connection timed out (no CONNACK).")
        client.loop_stop()
        return 1

    if connection_rc != 0:
        print(f"[ERROR] Connection rejected, rc={connection_rc}")
        client.loop_stop()
        return 1

    # Wait for messages
    end_time = time.time() + cfg.timeout
    while time.time() < end_time:
        time.sleep(0.1)

    client.disconnect()
    client.loop_stop()

    if received == 0:
        print("[INFO] No messages received within the timeout window.")
    else:
        print(f"[INFO] Received {received} message(s).")
    return 0


def parse_args() -> MqttConfig:
    parser = argparse.ArgumentParser(description="Week 13 - MQTT client (plaintext and TLS)")
    parser.add_argument("--broker", default="127.0.0.1", help="MQTT broker host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port (default: 1883)")
    parser.add_argument("--mode", choices=["publish", "subscribe"], required=True, help="Client mode")
    parser.add_argument("--topic", required=True, help="Topic (publish) or topic filter (subscribe)")
    parser.add_argument("--message", default="", help="Payload for publish mode")
    parser.add_argument("--count", type=int, default=1, help="Number of publish messages (default: 1)")
    parser.add_argument("--qos", type=int, default=0, choices=[0, 1, 2], help="QoS level (default: 0)")
    parser.add_argument("--username", default=None, help="Username (optional)")
    parser.add_argument("--password", default=None, help="Password (optional)")
    parser.add_argument("--tls", action="store_true", help="Enable TLS")
    parser.add_argument("--cafile", default=None, help="CA certificate file for TLS (required when --tls is used)")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification (not recommended)")
    parser.add_argument("--timeout", type=int, default=20, help="Subscribe timeout in seconds (default: 20)")
    args = parser.parse_args()

    if args.mode == "publish" and not args.message:
        raise SystemExit("Publish mode requires --message.")

    return MqttConfig(
        broker=args.broker,
        port=args.port,
        mode=args.mode,
        topic=args.topic,
        message=args.message,
        count=args.count,
        qos=args.qos,
        username=args.username,
        password=args.password,
        tls=args.tls,
        cafile=args.cafile,
        insecure=args.insecure,
        timeout=args.timeout,
    )


def main() -> int:
    cfg = parse_args()
    if cfg.mode == "publish":
        return run_publish(cfg)
    return run_subscribe(cfg)


if __name__ == "__main__":
    sys.exit(main())
