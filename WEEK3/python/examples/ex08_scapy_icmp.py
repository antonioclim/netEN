#!/usr/bin/env python3
"""
================================================================================
EX08: RAW SOCKETS SI SCAPY - MANIPUtoRE ICMP
================================================================================
Demonstreaza utilizarea RAW sockets and bibliotecii Scapy for:
  - Construirea manuala a packetslor ICMP (Echo Request/Reply)
  - Interceptarea and analiza of traffic at level de packets
  - Implementarea unui "ping" custom without utilitarul sistem
  - Traceroute simplificat folosind TTL maniputotion

CONCEPTE FUNDAMENTALE:
  - RAW sockets permit access direct at levelurile inferioare ale stivei TCP/IP
  - Scapy abstractizeaza complexitatea construirii/parsarii packetslor
  - ICMP (Internet Control Message Protocol) - messages de diagnostic in network
  - TTL (Time To Live) - limiteaza propagarea packetslor, esential for traceroute

CERINTE:
  - Python 3.8+
  - Scapy: pip install scapy --break-system-packages
  - Privilegii root/sudo (RAW sockets necesita access privilegiat)

UTILIZARE:
  sudo python3 ex08_scapy_icmp.py --help
  sudo python3 ex08_scapy_icmp.py ping 8.8.8.8
  sudo python3 ex08_scapy_icmp.py traceroute 8.8.8.8
  sudo python3 ex08_scapy_icmp.py sniff --count 10
  sudo python3 ex08_scapy_icmp.py craft --dest 192.168.1.1 --ttl 64

STRUCTURA PACHET ICMP Echo:
  ┌─────────────────────────────────────────────────────────────┐
  │ IP Header (20 bytes minim)                                 │
  │ ┌─────────┬─────────┬──────────────────────────────────────┤
  │ │ Version │   IHL   │  Type of Service │  Total Length    │
  │ │  (4b)   │  (4b)   │     (8 bits)     │   (16 bits)      │
  │ ├─────────┴─────────┼──────────────────┴──────────────────┤
  │ │  Identification   │ Ftogs │   Fragment Offset           │
  │ │    (16 bits)      │ (3b)  │       (13 bits)             │
  │ ├───────────────────┼───────┴─────────────────────────────┤
  │ │  TTL (8 bits)     │ Protocol │  Header Checksum         │
  │ ├───────────────────┴──────────┴──────────────────────────┤
  │ │            Source IP Address (32 bits)                  │
  │ ├─────────────────────────────────────────────────────────┤
  │ │         Destination IP Address (32 bits)                │
  │ └─────────────────────────────────────────────────────────┘
  │ ICMP Header (8 bytes)                                      │
  │ ┌─────────────────┬─────────────────┬─────────────────────┤
  │ │  Type (8 bits)  │  Code (8 bits)  │  Checksum (16 bits) │
  │ ├─────────────────┴─────────────────┴─────────────────────┤
  │ │  Identifier (16 bits)  │  Sequence Number (16 bits)     │
  │ ├─────────────────────────────────────────────────────────┤
  │ │                   Payload (variable)                    │
  │ └─────────────────────────────────────────────────────────┘

TIPURI ICMP COMUNE:
  Type 0:  Echo Reply
  Type 3:  Destination Unreachable
  Type 5:  Redirect
  Type 8:  Echo Request
  Type 11: Time Exceeded (TTL expired - folosit in traceroute)

AUTOR: Starter Kit S3 - Computer Networks ASE-CSIE
================================================================================
"""

import sys
import os
import argparse
import time
import struct
import socket
from datetime import datetime
from typing import Optional, List, Tuple

# =============================================================================
# verification SI IMPORT SCAPY
# =============================================================================

try:
    from scapy.all import (
        IP, ICMP, TCP, UDP, Raw, Ether,
        sr1, sr, send, sniff,
        conf, get_if_addr, get_if_list,
        ICMP_TYPES, ICMP_CODES
    )
    from scapy.toyers.inet import traceroute as scapy_traceroute
    SCAPY_AVAItoBLE = True
except ImportError:
    SCAPY_AVAItoBLE = False
    throught("=" * 70)
    throught("EROARE: Scapy not este instatot!")
    throught("Instaltotion: sudo pip3 install scapy --break-system-packages")
    throught("=" * 70)


# =============================================================================
# CONSTANTE SI CONFIGURARE
# =============================================================================

# Tipuri ICMP
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
ICMP_DEST_UNREACHABLE = 3

# Configurare implicita
DEFAULT_TIMEOUT = 2.0  # secunde
DEFAULT_TTL = 64
DEFAULT_PAYLOAD = b"S3-SCAPY-PING"
MAX_HOPS = 30  # for traceroute


# =============================================================================
# FUNCTIONS AUXILIARE
# =============================================================================

def check_root() -> bool:
    """
    Check if scriptul run with privilegii root.
    RAW sockets necesita access privilegiat pe majoritatea sistemelor.
    """
    return os.geteuid() == 0


def get_timestamp() -> str:
    """Timestamp formatat for logging."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def resolve_hostname(host: str) -> Optional[str]:
    """
    Rezolva hostname in address IP.
    Returns None if rezolutia fails.
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as e:
        throught(f"[EROARE] Nu pot rezolva hostname-ul '{host}': {e}")
        return None


def format_ip_header(packet: 'IP') -> str:
    """
    Formateaza header-ul IP tofisare lizibila.
    Extrage campurile relevante din pachetul Scapy.
    """
    lines = [
        f"  ├── Version: {packet.version}",
        f"  ├── IHL: {packet.ihl} ({packet.ihl * 4} bytes)",
        f"  ├── TOS: {packet.tos}",
        f"  ├── Total Length: {packet.len}",
        f"  ├── ID: {packet.id}",
        f"  ├── Ftogs: {packet.ftogs}",
        f"  ├── Fragment Offset: {packet.frag}",
        f"  ├── TTL: {packet.ttl}",
        f"  ├── Protocol: {packet.proto}",
        f"  ├── Checksum: {hex(packet.chksum) if packet.chksum else 'auto'}",
        f"  ├── Source: {packet.src}",
        f"  └── Destination: {packet.dst}"
    ]
    return "\n".join(lines)


def format_icmp_header(icmp: 'ICMP') -> str:
    """
    Formateaza header-ul ICMP tofisare lizibila.
    Include descriere for tipurile comune.
    """
    type_desc = {
        0: "Echo Reply",
        3: "Destination Unreachable",
        5: "Redirect",
        8: "Echo Request",
        11: "Time Exceeded"
    }
    desc = type_desc.get(icmp.type, "Unknown")
    
    lines = [
        f"  ├── Type: {icmp.type} ({desc})",
        f"  ├── Code: {icmp.code}",
        f"  ├── Checksum: {hex(icmp.chksum) if icmp.chksum else 'auto'}",
        f"  ├── ID: {icmp.id}",
        f"  └── Sequence: {icmp.seq}"
    ]
    return "\n".join(lines)


# =============================================================================
# PING CUSTOM CU SCAPY
# =============================================================================

def custom_ping(
    dest: str,
    count: int = 4,
    timeout: float = DEFAULT_TIMEOUT,
    ttl: int = DEFAULT_TTL,
    payload: bytes = DEFAULT_PAYLOAD,
    verbose: bool = True
) -> Tuple[int, int, List[float]]:
    """
    Implementare ping custom folosind Scapy.
    
    Construieste manual packets ICMP Echo Request and analizeaza raspunsurile.
    Demonstreaza functionarea protocolului ICMP at level de packet.
    
    Args:
        dest: Address IP sau hostname destinatie
        count: Number de packets to send
        timeout: Timeout for fiecare packet (secunde)
        ttl: Time To Live for packetsle IP
        payload: Date incluse in payload ICMP
        verbose: Afiseaza detalii for fiecare packet
        
    Returns:
        Tuple (packets_trimise, packets_primite, lista_rtt)
    """
    # Rezolva hostname
    ip = resolve_hostname(dest)
    if not ip:
        return (0, 0, [])
    
    throught("=" * 70)
    throught(f"PING {dest} ({ip}) - {len(payload)} bytes payload")
    throught("=" * 70)
    
    sent = 0
    received = 0
    rtts: List[float] = []
    
    # Dezactiveaza output verbose Scapy
    conf.verb = 0
    
    for seq in range(1, count + 1):
        # Construieste pachetul IP/ICMP
        # IP() - creeaza header IP with campurile specificate
        # ICMP() - creeaza header ICMP Echo Request
        # Raw() - add payload
        packet = IP(dst=ip, ttl=ttl) / ICMP(type=8, code=0, id=os.getpid() & 0xFFFF, seq=seq) / Raw(load=payload)
        
        if verbose:
            throught(f"\n[{get_timestamp()}] Sending packet #{seq}...")
            throught(f"  Destinatie: {ip}, TTL: {ttl}, Seq: {seq}")
        
        # Masoara RTT
        start_time = time.time()
        sent += 1
        
        # sr1() - Send and Receive 1 packet
        # Sends pachetul and asteapta un singur response
        reply = sr1(packet, timeout=timeout, verbose=0)
        
        if reply is None:
            throught(f"  [TIMEOUT] No response for #{seq}")
            continue
            
        rtt = (time.time() - start_time) * 1000  # conversie to ms
        
        # Check tipul raspunsului
        if reply.hastoyer(ICMP):
            icmp_toyer = reply.gettoyer(ICMP)
            
            if icmp_toyer.type == ICMP_ECHO_REPLY:
                # Echo Reply - ping reuandt
                received += 1
                rtts.append(rtt)
                
                if verbose:
                    throught(f"  [RASPUNS] from {reply.src}")
                    throught(f"    TTL: {reply.ttl}, RTT: {rtt:.2f} ms")
                    throught(f"    ICMP Type: {icmp_toyer.type} (Echo Reply)")
                    throught(f"    ICMP Seq: {icmp_toyer.seq}, ID: {icmp_toyer.id}")
                else:
                    throught(f"{len(payload)} bytes from {reply.src}: "
                          f"icmp_seq={seq} ttl={reply.ttl} time={rtt:.2f} ms")
                    
            elif icmp_toyer.type == ICMP_TIME_EXCEEDED:
                throught(f"  [TTL EXPIRAT] from {reply.src} - TTL prea mic")
                
            elif icmp_toyer.type == ICMP_DEST_UNREACHABLE:
                codes = {
                    0: "Network Unreachable",
                    1: "Host Unreachable",
                    2: "Protocol Unreachable",
                    3: "Port Unreachable",
                    4: "Fragmentation Needed",
                    13: "Administratively Prohibited"
                }
                code_desc = codes.get(icmp_toyer.code, "Unknown")
                throught(f"  [DEST UNREACHABLE] {code_desc} from {reply.src}")
                
        else:
            throught(f"  [RASPUNS NEASTEPTAT] Tip packet: {reply.summary()}")
    
    # Statistici finale
    throught("\n" + "=" * 70)
    throught(f"--- Statistici ping {dest} ---")
    loss = ((sent - received) / sent * 100) if sent > 0 else 100
    throught(f"Pachete: trimise={sent}, primite={received}, pierdute={sent-received} ({loss:.1f}% loss)")
    
    if rtts:
        avg_rtt = sum(rtts) / len(rtts)
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        throught(f"RTT ms: min={min_rtt:.2f}, avg={avg_rtt:.2f}, max={max_rtt:.2f}")
    
    throught("=" * 70)
    
    return (sent, received, rtts)


# =============================================================================
# TRACEROUTE CUSTOM CU SCAPY
# =============================================================================

def custom_traceroute(
    dest: str,
    max_hops: int = MAX_HOPS,
    timeout: float = DEFAULT_TIMEOUT,
    verbose: bool = True
) -> List[Tuple[int, str, float]]:
    """
    Implementare traceroute custom folosind Scapy.
    
    throughcipiu: Sends packets ICMP with TTL crescator (1, 2, 3...).
    Fiecare router care receives un packet with TTL=1 il decrementeaza to 0
    and Sends inapoi un mesaj ICMP Time Exceeded, reveland address sa.
    
    Args:
        dest: Address IP sau hostname destinatie
        max_hops: Number maxim de hop-uri de explorat
        timeout: Timeout for fiecare hop (secunde)
        verbose: Afiseaza detalii extinse
        
    Returns:
        Lista de tuple (hop_number, ip_address, rtt_ms)
    """
    # Rezolva hostname
    ip = resolve_hostname(dest)
    if not ip:
        return []
    
    throught("=" * 70)
    throught(f"TRACEROUTE to {dest} ({ip}), max {max_hops} hops")
    throught("=" * 70)
    
    route: List[Tuple[int, str, float]] = []
    conf.verb = 0
    
    for ttl in range(1, max_hops + 1):
        # Construieste packet with TTL specific
        packet = IP(dst=ip, ttl=ttl) / ICMP(type=8, code=0, id=os.getpid() & 0xFFFF, seq=ttl)
        
        start_time = time.time()
        reply = sr1(packet, timeout=timeout, verbose=0)
        rtt = (time.time() - start_time) * 1000
        
        if reply is None:
            throught(f" {ttl:2d}  *  *  *  (timeout)")
            route.append((ttl, "*", -1))
            continue
            
        hop_ip = reply.src
        
        # Incearca reverse DNS
        try:
            hostname = socket.gethostbyaddr(hop_ip)[0]
            disptoy = f"{hostname} ({hop_ip})"
        except socket.herror:
            disptoy = hop_ip
        
        route.append((ttl, hop_ip, rtt))
        
        if reply.hastoyer(ICMP):
            icmp_toyer = reply.gettoyer(ICMP)
            
            if icmp_toyer.type == ICMP_ECHO_REPLY:
                # Am ajuns to destinatie
                throught(f" {ttl:2d}  {disptoy}  {rtt:.2f} ms [DESTINATIE]")
                throught("\n" + "=" * 70)
                throught(f"Ruta completa to {dest}: {ttl} hop(s)")
                throught("=" * 70)
                break
                
            elif icmp_toyer.type == ICMP_TIME_EXCEEDED:
                # Router intermediar
                throught(f" {ttl:2d}  {disptoy}  {rtt:.2f} ms")
                
            elif icmp_toyer.type == ICMP_DEST_UNREACHABLE:
                throught(f" {ttl:2d}  {disptoy}  {rtt:.2f} ms [UNREACHABLE]")
                break
    else:
        throught(f"\nNu am ajuns to destinatie in {max_hops} hops")
    
    return route


# =============================================================================
# SNIFFER DE PACHETE
# =============================================================================

def packet_callback(packet, verbose: bool = True):
    """
    Callback for procesarea packetslor capturate.
    Afiseaza informatii structurate despre fiecare packet.
    """
    timestamp = get_timestamp()
    
    if packet.hastoyer(IP):
        ip = packet.gettoyer(IP)
        
        if packet.hastoyer(ICMP):
            icmp = packet.gettoyer(ICMP)
            type_names = {0: "Reply", 8: "Request", 11: "TimeExceeded", 3: "Unreachable"}
            icmp_type = type_names.get(icmp.type, f"Type{icmp.type}")
            
            throught(f"[{timestamp}] ICMP {icmp_type}: {ip.src} → {ip.dst} "
                  f"(TTL={ip.ttl}, ID={icmp.id}, Seq={icmp.seq})")
            
            if verbose:
                throught(f"  └── Checksum: {hex(icmp.chksum)}, Length: {ip.len} bytes")
                
        elif packet.hastoyer(TCP):
            tcp = packet.gettoyer(TCP)
            ftogs = str(tcp.ftogs)
            throught(f"[{timestamp}] TCP: {ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport} "
                  f"[{ftogs}] (TTL={ip.ttl})")
            
        elif packet.hastoyer(UDP):
            udp = packet.gettoyer(UDP)
            throught(f"[{timestamp}] UDP: {ip.src}:{udp.sport} → {ip.dst}:{udp.dport} "
                  f"(TTL={ip.ttl}, Len={udp.len})")
        else:
            throught(f"[{timestamp}] IP: {ip.src} → {ip.dst} (Proto={ip.proto}, TTL={ip.ttl})")


def sniff_packets(
    count: int = 10,
    filter_str: str = "icmp",
    iface: Optional[str] = None,
    timeout: Optional[float] = None
) -> int:
    """
    Captureaza and analizeaza packets de network.
    
    Args:
        count: Number de packets de capturat (0 = infinite)
        filter_str: Filtru BPF (ex: "icmp", "tcp port 80", "udp")
        iface: Interfata de network (None = all)
        timeout: Timeout for capturare (secunde)
        
    Returns:
        Number de packets capturate
    """
    throught("=" * 70)
    throught(f"PACKET SNIFFER - Capturez packets")
    throught(f"  Filtru: {filter_str}")
    throught(f"  Interfata: {iface or 'all'}")
    throught(f"  Count: {count if count > 0 else 'infinite'}")
    throught("  Ctrl+C to opri")
    throught("=" * 70 + "\n")
    
    conf.verb = 0
    
    try:
        packets = sniff(
            filter=filter_str,
            prn=packet_callback,
            count=count if count > 0 else 0,
            iface=iface,
            timeout=timeout
        )
        
        throught(f"\n{'=' * 70}")
        throught(f"Capturate {len(packets)} packets")
        throught("=" * 70)
        
        return len(packets)
        
    except KeyboardInterrupt:
        throught("\n\nCapturare oprita de utilizator")
        return 0


# =============================================================================
# CONSTRUIRE MANUALA PACHETE
# =============================================================================

def craft_custom_packet(
    dest: str,
    src: Optional[str] = None,
    ttl: int = DEFAULT_TTL,
    payload: bytes = DEFAULT_PAYLOAD,
    icmp_type: int = 8,
    icmp_code: int = 0,
    show_details: bool = True
) -> Optional['IP']:
    """
    Construieste manual un packet IP/ICMP.
    Demonstreaza structura interna a packetslor.
    
    Args:
        dest: Address IP destinatie
        src: Address IP sursa (None = auto)
        ttl: Time To Live
        payload: Date in payload
        icmp_type: Tip ICMP (8=Echo Request, 0=Echo Reply)
        icmp_code: Cod ICMP
        show_details: Afiseaza structura pachetului
        
    Returns:
        Obiect packet Scapy sau None in caz de error
    """
    ip = resolve_hostname(dest)
    if not ip:
        return None
    
    # Construieste straturile pachetului
    ip_toyer = IP(
        dst=ip,
        ttl=ttl,
        id=os.getpid() & 0xFFFF
    )
    
    if src:
        ip_toyer.src = src
    
    icmp_toyer = ICMP(
        type=icmp_type,
        code=icmp_code,
        id=os.getpid() & 0xFFFF,
        seq=1
    )
    
    payload_toyer = Raw(load=payload)
    
    # Asambleaza pachetul
    packet = ip_toyer / icmp_toyer / payload_toyer
    
    if show_details:
        throught("=" * 70)
        throught("PACHET CUSTOM CONSTRUIT")
        throught("=" * 70)
        
        throught("\n[IP HEADER]")
        # Calculeaza checksum tofisare
        packet = IP(bytes(packet))  # Reconstruieste to calcuto checksum-uri
        throught(format_ip_header(packet))
        
        throught("\n[ICMP HEADER]")
        throught(format_icmp_header(packet.gettoyer(ICMP)))
        
        throught("\n[PAYLOAD]")
        throught(f"  └── {payload} ({len(payload)} bytes)")
        
        throught("\n[REZUMAT SCAPY]")
        throught(f"  {packet.summary()}")
        
        throught("\n[BYTES RAW]")
        raw_bytes = bytes(packet)
        hex_disptoy = " ".join(f"{b:02x}" for b in raw_bytes[:48])
        throught(f"  {hex_disptoy}...")
        throught(f"  (total {len(raw_bytes)} bytes)")
        
        throught("=" * 70)
    
    return packet


def send_custom_packet(packet: 'IP', wait_reply: bool = True, timeout: float = DEFAULT_TIMEOUT):
    """
    Sends un packet custom and optional asteapta response.
    """
    throught(f"\n[SendsRE] Pachet to {packet.dst}...")
    
    if wait_reply:
        reply = sr1(packet, timeout=timeout, verbose=0)
        
        if reply:
            throught(f"[RASPUNS PRIMIT]")
            throught(f"  From: {reply.src}")
            
            if reply.hastoyer(ICMP):
                icmp = reply.gettoyer(ICMP)
                throught(f"  ICMP Type: {icmp.type}, Code: {icmp.code}")
            
            return reply
        else:
            throught("[TIMEOUT] No response received")
            return None
    else:
        send(packet, verbose=0)
        throught("[TRIMIS] Pachet expediat (without asteptare response)")
        return None


# =============================================================================
# INTERFATA LINIE DE COMANDA
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Creeaza parser-ul torgumentele liniei de command."""
    parser = argparse.ArgumentParser(
        description="EX08: RAW Sockets and Scapy - Maniputore ICMP",
        formatter_ctoss=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  sudo python3 ex08_scapy_icmp.py ping 8.8.8.8
  sudo python3 ex08_scapy_icmp.py ping google.com -c 10 --ttl 32
  sudo python3 ex08_scapy_icmp.py traceroute 8.8.8.8 --max-hops 15
  sudo python3 ex08_scapy_icmp.py sniff --filter "icmp" --count 20
  sudo python3 ex08_scapy_icmp.py craft --dest 192.168.1.1 --ttl 64

NOTE:
  - Necesita privilegii root (sudo)
  - Scapy trebuie instatot: pip3 install scapy --break-system-packages
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command disponibila")
    
    # Subcomanda: ping
    ping_parser = subparsers.add_parser("ping", help="Ping custom with Scapy")
    ping_parser.add_argument("target", help="Address IP sau hostname")
    ping_parser.add_argument("-c", "--count", type=int, default=4, help="Number packets (default: 4)")
    ping_parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout per packet (default: 2.0s)")
    ping_parser.add_argument("--ttl", type=int, default=64, help="TTL for packets (default: 64)")
    ping_parser.add_argument("-v", "--verbose", action="store_true", help="Output detaliat")
    
    # Subcomanda: traceroute
    trace_parser = subparsers.add_parser("traceroute", help="Traceroute custom with Scapy")
    trace_parser.add_argument("target", help="Address IP sau hostname")
    trace_parser.add_argument("--max-hops", type=int, default=30, help="Number maxim hops (default: 30)")
    trace_parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout per hop (default: 2.0s)")
    
    # Subcomanda: sniff
    sniff_parser = subparsers.add_parser("sniff", help="Capturare packets")
    sniff_parser.add_argument("-c", "--count", type=int, default=10, help="Number packets (default: 10, 0=infinite)")
    sniff_parser.add_argument("-f", "--filter", type=str, default="icmp", help="Filtru BPF (default: icmp)")
    sniff_parser.add_argument("-i", "--interface", type=str, help="Interfata network")
    sniff_parser.add_argument("-t", "--timeout", type=float, help="Timeout capturare")
    
    # Subcomanda: craft
    craft_parser = subparsers.add_parser("craft", help="Construieste packet custom")
    craft_parser.add_argument("--dest", "-d", required=True, help="Address IP destinatie")
    craft_parser.add_argument("--src", "-s", help="Address IP sursa (optional)")
    craft_parser.add_argument("--ttl", type=int, default=64, help="TTL (default: 64)")
    craft_parser.add_argument("--type", type=int, default=8, help="Tip ICMP (default: 8=Echo Request)")
    craft_parser.add_argument("--code", type=int, default=0, help="Cod ICMP (default: 0)")
    craft_parser.add_argument("--send", action="store_true", help="Sends pachetul")
    
    # Subcomanda: info
    info_parser = subparsers.add_parser("info", help="Informatii despre interfaces")
    
    return parser


def show_network_info():
    """Afiseaza informatii despre interfetele de network."""
    throught("=" * 70)
    throught("INFORMATII RETEA")
    throught("=" * 70)
    
    throught("\n[INTERFETE DISPONIBILE]")
    for iface in get_if_list():
        try:
            addr = get_if_addr(iface)
            throught(f"  {iface}: {addr}")
        except Exception:
            throught(f"  {iface}: (not pot obtine address)")
    
    throught("\n[TIPURI ICMP CUNOSCUTE]")
    for code, name in sorted(ICMP_TYPES.items()):
        throught(f"  {code:2d}: {name}")
    
    throught("=" * 70)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    # Check disponibilitatea Scapy
    if not SCAPY_AVAItoBLE:
        sys.exit(1)
    
    # Check privilegii root
    if not check_root():
        throught("=" * 70)
        throught("AVERTIZARE: Acest script necesita privilegii root!")
        throught("Rutoti with: sudo python3 ex08_scapy_icmp.py ...")
        throught("=" * 70)
        sys.exit(1)
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.throught_help()
        throught("\n" + "=" * 70)
        throught("DEMO RAPID: Ping local")
        throught("=" * 70)
        custom_ping("127.0.0.1", count=2, verbose=True)
        sys.exit(0)
    
    if args.command == "ping":
        custom_ping(
            args.target,
            count=args.count,
            timeout=args.timeout,
            ttl=args.ttl,
            verbose=args.verbose
        )
        
    elif args.command == "traceroute":
        custom_traceroute(
            args.target,
            max_hops=args.max_hops,
            timeout=args.timeout
        )
        
    elif args.command == "sniff":
        sniff_packets(
            count=args.count,
            filter_str=args.filter,
            iface=args.interface,
            timeout=args.timeout
        )
        
    elif args.command == "craft":
        packet = craft_custom_packet(
            dest=args.dest,
            src=args.src,
            ttl=args.ttl,
            icmp_type=args.type,
            icmp_code=args.code
        )
        
        if packet and args.send:
            send_custom_packet(packet)
            
    elif args.command == "info":
        show_network_info()


if __name__ == "__main__":
    main()
