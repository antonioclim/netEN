#!/usr/bin/env python3
"""
IoT Controller - Subscriber
Receive and process messages of at sensors.
"""
import argparse
import json
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("pip install paho-mqtt")
    exit(1)

def on_message(client, userdata, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        data = json.loads(msg.payload)
        print(f"[{ts}] {msg.topic}: T={data.get('temperature','?')}°C H={data.get('humidity','?')}%")
    except:
        print(f"[{ts}] {msg.topic}: {msg.payload.decode()}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="iot/#")
    args = parser.parse_args()
    
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(args.broker, args.port)
    client.subscribe(args.topic)
    
    print(f"[*] Controller listening on: {args.topic}")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
