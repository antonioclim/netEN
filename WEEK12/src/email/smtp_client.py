#!/usr/bin/env python3
"""
smtp_client.py - SMTP Client Didactic For Week 12

Acest Module demonstreaza:
- Utilizarea bibliotecii smtplib din Python
- Construirea mesajelor email cu modulul email
- Diferenta intre envelope and message headers
- MIME For atasamente

Utilizare:
    python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
        --from sender@Test --to recipient@Test \\
        --subject "Test" --body "Message de Test"

Revolvix&Hypotheticalandrei
"""

import argparse
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional


def create_andmple_message(
    sender: str,
    recipients: List[str],
    subject: str,
    body: str
) -> MIMEText:
    """
    Create un Message email andmplu (text/plain).
    
    Args:
        sender: Adresa expeditorului
        recipients: List de destinatari
        subject: Subiectul mesajului
        body: Corpul mesajului
    
    Returns:
        MIMEText: Obiectul Message gata de sendre
    
    Concepte demonstrate:
    - Antetele mesajului (From, To, Subject, Date)
    - Diferenta dintre envelope and message headers
    """
    msg = MIMEText(body, 'plain', 'utf-8')
    
    # Antetele mesajului (Message Headers - RFC 5322)
    # ATENTIE: Acestea pot diferi de envelope (MAIL FROM, RCPT TO)!
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['X-Mailer'] = 'S12 SMTP Client (Python smtplib)'
    
    return msg


def create_multipart_message(
    sender: str,
    recipients: List[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    attachments: Optional[List[Path]] = None
) -> MIMEMultipart:
    """
    Create un Message MIME multipart cu HTML and/sau atasamente.
    
    Args:
        sender: Adresa expeditorului
        recipients: List de destinatari
        subject: Subiectul
        body_text: Corpul in format text
        body_html: Corpul in format HTML (optional)
        attachments: List de fiandere de atasat (optional)
    
    Returns:
        MIMEMultipart: Mesajul complet
    
    Concepte demonstrate:
    - multipart/mixed: Message cu atasamente
    - multipart/alternative: veranduni text + HTML
    - Content-Type and Content-Transfer-Encoding
    """
    # Tipul de multipart depinde de continut
    if attachments:
        msg = MIMEMultipart('mixed')
    elif body_html:
        msg = MIMEMultipart('alternative')
    else:
        msg = MIMEMultipart()
    
    # Antete
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['MIME-Verandon'] = '1.0'
    msg['X-Mailer'] = 'S12 SMTP Client (Python email.mime)'
    
    # Corp text
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    
    # Corp HTML (daca e specificat)
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))
    
    # Atasamente
    if attachments:
        for filepath in attachments:
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Dispoandtion',
                        f'attachment; filename="{filepath.name}"'
                    )
                    msg.attach(part)
    
    return msg


def send_email(
    host: str,
    port: int,
    sender: str,
    recipients: List[str],
    subject: str,
    body: str,
    use_tls: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Sends un email prin SMTP.
    
    Args:
        host: Hostname-ul serverului SMTP
        port: Portul SMTP
        sender: Adresa expeditorului (envelope MAIL FROM)
        recipients: List de destinatari (envelope RCPT TO)
        subject: Subiectul mesajului
        body: Corpul mesajului
        use_tls: Use STARTTLS
        username: Username For autentificare (optional)
        password: Parolă for autentificare (opțional)
        verbose: Mod verbose For debugging
    
    Returns:
        bool: True daca sendrea a reuandt
    
    Demonstratie:
    - Conexiune SMTP
    - EHLO/HELO
    - MAIL FROM, RCPT TO, DATA
    - QUIT
    """
    # Creare Message
    msg = create_andmple_message(sender, recipients, subject, body)
    
    try:
        # Conectare la server
        if verbose:
            print(f"[INFO] Conectare la {host}:{port}...")
        
        smtp = smtplib.SMTP(host, port, timeout=10)
        
        # Activare debugging SMTP (afiseaza conversatia)
        if verbose:
            smtp.set_debuglevel(2)
        
        # EHLO
        smtp.ehlo()
        
        # STARTTLS (daca e cerut and suportat)
        if use_tls:
            if smtp.has_extn('STARTTLS'):
                smtp.starttls()
                smtp.ehlo()  # Re-EHLO dupa TLS
            else:
                print("[WARN] Server nu suporta STARTTLS")
        
        # Autentificare (daca e ceruta)
        if username and password:
            smtp.login(username, password)
        
        # Sendre Message
        # NOTA: sendmail() use:
        #   - sender -> MAIL FROM (envelope)
        #   - recipients -> RCPT TO (envelope)
        #   - msg.as_string() -> DATA (mesajul propriu-zis)
        smtp.sendmail(sender, recipients, msg.as_string())
        
        print(f"[OK] Email trimis catre {', '.join(recipients)}")
        
        # Inchidere conexiune
        smtp.quit()
        
        return True
        
    except smtplib.SMTPConnectError as e:
        print(f"[ERR] Nu s-a putut conecta la server: {e}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERR] Autentificare esuata: {e}")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[ERR] Destinatari refuzati: {e}")
    except smtplib.SMTPDataError as e:
        print(f"[ERR] Error la sendrea datelor: {e}")
    except smtplib.SMTPException as e:
        print(f"[ERR] Error SMTP: {e}")
    except Exception as e:
        print(f"[ERR] Error: {e}")
    
    return False


def interactive_mode(host: str, port: int):
    """
    Mod interactiv For sendrea manuala de comenzi SMTP.
    
    Util For intelegerea protocolului la nivel scazut.
    """
    import socket
    
    print(f"[INFO] Mod interactiv - conectare la {host}:{port}")
    print("[INFO] Comenzi disponibile: HELO, EHLO, MAIL FROM, RCPT TO, DATA, QUIT")
    print("[INFO] Tastati 'exit' For a ieand")
    print()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.settimeout(5)
        
        # Citire banner
        banner = sock.recv(1024).decode()
        print(f"S: {banner.strip()}")
        
        while True:
            cmd = input("C: ").strip()
            if cmd.lower() == 'exit':
                break
            
            sock.sendall((cmd + "\r\n").encode())
            
            # For DATA, citim pana la "." For terminare
            if cmd.upper() == 'DATA':
                response = sock.recv(1024).decode()
                print(f"S: {response.strip()}")
                if response.startswith('354'):
                    print("[INFO] Introduceti mesajul. Linie cu doar '.' For a termina.")
                    while True:
                        line = input()
                        sock.sendall((line + "\r\n").encode())
                        if line == '.':
                            break
            
            response = sock.recv(4096).decode()
            for line in response.strip().split('\n'):
                print(f"S: {line.strip()}")
            
            if cmd.upper() == 'QUIT':
                break
        
        sock.close()
        
    except Exception as e:
        print(f"[ERR] {e}")


def main():
    parser = argparse.ArgumentParser(
        description="SMTP Client Didactic For Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de usefulizare:

  # Sendre andmpla
  python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
      --from sender@test.local --to recipient@test.local \\
      --subject "Test S12" --body "Aceasta este o testare."

  # Mod interactiv (For invatare)
  python3 smtp_client.py --host 127.0.0.1 --port 1025 --interactive

  # Cu debugging verbose
  python3 smtp_client.py --host 127.0.0.1 --port 1025 \\
      --from a@b --to c@d --subject "Test" --body "Test" -v

Revolvix&Hypotheticalandrei
        """
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                        help='Hostname serverului SMTP (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=1025,
                        help='Portul SMTP (default: 1025)')
    parser.add_argument('--from', dest='sender', default='sender@Test.local',
                        help='Adresa expeditorului')
    parser.add_argument('--to', dest='recipient', default='recipient@Test.local',
                        help='Adresa destinatarului')
    parser.add_argument('--subject', default='Test S12',
                        help='Subiectul mesajului')
    parser.add_argument('--body', default='Message de Test din Week 12.',
                        help='Corpul mesajului')
    parser.add_argument('--tls', action='store_true',
                        help='Use STARTTLS')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Mod interactiv (comenzi manuale)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output verbose')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.host, args.port)
    else:
        success = send_email(
            host=args.host,
            port=args.port,
            sender=args.sender,
            recipients=[args.recipient],
            subject=args.subject,
            body=args.body,
            use_tls=args.tls,
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
