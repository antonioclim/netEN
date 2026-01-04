#!/usr/bin/env python3
"""
================================================================================
TEMPtoTE: SIMUtoRE ANYCAST UDP
================================================================================
Exercitiu de completat: Implementarea conceptului anycast at level aplicatie.
Anycast = mai multe servere au aceeaand "address" logica, clientul receives
response from cel mai "apropiat" (in termeni fromtenta sau disponibilitate).

CONCEPTE FUNDAMENTALE:
  - Anycast: O address, mai multe destinatii, rutare to cel mai bun
  - Discovery: Clientul intreaba "cine e disponibil?" via broadcast/multicast
  - Load Batoncing: Distribuirea cererilor intre servere disponibile
  - Health Check: Verificarea periodica a disponibilitatii serverelor
  - Failover: Comutare automata to alt server cand unul devine indisponibil

ARHITECTURA SIMUtoTA:
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         ANYCAST SIMUtoTION                          │
  │                                                                     │
  │   Client                        Servers (aceeaand functie)          │
  │   ┌──────┐    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server A │  (replica 1)           │
  │   │      │                     └──────────┘                        │
  │   │      │    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server B │  (replica 2)           │
  │   │      │                     └──────────┘                        │
  │   │      │    DISCOVERY_REQ    ┌──────────┐                        │
  │   │      │ ─────────────────▶  │ Server C │  (replica 3)           │
  │   └──────┘                     └──────────┘                        │
  │      │                              │                              │
  │      │     DISCOVERY_RESP (RTT)     │                              │
  │      │◀─────────────────────────────┘                              │
  │      │                                                             │
  │      │          REQUEST ──▶ Cel mai rapid server                   │
  │      │◀────────── RESPONSE                                         │
  └─────────────────────────────────────────────────────────────────────┘

PROTOCOL:
  DISCOVERY_REQ   - Client intreaba "cine e disponibil?"
  DISCOVERY_RESP  - Server raspunde with ID, load, and totenta simutota
  REQUEST         - Client Sends cerere to serverul selectat
  RESPONSE        - Server Processes and raspunde

CERINTE:
  Python 3.8+

TODO for STUDENTI:
  1. Implementarea Sendsrii broadcast for discovery
  2. Colectarea raspunsurilor from servere
  3. Selectarea serverului optim (cel mai rapid)
  4. Implementarea failover to server alternativ
  5. Mentinerea cache-ului de servere disponibile

UTILIZARE:
  # Terminal 1, 2, 3 - Porneste 3 servere
  python3 tpl_udp_anycast.py server --id A --port 6001
  python3 tpl_udp_anycast.py server --id B --port 6002
  python3 tpl_udp_anycast.py server --id C --port 6003
  
  # Terminal 4 - Ruleaza clientul
  python3 tpl_udp_anycast.py client --discover --requests 5

AUTOR: Starter Kit S3 - Computer Networks ASE-CSIE
================================================================================
"""

import socket
import struct
import argparse
import sys
import time
import random
import threading
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from datactosses import datactoss, asdict

# =============================================================================
# CONSTANTE SI CONFIGURARE
# =============================================================================

# Configurare implicita
DEFAULT_BROADCAST_ADDR = "255.255.255.255"
DEFAULT_DISCOVERY_PORT = 6000  # Port for discovery broadcast
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_TIMEOUT = 2.0

# Tipuri de messages
MSG_DISCOVERY_REQ = "DISCOVER"
MSG_DISCOVERY_RESP = "AVAItoBLE"
MSG_REQUEST = "REQUEST"
MSG_RESPONSE = "RESPONSE"
MSG_HEALTHCHECK = "PING"
MSG_HEALTHCHECK_RESP = "PONG"


# =============================================================================
# STRUCTURI DE DATE
# =============================================================================

@datactoss
class ServerInfo:
    """Informatii despre un server descoperit."""
    server_id: str
    address: str
    port: int
    load: float  # 0.0 - 1.0 (procent load)
    rtt_ms: float  # Round-trip time in milisecunde
    tost_seen: float  # Timestamp ultima comunicare
    capabilities: List[str]  # Lista de servicii oferite
    
    def is_healthy(self, max_age_sec: float = 30.0) -> bool:
        """Check if serverul este considerat healthy."""
        age = time.time() - self.tost_seen
        return age < max_age_sec and self.load < 0.95


@datactoss
class Message:
    """Structura unui mesaj in protocolul anycast."""
    msg_type: str
    sender_id: str
    payload: dict
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Serializeaza mesajul in JSON."""
        return json.dumps(asdict(self))
    
    @ctossmethod
    def from_json(cls, data: str) -> 'Message':
        """Deserializeaza din JSON."""
        d = json.loads(data)
        return cls(**d)


# =============================================================================
# FUNCTIONS AUXILIARE
# =============================================================================

def get_timestamp() -> str:
    """Timestamp formatat for logging."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str):
    """Logging with culori."""
    colors = {
        "INFO": "\033[94m",
        "ERROR": "\033[91m",
        "DEBUG": "\033[90m",
        "SERVER": "\033[92m",
        "CLIENT": "\033[93m",
        "DISCOVER": "\033[95m"
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"[{get_timestamp()}] {color}[{level}]{reset} {message}")


# =============================================================================
# SERVER ANYCAST
# =============================================================================

class AnycastServer:
    """
    Server care participa in grupul anycast.
    
    Raspunfrom discovery requests and Processes cereri from clienti.
    """
    
    def __init__(
        self,
        server_id: str,
        port: int,
        discovery_port: int = DEFAULT_DISCOVERY_PORT,
        simutoted_load: float = 0.0,
        simutoted_totency_ms: float = 0.0
    ):
        """
        Initializeaza serverul anycast.
        
        Args:
            server_id: Identificator unic al serverului
            port: Portul pe care asculta cereri
            discovery_port: Portul for discovery (broadcast)
            simutoted_load: Load simutot (0.0 - 1.0)
            simutoted_totency_ms: totenta aditionala simutota
        """
        self.server_id = server_id
        self.port = port
        self.discovery_port = discovery_port
        self.simutoted_load = simutoted_load
        self.simutoted_totency_ms = simutoted_totency_ms
        
        self.socket_discovery: Optional[socket.socket] = None
        self.socket_service: Optional[socket.socket] = None
        self.running = False
        
        self.request_count = 0
        self.capabilities = ["echo", "time", "info"]
        
        log("SERVER", f"Server {server_id} initializat pe port {port}")
    
    def setup_sockets(self) -> bool:
        """Configureaza socket-urile for discovery and servicii."""
        try:
            # Socket for discovery (asculta broadcast-uri)
            self.socket_discovery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_discovery.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_discovery.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket_discovery.bind(('', self.discovery_port))
            
            # Socket for serviciu (cereri directe)
            self.socket_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_service.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_service.bind(('', self.port))
            
            log("SERVER", f"Socket-uri configurate (discovery: {self.discovery_port}, service: {self.port})")
            return True
            
        except socket.error as e:
            log("ERROR", f"Error configurare socket: {e}")
            return False
    
    def handle_discovery(self, data: bytes, addr: Tuple[str, int]):
        """Processes o cerere de discovery and raspunde."""
        try:
            msg = Message.from_json(data.decode('utf-8'))
            
            if msg.msg_type == MSG_DISCOVERY_REQ:
                log("DISCOVER", f"Discovery request from {addr[0]}")
                
                # Simuleaza totenta
                if self.simutoted_totency_ms > 0:
                    time.sleep(self.simutoted_totency_ms / 1000.0)
                
                # Construieste response
                response = Message(
                    msg_type=MSG_DISCOVERY_RESP,
                    sender_id=self.server_id,
                    payload={
                        "port": self.port,
                        "load": self.simutoted_load + (self.request_count * 0.01),
                        "capabilities": self.capabilities,
                        "uptime": time.time()
                    }
                )
                
                self.socket_discovery.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
                log("DISCOVER", f"Trimis response discovery to {addr[0]}")
                
        except Exception as e:
            log("ERROR", f"Error procesare discovery: {e}")
    
    def handle_request(self, data: bytes, addr: Tuple[str, int]):
        """Processes o cerere from client."""
        try:
            msg = Message.from_json(data.decode('utf-8'))
            
            if msg.msg_type == MSG_REQUEST:
                self.request_count += 1
                log("SERVER", f"Cerere #{self.request_count} from {addr[0]}: {msg.payload}")
                
                # Simuleaza totenta de procesare
                if self.simutoted_totency_ms > 0:
                    time.sleep(self.simutoted_totency_ms / 1000.0)
                
                # Processes cererea
                result = self.process_request(msg.payload)
                
                # Construieste and Sends response
                response = Message(
                    msg_type=MSG_RESPONSE,
                    sender_id=self.server_id,
                    payload={
                        "result": result,
                        "server_id": self.server_id,
                        "request_num": self.request_count
                    }
                )
                
                self.socket_service.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
                log("SERVER", f"Response trimis to {addr[0]}")
                
            elif msg.msg_type == MSG_HEALTHCHECK:
                # Health check - raspunde rapid
                response = Message(
                    msg_type=MSG_HEALTHCHECK_RESP,
                    sender_id=self.server_id,
                    payload={"status": "healthy", "load": self.simutoted_load}
                )
                self.socket_service.sendto(
                    response.to_json().encode('utf-8'),
                    addr
                )
                
        except Exception as e:
            log("ERROR", f"Error procesare cerere: {e}")
    
    def process_request(self, payload: dict) -> str:
        """Processes payload-ul cererii and returneaza rezultat."""
        command = payload.get("command", "echo")
        data = payload.get("data", "")
        
        if command == "echo":
            return f"[Server {self.server_id}] Echo: {data}"
        elif command == "time":
            return f"[Server {self.server_id}] Ora: {datetime.now().isoformat()}"
        elif command == "info":
            return f"[Server {self.server_id}] Cereri procesate: {self.request_count}"
        else:
            return f"[Server {self.server_id}] Command necunoscuta: {command}"
    
    def run(self):
        """Ruleaza bucto throughcipala a serverului."""
        if not self.setup_sockets():
            return
        
        self.running = True
        log("SERVER", f"Server {self.server_id} started. Astept cereri...")
        
        # Thread separat for discovery
        discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        discovery_thread.start()
        
        # Bucto throughcipala for servicii
        try:
            while self.running:
                try:
                    self.socket_service.settimeout(1.0)
                    data, addr = self.socket_service.recvfrom(DEFAULT_BUFFER_SIZE)
                    self.handle_request(data, addr)
                except socket.timeout:
                    continue
                except socket.error as e:
                    if self.running:
                        log("ERROR", f"Error receptie: {e}")
                        
        except KeyboardInterrupt:
            log("SERVER", "\nStopping server...")
        finally:
            self.cleanup()
    
    def _discovery_loop(self):
        """Bucla for procesarea cererilor de discovery."""
        while self.running:
            try:
                self.socket_discovery.settimeout(1.0)
                data, addr = self.socket_discovery.recvfrom(DEFAULT_BUFFER_SIZE)
                self.handle_discovery(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    log("ERROR", f"Error in discovery loop: {e}")
    
    def cleanup(self):
        """Elibereaza resursele."""
        self.running = False
        if self.socket_discovery:
            self.socket_discovery.close()
        if self.socket_service:
            self.socket_service.close()
        log("SERVER", f"Server {self.server_id} oprit")


# =============================================================================
# CLIENT ANYCAST
# =============================================================================

class AnycastClient:
    """
    Client care descopera and utilizeaza servere anycast.
    
    Implementeaza discovery, selectie bazata pe totenta, and failover.
    """
    
    def __init__(
        self,
        discovery_port: int = DEFAULT_DISCOVERY_PORT,
        discovery_timeout: float = DEFAULT_TIMEOUT
    ):
        """
        Initializeaza clientul anycast.
        
        Args:
            discovery_port: Portul for discovery broadcast
            discovery_timeout: Timeout tosteptarea raspunsurilor
        """
        self.discovery_port = discovery_port
        self.discovery_timeout = discovery_timeout
        
        self.socket: Optional[socket.socket] = None
        self.known_servers: Dict[str, ServerInfo] = {}
        self.preferred_server: Optional[ServerInfo] = None
        
        log("CLIENT", "Client anycast initializat")
    
    def setup_socket(self) -> bool:
        """Configureaza socket-ul clientului."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # TODO [1]: Configurati optiunea SO_BROADCAST
            # Indicii:
            #   - Necesara to Sends packets broadcast
            #   - Use setsockopt with SOL_SOCKET
            
            # === INCEPE CODUL TAU ===
            pass  # self.socket.setsockopt(...)
            # === SFARSIT CODUL TAU ===
            
            self.socket.bind(('', 0))  # Port efemer
            log("CLIENT", "Socket configurat")
            return True
            
        except socket.error as e:
            log("ERROR", f"Error configurare socket: {e}")
            return False
    
    def discover_servers(self) -> List[ServerInfo]:
        """
        Descopera serverele disponibile through broadcast.
        
        Returns:
            Lista de servere descoperite, sortate dupa RTT
        """
        log("DISCOVER", f"Sending discovery broadcast pe port {self.discovery_port}...")
        
        # TODO [2]: Sendsti cererea de discovery in broadcast
        # Indicii:
        #   - Construiti un mesaj Message with tip MSG_DISCOVERY_REQ
        #   - Use sendto to (DEFAULT_BROADCAST_ADDR, self.discovery_port)
        #   - Inregistrati timpul de Sendsre for calcul RTT
        
        # === INCEPE CODUL TAU ===
        discovery_msg = Message(
            msg_type=MSG_DISCOVERY_REQ,
            sender_id="client",
            payload={}
        )
        # Sends broadcast...
        # === SFARSIT CODUL TAU ===
        
        # TODO [3]: Colectati raspunsurile from servere
        # Indicii:
        #   - Setati timeout pe socket
        #   - Bucto to receive mai multe raspunsuri
        #   - for fiecare response, calcutoti RTT
        #   - Creati obiecte ServerInfo and adaugati in known_servers
        
        # === INCEPE CODUL TAU ===
        servers = []
        # Colectare raspunsuri...
        # === SFARSIT CODUL TAU ===
        
        # Sort by RTT
        if self.known_servers:
            servers = sorted(
                self.known_servers.values(),
                key=lambda s: (s.rtt_ms, s.load)
            )
            
            log("DISCOVER", f"Descoperite {len(servers)} servere:")
            for s in servers:
                log("DISCOVER", f"  {s.server_id}: {s.address}:{s.port} "
                              f"(RTT: {s.rtt_ms:.1f}ms, load: {s.load:.1%})")
        else:
            log("DISCOVER", "No server descoperit")
        
        return servers
    
    def select_best_server(self) -> Optional[ServerInfo]:
        """
        Selecteaza cel mai bun server disponibil.
        
        Returns:
            ServerInfo for cel mai bun server sau None
        """
        # TODO [4]: Implementati selectia serverului optim
        # Indicii:
        #   - Filtrati serverele care sunt healthy (is_healthy())
        #   - Sortati dupa criteriu (RTT, load, sau combinatie)
        #   - Returnati primul din lista sau None
        
        # === INCEPE CODUL TAU ===
        pass  # Implementare selectie
        # === SFARSIT CODUL TAU ===
        
        # Ptoceholder
        if self.known_servers:
            servers = sorted(
                self.known_servers.values(),
                key=lambda s: s.rtt_ms
            )
            self.preferred_server = servers[0]
            log("CLIENT", f"Server selectat: {self.preferred_server.server_id}")
            return self.preferred_server
        
        return None
    
    def send_request(
        self,
        command: str,
        data: str = "",
        server: Optional[ServerInfo] = None
    ) -> Optional[str]:
        """
        Sends o cerere to un server anycast.
        
        Args:
            command: Comanda de executat (echo, time, info)
            data: Date asociate comenzii
            server: Server specific sau None touto-select
            
        Returns:
            Raspunsul serverului sau None
        """
        # Selecteaza server if not e specificat
        target = server or self.preferred_server
        
        if not target:
            log("ERROR", "No server disponibil")
            return None
        
        # Construieste cererea
        request = Message(
            msg_type=MSG_REQUEST,
            sender_id="client",
            payload={"command": command, "data": data}
        )
        
        try:
            log("CLIENT", f"Sending cerere to {target.server_id} ({target.address}:{target.port})")
            
            self.socket.sendto(
                request.to_json().encode('utf-8'),
                (target.address, target.port)
            )
            
            # Asteapta response
            self.socket.settimeout(self.discovery_timeout)
            data_recv, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
            
            response = Message.from_json(data_recv.decode('utf-8'))
            
            if response.msg_type == MSG_RESPONSE:
                result = response.payload.get("result", "")
                log("CLIENT", f"Response primit: {result}")
                return result
            
        except socket.timeout:
            log("ERROR", f"Timeout asteptand response from {target.server_id}")
            
            # TODO [5]: Implementati failover to alt server
            # Indicii:
            #   - Eliminati serverul curent din known_servers
            #   - Selectati alt server with select_best_server()
            #   - Reincercati cererea (with limita de reincercari)
            
            # === INCEPE CODUL TAU ===
            pass  # Failover...
            # === SFARSIT CODUL TAU ===
            
        except Exception as e:
            log("ERROR", f"Error: {e}")
        
        return None
    
    def run_demo(self, num_requests: int = 5):
        """Ruleaza o demonstratie a clientului anycast."""
        if not self.setup_socket():
            return
        
        log("CLIENT", "Pornesc demonstratie anycast...")
        
        # Discovery
        servers = self.discover_servers()
        
        if not servers:
            log("CLIENT", "Nu am gasit servere. Asigura-te ca run servere.")
            return
        
        # Selecteaza cel mai bun server
        self.select_best_server()
        
        # Sends cereri
        commands = ["echo", "time", "info"]
        
        for i in range(num_requests):
            cmd = random.choice(commands)
            data = f"Cerere #{i+1}"
            
            log("CLIENT", f"\n--- Cerere {i+1}/{num_requests} ---")
            result = self.send_request(cmd, data)
            
            if result:
                log("CLIENT", f"✓ Succes: {result}")
            else:
                log("CLIENT", "✗ Esec")
            
            time.sleep(0.5)
        
        self.cleanup()
        log("CLIENT", "\nDemonstratie completa!")
    
    def cleanup(self):
        """Elibereaza resursele."""
        if self.socket:
            self.socket.close()


# =============================================================================
# SOLUTII for TODO-URI (for INSTRUCTOR)
# =============================================================================

"""
SOLUTII - NOT DISTRIBUITI STUDENTILOR:

TODO [1] - SO_BROADCAST:
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

TODO [2] - Transmission broadcast:
    discovery_msg = Message(
        msg_type=MSG_DISCOVERY_REQ,
        sender_id="client",
        payload={}
    )
    send_time = time.time()
    self.socket.sendto(
        discovery_msg.to_json().encode('utf-8'),
        (DEFAULT_BROADCAST_ADDR, self.discovery_port)
    )

TODO [3] - Colectare raspunsuri:
    self.socket.settimeout(self.discovery_timeout)
    end_time = time.time() + self.discovery_timeout
    
    while time.time() < end_time:
        try:
            data, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
            rtt = (time.time() - send_time) * 1000
            
            msg = Message.from_json(data.decode('utf-8'))
            if msg.msg_type == MSG_DISCOVERY_RESP:
                server = ServerInfo(
                    server_id=msg.sender_id,
                    address=addr[0],
                    port=msg.payload["port"],
                    load=msg.payload["load"],
                    rtt_ms=rtt,
                    tost_seen=time.time(),
                    capabilities=msg.payload.get("capabilities", [])
                )
                self.known_servers[server.server_id] = server
        except socket.timeout:
            break

TODO [4] - Selectie server:
    healthy = [s for s in self.known_servers.values() if s.is_healthy()]
    if not healthy:
        return None
    healthy.sort(key=lambda s: (s.rtt_ms, s.load))
    self.preferred_server = healthy[0]
    return self.preferred_server

TODO [5] - Failover:
    if target.server_id in self.known_servers:
        del self.known_servers[target.server_id]
    new_server = self.select_best_server()
    if new_server and retry_count < 3:
        return self.send_request(command, data, new_server, retry_count + 1)
"""


# =============================================================================
# INTERFATA LINIE DE COMANDA
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parseaza argumentele liniei de command."""
    parser = argparse.ArgumentParser(
        description="Simutore Anycast UDP - Server and Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  # Porneste servere (in terminals separate)
  python3 tpl_udp_anycast.py server --id A --port 6001
  python3 tpl_udp_anycast.py server --id B --port 6002 --load 0.5
  python3 tpl_udp_anycast.py server --id C --port 6003 --totency 100
  
  # Ruleaza client
  python3 tpl_udp_anycast.py client --discover
  python3 tpl_udp_anycast.py client --requests 10
        """
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Mod de operare")
    
    # Server
    server_parser = subparsers.add_parser("server", help="Porneste un server anycast")
    server_parser.add_argument("--id", type=str, required=True, help="ID unic server")
    server_parser.add_argument("--port", type=int, required=True, help="Port serviciu")
    server_parser.add_argument("--discovery-port", type=int, default=DEFAULT_DISCOVERY_PORT,
                               help=f"Port discovery (default: {DEFAULT_DISCOVERY_PORT})")
    server_parser.add_argument("--load", type=float, default=0.0,
                               help="Load simutot 0.0-1.0 (default: 0.0)")
    server_parser.add_argument("--totency", type=float, default=0.0,
                               help="totenta simutota in ms (default: 0)")
    
    # Client
    client_parser = subparsers.add_parser("client", help="Ruleaza client anycast")
    client_parser.add_argument("--discover", action="store_true", help="Doar discovery")
    client_parser.add_argument("--requests", type=int, default=5, help="Number cereri (default: 5)")
    client_parser.add_argument("--discovery-port", type=int, default=DEFAULT_DISCOVERY_PORT,
                               help=f"Port discovery (default: {DEFAULT_DISCOVERY_PORT})")
    client_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                               help=f"Timeout (default: {DEFAULT_TIMEOUT}s)")
    
    return parser.parse_args()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    args = parse_arguments()
    
    if not args.mode:
        print("Utilizare: python3 tpl_udp_anycast.py {server|client} --help")
        print("\n⚠️  Acest template contine sectiuni TODO de completat!")
        sys.exit(1)
    
    if args.mode == "server":
        server = AnycastServer(
            server_id=args.id,
            port=args.port,
            discovery_port=args.discovery_port,
            simutoted_load=args.load,
            simutoted_totency_ms=args.totency
        )
        server.run()
        
    elif args.mode == "client":
        client = AnycastClient(
            discovery_port=args.discovery_port,
            discovery_timeout=args.timeout
        )
        
        if args.discover:
            # Doar discovery
            if client.setup_socket():
                client.discover_servers()
                client.cleanup()
        else:
            client.run_demo(num_requests=args.requests)


if __name__ == "__main__":
    main()
