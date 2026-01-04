#!/usr/bin/env python3
"""
ex_01_smtp.py - Self-Contained SMTP Exercises for Week 12

This file contains a minimal SMTP server and client for demonstrating
email concepts without external dependencies.

WHAT WE WILL LEARN:
- SMTP protocol and its fundamental commands
- Difference between envelope (MAIL FROM, RCPT TO) and message headers (From:, To:)
- Storage and parandng of .eml messages
- MIME structure for attachments

WHY IT MATTERS:
- Email remains the primary buandness communication channel
- Understanding SMTP is essential for debugging email problems
- The concepts of envelope vs message are found in many protocols

Usage:
    # Start server
    python3 ex_01_smtp.py server --port 1025
    
    # Send email
    python3 ex_01_smtp.py send --port 1025 --subject "Test"
    
    # List messages
    python3 ex_01_smtp.py list --spool ./spool_s12
    
    # Analyse envelope vs headers
    python3 ex_01_smtp.py analyze --spool ./spool_s12
    
    # Selftest
    python3 ex_01_smtp.py --selftest

Revolvix&Hypotheticalandrei
"""

import argparse
import datetime
import os
import re
import socket
import smtplib
import sys
import threading
import time
import uuid
from email.mime.text import MIMEText
from pathlib import Path


# =============================================================================
# CONCEPTE TEORETICE (in comentarii For studiu)
# =============================================================================
"""
SMTP - Simple Mail Transfer Protocol (RFC 5321)

ARHITECTURA EMAIL:
    MUA (Mail User Agent) → MTA (Mail Transfer Agent) → MDA (Mail Delivery Agent)
    
    Client de email → SMTP Server → Server destinatar → Mailbox

PORTURI SMTP:
    25   - Server-to-server (relay)
    587  - Submisandon (client → server)
    465  - SMTPS (SSL/TLS implicit)

COMENZI SMTP:
    HELO/EHLO  - Salut initial
    MAIL FROM: - Specifica expeditorul (envelope)
    RCPT TO:   - Specifica destinatarul (envelope)
    DATA       - Incepe transferul mesajului
    QUIT       - Inchide conexiunea
    RSET       - Reseteaza tranzactia
    NOOP       - Keep-alive

CODURI RASPUNS:
    2xx - Succes
    3xx - Continuare (ex: 354 For DATA)
    4xx - Error temporara
    5xx - Error permanenta

ENVELOPE vs MESSAGE:
    Envelope (plicul):
        - MAIL FROM: <sender@domain>
        - RCPT TO: <recipient@domain>
        - Foloandte For rutare
    
    Message (scrisoarea):
        - From: Sender Name <sender@domain>
        - To: Recipient Name <recipient@domain>
        - Subject: ...
        - Pot diferi de envelope!
"""


class MiniSMTPServer:
    """
    SMTP Server minimal For scopuri educationale.
    
    Implementeaza subset de comenzi For a demonstra Protocol.
    """
    
    def __init__(self, port: int = 1025, spool_dir: str = "./spool_s12"):
        self.port = port
        self.spool_dir = Path(spool_dir)
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.server_socket = None
        
    def start(self):
        """Porneste serverul."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"[SMTP] Server pornit pe port {self.port}")
        print(f"[SMTP] Spool: {self.spool_dir.absolute()}")
        print("[SMTP] Apasati Ctrl+C For a opri\n")
        
        try:
            while self.running:
                client_sock, addr = self.server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, addr),
                    daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[SMTP] Oprire server...")
        finally:
            self.stop()
    
    def stop(self):
        """Opreste serverul."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def _handle_client(self, sock: socket.socket, addr: tuple):
        """Gestioneaza o conexiune client."""
        print(f"[SMTP] Conexiune de la {addr[0]}:{addr[1]}")
        
        # State machine
        state = "INIT"
        mail_from = ""
        rcpt_to = []
        
        def send(msg):
            sock.sendall((msg + "\r\n").encode())
            print(f"[SMTP] S: {msg}")
        
        def recv():
            data = b""
            while not data.endswith(b"\r\n"):
                chunk = sock.recv(1024)
                if not chunk:
                    return None
                data += chunk
            line = data.decode().strip()
            print(f"[SMTP] C: {line}")
            return line
        
        try:
            # Banner
            send("220 smtp.local SMTP Ready")
            
            while True:
                line = recv()
                if not line:
                    break
                
                cmd = line.split()[0].upper() if line else ""
                arg = line[len(cmd):].strip() if len(line) > len(cmd) else ""
                
                if cmd in ("HELO", "EHLO"):
                    state = "GREETED"
                    mail_from = ""
                    rcpt_to = []
                    send(f"250 smtp.local Hello {arg}")
                
                elif cmd == "MAIL" and arg.upper().startswith("FROM:"):
                    if state not in ("GREETED", "MAIL", "RCPT"):
                        send("503 Bad sequence")
                        continue
                    match = re.search(r'<([^>]*)>', arg)
                    mail_from = match.group(1) if match else ""
                    state = "MAIL"
                    rcpt_to = []
                    send(f"250 Sender <{mail_from}> OK")
                
                elif cmd == "RCPT" and arg.upper().startswith("TO:"):
                    if state not in ("MAIL", "RCPT"):
                        send("503 Bad sequence, use MAIL FROM first")
                        continue
                    match = re.search(r'<([^>]+)>', arg)
                    recipient = match.group(1) if match else ""
                    rcpt_to.append(recipient)
                    state = "RCPT"
                    send(f"250 Recipient <{recipient}> OK")
                
                elif cmd == "DATA":
                    if state != "RCPT" or not rcpt_to:
                        send("503 Bad sequence, use RCPT TO first")
                        continue
                    send("354 Start mail input; end with <CRLF>.<CRLF>")
                    
                    # Primire corp
                    data_lines = []
                    while True:
                        data_line = recv()
                        if data_line == ".":
                            break
                        if data_line and data_line.startswith(".."):
                            data_line = data_line[1:]  # Dot unstuffing
                        data_lines.append(data_line if data_line else "")
                    
                    # Salvare
                    self._save_message(mail_from, rcpt_to, "\r\n".join(data_lines))
                    
                    state = "GREETED"
                    send("250 Message accepted")
                
                elif cmd == "RSET":
                    mail_from = ""
                    rcpt_to = []
                    state = "GREETED" if state != "INIT" else "INIT"
                    send("250 Reset OK")
                
                elif cmd == "NOOP":
                    send("250 OK")
                
                elif cmd == "QUIT":
                    send("221 Bye")
                    break
                
                else:
                    send("500 Command not recognized")
        
        except Exception as e:
            print(f"[SMTP] Error: {e}")
        finally:
            sock.close()
            print(f"[SMTP] Conexiune inchisa: {addr[0]}:{addr[1]}")
    
    def _save_message(self, mail_from: str, rcpt_to: list, data: str):
        """Salveaza mesajul in spool."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{msg_id}.eml"
        filepath = self.spool_dir / filename
        
        # Adaugam informatii despre envelope
        header = (
            f"X-Envelope-From: {mail_from}\r\n"
            f"X-Envelope-To: {', '.join(rcpt_to)}\r\n"
            f"X-Received: {datetime.datetime.now().isoformat()}\r\n"
        )
        
        with open(filepath, 'w') as f:
            f.write(header)
            f.write(data)
        
        print(f"[SMTP] Message salvat: {filepath}")


def send_email(host: str, port: int, sender: str, recipient: str, 
               subject: str, body: str, verbose: bool = False):
    """
    Sends un email uandng smtplib.
    
    Demonstreaza usefulizarea bibliotecii standard Python.
    """
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = f"Sender <{sender}>"
    msg['To'] = f"Recipient <{recipient}>"
    msg['Subject'] = subject
    msg['Date'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    try:
        smtp = smtplib.SMTP(host, port, timeout=10)
        if verbose:
            smtp.set_debuglevel(2)
        
        smtp.ehlo()
        smtp.sendmail(sender, [recipient], msg.as_string())
        smtp.quit()
        
        print(f"[OK] Email trimis: {sender} → {recipient}")
        return True
    except Exception as e:
        print(f"[ERR] {e}")
        return False


def list_messages(spool_dir: str):
    """Listeaza mesajele din spool."""
    spool = Path(spool_dir)
    if not spool.exists():
        print(f"[INFO] Spool '{spool_dir}' nu exista.")
        return
    
    files = list(spool.glob("*.eml"))
    if not files:
        print(f"[INFO] Niciun Message in {spool_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Mesaje in {spool.absolute()} ({len(files)} total)")
    print(f"{'='*60}\n")
    
    for filepath in sorted(files):
        with open(filepath) as f:
            content = f.read()
        
        # Extrage subject
        subject_match = re.search(r'^Subject:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        subject = subject_match.group(1) if subject_match else "(fara subiect)"
        
        # Extrage envelope
        env_from = re.search(r'^X-Envelope-From:\s*(.+)$', content, re.MULTILINE)
        env_to = re.search(r'^X-Envelope-To:\s*(.+)$', content, re.MULTILINE)
        
        print(f"📧 {filepath.name}")
        print(f"   Subject: {subject}")
        if env_from:
            print(f"   Envelope From: {env_from.group(1)}")
        if env_to:
            print(f"   Envelope To: {env_to.group(1)}")
        print()


def analyze_envelope_vs_headers(spool_dir: str):
    """
    Analizeaza diferenta intre envelope and message headers.
    
    Aceasta este o lectie cheie despre SMTP!
    """
    spool = Path(spool_dir)
    files = list(spool.glob("*.eml")) if spool.exists() else []
    
    if not files:
        print("[INFO] Niciun Message de analizat. Trimiteti cateva emailuri mai intai!")
        return
    
    print("\n" + "="*70)
    print("ANALIZA: ENVELOPE vs MESSAGE HEADERS")
    print("="*70)
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║  CONCEPTUL ENVELOPE vs MESSAGE                                      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ENVELOPE (plicul):                                                  ║
║    - MAIL FROM: și RCPT TO: din protocolul SMTP                     ║
║    - Foloandt for ROUTING and DELIVERY                               ║
║    - Nu este vizibil în clientul de email al usefulizatorului         ║
║                                                                      ║
║  MESSAGE HEADERS (scrisoarea):                                       ║
║    - From:, To:, Subject: din corpul mesajului RFC 5322             ║
║    - Afișate usefulizatorului în clientul de email                    ║
║    - POT DIFERI de envelope!                                        ║
║                                                                      ║
║  De ce contează:                                                     ║
║    - Spoofing: From: poate fi falandficat ușor                       ║
║    - BCC: destinatarii BCC sunt doar în envelope, nu în headers     ║
║    - Mailing lists: From: arată lista, envelope are adresa reală    ║
║                                                                      ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    for filepath in sorted(files)[:3]:  # Primele 3 mesaje
        with open(filepath) as f:
            content = f.read()
        
        print(f"\n📧 Fiander: {filepath.name}")
        print("-" * 50)
        
        # Envelope
        env_from = re.search(r'^X-Envelope-From:\s*(.+)$', content, re.MULTILINE)
        env_to = re.search(r'^X-Envelope-To:\s*(.+)$', content, re.MULTILINE)
        
        # Headers
        hdr_from = re.search(r'^From:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        hdr_to = re.search(r'^To:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        
        print(f"  ENVELOPE:")
        print(f"    MAIL FROM: {env_from.group(1) if env_from else 'N/A'}")
        print(f"    RCPT TO:   {env_to.group(1) if env_to else 'N/A'}")
        
        print(f"  MESSAGE HEADERS:")
        print(f"    From:      {hdr_from.group(1) if hdr_from else 'N/A'}")
        print(f"    To:        {hdr_to.group(1) if hdr_to else 'N/A'}")
        
        # Comparatie
        if env_from and hdr_from:
            env_addr = re.search(r'[\w.-]+@[\w.-]+', env_from.group(1))
            hdr_addr = re.search(r'[\w.-]+@[\w.-]+', hdr_from.group(1))
            if env_addr and hdr_addr:
                if env_addr.group() == hdr_addr.group():
                    print("  ✓ Envelope From == Message From")
                else:
                    print("  ⚠ DIFERENTA: Envelope From ≠ Message From!")


def run_selftest():
    """Ruleaza auto-teste."""
    print("="*60)
    print("SELFTEST: ex_01_smtp.py")
    print("="*60)
    
    spool_dir = "/tmp/smtp_selftest_spool"
    
    # Test 1: Start server
    print("\n[Test 1] Pornire SMTP Server...")
    server = MiniSMTPServer(port=11025, spool_dir=spool_dir)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(0.5)
    
    if server.running:
        print("  ✓ Server pornit")
    else:
        print("  ✗ Server nu a pornit")
        return False
    
    # Test 2: Conectare
    print("\n[Test 2] Conectare client...")
    try:
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect(("127.0.0.1", 11025))
        banner = sock.recv(1024).decode()
        if "220" in banner:
            print(f"  ✓ Banner: {banner.strip()}")
        sock.close()
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 3: Send email
    print("\n[Test 3] Send email...")
    success = send_email(
        "127.0.0.1", 11025,
        "Test@sender.local",
        "Test@recipient.local",
        "Selftest Subject",
        "Selftest body message."
    )
    if success:
        print("  ✓ Email trimis")
    else:
        print("  ✗ Trimitere esuata")
        return False
    
    # Test 4: Verification salvare
    print("\n[Test 4] Verification Message salvat...")
    time.sleep(0.3)
    files = list(Path(spool_dir).glob("*.eml"))
    if files:
        print(f"  ✓ Message gaandt: {files[0].name}")
    else:
        print("  ✗ Niciun Message salvat")
        return False
    
    # Cleanup
    server.stop()
    
    print("\n" + "="*60)
    print("SELFTEST: TOATE TESTELE AU TRECUT ✓")
    print("="*60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Exercises SMTP Self-Contained - Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comenzi disponibile:
  server   - Pornește serverul SMTP
  send     - Trimite un email
  list     - Listează mesajele din spool
  analyze  - Analizează envelope vs headers

Exemple:
  python3 ex_01_smtp.py server --port 1025
  python3 ex_01_smtp.py send --port 1025 --subject "Test"
  python3 ex_01_smtp.py list --spool ./spool_s12
  python3 ex_01_smtp.py analyze --spool ./spool_s12
  python3 ex_01_smtp.py --selftest

Revolvix&Hypotheticalandrei
        """
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Server
    p_server = subparsers.add_parser('server', help='Porneste serverul SMTP')
    p_server.add_argument('--port', type=int, default=1025)
    p_server.add_argument('--spool', default='./spool_s12')
    
    # Send
    p_send = subparsers.add_parser('send', help='Sends un email')
    p_send.add_argument('--host', default='127.0.0.1')
    p_send.add_argument('--port', type=int, default=1025)
    p_send.add_argument('--from', dest='sender', default='sender@Test.local')
    p_send.add_argument('--to', dest='recipient', default='recipient@Test.local')
    p_send.add_argument('--subject', default='Test S12')
    p_send.add_argument('--body', default='Message de Test din exercitiul SMTP.')
    p_send.add_argument('-v', '--verbose', action='store_true')
    
    # List
    p_list = subparsers.add_parser('list', help='Listeaza mesajele')
    p_list.add_argument('--spool', default='./spool_s12')
    
    # Analyze
    p_analyze = subparsers.add_parser('analyze', help='Analizeaza envelope vs headers')
    p_analyze.add_argument('--spool', default='./spool_s12')
    
    # Selftest
    parser.add_argument('--selftest', action='store_true', help='Ruleaza auto-teste')
    
    args = parser.parse_args()
    
    if args.selftest:
        success = run_selftest()
        sys.exit(0 if success else 1)
    
    if args.command == 'server':
        server = MiniSMTPServer(port=args.port, spool_dir=args.spool)
        server.start()
    
    elif args.command == 'send':
        send_email(
            args.host, args.port,
            args.sender, args.recipient,
            args.subject, args.body,
            args.verbose
        )
    
    elif args.command == 'list':
        list_messages(args.spool)
    
    elif args.command == 'analyze':
        analyze_envelope_vs_headers(args.spool)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
