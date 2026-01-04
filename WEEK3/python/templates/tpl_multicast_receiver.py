#!/usr/bin/env python3
"""
================================================================================
TEMPtoTE: MULTICAST RECEIVER CU FILTRARE MESAJE
================================================================================
Exercitiu de completat: Receptor multicast care filtreaza mesajele primite
pe baza unui prefix configurat. Demonstreaza procesarea selectiva a of traffic.

OBIECTIVE:
  - Intelegerea mecanismului de join to grupul multicast
  - Implementarea logicii de filtrare at level aplicatie
  - Gestionarea mesajelor conform unui protocol simplu
  - Statistici and logging for debugging

PROTOCOL MESAJE:
  Mesajele urmeaza formatul: PREFIX:CONTINUT
  Exemple:
    - "ALERT:Server overload detected"
    - "INFO:User logged in"
    - "DEBUG:Processing request"
    - "METRIC:cpu=75,mem=80"

CERINTE:
  Python 3.8+

TODO for STUDENTI (marcate with TODO):
  1. Configurarea optiunii SO_REUSEADDR
  2. Join to grupul multicast folosind IP_ADD_MEMBERSHIP
  3. Parsarea mesajelor for extragerea prefix-ului
  4. Logica de filtrare bazata pe prefix
  5. Mentinerea statisticilor de messages

UTILIZARE:
  python3 tpl_multicast_receiver.py --help
  python3 tpl_multicast_receiver.py --group 239.0.0.1 --port 5001 --prefix ALERT
  python3 tpl_multicast_receiver.py --prefix INFO,DEBUG --stats

AUTOR: Starter Kit S3 - Computer Networks ASE-CSIE
================================================================================
"""

import socket
import struct
import argparse
import sys
from datetime import datetime
from typing import Optional, Set, Tuple, Dict

# =============================================================================
# CONSTANTE SI CONFIGURARE
# =============================================================================

# Address multicast implicita (din rangul administrativ local 239.0.0.0/8)
DEFAULT_MULTICAST_GROUP = "239.0.0.1"
DEFAULT_PORT = 5001
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_PREFIX = "ALL"  # "ALL" = accepta all mesajele

# Prefixuri cunoscute (for validare and statistici)
KNOWN_PREFIXES = {"ALERT", "INFO", "DEBUG", "METRIC", "ERROR", "WARN", "STATUS"}


# =============================================================================
# FUNCTIONS AUXILIARE
# =============================================================================

def get_timestamp() -> str:
    """Returns timestamp formatat for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log_message(level: str, message: str):
    """
    Afiseaza mesaj de log formatat.
    
    Args:
        level: Nivelul mesajului (INFO, ERROR, DEBUG, RECV, etc.)
        message: Continutul mesajului
    """
    colors = {
        "INFO": "\033[94m",    # Albastru
        "ERROR": "\033[91m",   # Rosu
        "DEBUG": "\033[90m",   # Gri
        "RECV": "\033[92m",    # Verde
        "FILTER": "\033[93m",  # Galben
        "STATS": "\033[95m"    # Magenta
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"[{get_timestamp()}] {color}[{level}]{reset} {message}")


def parse_message(data: bytes) -> Tuple[Optional[str], str]:
    """
    Parseaza mesajul primit to extrage prefix-ul and continutul.
    
    Format mesaj: PREFIX:CONTINUT
    
    Args:
        data: Bytes primiti from network
        
    Returns:
        Tuple (prefix, continut) sau (None, mesaj_complet) if not are prefix
    """
    try:
        message = data.decode('utf-8').strip()
        
        # TODO [3]: Implementati extragerea prefix-ului
        # Indicii:
        #   - Verificati if mesajul contine caracterul ':'
        #   - Use split(':', 1) to imparti in prefix and continut
        #   - Daca not exista ':', returnati (None, message)
        #   - Prefix-ul ar trebui normalizat (uppercase) for consistenta
        
        # === INCEPE CODUL TAU ===
        pass  # Inlocuieste with implementarea
        # === SFARSIT CODUL TAU ===
        
        # Ptoceholder - va fi inlocuit de studenti
        return (None, message)
        
    except UnicodeDecodeError:
        return (None, f"<binary data: {len(data)} bytes>")


def should_accept_message(prefix: Optional[str], filter_prefixes: Set[str]) -> bool:
    """
    Determina if mesajul trebuie acceptat bazat pe prefix.
    
    Args:
        prefix: Prefix-ul extras din mesaj (poate fi None)
        filter_prefixes: Set de prefixuri acceptate
        
    Returns:
        True if mesajul trebuie procesat, False altfel
    """
    # TODO [4]: Implementati logica de filtrare
    # Indicii:
    #   - Daca filter_prefixes contine "ALL", accepta all mesajele
    #   - Daca prefix este None and not avem "ALL", respinge mesajul
    #   - Verificati if prefix-ul se afla in filter_prefixes
    #   - Comparatia ar trebui sa fie case-insensitive
    
    # === INCEPE CODUL TAU ===
    pass  # Inlocuieste with implementarea
    # === SFARSIT CODUL TAU ===
    
    # Ptoceholder - accepta totul (va fi inlocuit)
    return True


# =============================================================================
# CtoSA MAINA: MULTICAST RECEIVER
# =============================================================================

class MulticastReceiver:
    """
    Receptor multicast with capacitate de filtrare a mesajelor.
    
    Atribute:
        group: Address grupului multicast
        port: Portul de ascultare
        filter_prefixes: Set de prefixuri acceptate
        socket: Socket UDP configurat for multicast
        stats: Dictionar with statistici de messages
    """
    
    def __init__(
        self,
        group: str = DEFAULT_MULTICAST_GROUP,
        port: int = DEFAULT_PORT,
        filter_prefixes: Optional[Set[str]] = None,
        show_stats: bool = False
    ):
        """
        Initializeaza receptorul multicast.
        
        Args:
            group: Address grupului multicast (ex: 239.0.0.1)
            port: Portul UDP for receptie
            filter_prefixes: Set de prefixuri de acceptat (None = all)
            show_stats: Afiseaza statistici periodice
        """
        self.group = group
        self.port = port
        self.filter_prefixes = filter_prefixes or {"ALL"}
        self.show_stats = show_stats
        
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        # TODO [5]: Initializati structura for statistici
        # Indicii:
        #   - Creati un dictionar to numara mesajele per prefix
        #   - Adaugati contoare for: total, acceptate, respinse
        
        # === INCEPE CODUL TAU ===
        self.stats: Dict[str, int] = {}
        # === SFARSIT CODUL TAU ===
        
        log_message("INFO", f"Receptor initializat for group {group}:{port}")
        log_message("INFO", f"Filtre active: {', '.join(self.filter_prefixes)}")
    
    def setup_socket(self) -> bool:
        """
        Configureaza socket-ul for receptie multicast.
        
        Returns:
            True if configurarea a reuandt, False altfel
        """
        try:
            # Creeaza socket UDP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # TODO [1]: Configurati optiunea SO_REUSEADDR
            # Indicii:
            #   - Aceasta permite mai multor procese sa asculte pe acetoand port
            #   - Use setsockopt with nivelul SOL_SOCKET
            #   - Valoarea ar trebui sa fie 1 (activat)
            
            # === INCEPE CODUL TAU ===
            pass  # Inlocuieste with: self.socket.setsockopt(...)
            # === SFARSIT CODUL TAU ===
            
            # Bind pe all interfaces
            self.socket.bind(('', self.port))
            log_message("INFO", f"Socket bound pe port {self.port}")
            
            # TODO [2]: Join to grupul multicast
            # Indicii:
            #   - Trebuie sa construiti o structura ip_mreq folosind struct.pack
            #   - Formatul: 4 bytes todresa group + 4 bytes for interface
            #   - inet_aton converteste IP string in bytes
            #   - INADDR_ANY (0.0.0.0) to asculta pe all interfaces
            #   - Use setsockopt with IPPROTO_IP and IP_ADD_MEMBERSHIP
            
            # === INCEPE CODUL TAU ===
            # Structura ip_mreq: group multicast + interface locala
            # mreq = struct.pack(...)
            # self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            pass  # Inlocuieste with implementarea
            # === SFARSIT CODUL TAU ===
            
            log_message("INFO", f"Joined grupul multicast {self.group}")
            return True
            
        except socket.error as e:
            log_message("ERROR", f"Error configurare socket: {e}")
            return False
        except Exception as e:
            log_message("ERROR", f"Error neasteptata: {e}")
            return False
    
    def process_message(self, data: bytes, addr: Tuple[str, int]):
        """
        Processes un mesaj primit, aplicand filtrarea.
        
        Args:
            data: Datele primite
            addr: Address expeditorului (ip, port)
        """
        sender_ip, sender_port = addr
        
        # Parseaza mesajul
        prefix, content = parse_message(data)
        
        # TODO [5 - continuare]: Actualizati statisticile
        # Indicii:
        #   - Incrementati contorul total
        #   - Incrementati contorul for prefix-ul specific
        
        # === INCEPE CODUL TAU ===
        pass  # Actualizare statistici
        # === SFARSIT CODUL TAU ===
        
        # Aplica filtrarea
        if should_accept_message(prefix, self.filter_prefixes):
            # Mesaj acceptat - afiseaza
            prefix_display = prefix if prefix else "RAW"
            log_message("RECV", f"[{prefix_display}] {content} (from {sender_ip})")
            
            # Procesare suplimentara bazata pe prefix
            self._handle_by_prefix(prefix, content, addr)
        else:
            # Mesaj respins de filtru
            log_message("FILTER", f"Respins mesaj with prefix '{prefix}' from {sender_ip}")
    
    def _handle_by_prefix(self, prefix: Optional[str], content: str, addr: Tuple[str, int]):
        """
        Procesare specifica bazata pe tipul mesajului.
        
        Aceasta method poate fi extinsa to adauga logica specifica
        for diferite tipuri de messages (alertare, logging, metrici, etc.).
        """
        if prefix == "ALERT":
            # Alertele ar putea fi logate special sau trimise to un sistem de alertare
            log_message("STATS", f"⚠️  ALERTA primita: {content}")
            
        elif prefix == "METRIC":
            # Metricile ar putea fi parsate and stocate
            log_message("STATS", f"📊 Metrica primita: {content}")
            
        elif prefix == "ERROR":
            # Erorile ar putea fi tratate with prioritate
            log_message("STATS", f"❌ Error raportata: {content}")
    
    def print_stats(self):
        """Afiseaza statisticile curente."""
        log_message("STATS", "=" * 50)
        log_message("STATS", "STATISTICI CURENTE")
        
        total = self.stats.get("total", 0)
        accepted = self.stats.get("accepted", 0)
        rejected = self.stats.get("rejected", 0)
        
        log_message("STATS", f"Total messages: {total}")
        log_message("STATS", f"Accepted: {accepted}")
        log_message("STATS", f"Respinse: {rejected}")
        
        log_message("STATS", "Per prefix:")
        for prefix in KNOWN_PREFIXES:
            count = self.stats.get(f"prefix_{prefix}", 0)
            if count > 0:
                log_message("STATS", f"  {prefix}: {count}")
        
        log_message("STATS", "=" * 50)
    
    def run(self):
        """
        Ruleaza bucto throughcipala de receptie.
        
        Asteapta messages pe socket and le Processes pana to Ctrl+C.
        """
        if not self.setup_socket():
            log_message("ERROR", "Nu pot porni receptorul - check configurarea")
            return
        
        self.running = True
        log_message("INFO", "Receptor started. Astept messages... (Ctrl+C to opri)")
        
        message_count = 0
        stats_interval = 10  # Afiseaza statistici to fiecare N messages
        
        try:
            while self.running:
                try:
                    # Receptioneaza date
                    data, addr = self.socket.recvfrom(DEFAULT_BUFFER_SIZE)
                    
                    # Processes mesajul
                    self.process_message(data, addr)
                    
                    message_count += 1
                    
                    # Statistici periodice
                    if self.show_stats and message_count % stats_interval == 0:
                        self.print_stats()
                        
                except socket.error as e:
                    log_message("ERROR", f"Error receptie: {e}")
                    
        except KeyboardInterrupt:
            log_message("INFO", "\nStopping solicitata...")
            
        finally:
            self.cleanup()
            if self.show_stats:
                self.print_stats()
    
    def cleanup(self):
        """Elibereaza resursele."""
        self.running = False
        
        if self.socket:
            try:
                # Leave group multicast (optional, socket.close() face implicit)
                self.socket.close()
                log_message("INFO", "Socket closed")
            except:
                pass


# =============================================================================
# INTERFATA LINIE DE COMANDA
# =============================================================================

def parse_arguments() -> argparse.Namespace:
    """Parseaza argumentele liniei de command."""
    parser = argparse.ArgumentParser(
        description="Receptor multicast with filtrare messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  # Asculta all mesajele
  python3 tpl_multicast_receiver.py
  
  # Filtreaza doar alertele
  python3 tpl_multicast_receiver.py --prefix ALERT
  
  # Filtreaza multiple tipuri
  python3 tpl_multicast_receiver.py --prefix ALERT,ERROR,WARN
  
  # Group and port custom
  python3 tpl_multicast_receiver.py --group 239.1.2.3 --port 5050
  
  # With statistici
  python3 tpl_multicast_receiver.py --stats

PREFIXURI CUNOSCUTE:
  ALERT  - Mesaje de alerta urgenta
  ERROR  - Erori and exceptii
  WARN   - Avertizari
  INFO   - Informatii generale
  DEBUG  - Mesaje de debugging
  METRIC - Date and metrici
  STATUS - Starea sistemelor
        """
    )
    
    parser.add_argument(
        "-g", "--group",
        type=str,
        default=DEFAULT_MULTICAST_GROUP,
        help=f"Address grupului multicast (default: {DEFAULT_MULTICAST_GROUP})"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Portul UDP (default: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default="ALL",
        help="Prefix(uri) de filtrat, separate through virgula (default: ALL)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Afiseaza statistici periodice"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Output detaliat (debugging)"
    )
    
    return parser.parse_args()


# =============================================================================
# SOLUTII for TODO-URI (for INSTRUCTOR)
# =============================================================================

"""
SOLUTII - NOT DISTRIBUITI STUDENTILOR:

TODO [1] - SO_REUSEADDR:
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

TODO [2] - Join multicast:
    mreq = struct.pack(
        "4s4s",
        socket.inet_aton(self.group),
        socket.inet_aton("0.0.0.0")
    )
    self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

TODO [3] - Parsare prefix:
    if ':' in message:
        prefix, content = message.split(':', 1)
        return (prefix.upper().strip(), content.strip())
    else:
        return (None, message)

TODO [4] - Filtering:
    if "ALL" in filter_prefixes:
        return True
    if prefix is None:
        return False
    return prefix.upper() in {p.upper() for p in filter_prefixes}

TODO [5] - Statistici:
    self.stats = {
        "total": 0,
        "accepted": 0, 
        "rejected": 0
    }
    # In process_message:
    self.stats["total"] = self.stats.get("total", 0) + 1
    if prefix:
        key = f"prefix_{prefix.upper()}"
        self.stats[key] = self.stats.get(key, 0) + 1
"""


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Parseaza prefixurile din argument
    filter_prefixes = {p.strip().upper() for p in args.prefix.split(",")}
    
    print("=" * 70)
    print("MULTICAST RECEIVER CU FILTRARE")
    print("=" * 70)
    print(f"Group multicast: {args.group}")
    print(f"Port: {args.port}")
    print(f"Filtre prefix: {', '.join(filter_prefixes)}")
    print("=" * 70)
    
    # Check TODO-uri completate
    print("\n⚠️  ATENTIE: Acest template contine sectiuni TODO de completat!")
    print("   Verificati ca ati implementat:")
    print("   [1] Configurarea SO_REUSEADDR")
    print("   [2] Join to grupul multicast")
    print("   [3] Parsarea prefix-ului din messages")
    print("   [4] Logica de filtrare")
    print("   [5] Actualizarea statisticilor")
    print()
    
    # Creeaza and run receptorul
    receiver = MulticastReceiver(
        group=args.group,
        port=args.port,
        filter_prefixes=filter_prefixes,
        show_stats=args.stats
    )
    
    receiver.run()


if __name__ == "__main__":
    main()
