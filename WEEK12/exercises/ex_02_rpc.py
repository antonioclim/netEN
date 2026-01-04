#!/usr/bin/env python3
"""
ex_02_rpc.py - Self-contained RPC exercises for Week 12

This file demonstrates core RPC concepts without external dependencies:
- JSON-RPC 2.0 (server and client)
- XML-RPC (Python standard library)
- A simple comparison of overhead and latency

What you will learn:
- Remote Procedure Call compared to REST at a high level
- JSON-RPC 2.0 message structure
- Marshalling and unmarshalling (serialisation)
- Basic error handling patterns in RPC

Why it matters:
- Many modern distributed systems rely on RPC style interfaces, including gRPC
- JSON-RPC appears in tooling ecosystems such as language servers and some blockchain clients
- Understanding RPC helps with debugging and reasoning about service boundaries
"""

import argparse
import json
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import urllib.request


# =============================================================================
# CONCEPTE TEORETICE
# =============================================================================
"""
RPC - Remote Procedure Call

IDEEA FUNDAMENTALA:
    Apelarea unei functii pe un server remote ca si cum ar fi locala.
    
    Local:  result = add(2, 3)
    Remote: result = server.call("add", [2, 3])

COMPONENTE:
    Client Stub: Serializeaza parametrii, Sends cererea
    Server Stub: Deserializeaza, apeleaza functia reala, returneaza rezultatul

MODELE RPC:
    1. JSON-RPC 2.0
       - Payload JSON (human-readable)
       - Protocol simplu, specificatie clara
       - Folosit in: Ethereum, LSP, Bitcoin
    
    2. XML-RPC
       - Precursorul SOAP
       - Payload XML (verbose)
       - Suport nativ in Python (xmlrpc.server, xmlrpc.client)
    
    3. gRPC
       - Protocol Buffers (binary)
       - HTTP/2 with streaming
       - Performanta ridicata

JSON-RPC 2.0 STRUCTURA:
    Request:
    {
        "jsonrpc": "2.0",
        "method": "methodName",
        "params": [arg1, arg2] sau {"name": value},
        "id": 1
    }
    
    Response (succes):
    {
        "jsonrpc": "2.0",
        "result": value,
        "id": 1
    }
    
    Response (Error):
    {
        "jsonrpc": "2.0",
        "error": {"code": -32600, "message": "Invalid Request"},
        "id": 1
    }

CODURI Error STANDARD:
    -32700  Parse error
    -32600  Invalid Request
    -32601  Method not found
    -32602  Invalid params
    -32603  Internal error
"""


# =============================================================================
# FUNCTII RPC PARTAJATE
# =============================================================================

class RPCFunctions:
    """Functii expuse prin RPC."""
    
    @staticmethod
    def add(a, b):
        """Aduna doua numere."""
        return a + b
    
    @staticmethod
    def subtract(a, b):
        """Scade b din a."""
        return a - b
    
    @staticmethod
    def multiply(a, b):
        """Inmulteste doua numere."""
        return a * b
    
    @staticmethod
    def divide(a, b):
        """Imparte a at b."""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    @staticmethod
    def echo(message):
        """Returneaza mesajul primit."""
        return message
    
    @staticmethod
    def get_time():
        """Returneaza timestamp-ul serverului."""
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def sort_list(items, reverse=False):
        """Sorteaza o lista."""
        return sorted(items, reverse=reverse)
    
    @staticmethod
    def benchmark(iterations=1000):
        """Micro-benchmark For masurarea overhead-ului."""
        start = time.time()
        total = sum(range(iterations))
        elapsed = time.time() - start
        return {
            "iterations": iterations,
            "time_ms": round(elapsed * 1000, 2),
            "checksum": total
        }


# =============================================================================
# JSON-RPC SERVER
# =============================================================================

class JSONRPCHandler(BaseHTTPRequestHandler):
    """Handler HTTP For JSON-RPC 2.0."""
    
    rpc = RPCFunctions()
    
    def log_message(self, format, *args):
        print(f"[JSON-RPC] {format % args}")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_error(-32700, "Parse error", None)
            return
        
        response = self._process(request)
        self._send_response(response)
    
    def do_GET(self):
        """Info despre server."""
        methods = [m for m in dir(self.rpc) if not m.startswith('_')]
        info = {"service": "JSON-RPC 2.0", "methods": methods}
        self._send_response(info)
    
    def _process(self, req):
        if not isinstance(req, dict):
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}
        
        method = req.get("method")
        params = req.get("params")
        req_id = req.get("id")
        
        if not method or not hasattr(self.rpc, method) or method.startswith('_'):
            return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method not found: {method}"}, "id": req_id}
        
        try:
            func = getattr(self.rpc, method)
            if params is None:
                result = func()
            elif isinstance(params, list):
                result = func(*params)
            else:
                result = func(**params)
            
            return {"jsonrpc": "2.0", "result": result, "id": req_id}
        
        except TypeError as e:
            return {"jsonrpc": "2.0", "error": {"code": -32602, "message": str(e)}, "id": req_id}
        except Exception as e:
            return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": req_id}
    
    def _send_error(self, code, message, req_id):
        response = {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": req_id}
        self._send_response(response)
    
    def _send_response(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


def run_jsonrpc_server(port: int = 8080):
    """Porneste serverul JSON-RPC."""
    server = HTTPServer(('0.0.0.0', port), JSONRPCHandler)
    print(f"[JSON-RPC] Server pornit pe http://0.0.0.0:{port}")
    print("[JSON-RPC] Apasati Ctrl+C For a opri\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[JSON-RPC] Server oprit")
        server.shutdown()


# =============================================================================
# JSON-RPC CLIENT
# =============================================================================

class JSONRPCClient:
    """Client JSON-RPC simplu."""
    
    def __init__(self, url: str):
        self.url = url
        self._id = 0
    
    def call(self, method: str, params=None):
        self._id += 1
        request = {"jsonrpc": "2.0", "method": method, "id": self._id}
        if params is not None:
            request["params"] = params
        
        req = urllib.request.Request(
            self.url,
            data=json.dumps(request).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            response = json.loads(resp.read().decode())
        
        if "error" in response:
            raise Exception(f"RPC Error {response['error']['code']}: {response['error']['message']}")
        
        return response.get("result")


def run_jsonrpc_client(host: str, port: int):
    """Ruleaza demonstratie client JSON-RPC."""
    url = f"http://{host}:{port}"
    client = JSONRPCClient(url)
    
    print("="*60)
    print(f"JSON-RPC Client Demo - {url}")
    print("="*60)
    
    tests = [
        ("add", [2, 3], "2 + 3"),
        ("subtract", [10, 4], "10 - 4"),
        ("multiply", [7, 8], "7 * 8"),
        ("echo", ["Hello RPC!"], "echo"),
        ("get_time", None, "server time"),
        ("sort_list", [[5, 2, 8, 1, 9]], "sort [5,2,8,1,9]"),
    ]
    
    for method, params, desc in tests:
        try:
            result = client.call(method, params)
            print(f"  {desc}: {result}")
        except Exception as e:
            print(f"  {desc}: ERROR - {e}")
    
    print("\n" + "="*60)


# =============================================================================
# XML-RPC SERVER
# =============================================================================

def run_xmlrpc_server(port: int = 8000):
    """Porneste serverul XML-RPC."""
    server = SimpleXMLRPCServer(('0.0.0.0', port), logRequests=True)
    
    # Inregistrare functii
    rpc = RPCFunctions()
    for name in dir(rpc):
        if not name.startswith('_'):
            server.register_function(getattr(rpc, name), name)
    
    server.register_introspection_functions()
    
    print(f"[XML-RPC] Server pornit pe http://0.0.0.0:{port}")
    print("[XML-RPC] Apasati Ctrl+C For a opri\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[XML-RPC] Server oprit")


# =============================================================================
# XML-RPC CLIENT
# =============================================================================

def run_xmlrpc_client(host: str, port: int):
    """Ruleaza demonstratie client XML-RPC."""
    url = f"http://{host}:{port}"
    proxy = xmlrpc.client.ServerProxy(url)
    
    print("="*60)
    print(f"XML-RPC Client Demo - {url}")
    print("="*60)
    
    tests = [
        ("add", (2, 3), "2 + 3"),
        ("subtract", (10, 4), "10 - 4"),
        ("multiply", (7, 8), "7 * 8"),
        ("echo", ("Hello XML-RPC!",), "echo"),
        ("get_time", (), "server time"),
        ("sort_list", ([5, 2, 8, 1, 9],), "sort [5,2,8,1,9]"),
    ]
    
    for method, params, desc in tests:
        try:
            func = getattr(proxy, method)
            result = func(*params)
            print(f"  {desc}: {result}")
        except Exception as e:
            print(f"  {desc}: ERROR - {e}")
    
    # Introspection
    print("\n[Introspection]")
    methods = proxy.system.listMethods()
    print(f"  Metode disponibile: {', '.join(methods[:5])}...")
    
    print("\n" + "="*60)


# =============================================================================
# BENCHMARK
# =============================================================================

def run_benchmark(jsonrpc_port: int, xmlrpc_port: int, iterations: int = 100):
    """
    Benchmark comparativ JSON-RPC vs XML-RPC.
    
    Masoara:
    - Latenta medie per apel
    - Throughput (apeluri/secunda)
    """
    print("="*70)
    print("BENCHMARK: JSON-RPC vs XML-RPC")
    print("="*70)
    print(f"\nIteratii: {iterations}")
    print("Apel testat: add(1, 2)\n")
    
    results = {}
    
    # JSON-RPC
    print("[JSON-RPC]")
    try:
        client = JSONRPCClient(f"http://127.0.0.1:{jsonrpc_port}")
        
        # Warmup
        for _ in range(10):
            client.call("add", [1, 2])
        
        # Benchmark
        times = []
        start_total = time.time()
        for _ in range(iterations):
            start = time.time()
            client.call("add", [1, 2])
            times.append((time.time() - start) * 1000)
        total_time = time.time() - start_total
        
        results['jsonrpc'] = {
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'total_s': total_time,
            'rps': iterations / total_time
        }
        
        print(f"  Latenta medie: {results['jsonrpc']['avg_ms']:.2f} ms")
        print(f"  Min/Max: {results['jsonrpc']['min_ms']:.2f} / {results['jsonrpc']['max_ms']:.2f} ms")
        print(f"  Throughput: {results['jsonrpc']['rps']:.0f} req/s")
        
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Asigurati-va ca serverul ruleaza: python3 ex_02_rpc.py jsonrpc-server --port {jsonrpc_port}")
    
    # XML-RPC
    print("\n[XML-RPC]")
    try:
        proxy = xmlrpc.client.ServerProxy(f"http://127.0.0.1:{xmlrpc_port}")
        
        # Warmup
        for _ in range(10):
            proxy.add(1, 2)
        
        # Benchmark
        times = []
        start_total = time.time()
        for _ in range(iterations):
            start = time.time()
            proxy.add(1, 2)
            times.append((time.time() - start) * 1000)
        total_time = time.time() - start_total
        
        results['xmlrpc'] = {
            'avg_ms': sum(times) / len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'total_s': total_time,
            'rps': iterations / total_time
        }
        
        print(f"  Latenta medie: {results['xmlrpc']['avg_ms']:.2f} ms")
        print(f"  Min/Max: {results['xmlrpc']['min_ms']:.2f} / {results['xmlrpc']['max_ms']:.2f} ms")
        print(f"  Throughput: {results['xmlrpc']['rps']:.0f} req/s")
        
    except Exception as e:
        print(f"  Error: {e}")
        print(f"  Asigurati-va ca serverul ruleaza: python3 ex_02_rpc.py xmlrpc-server --port {xmlrpc_port}")
    
    # Comparatie
    if 'jsonrpc' in results and 'xmlrpc' in results:
        print("\n" + "-"*50)
        print("COMPARATIE:")
        
        ratio = results['xmlrpc']['avg_ms'] / results['jsonrpc']['avg_ms']
        if ratio > 1:
            print(f"  JSON-RPC este {ratio:.1f}x mai rapid decat XML-RPC")
        else:
            print(f"  XML-RPC este {1/ratio:.1f}x mai rapid decat JSON-RPC")
        
        print("""
  EXPLICAȚIE:
    - XML-RPC generează payload mai mare (XML verbose)
    - JSON-RPC are overhead mai mic (JSON compact)
    - Diferența crește with dimensiunea datelor
        """)
    
    print("="*70)


# =============================================================================
# SELFTEST
# =============================================================================

def run_selftest():
    """Ruleaza auto-teste."""
    print("="*60)
    print("SELFTEST: ex_02_rpc.py")
    print("="*60)
    
    # Test 1: JSON-RPC Server
    print("\n[Test 1] Pornire server JSON-RPC...")
    json_server = HTTPServer(('127.0.0.1', 18080), JSONRPCHandler)
    json_thread = threading.Thread(target=json_server.serve_forever, daemon=True)
    json_thread.start()
    time.sleep(0.3)
    print("  ✓ Server JSON-RPC pornit pe 18080")
    
    # Test 2: JSON-RPC Client
    print("\n[Test 2] Apel JSON-RPC add(2, 3)...")
    client = JSONRPCClient("http://127.0.0.1:18080")
    result = client.call("add", [2, 3])
    if result == 5:
        print(f"  ✓ Rezultat corect: {result}")
    else:
        print(f"  ✗ Rezultat incorect: {result}")
        return False
    
    # Test 3: XML-RPC Server
    print("\n[Test 3] Pornire server XML-RPC...")
    xml_server = SimpleXMLRPCServer(('127.0.0.1', 18000), logRequests=False)
    rpc = RPCFunctions()
    xml_server.register_function(rpc.add, 'add')
    xml_thread = threading.Thread(target=xml_server.serve_forever, daemon=True)
    xml_thread.start()
    time.sleep(0.3)
    print("  ✓ Server XML-RPC pornit pe 18000")
    
    # Test 4: XML-RPC Client
    print("\n[Test 4] Apel XML-RPC add(2, 3)...")
    proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:18000")
    result = proxy.add(2, 3)
    if result == 5:
        print(f"  ✓ Rezultat corect: {result}")
    else:
        print(f"  ✗ Rezultat incorect: {result}")
        return False
    
    # Test 5: Error JSON-RPC
    print("\n[Test 5] Test Error JSON-RPC (metoda inexistence)...")
    try:
        client.call("nonexistent_method")
        print("  ✗ Nu s-a generat Error")
        return False
    except Exception as e:
        if "not found" in str(e).lower() or "-32601" in str(e):
            print(f"  ✓ Error corecta: {e}")
        else:
            print(f"  ✗ Error incorecta: {e}")
            return False
    
    # Cleanup
    json_server.shutdown()
    xml_server.shutdown()
    
    print("\n" + "="*60)
    print("SELFTEST: TOATE TESTELE AU TRECUT ✓")
    print("="*60)
    return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Exercises RPC Self-Contained - Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comenzi disponibile:
  jsonrpc-server  - Pornește server JSON-RPC
  jsonrpc-client  - Rulează demo client JSON-RPC
  xmlrpc-server   - Pornește server XML-RPC
  xmlrpc-client   - Rulează demo client XML-RPC
  benchmark       - Benchmark comparativ

Exemple:
  python3 ex_02_rpc.py jsonrpc-server --port 8080
  python3 ex_02_rpc.py jsonrpc-client --port 8080
  python3 ex_02_rpc.py xmlrpc-server --port 8000
  python3 ex_02_rpc.py benchmark
  python3 ex_02_rpc.py --selftest

Revolvix&Hypotheticalandrei
        """
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # JSON-RPC Server
    p = subparsers.add_parser('jsonrpc-server')
    p.add_argument('--port', type=int, default=8080)
    
    # JSON-RPC Client
    p = subparsers.add_parser('jsonrpc-client')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8080)
    
    # XML-RPC Server
    p = subparsers.add_parser('xmlrpc-server')
    p.add_argument('--port', type=int, default=8000)
    
    # XML-RPC Client
    p = subparsers.add_parser('xmlrpc-client')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)
    
    # Benchmark
    p = subparsers.add_parser('benchmark')
    p.add_argument('--jsonrpc-port', type=int, default=8080)
    p.add_argument('--xmlrpc-port', type=int, default=8000)
    p.add_argument('--iterations', type=int, default=100)
    
    # Selftest
    parser.add_argument('--selftest', action='store_true')
    
    args = parser.parse_args()
    
    if args.selftest:
        success = run_selftest()
        sys.exit(0 if success else 1)
    
    if args.command == 'jsonrpc-server':
        run_jsonrpc_server(args.port)
    elif args.command == 'jsonrpc-client':
        run_jsonrpc_client(args.host, args.port)
    elif args.command == 'xmlrpc-server':
        run_xmlrpc_server(args.port)
    elif args.command == 'xmlrpc-client':
        run_xmlrpc_client(args.host, args.port)
    elif args.command == 'benchmark':
        run_benchmark(args.jsonrpc_port, args.xmlrpc_port, args.iterations)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
