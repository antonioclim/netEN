#!/usr/bin/env python3
"""
Template: Client UDP Senzor
============================

Completati functiile marcate with TODO for a implementa a client
UDP care trimite date of to un senzor simulat.

Structura datagrama (23 bytes):
  [0]      version: uint8 = 1
  [1:5]    sensor_id: uint32 BE
  [5:9]    temperature: float32 BE
  [9:19]   location: 10 chars (padding with spatii)
  [19:23]  crc32: uint32 BE

Autor: Revolvix&Hypotheticalandrei
Week 4 - Template client UDP senzor
"""

import socket
import struct
import zlib
import time
import random

# Constante protocol
DATAGRAM_VERSION = 1
DATAGRAM_SIZE = 23
DEFAULT_PORT = 5402
DEFAULT_HOST = 'localhost'


def calculate_crc32(data: bytes) -> int:
    """Calculate CRC32 for date."""
    return zlib.crc32(data) & 0xFFFFFFFF


def pad_location(location: str, length: int = 10) -> bytes:
    """
    Format location-ul to lungime fixa.
    
    TODO: Implementati aceasta function
    Hint: 
    - Trunchiati to length caractere daca e prea lung
    - Adaugati spatii to dreapta daca e prea scurt
    - Codificati in UTF-8
    """
    # TODO: Implementare
    # location_str = location[:length].ljust(length)
    # return location_str.encode('utf-8')
    pass


def create_datagram(sensor_id: int, temperature: float, location: str) -> bytes:
    """
    Creeaza o datagrama for senzor.
    
    Args:
        sensor_id: ID-ul senzorului (uint32)
        temperature: Temperatura in graof Celsius (float)
        location: Locatia senzorului (max 10 caractere)
    
    Returns:
        bytes: Datagrama of 23 bytes
    
    TODO: Implementati aceasta function
    Pasi:
    1. Formatati location-ul (pad_location)
    2. Pack payload fara CRC: struct.pack('>BIf10s', ...)
    3. Calculati CRC pe payload
    4. Pack CRC and concatenati
    """
    # TODO: Implementare
    # location_bytes = pad_location(location)
    # 
    # payload = struct.pack(
    #     '>BIf10s',
    #     DATAGRAM_VERSION,
    #     sensor_id,
    #     temperature,
    #     location_bytes
    # )
    # 
    # crc = calculate_crc32(payload)
    # datagram = payload + struct.pack('>I', crc)
    # 
    # return datagram
    pass


def send_reading(sock: socket.socket, 
                 server_addr: tuple, 
                 sensor_id: int,
                 temperature: float, 
                 location: str) -> bool:
    """
    Send o citire of senzor catre server.
    
    Args:
        sock: Socket UDP
        server_addr: Tuple (host, port)
        sensor_id: ID-ul senzorului
        temperature: Temperatura citita
        location: Locatia senzorului
    
    Returns:
        bool: True daca trimiterea a reusit
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # try:
    #     datagram = create_datagram(sensor_id, temperature, location)
    #     sock.sendto(datagram, server_addr)
    #     return True
    # except Exception as e:
    #     print(f"Eroare trimitere: {e}")
    #     return False
    pass


def simulate_sensor(host: str = DEFAULT_HOST,
                    port: int = DEFAULT_PORT,
                    sensor_id: int = 1001,
                    location: str = "Lab",
                    interval: float = 1.0,
                    count: int = 10):
    """
    Simuleaza un senzor care trimite citiri periodice.
    
    TODO: Implementati aceasta function
    Pasi:
    1. Creati socket UDP
    2. Loop for count citiri:
       - Generati temperatura random (18-28°C)
       - Sendti citirea
       - Asteptati interval secunde
    """
    # TODO: Implementare
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # server_addr = (host, port)
    # 
    # print(f"[*] Senzor {sensor_id} @ {location}")
    # print(f"[*] Sendre catre {host}:{port}")
    # 
    # try:
    #     for i in range(count):
    #         temperature = random.uniform(18.0, 28.0)
    #         
    #         if send_reading(sock, server_addr, sensor_id, temperature, location):
    #             print(f"    [{i+1}/{count}] Trimis: {temperature:.1f}°C")
    #         else:
    #             print(f"    [{i+1}/{count}] Eroare trimitere")
    #         
    #         time.sleep(interval)
    #         
    # finally:
    #     sock.close()
    #     print("[*] Senzor oprit")
    pass


def main():
    """Punctul of intrare principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Client UDP Senzor')
    parser.add_argument('--host', default=DEFAULT_HOST, help='Adresa serverului')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Portul serverului')
    parser.add_argument('--sensor-id', type=int, default=1001, help='ID-ul senzorului')
    parser.add_argument('--location', default='Lab', help='Locatia senzorului')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval intre citiri')
    parser.add_argument('--count', type=int, default=10, help='Numar of citiri')
    
    args = parser.parse_args()
    
    simulate_sensor(
        host=args.host,
        port=args.port,
        sensor_id=args.sensor_id,
        location=args.location,
        interval=args.interval,
        count=args.count
    )


if __name__ == '__main__':
    main()
