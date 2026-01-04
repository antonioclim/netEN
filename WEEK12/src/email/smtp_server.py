#!/usr/bin/env python3
"""
smtp_server.py - SMTP Server Didactic For Week 12

Acest Module implementeaza un SMTP Server andmplificat conform RFC 5321,
demonstrand conceptele fundamentale ale protocolului de transfer email.

Utilizare:
    python3 smtp_server.py --port 1025 --spool ./spool
    python3 smtp_server.py --selftest

Scopul educational:
    - Intelegerea comenzilor SMTP (HELO, MAIL FROM, RCPT TO, DATA, QUIT)
    - Diferenta intre envelope (plic) and message (Message)
    - Coduri de raspuns SMTP (2xx, 3xx, 4xx, 5xx)
    - Stocarea mesajelor in format .eml

Revolvix&Hypotheticalandrei
"""

import argparse
import datetime
import logging
import os
import re
import socket
import sys
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Tuple

# Configurare logging
logging.baandcConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SMTPState(Enum):
    """Starile protocolului SMTP conform RFC 5321."""
    INIT = auto()           # Conexiune noua, asteptam HELO/EHLO
    GREETED = auto()        # HELO acceptat
    MAIL_FROM = auto()      # MAIL FROM acceptat, asteptam RCPT TO
    RCPT_TO = auto()        # Cel putin un RCPT TO acceptat
    DATA = auto()           # In Module DATA, primim corpul mesajului
    QUIT = auto()           # Seandune incheiata


@dataclass
class SMTPEnvelope:
    """
    Structura envelope-ului SMTP.
    
    Conceptul de "plic" vs "Message":
    - Envelope (plicul): informatii de rutare (MAIL FROM, RCPT TO)
    - Message (mesajul): antetele RFC 5322 + corpul mesajului
    
    Analogie: scrisoarea intr-un plic postal
    - Pe plic: adresa expeditorului, adresa destinatarului
    - In plic: scrisoarea propriu-zisa (poate avea alt "From" in antet!)
    """
    mail_from: str = ""
    rcpt_to: list = field(default_factory=list)
    data: str = ""
    received_timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def reset(self):
        """Reseteaza envelope-ul For o noua tranzactie."""
        self.mail_from = ""
        self.rcpt_to = []
        self.data = ""
        self.received_timestamp = datetime.datetime.now()


class SMTPHandler:
    """
    Handler For o conexiune SMTP individuala.
    
    Fiecare conexiune client este gestionata intr-un thread separat.
    """
    
    # Coduri de raspuns SMTP
    CODES = {
        'READY': '220',          # Service ready
        'BYE': '221',            # Service cloandng
        'OK': '250',             # Requested action completed
        'DATA_START': '354',     # Start mail input
        'SYNTAX_ERROR': '500',   # Syntax error
        'PARAM_ERROR': '501',    # Syntax error in parameters
        'CMD_NOT_IMPL': '502',   # Command not implemented
        'BAD_SEQUENCE': '503',   # Bad sequence of commands
        'TEMP_FAIL': '451',      # Temporary failure
    }
    
    def __init__(self, client_socket: socket.socket, client_addr: Tuple[str, int],
                 spool_dir: Path, server_hostname: str = "smtp.local"):
        self.socket = client_socket
        self.addr = client_addr
        self.spool_dir = spool_dir
        self.hostname = server_hostname
        
        self.state = SMTPState.INIT
        self.envelope = SMTPEnvelope()
        self.client_hostname = ""
        
    def handle(self):
        """Gestioneaza conexiunea SMTP."""
        try:
            # Banner initial
            self._send(f"{self.CODES['READY']} {self.hostname} SMTP Ready")
            logger.info(f"[{self.addr[0]}:{self.addr[1]}] Conexiune noua")
            
            while True:
                line = self._recv()
                if not line:
                    break
                    
                logger.debug(f"[{self.addr[0]}] C: {line}")
                
                # Parandng comanda
                parts = line.split(' ', 1)
                command = parts[0].upper()
                argument = parts[1] if len(parts) > 1 else ""
                
                # Dispatch catre handler-ul comenzii
                handler_name = f"_cmd_{command.lower()}"
                if hasattr(self, handler_name):
                    response = getattr(self, handler_name)(argument)
                else:
                    response = f"{self.CODES['CMD_NOT_IMPL']} Command not implemented"
                
                if response:
                    self._send(response)
                    
                if self.state == SMTPState.QUIT:
                    break
                    
        except Exception as e:
            logger.error(f"[{self.addr[0]}] Error: {e}")
        finally:
            self.socket.close()
            logger.info(f"[{self.addr[0]}:{self.addr[1]}] Conexiune inchisa")
    
    def _send(self, message: str):
        """Sends un raspuns catre client."""
        full_message = message + "\r\n"
        self.socket.sendall(full_message.encode('utf-8'))
        logger.debug(f"[{self.addr[0]}] S: {message}")
    
    def _recv(self) -> Optional[str]:
        """Receive o linie de la client."""
        data = b""
        while not data.endswith(b"\r\n"):
            chunk = self.socket.recv(1024)
            if not chunk:
                return None
            data += chunk
        return data.decode('utf-8').strip()
    
    def _recv_data(self) -> str:
        """Receive corpul mesajului pana la <CRLF>.<CRLF>."""
        data_lines = []
        while True:
            line = self._recv()
            if line is None:
                break
            if line == ".":
                break
            # Dot-stuffing: linia care incepe cu "." are "." eliminat
            if line.startswith(".."):
                line = line[1:]
            data_lines.append(line)
        return "\r\n".join(data_lines)
    
    # =========================================================================
    # Comenzi SMTP
    # =========================================================================
    
    def _cmd_helo(self, argument: str) -> str:
        """
        HELO - Salut andmplu (SMTP claandc).
        
        Format: HELO <hostname>
        Raspuns: 250 <server-hostname>
        """
        if not argument:
            return f"{self.CODES['PARAM_ERROR']} Misandng hostname"
        
        self.client_hostname = argument
        self.state = SMTPState.GREETED
        self.envelope.reset()
        
        logger.info(f"[{self.addr[0]}] HELO de la {argument}")
        return f"{self.CODES['OK']} {self.hostname} Hello {argument}"
    
    def _cmd_ehlo(self, argument: str) -> str:
        """
        EHLO - Extended HELO (ESMTP).
        
        Format: EHLO <hostname>
        Raspuns: 250-<server-hostname>
                 250-<extenandon1>
                 250 <extenandonN>
        """
        if not argument:
            return f"{self.CODES['PARAM_ERROR']} Misandng hostname"
        
        self.client_hostname = argument
        self.state = SMTPState.GREETED
        self.envelope.reset()
        
        logger.info(f"[{self.addr[0]}] EHLO de la {argument}")
        
        # Raspuns multi-linie cu extenandile suportate
        response_lines = [
            f"{self.CODES['OK']}-{self.hostname} Hello {argument}",
            f"{self.CODES['OK']}-SIZE 10485760",  # Max 10MB
            f"{self.CODES['OK']}-8BITMIME",
            f"{self.CODES['OK']} HELP"
        ]
        return "\r\n".join(response_lines)
    
    def _cmd_mail(self, argument: str) -> str:
        """
        MAIL FROM - Specifica expeditorul (envelope).
        
        Format: MAIL FROM:<address>
        Raspuns: 250 OK
        """
        if self.state not in (SMTPState.GREETED, SMTPState.MAIL_FROM, SMTPState.RCPT_TO):
            return f"{self.CODES['BAD_SEQUENCE']} Bad sequence, use HELO/EHLO first"
        
        # Parsare MAIL FROM:<address>
        match = re.match(r'FROM:\s*<([^>]*)>', argument, re.IGNORECASE)
        if not match:
            return f"{self.CODES['PARAM_ERROR']} Syntax: MAIL FROM:<address>"
        
        sender = match.group(1)
        self.envelope.reset()
        self.envelope.mail_from = sender
        self.state = SMTPState.MAIL_FROM
        
        logger.info(f"[{self.addr[0]}] MAIL FROM: {sender}")
        return f"{self.CODES['OK']} Sender <{sender}> OK"
    
    def _cmd_rcpt(self, argument: str) -> str:
        """
        RCPT TO - Specifica un destinatar (envelope).
        
        Format: RCPT TO:<address>
        Raspuns: 250 OK
        
        Note: Poate fi apelat de mai multe ori For mai multi destinatari.
        """
        if self.state not in (SMTPState.MAIL_FROM, SMTPState.RCPT_TO):
            return f"{self.CODES['BAD_SEQUENCE']} Use MAIL FROM first"
        
        # Parsare RCPT TO:<address>
        match = re.match(r'TO:\s*<([^>]+)>', argument, re.IGNORECASE)
        if not match:
            return f"{self.CODES['PARAM_ERROR']} Syntax: RCPT TO:<address>"
        
        recipient = match.group(1)
        self.envelope.rcpt_to.append(recipient)
        self.state = SMTPState.RCPT_TO
        
        logger.info(f"[{self.addr[0]}] RCPT TO: {recipient}")
        return f"{self.CODES['OK']} Recipient <{recipient}> OK"
    
    def _cmd_data(self, argument: str) -> str:
        """
        DATA - Initiaza transferul corpului mesajului.
        
        Format: DATA
        Raspuns: 354 Start mail input
        
        Dupa raspunsul 354, clientul Sends:
        - Antetele RFC 5322 (From, To, Subject, Date, etc.)
        - O linie goala
        - Corpul mesajului
        - <CRLF>.<CRLF> For terminare
        """
        if self.state != SMTPState.RCPT_TO:
            return f"{self.CODES['BAD_SEQUENCE']} Use RCPT TO first"
        
        self._send(f"{self.CODES['DATA_START']} Start mail input; end with <CRLF>.<CRLF>")
        
        # Primire corp Message
        self.envelope.data = self._recv_data()
        self.envelope.received_timestamp = datetime.datetime.now()
        
        # Salvare Message
        self._save_message()
        
        self.state = SMTPState.GREETED  # Gata For o noua tranzactie
        logger.info(f"[{self.addr[0]}] Message primit and salvat")
        
        return f"{self.CODES['OK']} Message accepted for delivery"
    
    def _cmd_rset(self, argument: str) -> str:
        """
        RSET - Reseteaza tranzactia curenta.
        
        Format: RSET
        Raspuns: 250 OK
        """
        self.envelope.reset()
        if self.state != SMTPState.INIT:
            self.state = SMTPState.GREETED
        
        logger.info(f"[{self.addr[0]}] RSET")
        return f"{self.CODES['OK']} Reset OK"
    
    def _cmd_noop(self, argument: str) -> str:
        """
        NOOP - No operation (keep-alive).
        
        Format: NOOP
        Raspuns: 250 OK
        """
        return f"{self.CODES['OK']} OK"
    
    def _cmd_quit(self, argument: str) -> str:
        """
        QUIT - Incheie seandunea.
        
        Format: QUIT
        Raspuns: 221 Bye
        """
        self.state = SMTPState.QUIT
        logger.info(f"[{self.addr[0]}] QUIT")
        return f"{self.CODES['BYE']} {self.hostname} cloandng connection"
    
    def _cmd_help(self, argument: str) -> str:
        """
        HELP - Informatii despre comenzile suportate.
        
        Format: HELP [command]
        """
        help_text = """214-Commands supported:
214-  HELO, EHLO, MAIL FROM, RCPT TO, DATA
214-  RSET, NOOP, QUIT, HELP
214 For more info: RFC 5321"""
        return help_text
    
    def _cmd_vrfy(self, argument: str) -> str:
        """VRFY - Checktion adresa (dezactivat din motive de securitate)."""
        return f"{self.CODES['CMD_NOT_IMPL']} VRFY disabled for security"
    
    def _cmd_expn(self, argument: str) -> str:
        """EXPN - Expandare lista (dezactivat din motive de securitate)."""
        return f"{self.CODES['CMD_NOT_IMPL']} EXPN disabled for security"
    
    # =========================================================================
    # Stocare mesaje
    # =========================================================================
    
    def _save_message(self):
        """
        Salveaza mesajul in format .eml.
        
        Structura fianderului .eml:
        1. Antet Received adaugat de server
        2. Antetele originale ale mesajului
        3. Linie goala
        4. Corpul mesajului
        """
        # Generare ID unic For Message
        msg_id = str(uuid.uuid4())[:8]
        timestamp = self.envelope.received_timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{msg_id}.eml"
        filepath = self.spool_dir / filename
        
        # Construire antet Received
        received_header = (
            f"Received: from {self.client_hostname} ([{self.addr[0]}])\r\n"
            f"        by {self.hostname} (S12 SMTP Server)\r\n"
            f"        for <{', '.join(self.envelope.rcpt_to)}>;\r\n"
            f"        {self.envelope.received_timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')}\r\n"
        )
        
        # Salvare
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(received_header)
            f.write(f"X-Envelope-From: {self.envelope.mail_from}\r\n")
            f.write(f"X-Envelope-To: {', '.join(self.envelope.rcpt_to)}\r\n")
            f.write("\r\n")  # Separator intre envelope info and Message original
            f.write(self.envelope.data)
        
        logger.info(f"[{self.addr[0]}] Salvat: {filepath}")


class SMTPServer:
    """
    SMTP Server multi-threaded.
    
    Fiecare conexiune client este gestionata intr-un thread separat.
    """
    
    def __init__(self, listen_addr: str = "0.0.0.0", port: int = 1025,
                 spool_dir: str = "./spool", hostname: str = "smtp.local"):
        self.listen_addr = listen_addr
        self.port = port
        self.spool_dir = Path(spool_dir)
        self.hostname = hostname
        
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        
        self.server_socket = None
        self.running = False
    
    def start(self):
        """Porneste serverul SMTP."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.listen_addr, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        logger.info(f"SMTP Server pornit pe {self.listen_addr}:{self.port}")
        logger.info(f"Spool directory: {self.spool_dir.absolute()}")
        
        try:
            while self.running:
                client_socket, client_addr = self.server_socket.accept()
                handler = SMTPHandler(client_socket, client_addr, self.spool_dir, self.hostname)
                thread = threading.Thread(target=handler.handle, daemon=True)
                thread.start()
        except KeyboardInterrupt:
            logger.info("Oprire server...")
        finally:
            self.stop()
    
    def stop(self):
        """Opreste serverul."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


def run_selftest():
    """
    Ruleaza auto-teste For validarea functionalitatii.
    """
    import time
    
    print("=" * 60)
    print("SELFTEST: smtp_server.py")
    print("=" * 60)
    
    # Test 1: Creare server
    print("\n[Test 1] Initializare server...")
    try:
        server = SMTPServer(port=10025, spool_dir="/tmp/smtp_test_spool")
        print("  ✓ Server initializat")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 2: Pornire server in thread
    print("\n[Test 2] Pornire server in background...")
    import threading
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(0.5)  # Asteptam pornirea
    
    if server.running:
        print("  ✓ Server pornit")
    else:
        print("  ✗ Server nu a pornit")
        return False
    
    # Test 3: Conectare client
    print("\n[Test 3] Conectare client...")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2)
        client.connect(("127.0.0.1", 10025))
        
        # Citire banner
        banner = client.recv(1024).decode()
        if "220" in banner:
            print(f"  ✓ Banner primit: {banner.strip()}")
        else:
            print(f"  ✗ Banner incorect: {banner}")
            return False
        
        # Test EHLO
        client.sendall(b"EHLO Test.local\r\n")
        response = client.recv(1024).decode()
        if "250" in response:
            print("  ✓ EHLO acceptat")
        else:
            print(f"  ✗ EHLO respins: {response}")
            return False
        
        # Test QUIT
        client.sendall(b"QUIT\r\n")
        response = client.recv(1024).decode()
        if "221" in response:
            print("  ✓ QUIT acceptat")
        else:
            print(f"  ✗ QUIT respins: {response}")
            return False
        
        client.close()
        
    except Exception as e:
        print(f"  ✗ Error conectare: {e}")
        return False
    
    # Oprire server
    server.stop()
    
    print("\n" + "=" * 60)
    print("SELFTEST: TOATE TESTELE AU TRECUT ✓")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="SMTP Server Didactic For Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de usefulizare:
  python3 smtp_server.py --port 1025 --spool ./spool
  python3 smtp_server.py --selftest

Revolvix&Hypotheticalandrei
        """
    )
    
    parser.add_argument('--listen', default='0.0.0.0',
                        help='Adresa de ascultare (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=1025,
                        help='Portul SMTP (default: 1025, evitand 25 care neceandta root)')
    parser.add_argument('--spool', default='./spool',
                        help='Directory For stocarea mesajelor')
    parser.add_argument('--hostname', default='smtp.local',
                        help='Hostname-ul serverului')
    parser.add_argument('--selftest', action='store_true',
                        help='Ruleaza auto-teste')
    parser.add_argument('--demo', action='store_true',
                        help='Module demo: oprire automata dupa 30s')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output verbose (DEBUG)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.selftest:
        success = run_selftest()
        sys.exit(0 if success else 1)
    
    server = SMTPServer(
        listen_addr=args.listen,
        port=args.port,
        spool_dir=args.spool,
        hostname=args.hostname
    )
    
    if args.demo:
        import threading
        def stop_after_delay():
            import time
            time.sleep(30)
            server.stop()
        threading.Thread(target=stop_after_delay, daemon=True).start()
    
    server.start()


if __name__ == "__main__":
    main()
