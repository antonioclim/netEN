#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML-RPC Client - Week 12 | Retele de Calculatoare
ASE-CSIE, 2025

Client XML-RPC For interactiunea cu serverul calculator.
Demonstreaza apeluri andncrone, gestionarea erorilor and benchmarking.

XML-RPC Wire Format (Example For add(5, 3)):
    Request:
        POST /RPC2 HTTP/1.1
        Content-Type: text/xml
        
        <?xml verandon="1.0"?>
        <methodCall>
          <methodName>add</methodName>
          <params>
            <param><value><int>5</int></value></param>
            <param><value><int>3</int></value></param>
          </params>
        </methodCall>
    
    Response:
        HTTP/1.1 200 OK
        Content-Type: text/xml
        
        <?xml verandon="1.0"?>
        <methodResponse>
          <params>
            <param><value><int>8</int></value></param>
          </params>
        </methodResponse>

Rulare:
    python xmlrpc_client.py [--host HOST] [--port PORT] [--demo|--benchmark|--interactive]
"""

from __future__ import annotations

import argparse
import sys
import time
import random
from datetime import datetime
from typing import Any, List, Optional
import xmlrpc.client

# =============================================================================
# Configuratie
# =============================================================================

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001


# =============================================================================
# Clasa Client
# =============================================================================

class XMLRPCCalculatorClient:
    """
    Client For serviciul Calculator XML-RPC.
    
    Incapsuleaza conexiunea and ofera metode de convenienta.
    """
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                 verbose: bool = False, timeout: float = 30.0):
        """
        Initializeaza clientul XML-RPC.
        
        Args:
            host: Adresa serverului
            port: Portul serverului
            verbose: Afiseaza XML request/response
            timeout: Timeout For conexiune (secunde)
        """
        self.url = f"http://{host}:{port}/RPC2"
        self.verbose = verbose
        
        # Creeaza proxy-ul cu transport personalizat For timeout
        transport = xmlrpc.client.Transport()
        transport.timeout = timeout
        
        self.proxy = xmlrpc.client.ServerProxy(
            self.url,
            transport=transport,
            verbose=verbose,  # Afiseaza XML daca True
            allow_none=True,
            encoding='utf-8'
        )
    
    def call(self, method: str, *args, **kwargs) -> Any:
        """
        Apeleaza o metoda RPC generic.
        
        Args:
            method: Numele metodei
            *args: Argumentele pozitionale
            **kwargs: Argumentele numite (convertite la struct)
        
        Returns:
            Rezultatul apelului
        
        Raises:
            xmlrpc.client.Fault: Error de la server
            ConnectionError: Nu se poate conecta
        """
        try:
            func = getattr(self.proxy, method)
            if kwargs:
                # XML-RPC nu suporta kwargs nativ, le sendm ca struct
                return func(*args, kwargs)
            return func(*args)
        except xmlrpc.client.Fault as e:
            raise RuntimeError(f"Eroare server: [{e.faultCode}] {e.faultString}")
        except ConnectionRefusedError:
            raise ConnectionError(f"Nu pot conecta la {self.url}")
    
    # Metode de convenienta
    def add(self, a, b): return self.proxy.add(a, b)
    def subtract(self, a, b): return self.proxy.subtract(a, b)
    def multiply(self, a, b): return self.proxy.multiply(a, b)
    def divide(self, a, b): return self.proxy.divide(a, b)
    def power(self, base, exp): return self.proxy.power(base, exp)
    def is_prime(self, n): return self.proxy.is_prime(n)
    def factorial(self, n): return self.proxy.factorial(n)
    def sort_list(self, lst): return self.proxy.sort_list(lst)
    def health(self): return self.proxy.health()
    def get_stats(self): return self.proxy.get_stats()
    def list_methods(self): return self.proxy.system.listMethods()


# =============================================================================
# Demonstratii
# =============================================================================

def demo_baandc_calls(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza apeluri de baza."""
    print("\n" + "=" * 60)
    print("DEMO 1: Operatii Aritmetice de Baza")
    print("=" * 60)
    
    operations = [
        ("add(15, 27)", lambda: client.add(15, 27)),
        ("subtract(100, 42)", lambda: client.subtract(100, 42)),
        ("multiply(7, 8)", lambda: client.multiply(7, 8)),
        ("divide(144, 12)", lambda: client.divide(144, 12)),
        ("power(2, 10)", lambda: client.power(2, 10)),
    ]
    
    for name, func in operations:
        result = func()
        print(f"  {name:25} = {result}")


def demo_checktion(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza functii de checkre."""
    print("\n" + "=" * 60)
    print("DEMO 2: Checkri and Calcule Avansate")
    print("=" * 60)
    
    # Checkri prime
    primes = [17, 23, 97, 100]
    print("\n  Numere prime:")
    for n in primes:
        is_p = client.is_prime(n)
        status = "✓ prim" if is_p else "✗ compus"
        print(f"    {n}: {status}")
    
    # Factorial
    print("\n  Factorial:")
    for n in [5, 7, 10]:
        result = client.factorial(n)
        print(f"    {n}! = {result:,}")


def demo_lists(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza operatii pe liste."""
    print("\n" + "=" * 60)
    print("DEMO 3: Operatii pe Liste (array in XML-RPC)")
    print("=" * 60)
    
    test_list = [64, 25, 12, 22, 11, 90, 45]
    print(f"\n  List originala: {test_list}")
    
    sorted_list = client.proxy.sort_list(test_list)
    print(f"  sort_list:       {sorted_list}")
    
    sum_result = client.proxy.sum_list(test_list)
    print(f"  sum_list:        {sum_result}")
    
    avg_result = client.proxy.average(test_list)
    print(f"  average:         {avg_result:.2f}")
    
    minmax = client.proxy.min_max(test_list)
    print(f"  min_max:         min={minmax['min']}, max={minmax['max']}")


def demo_strings(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza operatii pe andruri."""
    print("\n" + "=" * 60)
    print("DEMO 4: Operatii pe Siruri")
    print("=" * 60)
    
    test_str = "ASE-CSIE Retele 2025"
    print(f"\n  Sir original:    '{test_str}'")
    
    reversed_str = client.proxy.reverse_string(test_str)
    print(f"  reverse_string:  '{reversed_str}'")
    
    upper = client.proxy.to_uppercase(test_str)
    print(f"  to_uppercase:    '{upper}'")
    
    sha = client.proxy.sha256_hash(test_str)
    print(f"  sha256_hash:     {sha[:32]}...")


def demo_introspection(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza introspection (system.*)."""
    print("\n" + "=" * 60)
    print("DEMO 5: Introspection (system.*)")
    print("=" * 60)
    
    print("\n  system.listMethods():")
    methods = client.list_methods()
    # Afiseaza in coloane
    for i in range(0, len(methods), 4):
        row = methods[i:i+4]
        print("    " + ", ".join(f"{m:20}" for m in row))
    
    print("\n  system.methodHelp('add'):")
    help_text = client.proxy.system.methodHelp("add")
    # Afiseaza primele 5 linii
    lines = help_text.strip().split('\n')[:5]
    for line in lines:
        print(f"    {line}")
    if len(lines) < len(help_text.strip().split('\n')):
        print("    ...")


def demo_error_handling(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza gestionarea erorilor."""
    print("\n" + "=" * 60)
    print("DEMO 6: Gestionarea Erorilor XML-RPC")
    print("=" * 60)
    
    error_cases = [
        ("divide(10, 0)", lambda: client.divide(10, 0)),
        ("factorial(-5)", lambda: client.factorial(-5)),
        ("metoda_inexistenta()", lambda: client.proxy.metoda_inexistenta()),
    ]
    
    for name, func in error_cases:
        try:
            result = func()
            print(f"  {name}: {result}")
        except xmlrpc.client.Fault as e:
            print(f"  {name}")
            print(f"    → Fault [{e.faultCode}]: {e.faultString[:50]}...")
        except Exception as e:
            print(f"  {name}")
            print(f"    → {type(e).__name__}: {str(e)[:50]}...")


def demo_server_info(client: XMLRPCCalculatorClient) -> None:
    """Demonstreaza informatii despre server."""
    print("\n" + "=" * 60)
    print("DEMO 7: Informatii Server")
    print("=" * 60)
    
    health = client.health()
    print("\n  health():")
    for key, value in health.items():
        print(f"    {key}: {value}")
    
    stats = client.get_stats()
    print("\n  get_stats():")
    print(f"    Total apeluri: {stats['total_calls']}")
    print(f"    Uptime: {stats['uptime_seconds']}s")
    if stats['per_method']:
        print("    Top 5 metode:")
        sorted_methods = sorted(
            stats['per_method'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for method, count in sorted_methods:
            print(f"      {method}: {count}")


def run_all_demos(client: XMLRPCCalculatorClient) -> None:
    """Ruleaza toate demonstratiile."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " DEMO XML-RPC Client ".center(68) + "║")
    print("║" + f" Server: {client.url} ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    demo_baandc_calls(client)
    demo_checktion(client)
    demo_lists(client)
    demo_strings(client)
    demo_introspection(client)
    demo_error_handling(client)
    demo_server_info(client)
    
    print("\n" + "=" * 60)
    print("Demo complet!")
    print("=" * 60 + "\n")


# =============================================================================
# Benchmark
# =============================================================================

def benchmark_xmlrpc(client: XMLRPCCalculatorClient, iterations: int = 100) -> dict:
    """
    Benchmark For a masura overhead-ul XML-RPC.
    
    Compara:
    1. Apeluri andmple (latenta de baza)
    2. Transfer date mari (overhead serializare)
    3. Operatii CPU-intenandve
    4. Batch andmulation (multiple apeluri secventiale)
    
    Returns:
        Dict cu rezultatele benchmark-ului
    """
    results = {}
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " BENCHMARK XML-RPC ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Test 1: Latenta de baza
    print(f"\n[Test 1] Apeluri andmple add(1, 2) × {iterations}")
    start = time.perf_counter()
    for _ in range(iterations):
        client.add(1, 2)
    elapsed = time.perf_counter() - start
    
    rps = iterations / elapsed
    avg_ms = (elapsed / iterations) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    print(f"  Throughput: {rps:.1f} apeluri/secunda")
    results["andmple_calls"] = {"total_s": elapsed, "avg_ms": avg_ms, "rps": rps}
    
    # Test 2: Transfer date mari
    large_list = list(range(5000))
    print(f"\n[Test 2] sort_list cu {len(large_list)} elemente × 10")
    
    start = time.perf_counter()
    for _ in range(10):
        client.sort_list(large_list)
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / 10) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    
    # Comparatie cu sortare locala
    start_local = time.perf_counter()
    for _ in range(10):
        sorted(large_list)
    elapsed_local = time.perf_counter() - start_local
    overhead = elapsed / elapsed_local
    print(f"  Overhead vs local: {overhead:.1f}x")
    results["large_data"] = {"total_s": elapsed, "avg_ms": avg_ms, "overhead": overhead}
    
    # Test 3: Operatii CPU-intenandve
    print(f"\n[Test 3] sha256_hash pe 1KB date × {iterations}")
    test_data = "x" * 1024
    
    start = time.perf_counter()
    for _ in range(iterations):
        client.proxy.sha256_hash(test_data)
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / iterations) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    results["cpu_intenandve"] = {"total_s": elapsed, "avg_ms": avg_ms}
    
    # Test 4: Multiple apeluri diferite (andmulare workflow real)
    print(f"\n[Test 4] Workflow complet (5 operatii) × {iterations // 5}")
    
    workflow_iters = iterations // 5
    start = time.perf_counter()
    for i in range(workflow_iters):
        # Simuleaza un flux tipic
        client.add(i, i + 1)
        client.multiply(i, 2)
        client.is_prime(i)
        client.proxy.echo(f"test_{i}")
        client.proxy.get_time()
    elapsed = time.perf_counter() - start
    
    ops_per_sec = (workflow_iters * 5) / elapsed
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Operatii/secunda: {ops_per_sec:.1f}")
    results["workflow"] = {"total_s": elapsed, "ops_per_sec": ops_per_sec}
    
    # Sumar
    print("\n" + "-" * 60)
    print("SUMAR BENCHMARK")
    print("-" * 60)
    print(f"  Latenta medie (apel andmplu): {results['andmple_calls']['avg_ms']:.2f}ms")
    print(f"  Throughput maxim: {results['andmple_calls']['rps']:.0f} req/s")
    print(f"  Overhead For date mari: {results['large_data']['overhead']:.1f}x")
    print("-" * 60)
    
    return results


# =============================================================================
# Mod Interactiv
# =============================================================================

def interactive_mode(client: XMLRPCCalculatorClient) -> None:
    """
    Mod interactiv For testare manuala.
    
    Permite usefulizatorului sa introduca apeluri XML-RPC direct.
    """
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " MOD INTERACTIV XML-RPC ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("""
Comenzi disponibile:
  list              - Afișează toate metodele
  help <metodă>     - Documentația unei metode  
  <metodă> args...  - Apelează metoda cu argumente
  quit / exit       - Ieșire

Exemple:
  add 5 3           → 8
  is_prime 17       → True
  sort_list [5,2,8] → [2, 5, 8]
  echo "Hello"      → Hello
""")
    
    while True:
        try:
            cmd = input("\nxml-rpc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break
        
        if not cmd:
            continue
        
        if cmd.lower() in ("quit", "exit", "q"):
            print("La revedere!")
            break
        
        if cmd.lower() == "list":
            methods = client.list_methods()
            print("Metode disponibile:")
            for i, m in enumerate(methods, 1):
                print(f"  {i:2}. {m}")
            continue
        
        if cmd.lower().startswith("help "):
            method_name = cmd[5:].strip()
            try:
                help_text = client.proxy.system.methodHelp(method_name)
                print(f"Documentatie For {method_name}:")
                print(help_text)
            except Exception as e:
                print(f"Error: {e}")
            continue
        
        # Parse method call
        parts = cmd.split(maxsplit=1)
        method_name = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        try:
            # Evalueaza argumentele (atentie la securitate in productie!)
            if args_str:
                # Inlocuieste List cu andntaxa Python
                args_str = args_str.replace('[', '(').replace(']', ',)')
                args = eval(f"({args_str},)")
            else:
                args = ()
            
            # Apeleaza metoda
            method = getattr(client.proxy, method_name)
            result = method(*args)
            print(f"Rezultat: {result}")
            
        except xmlrpc.client.Fault as e:
            print(f"Error XML-RPC [{e.faultCode}]: {e.faultString}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="XML-RPC Calculator Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Ruleaza demo-uri
  python xmlrpc_client.py --demo
  
  # Benchmark
  python xmlrpc_client.py --benchmark
  
  # Mod interactiv
  python xmlrpc_client.py --interactive
  
  # Verbose (afiseaza XML)
  python xmlrpc_client.py --demo --verbose
"""
    )
    
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Adresa serverului (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Portul serverului (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ruleaza toate demonstratiile"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Ruleaza benchmark"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Porneste mod interactiv"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afiseaza XML request/response"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Numar de iteratii For benchmark (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Implicit: demo daca nu e specificat altceva
    if not (args.demo or args.benchmark or args.interactive):
        args.demo = True
    
    try:
        client = XMLRPCCalculatorClient(
            host=args.host,
            port=args.port,
            verbose=args.verbose
        )
        
        # Check conectivitatea
        try:
            client.health()
        except Exception as e:
            print(f"[Error] Nu pot conecta la {client.url}")
            print(f"  {type(e).__name__}: {e}")
            print(f"\n  Aandgurati-va ca serverul ruleaza:")
            print(f"    python xmlrpc_server.py --port {args.port}")
            sys.exit(1)
        
        if args.demo:
            run_all_demos(client)
        
        if args.benchmark:
            benchmark_xmlrpc(client, iterations=args.iterations)
        
        if args.interactive:
            interactive_mode(client)
    
    except KeyboardInterrupt:
        print("\n[Intrerupt de usefulizator]")
        sys.exit(0)


if __name__ == "__main__":
    main()
