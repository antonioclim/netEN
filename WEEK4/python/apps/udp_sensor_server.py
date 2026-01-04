#!/usr/bin/env python3
"""
Server UDP for citiri of senzori (protocol binar with CRC32).

PROTOCOL:
---------
Datagram format (23 bytes):
  +--------+--------+--------+--------+--------+
  |version |sensor_id| temp  |location| crc32  |
  | 1B     | 4B     | 4B(f) | 10B    | 4B     |
  +--------+--------+--------+--------+--------+

  version: 1
  sensor_id: ID unic senzor (unsigned int, big-endian)
  temp: temperatura in °C (float IEEE 754, big-endian)
  location: nume locatie (10 chars, padding with \0)
  crc32: checksum peste primii 19 bytes

COMPORTAMENT:
- Receive datagrame of to senzori
- Verify CRC and valideaza format
- Logheaza citirile valide
- Ignora pachetele corupte (with log warning)
- Calculate statistici (medie, min, max)

UTILIZARE:
----------
  python3 udp_sensor_server.py --port 5402 --verbose
"""
from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, NamedTuple

# Add utils directory to path
sys.path.insert(0, str(__file__).rsplit('/', 2)[0] + '/utils')
from proto_common import unpack_udp_sensor, UDP_LEN, format_sensor_reading


class SensorReading(NamedTuple):
    """O citire of senzor."""
    timestamp: datetime
    sensor_id: int
    temperature: float
    location: str


class SensorStats:
    """Statistici for un senzor."""
    
    def __init__(self):
        self.readings: List[float] = []
        self.last_location: str = ""
        self.last_reading: datetime | None = None
    
    def add(self, temp: float, location: str) -> None:
        self.readings.append(temp)
        self.last_location = location
        self.last_reading = datetime.now()
    
    @property
    def count(self) -> int:
        return len(self.readings)
    
    @property
    def avg(self) -> float:
        return sum(self.readings) / len(self.readings) if self.readings else 0.0
    
    @property
    def min_temp(self) -> float:
        return min(self.readings) if self.readings else 0.0
    
    @property
    def max_temp(self) -> float:
        return max(self.readings) if self.readings else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Server UDP for citiri of senzori"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Adresa of bind")
    parser.add_argument("--port", type=int, default=5402, help="Portul UDP")
    parser.add_argument("--verbose", "-v", action="store_true", help="Afiseaza fiecare citire")
    parser.add_argument("--stats-interval", type=int, default=10, help="Afiseaza statistici to fiecare N citiri")
    
    args = parser.parse_args()
    
    # Statistici per senzor
    stats: Dict[int, SensorStats] = defaultdict(SensorStats)
    total_received = 0
    total_valid = 0
    total_invalid = 0
    
    # Creare socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((args.host, args.port))
        
        print(f"[UDP] Sensor server listening on {args.host}:{args.port}")
        print(f"[UDP] Expected datagram size: {UDP_LEN} bytes")
        print(f"[UDP] Press Ctrl+C to stop and see statistics")
        print()
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)  # Buffer generos
                total_received += 1
                
                # Validare dimensiune
                if len(data) != UDP_LEN:
                    total_invalid += 1
                    if args.verbose:
                        print(f"[UDP] ! Invalid size from {addr}: {len(data)} bytes (expected {UDP_LEN})")
                    continue
                
                # Decodare and validare CRC
                try:
                    ver, sensor_id, temp_c, location = unpack_udp_sensor(data)
                except ValueError as e:
                    total_invalid += 1
                    if args.verbose:
                        print(f"[UDP] ! Invalid packet from {addr}: {e}")
                    continue
                
                # Citire valida
                total_valid += 1
                stats[sensor_id].add(temp_c, location)
                
                if args.verbose:
                    reading = format_sensor_reading(sensor_id, temp_c, location)
                    print(f"[UDP] < {addr[0]}:{addr[1]} {reading}")
                
                # Afisare statistici periodice
                if args.stats_interval > 0 and total_valid % args.stats_interval == 0:
                    print_stats(stats, total_received, total_valid, total_invalid)
                    
            except Exception as e:
                print(f"[UDP] ! Error: {e}")
                
    except KeyboardInterrupt:
        print("\n")
        print_stats(stats, total_received, total_valid, total_invalid)
        print("\n[UDP] Server stopped")
        return 0
    finally:
        sock.close()


def print_stats(stats: Dict[int, SensorStats], received: int, valid: int, invalid: int) -> None:
    """Afiseaza statistici agregate."""
    print()
    print("=" * 60)
    print(f"STATISTICS: {received} received, {valid} valid, {invalid} invalid ({invalid*100/max(received,1):.1f}% error rate)")
    print("-" * 60)
    
    if not stats:
        print("  (no valid readings yet)")
    else:
        for sensor_id in sorted(stats.keys()):
            s = stats[sensor_id]
            print(f"  Sensor {sensor_id:04d} ({s.last_location:10s}): "
                  f"{s.count} readings, avg={s.avg:+.1f}°C, "
                  f"min={s.min_temp:+.1f}°C, max={s.max_temp:+.1f}°C")
    
    print("=" * 60)
    print()


if __name__ == "__main__":
    raise SystemExit(main())
