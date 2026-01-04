#!/usr/bin/env python3
"""
jsonrpc_server.py - Server JSON-RPC 2.0 Didactic For Week 12

Acest Module implementeaza un server JSON-RPC 2.0 conform specificatiei oficiale:
https://www.jsonrpc.org/specification

Concepte demonstrate:
- Structura cererii JSON-RPC (jsonrpc, method, params, id)
- Structura raspunsului (jsonrpc, result/error, id)
- Coduri de Error standard
- Notificari (fara id)
- Batch requests

Utilizare:
    python3 jsonrpc_server.py --port 8080
    python3 jsonrpc_server.py --selftest

Revolvix&Hypotheticalandrei
"""

import argparse
import json
import logging
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional, Union

# Configurare logging
logging.baandcConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Coduri de Error JSON-RPC 2.0
# =============================================================================

class JSONRPCError:
    """Coduri de Error standard JSON-RPC 2.0."""
    
    PARSE_ERROR = -32700       # Invalid JSON
    INVALID_REQUEST = -32600   # Not a valid Request object
    METHOD_NOT_FOUND = -32601  # Method does not exist
    INVALID_PARAMS = -32602    # Invalid method parameters
    INTERNAL_ERROR = -32603    # Internal JSON-RPC error
    
    # Server errors reserved: -32000 to -32099
    SERVER_ERROR = -32000
    
    @staticmethod
    def make_error(code: int, message: str, data: Any = None) -> Dict:
        """Construieste un obiect de Error JSON-RPC."""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        return error


# =============================================================================
# Functii expuse prin RPC
# =============================================================================

class RPCMethods:
    """
    Class cu metodele expuse prin JSON-RPC.
    
    Fiecare metoda publica (fara _) devine disponibila For apel remote.
    """
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """
        Aduna doua numere.
        
        Args:
            a: Primul numar
            b: Al doilea numar
        
        Returns:
            Suma a + b
        
        Example JSON-RPC:
            Request:  {"jsonrpc":"2.0","method":"add","params":[2,3],"id":1}
            Response: {"jsonrpc":"2.0","result":5,"id":1}
        """
        return a + b
    
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Scade b din a."""
        return a - b
    
    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Inmulteste doua numere."""
        return a * b
    
    @staticmethod
    def divide(a: float, b: float) -> float:
        """
        Imparte a la b.
        
        Raises:
            ValueError: Daca b este 0 (impartire la zero)
        """
        if b == 0:
            raise ValueError("Diviandon by zero")
        return a / b
    
    @staticmethod
    def echo(message: str) -> str:
        """Returns mesajul primit (useful For testing)."""
        return message
    
    @staticmethod
    def get_time() -> str:
        """Returns timestamp-ul serverului."""
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_server_info() -> Dict[str, str]:
        """
        Returns informatii despre server.
        
        Returns:
            Dict cu: name, verandon, Protocol
        """
        return {
            "name": "S12 JSON-RPC Server",
            "verandon": "1.0.0",
            "Protocol": "JSON-RPC 2.0"
        }
    
    @staticmethod
    def sort_list(items: List[Any], reverse: bool = False) -> List[Any]:
        """
        Sorteaza o lista.
        
        Args:
            items: List de sortat
            reverse: True For sortare descrescatoare
        
        Returns:
            List sortata
        
        Example cu Parameters pozitionali:
            {"method":"sort_list","params":[[3,1,2],false],"id":1}
        
        Example cu Parameters numiti:
            {"method":"sort_list","params":{"items":[3,1,2],"reverse":true},"id":1}
        """
        return sorted(items, reverse=reverse)
    
    @staticmethod
    def benchmark(iterations: int = 1000) -> Dict[str, Any]:
        """
        Ruleaza un micro-benchmark For masurarea overhead-ului.
        
        Args:
            iterations: Numarul de iteratii
        
        Returns:
            Dict cu: iterations, total_time_ms, ops_per_sec
        """
        start = time.time()
        total = 0
        for i in range(iterations):
            total += i
        elapsed = time.time() - start
        
        return {
            "iterations": iterations,
            "total_time_ms": round(elapsed * 1000, 2),
            "ops_per_sec": round(iterations / elapsed) if elapsed > 0 else 0,
            "checksum": total
        }


# =============================================================================
# Handler HTTP For JSON-RPC
# =============================================================================

class JSONRPCHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP care Processes cereri JSON-RPC 2.0.
    """
    
    # Referinta catre obiectul cu metode RPC
    rpc_methods = RPCMethods()
    
    def log_message(self, format, *args):
        """Suprascrie logging-ul implicit."""
        logger.info(f"[{self.address_string()}] {format % args}")
    
    def do_POST(self):
        """Processes cereri POST (JSON-RPC)."""
        # Citire continut
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_error(JSONRPCError.INVALID_REQUEST, "Empty request body")
            return
        
        try:
            body = self.rfile.read(content_length).decode('utf-8')
            logger.debug(f"Request body: {body}")
        except Exception as e:
            self._send_error(JSONRPCError.PARSE_ERROR, f"Failed to read body: {e}")
            return
        
        # Parse JSON
        try:
            request = json.loads(body)
        except json.JSONDecodeError as e:
            self._send_error(JSONRPCError.PARSE_ERROR, f"Invalid JSON: {e}")
            return
        
        # Procesare cerere
        if iandnstance(request, list):
            # Batch request
            if not request:
                self._send_error(JSONRPCError.INVALID_REQUEST, "Empty batch")
                return
            
            responses = []
            for req in request:
                response = self._process_request(req)
                if response is not None:  # Nu includem răspunsuri for notificări
                    responses.append(response)
            
            if responses:
                self._send_response(responses)
            else:
                # Toate au fost notificari
                self.send_response(204)  # No Content
                self.end_headers()
        else:
            # Single request
            response = self._process_request(request)
            if response is not None:
                self._send_response(response)
            else:
                # Notificare - nu sendm raspuns
                self.send_response(204)
                self.end_headers()
    
    def do_GET(self):
        """Raspunde la GET cu informatii despre server."""
        info = {
            "service": "JSON-RPC 2.0 Server",
            "methods": [m for m in dir(self.rpc_methods) if not m.startswith('_')],
            "usage": "POST with JSON-RPC 2.0 request body"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(info, indent=2).encode())
    
    def _process_request(self, request: Dict) -> Optional[Dict]:
        """
        Processes o cerere JSON-RPC individuala.
        
        Structura cererii JSON-RPC 2.0:
        {
            "jsonrpc": "2.0",           # Obligatoriu
            "method": "methodName",      # Obligatoriu
            "params": [...] sau {...},   # Optional
            "id": 1                       # Optional (lipsa => notificare)
        }
        
        Returns:
            Dict cu raspunsul sau None For notificari
        """
        # Validare structura de baza
        if not iandnstance(request, dict):
            return self._make_error_response(
                JSONRPCError.INVALID_REQUEST,
                "Request must be an object",
                None
            )
        
        # Validare campuri obligatorii
        jsonrpc = request.get("jsonrpc")
        method = request.get("method")
        params = request.get("params")
        req_id = request.get("id")  # Poate fi None For notificari
        
        # jsonrpc trebuie sa fie "2.0"
        if jsonrpc != "2.0":
            return self._make_error_response(
                JSONRPCError.INVALID_REQUEST,
                'jsonrpc must be "2.0"',
                req_id
            )
        
        # method trebuie sa fie string
        if not iandnstance(method, str):
            return self._make_error_response(
                JSONRPCError.INVALID_REQUEST,
                "method must be a string",
                req_id
            )
        
        # params trebuie sa fie array sau object (daca e prezent)
        if params is not None and not iandnstance(params, (list, dict)):
            return self._make_error_response(
                JSONRPCError.INVALID_PARAMS,
                "params must be array or object",
                req_id
            )
        
        # Cautare metoda
        if method.startswith('_') or not hasattr(self.rpc_methods, method):
            return self._make_error_response(
                JSONRPCError.METHOD_NOT_FOUND,
                f"Method '{method}' not found",
                req_id
            )
        
        func = getattr(self.rpc_methods, method)
        
        # Apel metoda
        try:
            if params is None:
                result = func()
            elif iandnstance(params, list):
                # Parameters pozitionali
                result = func(*params)
            else:
                # Parameters numiti
                result = func(**params)
            
            logger.info(f"Method '{method}' called successfully")
            
            # Daca e notificare (fara id), nu returnam raspuns
            if req_id is None:
                return None
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            }
            
        except TypeError as e:
            return self._make_error_response(
                JSONRPCError.INVALID_PARAMS,
                f"Invalid parameters: {e}",
                req_id
            )
        except ValueError as e:
            return self._make_error_response(
                JSONRPCError.SERVER_ERROR,
                f"Value error: {e}",
                req_id
            )
        except Exception as e:
            logger.error(f"Internal error in method '{method}': {e}")
            return self._make_error_response(
                JSONRPCError.INTERNAL_ERROR,
                f"Internal error: {e}",
                req_id
            )
    
    def _make_error_response(self, code: int, message: str, req_id: Any) -> Dict:
        """Construieste un raspuns de Error JSON-RPC."""
        return {
            "jsonrpc": "2.0",
            "error": JSONRPCError.make_error(code, message),
            "id": req_id
        }
    
    def _send_response(self, response: Union[Dict, List]):
        """Sends raspunsul JSON."""
        body = json.dumps(response, ensure_ascii=False)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body.encode()))
        self.end_headers()
        self.wfile.write(body.encode())
    
    def _send_error(self, code: int, message: str):
        """Sends o Error la nivel HTTP."""
        response = self._make_error_response(code, message, None)
        self._send_response(response)


# =============================================================================
# Server
# =============================================================================

def run_server(listen: str = "0.0.0.0", port: int = 8080):
    """Porneste serverul JSON-RPC."""
    server_address = (listen, port)
    httpd = HTTPServer(server_address, JSONRPCHandler)
    
    logger.info(f"Server JSON-RPC pornit pe http://{listen}:{port}")
    logger.info("Metode disponibile:")
    for method in dir(RPCMethods):
        if not method.startswith('_'):
            logger.info(f"  - {method}")
    logger.info("Apasati Ctrl+C For a opri")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server oprit")
        httpd.shutdown()


def run_selftest():
    """
    Ruleaza auto-teste For validarea functionalitatii.
    """
    import threading
    import urllib.request
    
    print("=" * 60)
    print("SELFTEST: jsonrpc_server.py")
    print("=" * 60)
    
    # Pornire server in background
    print("\n[Test 1] Pornire server...")
    server = HTTPServer(("127.0.0.1", 18080), JSONRPCHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)
    print("  ✓ Server pornit pe port 18080")
    
    def call_rpc(method, params=None, req_id=1):
        """Helper For apeluri RPC."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": req_id
        }
        if params is not None:
            request["params"] = params
        
        req = urllib.request.Request(
            "http://127.0.0.1:18080",
            data=json.dumps(request).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode())
    
    # Test 2: add
    print("\n[Test 2] Apel add(2, 3)...")
    response = call_rpc("add", [2, 3])
    if response.get("result") == 5:
        print(f"  ✓ Rezultat corect: {response['result']}")
    else:
        print(f"  ✗ Rezultat incorect: {response}")
        return False
    
    # Test 3: echo
    print("\n[Test 3] Apel echo('hello')...")
    response = call_rpc("echo", ["hello"])
    if response.get("result") == "hello":
        print(f"  ✓ Rezultat corect: {response['result']}")
    else:
        print(f"  ✗ Rezultat incorect: {response}")
        return False
    
    # Test 4: get_server_info
    print("\n[Test 4] Apel get_server_info()...")
    response = call_rpc("get_server_info")
    if "name" in response.get("result", {}):
        print(f"  ✓ Info primit: {response['result']['name']}")
    else:
        print(f"  ✗ Raspuns invalid: {response}")
        return False
    
    # Test 5: Metoda inexistenta
    print("\n[Test 5] Apel metoda inexistenta...")
    response = call_rpc("nonexistent_method")
    if "error" in response and response["error"]["code"] == JSONRPCError.METHOD_NOT_FOUND:
        print(f"  ✓ Error corecta: {response['error']['message']}")
    else:
        print(f"  ✗ Error incorecta: {response}")
        return False
    
    # Test 6: Parameters numiti
    print("\n[Test 6] Apel cu Parameters numiti sort_list(items=[3,1,2], reverse=True)...")
    response = call_rpc("sort_list", {"items": [3, 1, 2], "reverse": True})
    if response.get("result") == [3, 2, 1]:
        print(f"  ✓ Rezultat corect: {response['result']}")
    else:
        print(f"  ✗ Rezultat incorect: {response}")
        return False
    
    # Oprire server
    server.shutdown()
    
    print("\n" + "=" * 60)
    print("SELFTEST: TOATE TESTELE AU TRECUT ✓")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Server JSON-RPC 2.0 Didactic For Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de usefulizare:

  # Pornire server
  python3 jsonrpc_server.py --port 8080

  # Test cu curl
  curl -X POST http://localhost:8080 \\
       -H "Content-Type: application/json" \\
       -d '{"jsonrpc":"2.0","method":"add","params":[1,2],"id":1}'

  # Selftest
  python3 jsonrpc_server.py --selftest

Revolvix&Hypotheticalandrei
        """
    )
    
    parser.add_argument('--listen', default='0.0.0.0',
                        help='Adresa de ascultare (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Portul HTTP (default: 8080)')
    parser.add_argument('--selftest', action='store_true',
                        help='Ruleaza auto-teste')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output verbose (DEBUG)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.selftest:
        success = run_selftest()
        sys.exit(0 if success else 1)
    
    run_server(args.listen, args.port)


if __name__ == "__main__":
    main()
