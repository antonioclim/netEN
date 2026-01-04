#!/usr/bin/env python3
"""
EXERCISE 3: Suport POST For Server HTTP
=============================================
Subject: Computer Networks, Week 8
Level: Advanced
estimated time: 25 minutes

OBJECTIVES:
- Extension serverului For metoda POST
- parsing body-ului din cereri HTTP
- Procesarea form data (application/x-www-form-urlencoded)
- Returna responseurilor JSON

INSTRUCTIONS:
1. Complete the functions marked with TODO
2. Run the tests: python3 -m pytest tests/test_ex03.py -v
3. Test manually:
   curl -X POST -d "name=John&age=25" http://localhost:8081/api/form
   curl -X POST -H "Content-Type: application/json" -d '{"name":"John"}' http://localhost:8081/api/json

EVALUATION:
- Parsare Content-Length: 25%
- Citire body complete: 25%
- Parsare form data: 25%
- Raspuns JSON: 25%

© Revolvix&Hypotheticalandrei
"""

import socket
import json
import argparse
from urllib.parse import parse_qs, unquote_plus
from typing import Dict, Tuple, Any, Optional

# ============================================================================
# CONSTANTS
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"
MAX_BODY_SIZE = 1024 * 1024  # 1 MB


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def read_request_with_body(client_socket: socket.socket) -> Tuple[str, bytes]:
    """
    Read un request HTTP complete, inclusiv body-ul.
    
    Args:
        client_socket: Socket-ul clientului
    
    Returns:
        Tuple with (headers_string, body_bytes)
    
    ALGORITM:
    1. Read pana gasesti \\r\\n\\r\\n (end of headers)
    2. Parseaza Content-Length din headers
    3. If exists Content-Length, read exact that many bytes For body
    4. Returns headers and body separat
    
    EDGE CASES:
    - Request fara body (GET, HEAD) → body = b""
    - Content-Length lipsa dar metoda POST → error or body = b""
    - Body mai mare decat MAX_BODY_SIZE → truncare or error
    
    HINT:
    - Cititi in bucle pana gasiti DOUBLE_CRLF
    - Aveti grija ca buffer-ul poate contine and partea de inceput a body-ului
    - use socket.recv() cu dimensiune mica For headers
    """
    
    # TODO: Implement citirea request cu body
    #
    # steps sugerati:
    # 1. Initializati buffer gol
    # 2. Cititi in bucle pana gasiti DOUBLE_CRLF
    # 3. Separati headers de ce a mai ramas
    # 4. Parsati Content-Length din headers
    # 5. Calculati cati bytes de body mai trebuie cititi
    # 6. Cititi restul body-ului
    # 7. Returnati (headers_str, body_bytes)
    
    raise NotImplementedError("TODO: Implement read_request_with_body")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def parse_form_data(body: bytes, content_type: str) -> Dict[str, str]:
    """
    Parseaza body-ul din format application/x-www-form-urlencoded.
    
    Args:
        body: Body-ul cererii in bytes
        content_type: Valoarea header-ului Content-Type
    
    Returns:
        Dictionary with extracted parameters
    
    FORMAT INPUT:
        name=John+Doe&age=25&city=New%20York
    
    FORMAT OUTPUT:
        {"name": "John Doe", "age": "25", "city": "New York"}
    
    DECODIFICARE:
    - + → spatiu
    - %XX → caracter cu cod hex XX
    
    HINT:
    - Verificati ca Content-Type incepe cu "application/x-www-form-urlencoded"
    - use urllib.parse.parse_qs() or Implement manual
    - parse_qs returneaza liste, luati primul element
    - Tratati caracterele speciale cu unquote_plus()
    """
    
    # TODO: Implement parsing form data
    #
    # steps sugerati:
    # 1. Verificati content_type
    # 2. Decodifica body din bytes in string
    # 3. Parsati perechi key=value separate de &
    # 4. Decodificati fiecare key and value (URL decoding)
    # 5. Construiti and returnati dictionarul
    
    raise NotImplementedError("TODO: Implement parse_form_data")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def parse_json_body(body: bytes, content_type: str) -> Optional[Dict[str, Any]]:
    """
    Parseaza body-ul din format JSON.
    
    Args:
        body: Body-ul cererii in bytes
        content_type: Valoarea header-ului Content-Type
    
    Returns:
        Dictionar parsat or None if parsing esueaza
    
    HINT:
    - Verificati ca Content-Type contine "application/json"
    - use json.loads()
    - Tratati json.JSONDecodeError
    """
    
    # TODO: Implement parsing JSON
    #
    # steps sugerati:
    # 1. Verificati content_type
    # 2. Decodificati body in string (utf-8)
    # 3. Parsati cu json.loads()
    # 4. Tratati exceptiile and returnati None to error
    
    raise NotImplementedError("TODO: Implement parse_json_body")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def build_json_response(status_code: int, data: Dict[str, Any]) -> bytes:
    """
    Build un response HTTP cu body JSON.
    
    Args:
        status_code: Codul de status HTTP
        data: Dictionarul de serializat ca JSON
    
    Returns:
        Raspunsul HTTP complete in bytes
    
    EXEMPLU OUTPUT:
        HTTP/1.1 200 OK\r\n
        Content-Type: application/json\r\n
        Content-Length: 42\r\n
        \r\n
        {"success": true, "data": {"name": "John"}}
    
    HINT:
    - Serializati data cu json.dumps()
    - Setati Content-Type: application/json
    - Calculati Content-Length corect
    """
    
    # TODO: Implement building response JSON
    #
    # steps sugerati:
    # 1. Serializati data cu json.dumps()
    # 2. Codificati body-ul in bytes (utf-8)
    # 3. Construiti headers (Content-Type, Content-Length)
    # 4. Construiti status line
    # 5. Asamblati responseul complete
    
    raise NotImplementedError("TODO: Implement build_json_response")


# ============================================================================
# TODO: IMPLEMENT THIS FUNCTION
# ============================================================================

def handle_post_request(path: str, headers: Dict[str, str], body: bytes) -> bytes:
    """
    Proceseaza o request POST and returneaza responseul.
    
    Args:
        path: path ceruta (ex: "/api/form")
        headers: Dictionary with headers
        body: Body-ul cererii
    
    Returns:
        Raspunsul HTTP in bytes
    
    RUTE SUPORTATE:
    - /api/form: Parseaza form data and returneaza JSON cu datele primite
    - /api/json: Parseaza JSON and returneaza JSON cu datele primite (echo)
    - /api/echo: Returns body-ul primit ca text
    - Altele: 404 Not Found
    
    RASPUNS FORMAT:
        {
            "success": true/false,
            "path": "/api/form",
            "method": "POST",
            "data": { ... parsed data ... }
        }
    """
    
    # TODO: Implement handler POST
    #
    # steps sugerati:
    # 1. Determinati ruta din path
    # 2. For /api/form: parsati cu parse_form_data()
    # 3. For /api/json: parsati cu parse_json_body()
    # 4. For /api/echo: returnati body-ul direct
    # 5. Construiti responseul JSON cu datele procesate
    # 6. Tratati erorile (404, 400 For parsare esuata)
    
    raise NotImplementedError("TODO: Implement handle_post_request")


# ============================================================================
# COD FURNIZAT - SERVER PRINCIPAL
# ============================================================================

def parse_request_line(first_line: str) -> Tuple[str, str, str]:
    """Parseaza request line."""
    parts = first_line.split(" ", 2)
    if len(parts) != 3:
        raise ValueError("Invalid request line")
    return parts[0], parts[1], parts[2]


def parse_headers(header_lines: list) -> Dict[str, str]:
    """Parseaza headers in dictionar."""
    headers = {}
    for line in header_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def run_server(host: str, port: int):
    """starts serverul."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[INFO] Server POST pornit pe http://{host}:{port}/")
        print("[INFO] Rute availablee: /api/form, /api/json, /api/echo")
        print("[INFO] Press Ctrl+C For oprire")
        
        while True:
            client, addr = server.accept()
            print(f"[CONN] {addr[0]}:{addr[1]}")
            
            try:
                headers_str, body = read_request_with_body(client)
                lines = headers_str.split(CRLF)
                method, path, version = parse_request_line(lines[0])
                headers = parse_headers(lines[1:])
                
                print(f"[REQ] {method} {path} ({len(body)} bytes body)")
                
                if method == "POST":
                    response = handle_post_request(path, headers, body)
                elif method == "GET":
                    response = build_json_response(200, {
                        "message": "Use POST method for this API",
                        "endpoints": ["/api/form", "/api/json", "/api/echo"]
                    })
                else:
                    response = build_json_response(405, {"error": "Method not allowed"})
                
                client.sendall(response)
                
            except Exception as e:
                print(f"[ERROR] {e}")
                error_resp = build_json_response(500, {"error": str(e)})
                client.sendall(error_resp)
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server oprit")
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP cu suport POST")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
