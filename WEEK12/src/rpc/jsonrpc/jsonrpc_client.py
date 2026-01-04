#!/usr/bin/env python3
"""
jsonrpc_client.py - Client JSON-RPC 2.0 Didactic For Week 12

Demonstreaza:
- Construirea cererilor JSON-RPC 2.0
- Parameters pozitionali vs numiti
- Tratarea erorilor
- Batch requests
- Notificari

Utilizare:
    python3 jsonrpc_client.py --host 127.0.0.1 --port 8080

Revolvix&Hypotheticalandrei
"""

import argparse
import json
import sys
import time
import urllib.request
from typing import Any, Dict, List, Optional, Union


class JSONRPCClient:
    """
    Client JSON-RPC 2.0.
    
    Example de usefulizare:
        client = JSONRPCClient("http://localhost:8080")
        result = client.call("add", [2, 3])
        print(result)  # 5
    """
    
    def __init__(self, url: str, timeout: float = 10.0):
        """
        Initializeaza clientul.
        
        Args:
            url: URL-ul serverului JSON-RPC
            timeout: Timeout For cereri (secunde)
        """
        self.url = url
        self.timeout = timeout
        self._id_counter = 0
    
    def _next_id(self) -> int:
        """Genereaza ID unic For cerere."""
        self._id_counter += 1
        return self._id_counter
    
    def call(self, method: str, params: Union[List, Dict, None] = None) -> Any:
        """
        Apeleaza o metoda RPC and return rezultatul.
        
        Args:
            method: Numele metodei
            params: Parameters (lista For pozitionali, dict For numiti)
        
        Returns:
            Rezultatul metodei
        
        Raises:
            JSONRPCError: Daca serverul return Error
            Exception: For erori de comunicare
        """
        request = self._build_request(method, params, self._next_id())
        response = self._send(request)
        
        if "error" in response:
            error = response["error"]
            raise JSONRPCException(
                error.get("code", -1),
                error.get("message", "Unknown error"),
                error.get("data")
            )
        
        return response.get("result")
    
    def notify(self, method: str, params: Union[List, Dict, None] = None):
        """
        Sends o notificare (fara a astepta raspuns).
        
        Notificarile JSON-RPC nu au campul "id" and serverul nu Sends raspuns.
        """
        request = self._build_request(method, params, None)
        self._send(request, expect_response=False)
    
    def batch(self, calls: List[tuple]) -> List[Any]:
        """
        Executa mai multe apeluri intr-o andngura cerere.
        
        Args:
            calls: List de tuple (method, params)
        
        Returns:
            List de rezultate
        
        Example:
            results = client.batch([
                ("add", [1, 2]),
                ("multiply", [3, 4]),
                ("get_time", None)
            ])
        """
        requests = []
        for method, params in calls:
            requests.append(self._build_request(method, params, self._next_id()))
        
        responses = self._send(requests)
        
        # Sortam raspunsurile dupa id
        response_map = {r["id"]: r for r in responses}
        
        results = []
        for req in requests:
            resp = response_map.get(req["id"])
            if resp and "error" in resp:
                results.append(JSONRPCException(
                    resp["error"].get("code"),
                    resp["error"].get("message"),
                    resp["error"].get("data")
                ))
            else:
                results.append(resp.get("result") if resp else None)
        
        return results
    
    def _build_request(self, method: str, params: Any, req_id: Optional[int]) -> Dict:
        """Construieste obiectul cerere JSON-RPC."""
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params is not None:
            request["params"] = params
        
        if req_id is not None:
            request["id"] = req_id
        
        return request
    
    def _send(self, request: Union[Dict, List], expect_response: bool = True) -> Any:
        """Sends cererea and receive raspunsul."""
        body = json.dumps(request).encode('utf-8')
        
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            if expect_response and resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
            return None


class JSONRPCException(Exception):
    """Exceptie For erori JSON-RPC."""
    
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"JSON-RPC Error {code}: {message}")


def demo_calls(host: str, port: int, verbose: bool = False):
    """
    Demonstreaza diverse apeluri JSON-RPC.
    """
    url = f"http://{host}:{port}"
    client = JSONRPCClient(url)
    
    print("=" * 60)
    print(f"JSON-RPC Client Demo - {url}")
    print("=" * 60)
    
    # Demo 1: Apel andmplu
    print("\n[Demo 1] Apel andmplu: add(2, 3)")
    try:
        result = client.call("add", [2, 3])
        print(f"  Rezultat: {result}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 2: Parameters numiti
    print("\n[Demo 2] Parameters numiti: subtract(a=10, b=4)")
    try:
        result = client.call("subtract", {"a": 10, "b": 4})
        print(f"  Rezultat: {result}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 3: Metoda cu obiect complex
    print("\n[Demo 3] sort_list([3, 1, 4, 1, 5, 9], reverse=True)")
    try:
        result = client.call("sort_list", {"items": [3, 1, 4, 1, 5, 9], "reverse": True})
        print(f"  Rezultat: {result}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 4: Informatii server
    print("\n[Demo 4] get_server_info()")
    try:
        info = client.call("get_server_info")
        print(f"  Server: {info['name']}")
        print(f"  Verandune: {info['verandon']}")
        print(f"  Protocol: {info['Protocol']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 5: Error (metoda inexistenta)
    print("\n[Demo 5] Apel metoda inexistenta")
    try:
        client.call("nonexistent_method")
    except JSONRPCException as e:
        print(f"  Error capturata corect: {e}")
    except Exception as e:
        print(f"  Error neasteptata: {e}")
    
    # Demo 6: Batch request
    print("\n[Demo 6] Batch request (3 apeluri andmultane)")
    try:
        results = client.batch([
            ("add", [1, 2]),
            ("multiply", [3, 4]),
            ("get_time", None)
        ])
        print(f"  add(1,2) = {results[0]}")
        print(f"  multiply(3,4) = {results[1]}")
        print(f"  get_time() = {results[2]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 7: Benchmark
    print("\n[Demo 7] Benchmark overhead RPC")
    try:
        # Apel local For comparatie
        start_local = time.time()
        local_sum = sum(range(1000))
        local_time = (time.time() - start_local) * 1000
        
        # Apel remote
        start_remote = time.time()
        result = client.call("benchmark", [1000])
        remote_time = (time.time() - start_remote) * 1000
        
        print(f"  Apel local: {local_time:.2f} ms")
        print(f"  Apel remote: {remote_time:.2f} ms")
        print(f"  Overhead RPC: ~{remote_time - local_time:.2f} ms")
        print(f"  Server procesandng: {result['total_time_ms']} ms")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Demo 8: Multiple apeluri For latenta medie
    print("\n[Demo 8] Latenta medie (10 apeluri)")
    try:
        times = []
        for i in range(10):
            start = time.time()
            client.call("echo", [f"test_{i}"])
            times.append((time.time() - start) * 1000)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  Medie: {avg_time:.2f} ms")
        print(f"  Min: {min_time:.2f} ms")
        print(f"  Max: {max_time:.2f} ms")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo complet!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Client JSON-RPC 2.0 Didactic For Week 12",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de usefulizare:

  # Demo complet
  python3 jsonrpc_client.py --host 127.0.0.1 --port 8080

  # Apel individual
  python3 jsonrpc_client.py --host 127.0.0.1 --port 8080 \\
      --call add --params "[2, 3]"

Revolvix&Hypotheticalandrei
        """
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                        help='Hostname server (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port server (default: 8080)')
    parser.add_argument('--call', metavar='METHOD',
                        help='Apeleaza o metoda specifica')
    parser.add_argument('--params', metavar='JSON',
                        help='Parameters JSON For metoda')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output verbose')
    
    args = parser.parse_args()
    
    if args.call:
        # Apel individual
        client = JSONRPCClient(f"http://{args.host}:{args.port}")
        params = json.loads(args.params) if args.params else None
        
        try:
            result = client.call(args.call, params)
            print(json.dumps({"result": result}, indent=2, ensure_ascii=False))
        except JSONRPCException as e:
            print(json.dumps({"error": {"code": e.code, "message": e.message}}, indent=2))
            sys.exit(1)
    else:
        # Demo complet
        demo_calls(args.host, args.port, args.verbose)


if __name__ == "__main__":
    main()
