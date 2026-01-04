#!/usr/bin/env python3
"""
Exercitiul 4.01: Implementare Protocol TCP Custom
==================================================

Obiectiv: Implementati a protocol TEXT modificat care suporta commands multiple.

Specificatii protocol:
- Format: "<COMMAND> <LENGTH> <PAYLOAD>"
- COMMAND: ECHO, UPPER, LOWER, REVERSE, COUNT
- LENGTH: payload length-ului in bytes
- PAYLOAD: datele text

Exemple:
- "ECHO 5 hello"  -> server raspunof "hello"
- "UPPER 5 hello" -> server raspunof "HELLO"
- "LOWER 5 HELLO" -> server raspunof "hello"
- "REVERSE 5 hello" -> server raspunof "olleh"
- "COUNT 5 hello" -> server raspunof "5" (numar caractere)

TODO-uri of implementat:
1. parse_command() - parseaza comanda din mesaj
2. execute_command() - executa comanda and returns rezultat
3. handle_client() - gestioneaza comunicarea with clientul
4. Server principal with threading

Autor: Revolvix&Hypotheticalandrei
Week 4 - Exercitiu practic TCP
"""

import socket
import threading
import sys

# Constante protocol
VALID_COMMANDS = {'ECHO', 'UPPER', 'LOWER', 'REVERSE', 'COUNT'}
DEFAULT_PORT = 3334
BUFFER_SIZE = 4096


def parse_command(data: str) -> tuple:
    """
    Parseaza mesajul primit and extrage comanda, lungimea and payload-ul.
    
    Args:
        data: String in format "<COMMAND> <LENGTH> <PAYLOAD>"
    
    Returns:
        tuple: (command, length, payload) or (None, None, None) daca invalid
    
    Exemple:
        >>> parse_command("ECHO 5 hello")
        ('ECHO', 5, 'hello')
        >>> parse_command("UPPER 11 hello world")
        ('UPPER', 11, 'hello world')
        >>> parse_command("INVALID")
        (None, None, None)
    
    TODO: Implementati aceasta function
    Hints:
    - Folositi split(' ', 2) for a separa in maxim 3 parti
    - Validati ca prima parte este in VALID_COMMANDS
    - Convertiti a doua parte to int
    - Verificati ca payload length-ului corespunof with valoarea declarata
    """
    # TODO: Implementare
    # Pasul 1: Separati string-ul in parti
    # parts = data.split(' ', 2)
    
    # Pasul 2: Validati number of of parti
    # if len(parts) < 3:
    #     return (None, None, None)
    
    # Pasul 3: Extrageti and validati comanda
    # command = parts[0].upper()
    # if command not in VALID_COMMANDS:
    #     return (None, None, None)
    
    # Pasul 4: Extrageti and validati lungimea
    # try:
    #     length = int(parts[1])
    # except ValueError:
    #     return (None, None, None)
    
    # Pasul 5: Extrageti payload-ul
    # payload = parts[2]
    
    # Pasul 6: Verificati consistenta lungimii
    # if len(payload.encode('utf-8')) != length:
    #     return (None, None, None)
    
    # return (command, length, payload)
    
    pass  # Inlocuiti with implementarea


def execute_command(command: str, payload: str) -> str:
    """
    Executa comanda specificata pe payload.
    
    Args:
        command: Una din VALID_COMMANDS
        payload: Datele pe care se aplica comanda
    
    Returns:
        str: Rezultatul executiei comenzii
    
    Exemple:
        >>> execute_command('ECHO', 'hello')
        'hello'
        >>> execute_command('UPPER', 'hello')
        'HELLO'
        >>> execute_command('REVERSE', 'hello')
        'olleh'
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # if command == 'ECHO':
    #     return payload
    # elif command == 'UPPER':
    #     return payload.upper()
    # elif command == 'LOWER':
    #     return payload.lower()
    # elif command == 'REVERSE':
    #     return payload[::-1]
    # elif command == 'COUNT':
    #     return str(len(payload))
    # else:
    #     return 'ERROR: Unknown command'
    
    pass  # Inlocuiti with implementarea


def format_response(result: str) -> str:
    """
    Format raspunsul for client.
    
    Format: "<LENGTH> <RESULT>"
    
    Args:
        result: Rezultatul of trimis
    
    Returns:
        str: Raspunsul formatat
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # length = len(result.encode('utf-8'))
    # return f"{length} {result}"
    
    pass  # Inlocuiti with implementarea


def handle_client(client_socket: socket.socket, address: tuple):
    """
    Handle comunicarea with a client.
    
    Args:
        client_socket: Socket-ul clientului
        address: Tuple (ip, port) al clientului
    
    TODO: Implementati aceasta function
    Hints:
    - Folositi un loop while for a procesa multiple mesaje
    - Apelati parse_command(), execute_command(), format_response()
    - Gestionati exceptiile (ConnectionResetError, etc.)
    - Inchideti socket-ul to final
    """
    print(f"[+] Client conectat: {address}")
    
    # TODO: Implementare
    # try:
    #     while True:
    #         # Primire date
    #         data = client_socket.recv(BUFFER_SIZE)
    #         if not data:
    #             break
    #         
    #         message = data.decode('utf-8').strip()
    #         print(f"[{address}] Primit: {message}")
    #         
    #         # Parsare comanda
    #         command, length, payload = parse_command(message)
    #         
    #         if command is None:
    #             response = format_response("ERROR: Invalid command format")
    #         else:
    #             result = execute_command(command, payload)
    #             response = format_response(result)
    #         
    #         # Sendre response
    #         client_socket.sendall(response.encode('utf-8'))
    #         print(f"[{address}] Trimis: {response}")
    #         
    # except ConnectionResetError:
    #     print(f"[-] Conexiune resetata: {address}")
    # except Exception as e:
    #     print(f"[!] Eroare: {e}")
    # finally:
    #     client_socket.close()
    #     print(f"[-] Client deconectat: {address}")
    
    pass  # Inlocuiti with implementarea


def start_server(host: str = '0.0.0.0', port: int = DEFAULT_PORT):
    """
    Porneste serverul TCP multi-threaded.
    
    Args:
        host: Adresa of ascultare
        port: Portul of ascultare
    
    TODO: Implementati aceasta function
    """
    # TODO: Implementare
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 
    # try:
    #     server_socket.bind((host, port))
    #     server_socket.listen(5)
    #     print(f"[*] Server pornit pe {host}:{port}")
    #     print(f"[*] Comenzi acceptate: {', '.join(VALID_COMMANDS)}")
    #     
    #     while True:
    #         client_socket, address = server_socket.accept()
    #         client_thread = threading.Thread(
    #             target=handle_client,
    #             args=(client_socket, address),
    #             daemon=True
    #         )
    #         client_thread.start()
    #         
    # except KeyboardInterrupt:
    #     print("\n[*] Server oprit")
    # finally:
    #     server_socket.close()
    
    pass  # Inlocuiti with implementarea


# =============================================================================
# CLIENT DE TEST (nu trebuie modificat)
# =============================================================================

def test_client(host: str = 'localhost', port: int = DEFAULT_PORT):
    """
    Client of test for verificarea implementarii.
    """
    test_cases = [
        ("ECHO 5 hello", "5 hello"),
        ("UPPER 5 hello", "5 HELLO"),
        ("LOWER 5 HELLO", "5 hello"),
        ("REVERSE 5 hello", "5 olleh"),
        ("COUNT 5 hello", "1 5"),
        ("UPPER 11 hello world", "11 HELLO WORLD"),
    ]
    
    print(f"\n{'='*60}")
    print("TEST CLIENT - Verificare implementare")
    print(f"{'='*60}\n")
    
    passed = 0
    failed = 0
    
    for test_input, expected in test_cases:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            sock.sendall(test_input.encode('utf-8'))
            response = sock.recv(BUFFER_SIZE).decode('utf-8').strip()
            
            sock.close()
            
            if response == expected:
                print(f"✓ PASS: {test_input}")
                print(f"        Raspuns: {response}")
                passed += 1
            else:
                print(f"✗ FAIL: {test_input}")
                print(f"        Asteptat: {expected}")
                print(f"        Primit:   {response}")
                failed += 1
                
        except Exception as e:
            print(f"✗ ERROR: {test_input}")
            print(f"         {e}")
            failed += 1
        
        print()
    
    print(f"{'='*60}")
    print(f"Rezultat: {passed}/{passed+failed} teste trecute")
    print(f"{'='*60}")
    
    return failed == 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mod test client
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
        success = test_client(host, port)
        sys.exit(0 if success else 1)
    else:
        # Mod server
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
        start_server(port=port)
