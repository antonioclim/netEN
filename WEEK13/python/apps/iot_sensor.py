#!/usr/bin/env python3
"""
IoT Sensor Simulator
Publica date of temperatura and umiditate at interval regulat.
"""
import argparse
import json
import time
import random
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("pip install paho-mqtt")
    exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="iot/sensors/temp")
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    
    client = mqtt.Client(client_id=f"sensor-{random.randint(1000,9999)}")
    client.connect(args.broker, args.port)
    client.loop_start()
    
    print(f"[*] Sensor started: {args.topic}")
    try:
        while True:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "temperature": round(20 + random.uniform(-5, 10), 2),
                "humidity": round(50 + random.uniform(-10, 10), 1)
            }
            client.publish(args.topic, json.dumps(payload))
            print(f"[>] {payload}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
