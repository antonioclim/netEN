#!/usr/bin/env python3
"""
Exercitiul 4.02: Agregator Date Senzori UDP
============================================

Obiectiv: Implementati a server UDP care colecteaza and agrega date of to senzori.

Specificatii:
- Server UDP care primeste datagrame of to senzori
- Agregare: medie, min, max, numar citiri per senzor
- Raport periodic (to fiecare N citiri)
- Export statistici in format JSON

Format datagrama senzor (23 bytes - din lab):
  [0]      version: uint8 = 1
  [1:5]    sensor_id: uint32 BE
  [5:9]    temperature: float32 BE
  [9:19]   location: 10 chars (padding spatii)
  [19:23]  crc32: uint32 BE

TODO-uri of implementat:
1. parse_sensor_datagram() - parseaza datagrama binara
2. validate_crc() - verifica CRC32
3. update_statistics() - actualizeaza statisticile per senzor
4. generate_report() - genereaza raport JSON
5. run_aggregator() - bucto principala server

Autor: Revolvix&Hypotheticalandrei
Week 4 - Exercitiu practic UDP
"""

import socket
import struct
import zlib
import json
import time
import threading
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Constante protocol
DATAGRAM_SIZE = 23
DATAGRAM_VERSION = 1
DEFAULT_PORT = 5556
REPORT_INTERVAL = 5  # secunde


@dataclass
class SensorStats:
    """
    Statistici for un senzor.
    """
    sensor_id: int
    location: str
    count: int = 0
    total: float = 0.0
    min_temp: float = float('inf')
    max_temp: float = float('-inf')
    last_reading: float = 0.0
    last_timestamp: str = ""
    
    @property
    def average(self) -> float:
        """Calculate media temperaturilor."""
        return self.total / self.count if self.count > 0 else 0.0
    
    def to_dict(self) -> dict:
        """Converteste to dictionar for JSON."""
        return {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'readings_count': self.count,
            'average_temp': round(self.average, 2),
            'min_temp': round(self.min_temp, 2) if self.min_temp != float('inf') else None,
            'max_temp': round(self.max_temp, 2) if self.max_temp != float('-inf') else None,
            'last_reading': round(self.last_reading, 2),
            'last_timestamp': self.last_timestamp
        }


def calculate_crc32(data: bytes) -> int:
    """
    Calculate CRC32 for date.
    
    Args:
        data: Bytes for care se calculeaza CRC
    
    Returns:
        int: Valoarea CRC32 (unsigned 32-bit)
    """
    return zlib.crc32(data) & 0xFFFFFFFF


def parse_sensor_datagram(datagram: bytes) -> Optional[Tuple[int, float, str]]:
    """
    Parseaza o datagrama primita of to un senzor.
    
    Structura datagrama (23 bytes):
        [0]      version: uint8
        [1:5]    sensor_id: uint32 BE
        [5:9]    temperature: float32 BE
        [9:19]   location: 10 bytes string
        [19:23]  crc32: uint32 BE
    
    Args:
        datagram: Bytes primite of to senzor
    
    Returns:
        Optional[Tuple]: (sensor_id, temperature, location) or None daca invalid
    
    TODO: Implementati aceasta function
    Hints:
    - Verificati lungimea datagramei (DATAGRAM_SIZE = 23)
    - Folositi struct.unpack() with format '>BIf10sI' for big-endian
    - Verificati versiunea (trebuie sa fie DATAGRAM_VERSION = 1)
    - Extrageti location and faceti strip() for a elimina spatiile of padding
    - Validati CRC32 folosind calculate_crc32() pe primii 19 bytes
    """
    # TODO: Implementare
    # 
    # Pasul 1: Verificati lungimea
    # if len(datagram) != DATAGRAM_SIZE:
    #     print(f"[!] Datagrama invalida: lungime {len(datagram)}, asteptat {DATAGRAM_SIZE}")
    #     return None
    # 
    # Pasul 2: Unpacking
    # try:
    #     version, sensor_id, temperature, location_bytes, received_crc = struct.unpack(
    #         '>BIf10sI', datagram
    #     )
    # except struct.error as e:
    #     print(f"[!] Eroare unpacking: {e}")
    #     return None
    # 
    # Pasul 3: Verificare versiune
    # if version != DATAGRAM_VERSION:
    #     print(f"[!] Versiune invalida: {version}, asteptat {DATAGRAM_VERSION}")
    #     return None
    # 
    # Pasul 4: Validare CRC32
    # payload_for_crc = datagram[:19]  # Tot mai putin CRC-ul
    # calculated_crc = calculate_crc32(payload_for_crc)
    # if calculated_crc != received_crc:
    #     print(f"[!] CRC invalid: primit {received_crc:08X}, calculat {calculated_crc:08X}")
    #     return None
    # 
    # Pasul 5: Decodare location
    # location = location_bytes.decode('utf-8', errors='replace').strip()
    # 
    # return (sensor_id, temperature, location)
    
    pass  # Inlocuiti with implementarea


def update_statistics(stats: Dict[int, SensorStats], 
                     sensor_id: int, 
                     temperature: float, 
                     location: str) -> None:
    """
    Actualizeaza statisticile for un senzor.
    
    Args:
        stats: Dictionar with statistici per sensor_id
        sensor_id: ID-ul senzorului
        temperature: Temperatura citita
        location: Locatia senzorului
    
    TODO: Implementati aceasta function
    Hints:
    - Daca sensor_id nu exists in stats, creati o noua intrare SensorStats
    - Actualizati: count, total, min_temp, max_temp, last_reading, last_timestamp
    - Folositi datetime.now().isoformat() for timestamp
    """
    # TODO: Implementare
    # 
    # if sensor_id not in stats:
    #     stats[sensor_id] = SensorStats(sensor_id=sensor_id, location=location)
    # 
    # sensor = stats[sensor_id]
    # sensor.count += 1
    # sensor.total += temperature
    # sensor.min_temp = min(sensor.min_temp, temperature)
    # sensor.max_temp = max(sensor.max_temp, temperature)
    # sensor.last_reading = temperature
    # sensor.last_timestamp = datetime.now().isoformat()
    # sensor.location = location  # Actualizam in caz ca s-a schimbat
    
    pass  # Inlocuiti with implementarea


def generate_report(stats: Dict[int, SensorStats]) -> dict:
    """
    Genereaza un raport JSON with toate statisticile.
    
    Args:
        stats: Dictionar with statistici per senzor
    
    Returns:
        dict: Raport structurat
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # 
    # total_readings = sum(s.count for s in stats.values())
    # all_temps = [s.last_reading for s in stats.values() if s.count > 0]
    # 
    # report = {
    #     'timestamp': datetime.now().isoformat(),
    #     'total_sensors': len(stats),
    #     'total_readings': total_readings,
    #     'global_average': round(sum(all_temps) / len(all_temps), 2) if all_temps else None,
    #     'sensors': [s.to_dict() for s in stats.values()]
    # }
    # 
    # return report
    
    pass  # Inlocuiti with implementarea


def print_report(stats: Dict[int, SensorStats]) -> None:
    """
    Afiseaza raportul in consola.
    """
    report = generate_report(stats)
    
    if report is None:
        print("[!] Raport nu a putut fi generat")
        return
    
    print("\n" + "="*60)
    print(f"RAPORT SENZORI - {report.get('timestamp', 'N/A')}")
    print("="*60)
    print(f"Senzori activi: {report.get('total_sensors', 0)}")
    print(f"Total citiri: {report.get('total_readings', 0)}")
    
    if report.get('global_average'):
        print(f"Medie globala: {report['global_average']}°C")
    
    print("\nDetalii per senzor:")
    print("-"*60)
    
    for sensor in report.get('sensors', []):
        print(f"  Senzor {sensor['sensor_id']} @ {sensor['location']}:")
        print(f"    Citiri: {sensor['readings_count']}")
        print(f"    Medie: {sensor['average_temp']}°C")
        print(f"    Min/Max: {sensor['min_temp']}°C / {sensor['max_temp']}°C")
        print(f"    Ultima: {sensor['last_reading']}°C @ {sensor['last_timestamp']}")
    
    print("="*60 + "\n")


def export_json(stats: Dict[int, SensorStats], filename: str = 'sensor_report.json') -> None:
    """
    Exporta raportul in fisier JSON.
    
    Args:
        stats: Statistici senzori
        filename: Numele fisierului of output
    """
    report = generate_report(stats)
    if report:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[*] Raport exportat in {filename}")


def periodic_reporter(stats: Dict[int, SensorStats], 
                     interval: int, 
                     stop_event: threading.Event):
    """
    Thread for raportare periodica.
    
    Args:
        stats: Dictionar with statistici
        interval: Interval of raportare (secunde)
        stop_event: Event for oprire thread
    """
    while not stop_event.is_set():
        stop_event.wait(interval)
        if not stop_event.is_set() and stats:
            print_report(stats)


def run_aggregator(host: str = '0.0.0.0', 
                   port: int = DEFAULT_PORT,
                   report_interval: int = REPORT_INTERVAL) -> None:
    """
    Ruleaza serverul agregator UDP.
    
    Args:
        host: Adresa of ascultare
        port: Portul UDP
        report_interval: Interval for rapoarte automate (0 = dezactivat)
    
    TODO: Implementati aceasta function
    Hints:
    - Creati socket UDP: socket.socket(AF_INET, SOCK_DGRAM)
    - Folositi recvfrom() for a primi datagrame
    - Apelati parse_sensor_datagram() and update_statistics()
    - Optional: porniti thread for raportare periodica
    """
    # Statistici globale
    stats: Dict[int, SensorStats] = {}
    
    # TODO: Implementare
    # 
    # # Creare socket UDP
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind((host, port))
    # sock.settimeout(1.0)  # Timeout for a putea verifica stop
    # 
    # print(f"[*] Agregator UDP pornit pe {host}:{port}")
    # print(f"[*] Raportare to fiecare {report_interval} secunde")
    # 
    # # Thread for raportare periodica
    # stop_event = threading.Event()
    # if report_interval > 0:
    #     reporter = threading.Thread(
    #         target=periodic_reporter,
    #         args=(stats, report_interval, stop_event),
    #         daemon=True
    #     )
    #     reporter.start()
    # 
    # try:
    #     while True:
    #         try:
    #             datagram, addr = sock.recvfrom(DATAGRAM_SIZE + 100)  # Buffer with margine
    #             
    #             result = parse_sensor_datagram(datagram)
    #             if result:
    #                 sensor_id, temperature, location = result
    #                 update_statistics(stats, sensor_id, temperature, location)
    #                 print(f"[+] Senzor {sensor_id} @ {location}: {temperature:.1f}°C")
    #             else:
    #                 print(f"[-] Datagrama invalida of to {addr}")
    #                 
    #         except socket.timeout:
    #             continue  # Normal, verificam periodic for Ctrl+C
    #             
    # except KeyboardInterrupt:
    #     print("\n[*] Oprire...")
    #     stop_event.set()
    #     
    #     # Raport final
    #     if stats:
    #         print_report(stats)
    #         export_json(stats)
    #         
    # finally:
    #     sock.close()
    #     print("[*] Agregator oprit")
    
    pass  # Inlocuiti with implementarea


# =============================================================================
# CLIENT DE TEST (nu trebuie modificat)
# =============================================================================

def create_test_datagram(sensor_id: int, temperature: float, location: str) -> bytes:
    """
    Creeaza o datagrama of test valida.
    """
    location_padded = location[:10].ljust(10)
    
    # Pack fara CRC
    payload = struct.pack(
        '>BIf10s',
        DATAGRAM_VERSION,
        sensor_id,
        temperature,
        location_padded.encode('utf-8')
    )
    
    # Calculare and adaugare CRC
    crc = calculate_crc32(payload)
    datagram = payload + struct.pack('>I', crc)
    
    return datagram


def test_client(host: str = 'localhost', port: int = DEFAULT_PORT):
    """
    Client of test care trimite datagrame simulate.
    """
    import random
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sensors = [
        (1001, "Sala_A1"),
        (1002, "Sala_B2"),
        (2001, "Exterior"),
    ]
    
    print(f"[*] Sendre datagrame catre {host}:{port}")
    
    try:
        for _ in range(10):
            sensor_id, location = random.choice(sensors)
            temperature = random.uniform(18.0, 28.0)
            
            datagram = create_test_datagram(sensor_id, temperature, location)
            sock.sendto(datagram, (host, port))
            
            print(f"    Trimis: Senzor {sensor_id} @ {location}: {temperature:.1f}°C")
            time.sleep(0.5)
            
    finally:
        sock.close()
        print("[*] Test client terminat")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mod test client
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
        test_client(host, port)
    else:
        # Mod server agregator
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
        run_aggregator(port=port)
