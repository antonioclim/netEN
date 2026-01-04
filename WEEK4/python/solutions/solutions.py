#!/usr/bin/env python3
"""
Solutii for Exercitiile Saptamanii 4
========================================

ATENTIE: Acest fisier contine solutiile complete.
Consultati-l doar dupa ce ati incercat sa rezolvati exercitiile singuri!

Autor: Revolvix&Hypotheticalandrei
"""

# =============================================================================
# SOLUTIE EXERCITIUL 4.01: Protocol TCP Custom
# =============================================================================

import socket
import struct
import zlib
import json
import threading
import time
from datetime import datetime
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# Constante protocol TCP
VALID_COMMANDS = {'ECHO', 'UPPER', 'LOWER', 'REVERSE', 'COUNT'}
TCP_DEFAULT_PORT = 3334
BUFFER_SIZE = 4096


def sol_parse_command(data: str) -> tuple:
    """
    SOLUTIE: Parseaza mesajul primit and extrage comanda, lungimea and payload-ul.
    """
    parts = data.split(' ', 2)
    
    if len(parts) < 3:
        return (None, None, None)
    
    command = parts[0].upper()
    if command not in VALID_COMMANDS:
        return (None, None, None)
    
    try:
        length = int(parts[1])
    except ValueError:
        return (None, None, None)
    
    payload = parts[2]
    
    # Verifym consistenta lungimii (in bytes UTF-8)
    if len(payload.encode('utf-8')) != length:
        return (None, None, None)
    
    return (command, length, payload)


def sol_execute_command(command: str, payload: str) -> str:
    """
    SOLUTIE: Executa comanda specificata pe payload.
    """
    if command == 'ECHO':
        return payload
    elif command == 'UPPER':
        return payload.upper()
    elif command == 'LOWER':
        return payload.lower()
    elif command == 'REVERSE':
        return payload[::-1]
    elif command == 'COUNT':
        return str(len(payload))
    else:
        return 'ERROR: Unknown command'


def sol_format_response(result: str) -> str:
    """
    SOLUTIE: Format raspunsul for client.
    """
    length = len(result.encode('utf-8'))
    return f"{length} {result}"


def sol_handle_client(client_socket: socket.socket, address: tuple):
    """
    SOLUTIE: Handle comunicarea with a client.
    """
    print(f"[+] Client conectat: {address}")
    
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            print(f"[{address}] Primit: {message}")
            
            command, length, payload = sol_parse_command(message)
            
            if command is None:
                response = sol_format_response("ERROR: Invalid command format")
            else:
                result = sol_execute_command(command, payload)
                response = sol_format_response(result)
            
            client_socket.sendall(response.encode('utf-8'))
            print(f"[{address}] Trimis: {response}")
            
    except ConnectionResetError:
        print(f"[-] Conexiune resetata: {address}")
    except Exception as e:
        print(f"[!] Eroare: {e}")
    finally:
        client_socket.close()
        print(f"[-] Client deconectat: {address}")


def sol_start_tcp_server(host: str = '0.0.0.0', port: int = TCP_DEFAULT_PORT):
    """
    SOLUTIE: Porneste serverul TCP multi-threaded.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[*] Server TCP pornit pe {host}:{port}")
        print(f"[*] Comenzi acceptate: {', '.join(VALID_COMMANDS)}")
        
        while True:
            client_socket, address = server_socket.accept()
            client_thread = threading.Thread(
                target=sol_handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[*] Server oprit")
    finally:
        server_socket.close()


# =============================================================================
# SOLUTIE EXERCITIUL 4.02: Agregator UDP Senzori
# =============================================================================

DATAGRAM_SIZE = 23
DATAGRAM_VERSION = 1
UDP_DEFAULT_PORT = 5556
REPORT_INTERVAL = 5


@dataclass
class SensorStatsSolution:
    """Statistici for un senzor."""
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
        return self.total / self.count if self.count > 0 else 0.0
    
    def to_dict(self) -> dict:
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


def sol_calculate_crc32(data: bytes) -> int:
    """Calculate CRC32."""
    return zlib.crc32(data) & 0xFFFFFFFF


def sol_parse_sensor_datagram(datagram: bytes) -> Optional[Tuple[int, float, str]]:
    """
    SOLUTIE: Parseaza o datagrama primita of to un senzor.
    """
    if len(datagram) != DATAGRAM_SIZE:
        print(f"[!] Datagrama invalida: lungime {len(datagram)}, asteptat {DATAGRAM_SIZE}")
        return None
    
    try:
        version, sensor_id, temperature, location_bytes, received_crc = struct.unpack(
            '>BIf10sI', datagram
        )
    except struct.error as e:
        print(f"[!] Eroare unpacking: {e}")
        return None
    
    if version != DATAGRAM_VERSION:
        print(f"[!] Versiune invalida: {version}, asteptat {DATAGRAM_VERSION}")
        return None
    
    # Validare CRC32
    payload_for_crc = datagram[:19]
    calculated_crc = sol_calculate_crc32(payload_for_crc)
    if calculated_crc != received_crc:
        print(f"[!] CRC invalid: primit {received_crc:08X}, calculat {calculated_crc:08X}")
        return None
    
    location = location_bytes.decode('utf-8', errors='replace').strip()
    
    return (sensor_id, temperature, location)


def sol_update_statistics(stats: Dict[int, SensorStatsSolution],
                          sensor_id: int,
                          temperature: float,
                          location: str) -> None:
    """
    SOLUTIE: Actualizeaza statisticile for un senzor.
    """
    if sensor_id not in stats:
        stats[sensor_id] = SensorStatsSolution(sensor_id=sensor_id, location=location)
    
    sensor = stats[sensor_id]
    sensor.count += 1
    sensor.total += temperature
    sensor.min_temp = min(sensor.min_temp, temperature)
    sensor.max_temp = max(sensor.max_temp, temperature)
    sensor.last_reading = temperature
    sensor.last_timestamp = datetime.now().isoformat()
    sensor.location = location


def sol_generate_report(stats: Dict[int, SensorStatsSolution]) -> dict:
    """
    SOLUTIE: Genereaza un raport JSON with toate statisticile.
    """
    total_readings = sum(s.count for s in stats.values())
    all_temps = [s.last_reading for s in stats.values() if s.count > 0]
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_sensors': len(stats),
        'total_readings': total_readings,
        'global_average': round(sum(all_temps) / len(all_temps), 2) if all_temps else None,
        'sensors': [s.to_dict() for s in stats.values()]
    }
    
    return report


def sol_print_report(stats: Dict[int, SensorStatsSolution]) -> None:
    """Afiseaza raportul in consola."""
    report = sol_generate_report(stats)
    
    print("\n" + "="*60)
    print(f"RAPORT SENZORI - {report['timestamp']}")
    print("="*60)
    print(f"Senzori activi: {report['total_sensors']}")
    print(f"Total citiri: {report['total_readings']}")
    
    if report['global_average']:
        print(f"Medie globala: {report['global_average']}°C")
    
    print("\nDetalii per senzor:")
    print("-"*60)
    
    for sensor in report['sensors']:
        print(f"  Senzor {sensor['sensor_id']} @ {sensor['location']}:")
        print(f"    Citiri: {sensor['readings_count']}")
        print(f"    Medie: {sensor['average_temp']}°C")
        print(f"    Min/Max: {sensor['min_temp']}°C / {sensor['max_temp']}°C")
        print(f"    Ultima: {sensor['last_reading']}°C")
    
    print("="*60 + "\n")


def sol_periodic_reporter(stats: Dict[int, SensorStatsSolution],
                          interval: int,
                          stop_event: threading.Event):
    """Thread for raportare periodica."""
    while not stop_event.is_set():
        stop_event.wait(interval)
        if not stop_event.is_set() and stats:
            sol_print_report(stats)


def sol_run_aggregator(host: str = '0.0.0.0',
                       port: int = UDP_DEFAULT_PORT,
                       report_interval: int = REPORT_INTERVAL) -> None:
    """
    SOLUTIE: Ruleaza serverul agregator UDP.
    """
    stats: Dict[int, SensorStatsSolution] = {}
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(1.0)
    
    print(f"[*] Agregator UDP pornit pe {host}:{port}")
    print(f"[*] Raportare to fiecare {report_interval} secunde")
    
    stop_event = threading.Event()
    if report_interval > 0:
        reporter = threading.Thread(
            target=sol_periodic_reporter,
            args=(stats, report_interval, stop_event),
            daemon=True
        )
        reporter.start()
    
    try:
        while True:
            try:
                datagram, addr = sock.recvfrom(DATAGRAM_SIZE + 100)
                
                result = sol_parse_sensor_datagram(datagram)
                if result:
                    sensor_id, temperature, location = result
                    sol_update_statistics(stats, sensor_id, temperature, location)
                    print(f"[+] Senzor {sensor_id} @ {location}: {temperature:.1f}°C")
                else:
                    print(f"[-] Datagrama invalida of to {addr}")
                    
            except socket.timeout:
                continue
                
    except KeyboardInterrupt:
        print("\n[*] Oprire...")
        stop_event.set()
        
        if stats:
            sol_print_report(stats)
            
    finally:
        sock.close()
        print("[*] Agregator oprit")


# =============================================================================
# HELPER FUNCTIONS FOR TESTING
# =============================================================================

def create_test_datagram(sensor_id: int, temperature: float, location: str) -> bytes:
    """Creeaza o datagrama of test valida."""
    location_padded = location[:10].ljust(10)
    
    payload = struct.pack(
        '>BIf10s',
        DATAGRAM_VERSION,
        sensor_id,
        temperature,
        location_padded.encode('utf-8')
    )
    
    crc = sol_calculate_crc32(payload)
    datagram = payload + struct.pack('>I', crc)
    
    return datagram


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    import sys
    
    print("="*60)
    print("FISIER SOLUTII - Exercitiile Saptamanii 4")
    print("="*60)
    print("""
Acest fisier contine solutiile complete for:

1. sol_parse_command() - Parsare comanda protocol TCP
2. sol_execute_command() - Executie comanda
3. sol_format_response() - Formatare response
4. sol_handle_client() - Handler client TCP
5. sol_start_tcp_server() - Server TCP multi-threaded

6. sol_parse_sensor_datagram() - Parsare datagrama UDP
7. sol_update_statistics() - Actualizare statistici
8. sol_generate_report() - Generare raport JSON
9. sol_run_aggregator() - Server agregator UDP

Utilizare:
  python3 solutions.py tcp     # Porneste serverul TCP (ex 4.01)
  python3 solutions.py udp     # Porneste agregatorul UDP (ex 4.02)
""")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'tcp':
            sol_start_tcp_server()
        elif sys.argv[1] == 'udp':
            sol_run_aggregator()
        else:
            print(f"Optiune necunoscuta: {sys.argv[1]}")
    else:
        print("Specificati 'tcp' or 'udp' for a ruto serverul corespunzator.")
