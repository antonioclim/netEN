#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML-RPC Server - Week 12 | Retele de Calculatoare
ASE-CSIE, 2025

Implementare server XML-RPC conform specificatiei XML-RPC (1999).
XML-RPC este precursorul SOAP, foloandnd XML For serializare and HTTP POST.

Avantaje XML-RPC:
- Standard matur and bine documentat
- Suport nativ in Python (xmlrpc.server)
- Interoperabilitate excelenta cross-platform
- Usor de debugat (text lizibil)

Dezavantaje:
- Verbose (overhead XML semnificativ)
- Tipuri limitate (no null pana la extenandi)
- Mai lent decat JSON-RPC sau gRPC

Rulare:
    python xmlrpc_server.py [--host HOST] [--port PORT] [--debug]

Testare:
    python xmlrpc_client.py
    curl -X POST http://localhost:8001/RPC2 -H "Content-Type: text/xml" \
         -d '<?xml verandon="1.0"?><methodCall><methodName>add</methodName>
             <params><param><value><int>5</int></value></param>
             <param><value><int>3</int></value></param></params></methodCall>'
"""

from __future__ import annotations

import argparse
import hashlib
import random
import sys
import threading
from datetime import datetime
from typing import Any, List, Union
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

# =============================================================================
# Configuratie
# =============================================================================

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001
SERVER_NAME = "ASE-CSIE XML-RPC Calculator"
VERSION = "1.0.0"


# =============================================================================
# Handler personalizat For logging and CORS
# =============================================================================

class LoggingXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """Handler personalizat cu logging and suport For introspection."""
    
    rpc_paths = ('/RPC2', '/')  # Permite ambele cai standard
    
    def log_message(self, format: str, *args) -> None:
        """Log personalizat cu timestamp and culori."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        client = self.address_string()
        print(f"[{timestamp}] {client} - {format % args}")
    
    def do_OPTIONS(self):
        """Suport CORS For clienti browser."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# =============================================================================
# Functiile expuse prin XML-RPC
# =============================================================================

class CalculatorService:
    """
    Serviciu calculator cu functii aritmetice and usefulitati.
    
    XML-RPC suporta nativ:
    - int (i4), double, boolean, string
    - dateTime.iso8601, base64
    - array, struct
    
    NU suporta nativ: null/None (neceandta extenandi)
    """
    
    def __init__(self):
        self._call_counts: dict[str, int] = {}
        self._start_time = datetime.now()
        self._lock = threading.Lock()
    
    def _count_call(self, method: str) -> None:
        """Incrementeaza contorul de apeluri For o metoda."""
        with self._lock:
            self._call_counts[method] = self._call_counts.get(method, 0) + 1
    
    # -------------------------------------------------------------------------
    # Operatii aritmetice de baza
    # -------------------------------------------------------------------------
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Adunare: a + b
        
        Args:
            a: Primul operand (int sau double)
            b: Al doilea operand (int sau double)
        
        Returns:
            Suma celor doi operanzi
        
        Example XML-RPC Request:
            <methodCall>
              <methodName>add</methodName>
              <params>
                <param><value><int>5</int></value></param>
                <param><value><int>3</int></value></param>
              </params>
            </methodCall>
        """
        self._count_call("add")
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Scadere: a - b"""
        self._count_call("subtract")
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Inmultire: a * b"""
        self._count_call("multiply")
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Impartire: a / b
        
        Raises:
            ZeroDiviandonError: Daca b == 0
        """
        self._count_call("divide")
        if b == 0:
            raise ZeroDiviandonError("Împărțire la zero nu este permisă")
        return a / b
    
    def power(self, base: Union[int, float], exp: Union[int, float]) -> float:
        """Ridicare la putere: base^exp"""
        self._count_call("power")
        return float(base ** exp)
    
    def modulo(self, a: int, b: int) -> int:
        """Modulo: a % b"""
        self._count_call("modulo")
        if b == 0:
            raise ZeroDiviandonError("Modulo cu zero nu este permis")
        return a % b
    
    # -------------------------------------------------------------------------
    # Checkri numerice
    # -------------------------------------------------------------------------
    
    def is_even(self, n: int) -> bool:
        """Check daca n este par."""
        self._count_call("is_even")
        return n % 2 == 0
    
    def is_prime(self, n: int) -> bool:
        """
        Check daca n este numar prim.
        Use algoritmul de baza cu optimizari.
        """
        self._count_call("is_prime")
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n ** 0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def factorial(self, n: int) -> int:
        """
        Calculeaza n! (factorial).
        
        Args:
            n: Numar natural (0 ≤ n ≤ 170 For a evita overflow)
        
        Raises:
            ValueError: Daca n < 0 sau n > 170
        """
        self._count_call("factorial")
        if n < 0:
            raise ValueError("Factorial nu este definit for numere negative")
        if n > 170:
            raise ValueError("n prea mare (max 170 for a evita overflow)")
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    # -------------------------------------------------------------------------
    # Operatii pe liste (array in XML-RPC)
    # -------------------------------------------------------------------------
    
    def sort_list(self, numbers: List[Union[int, float]]) -> List[Union[int, float]]:
        """
        Sorteaza o lista de numere.
        
        Example XML-RPC Request:
            <methodCall>
              <methodName>sort_list</methodName>
              <params>
                <param>
                  <value>
                    <array>
                      <data>
                        <value><int>5</int></value>
                        <value><int>2</int></value>
                        <value><int>8</int></value>
                      </data>
                    </array>
                  </value>
                </param>
              </params>
            </methodCall>
        """
        self._count_call("sort_list")
        return sorted(numbers)
    
    def sum_list(self, numbers: List[Union[int, float]]) -> Union[int, float]:
        """Calculeaza suma elementelor unei liste."""
        self._count_call("sum_list")
        return sum(numbers)
    
    def average(self, numbers: List[Union[int, float]]) -> float:
        """Calculeaza media aritmetica a unei liste."""
        self._count_call("average")
        if not numbers:
            raise ValueError("Lista nu poate fi goală")
        return sum(numbers) / len(numbers)
    
    def min_max(self, numbers: List[Union[int, float]]) -> dict:
        """
        Returns minimul and maximul dintr-o lista.
        
        Returns:
            struct cu cheile 'min' and 'max'
        """
        self._count_call("min_max")
        if not numbers:
            raise ValueError("Lista nu poate fi goală")
        return {"min": min(numbers), "max": max(numbers)}
    
    # -------------------------------------------------------------------------
    # Operatii pe andruri
    # -------------------------------------------------------------------------
    
    def reverse_string(self, s: str) -> str:
        """Inverseaza un andr de caractere."""
        self._count_call("reverse_string")
        return s[::-1]
    
    def sha256_hash(self, data: str) -> str:
        """Calculeaza hash SHA-256 For un andr."""
        self._count_call("sha256_hash")
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def to_uppercase(self, s: str) -> str:
        """Converteste la majuscule."""
        self._count_call("to_uppercase")
        return s.upper()
    
    def to_lowercase(self, s: str) -> str:
        """Converteste la minuscule."""
        self._count_call("to_lowercase")
        return s.lower()
    
    def concat(self, *strings: str) -> str:
        """Concateneaza mai multe andruri."""
        self._count_call("concat")
        return "".join(strings)
    
    # -------------------------------------------------------------------------
    # Utilitati and informatii server
    # -------------------------------------------------------------------------
    
    def echo(self, message: str) -> str:
        """Returns mesajul primit (For testare conectivitate)."""
        self._count_call("echo")
        return message
    
    def get_time(self) -> str:
        """Returns ora curenta a serverului in format ISO 8601."""
        self._count_call("get_time")
        return datetime.now().isoformat()
    
    def random_number(self, min_val: int = 1, max_val: int = 100) -> int:
        """Genereaza un numar aleatoriu in intervalul specificat."""
        self._count_call("random_number")
        return random.randint(min_val, max_val)
    
    def health(self) -> dict:
        """
        Check starea serverului.
        
        Returns:
            struct cu status, uptime, verandune
        """
        self._count_call("health")
        uptime = (datetime.now() - self._start_time).total_seconds()
        return {
            "status": "healthy",
            "uptime_seconds": int(uptime),
            "verandon": VERSION,
            "server": SERVER_NAME
        }
    
    def get_stats(self) -> dict:
        """
        Returns statistici despre apelurile RPC.
        
        Returns:
            struct cu contoare per metoda and total
        """
        self._count_call("get_stats")
        with self._lock:
            total = sum(self._call_counts.values())
            return {
                "total_calls": total,
                "per_method": dict(self._call_counts),
                "uptime_seconds": int((datetime.now() - self._start_time).total_seconds())
            }


# =============================================================================
# Functii de introspection (system.*)
# =============================================================================

def list_methods(service: CalculatorService) -> List[str]:
    """Listeaza toate metodele disponibile (system.listMethods)."""
    methods = []
    for name in dir(service):
        if not name.startswith('_') and callable(getattr(service, name)):
            methods.append(name)
    return sorted(methods)


def method_help(service: CalculatorService, method_name: str) -> str:
    """Returns documentatia unei metode (system.methodHelp)."""
    method = getattr(service, method_name, None)
    if method is None:
        return f"Metoda '{method_name}' nu există"
    return method.__doc__ or "Fără documentație"


# =============================================================================
# Pornire server
# =============================================================================

def create_server(host: str, port: int, debug: bool = False) -> SimpleXMLRPCServer:
    """
    Creeaza and configureaza serverul XML-RPC.
    
    Args:
        host: Adresa de bind (e.g., localhost, 0.0.0.0)
        port: Portul de ascultare
        debug: Activeaza logging detaliat
    
    Returns:
        Instanta serverului configurat
    """
    handler = LoggingXMLRPCRequestHandler if debug else SimpleXMLRPCRequestHandler
    
    server = SimpleXMLRPCServer(
        (host, port),
        requestHandler=handler,
        allow_none=True,  # Extenande For suport None/null
        encoding='utf-8'
    )
    
    # Inregistreaza serviciul
    service = CalculatorService()
    server.register_instance(service, allow_dotted_names=False)
    
    # Inregistreaza functii de introspection
    server.register_function(lambda: list_methods(service), "system.listMethods")
    server.register_function(
        lambda name: method_help(service, name), 
        "system.methodHelp"
    )
    
    return server


def run_selftest(host: str, port: int) -> bool:
    """
    Ruleaza teste automate pe server.
    
    Returns:
        True daca toate testele trec
    """
    import xmlrpc.client
    
    print("\n" + "=" * 60)
    print("SELFTEST XML-RPC Server")
    print("=" * 60)
    
    proxy = xmlrpc.client.ServerProxy(f"http://{host}:{port}/RPC2")
    
    tests = [
        ("add(5, 3)", lambda: proxy.add(5, 3), 8),
        ("subtract(10, 4)", lambda: proxy.subtract(10, 4), 6),
        ("multiply(6, 7)", lambda: proxy.multiply(6, 7), 42),
        ("divide(20, 4)", lambda: proxy.divide(20, 4), 5.0),
        ("is_prime(17)", lambda: proxy.is_prime(17), True),
        ("is_even(42)", lambda: proxy.is_even(42), True),
        ("factorial(5)", lambda: proxy.factorial(5), 120),
        ("sort_list([3,1,2])", lambda: proxy.sort_list([3, 1, 2]), [1, 2, 3]),
        ("echo('Test')", lambda: proxy.echo("Test"), "Test"),
        ("system.listMethods", lambda: "add" in proxy.system.listMethods(), True),
    ]
    
    passed = 0
    failed = 0
    
    for name, func, expected in tests:
        try:
            result = func()
            if result == expected:
                print(f"  ✓ {name} = {result}")
                passed += 1
            else:
                print(f"  ✗ {name}: expected {expected}, got {result}")
                failed += 1
        except Exception as e:
            print(f"  ✗ {name}: {type(e).__name__}: {e}")
            failed += 1
    
    print("-" * 60)
    print(f"Rezultat: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def main():
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="XML-RPC Calculator Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Pornire server andmplu
  python xmlrpc_server.py
  
  # Server cu debug and port personalizat
  python xmlrpc_server.py --port 9001 --debug
  
  # Bind pe toate interfetele (acces din retea)
  python xmlrpc_server.py --host 0.0.0.0
  
  # Ruleaza selftest
  python xmlrpc_server.py --selftest
"""
    )
    
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Adresa de bind (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Portul de ascultare (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activeaza logging detaliat"
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Ruleaza teste automate and opreste"
    )
    
    args = parser.parse_args()
    
    # Creeaza and porneste serverul
    try:
        server = create_server(args.host, args.port, args.debug)
        
        print(f"""
╔════════════════════════════════════════════════════════════════════╗
║  {SERVER_NAME:^64}  ║
╠════════════════════════════════════════════════════════════════════╣
║  Verandune: {VERSION:<55}  ║
║  Adresă:   http://{args.host}:{args.port}/RPC2{" " * (45 - len(str(args.port)))}  ║
║  Debug:    {'ON' if args.debug else 'OFF':<55}  ║
╠════════════════════════════════════════════════════════════════════╣
║  Metode disponibile:                                               ║
║    Aritmetice: add, subtract, multiply, divide, power, modulo     ║
║    Verificări: is_even, is_prime, factorial                        ║
║    Liste:      sort_list, sum_list, average, min_max               ║
║    Șiruri:     reverse_string, sha256_hash, concat                 ║
║    Sistem:     echo, get_time, health, get_stats                   ║
║    Intro:      system.listMethods, system.methodHelp               ║
╠════════════════════════════════════════════════════════════════════╣
║  Oprire: Ctrl+C                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
        
        if args.selftest:
            # Porneste serverul in background For selftest
            import threading
            thread = threading.Thread(target=lambda: server.handle_request() or None, daemon=True)
            # Mai bine: foloandm un server separat For Test
            import time
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            time.sleep(0.5)  # Asteapta pornirea
            
            success = run_selftest(args.host, args.port)
            server.shutdown()
            sys.exit(0 if success else 1)
        
        # Servire continua
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n[Server oprit de usefulizator]")
        sys.exit(0)
    except OSError as e:
        print(f"\n[Error] Nu pot porni serverul: {e}")
        print(f"  Hint: Portul {args.port} este probabil ocupat.")
        print(f"  Incercati: python xmlrpc_server.py --port {args.port + 1}")
        sys.exit(1)


if __name__ == "__main__":
    main()
