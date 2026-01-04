# Seminar 12: Remote Procedure Call (RPC)

> **Course:** Computer Networks  
> **Week:** 12 of 14  
> **Duration:** 2 hours  
> **Author:** Revolvix&Hypotheticalandrei

---

## What We Will Learn

In this seminar we explore **Remote Procedure Call (RPC)**, the mechanism that allows invoking functions on a remote server as if they were local. We will study:

- RPC concept and architecture
- **JSON-RPC 2.0** – the modern, lightweight specification
- **XML-RPC** – the XML-based precursor
- **gRPC with Protocol Buffers** – the high-performance solution
- RPC traffic analysis with Wireshark
- Benchmark and performance comparisons

## Why It Matters

RPC is the foundation of modern distributed architectures:
- **Microservices**: Communication between services in a cluster
- **Blockchain APIs**: Bitcoin, Ethereum expose JSON-RPC
- **IDE extensions**: Language Server Protocol uses JSON-RPC
- **Internal APIs**: Google, Netflix use gRPC extensively

---

## 1. The RPC Concept

### 1.1 Definition

**Remote Procedure Call** abstracts network communication, allowing calling functions on a remote server **as if they were local**.

```
Local call:        result = add(2, 3)
Remote call (RPC): result = remote_server.add(2, 3)  # Same syntax!
```

The client does not explicitly manage:
- Socket connections
- Serialisation/deserialisation
- Transport protocol
- Network-level error handling

### 1.2 Components of an RPC System

```
┌─────────────────────────────────────────────────────────┐
│                       CLIENT                            │
│  ┌──────────────┐    ┌─────────────┐    ┌───────────┐  │
│  │  Application │───▶│ Client Stub │───▶│ Transport │  │
│  │     Code     │    │  (Proxy)    │    │   Layer   │  │
│  └──────────────┘    └─────────────┘    └─────┬─────┘  │
└────────────────────────────────────────────────│────────┘
                                                 │
                        Network                  │ TCP/HTTP
                                                 │
┌────────────────────────────────────────────────│────────┐
│                       SERVER                   │        │
│  ┌──────────────┐    ┌─────────────┐    ┌─────▼─────┐  │
│  │   Actual     │◀───│ Server Stub │◀───│ Transport │  │
│  │   Methods    │    │ (Dispatcher)│    │   Layer   │  │
│  └──────────────┘    └─────────────┘    └───────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Components:**

| Component | Role |
|-----------|------|
| **Client Stub** | Local proxy that exposes remote methods as native functions |
| **Server Stub** | Dispatcher that receives requests and invokes actual implementation |
| **Transport** | TCP, HTTP or other protocol for transmission |
| **Serialisation** | JSON, XML, Protocol Buffers – encodes parameters and results |

### 1.3 RPC Call Flow

1. Client calls the method on the local stub
2. Stub **serialises** parameters in the specified format
3. Message is **transmitted** via network to server
4. Server stub **deserialises** the request
5. Actual method is **executed**
6. Result is **serialised** and sent back
7. Client stub **deserialises** and returns the result

---

## 2. JSON-RPC 2.0

### 2.1 Specification

JSON-RPC is a stateless, lightweight RPC protocol that uses JSON for serialisation.

**Characteristics:**
- Transport agnostic (HTTP, WebSocket, raw TCP)
- Supports single and batch requests
- ID for request-response correlation
- Notification (request without waiting for response)

### 2.2 Request Structure

```json
{
    "jsonrpc": "2.0",
    "method": "subtract",
    "params": [42, 23],
    "id": 1
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `jsonrpc` | Yes | Protocol version, always "2.0" |
| `method` | Yes | Name of method to call |
| `params` | No | Array or object with parameters |
| `id` | Conditional | Unique identifier; absent for notifications |

**Positional vs named parameters:**

```json
// Positional (array)
{"params": [42, 23]}

// Named (object)
{"params": {"minuend": 42, "subtrahend": 23}}
```

### 2.3 Response Structure

**Successs:**
```json
{
    "jsonrpc": "2.0",
    "result": 19,
    "id": 1
}
```

**Error:**
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32601,
        "message": "Method not found",
        "data": "subtract_numbers is not a valid method"
    },
    "id": 1
}
```

### 2.4 Standard Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Invalid request structure |
| -32601 | Method not found | Method does not exist |
| -32602 | Invalid params | Invalid parameters (type/number) |
| -32603 | Internal error | Server internal error |
| -32000 to -32099 | Server error | Application-specific errors |

### 2.5 Batch Requests

Send multiple requests in a single HTTP request:

```json
[
    {"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1},
    {"jsonrpc": "2.0", "method": "subtract", "params": [10, 5], "id": 2},
    {"jsonrpc": "2.0", "method": "multiply", "params": [3, 4], "id": 3}
]
```

Response (order may differ):
```json
[
    {"jsonrpc": "2.0", "result": 3, "id": 1},
    {"jsonrpc": "2.0", "result": 5, "id": 2},
    {"jsonrpc": "2.0", "result": 12, "id": 3}
]
```

**Batch advantages:**
- Reduces connection overhead (1 TCP handshake vs 3)
- Reduces total latency
- Efficient for multiple dependent operations

### 2.6 Notifications

Requests without `id` receive no response:

```json
{"jsonrpc": "2.0", "method": "log_event", "params": ["user_login", "alice"]}
```

Use cases: logging, metrics, fire-and-forget operations.

---

## 3. XML-RPC

### 3.1 Characteristics

The JSON-RPC precursor, using XML for serialisation.

- More verbose than JSON-RPC
- Good introspection support
- Still present in legacy systems (WordPress, many PHP systems)
- Exclusively HTTP POST transport

### 3.2 Request Structure

```xml
<?xml version="1.0"?>
<methodCall>
    <methodName>subtract</methodName>
    <params>
        <param><value><int>42</int></value></param>
        <param><value><int>23</int></value></param>
    </params>
</methodCall>
```

### 3.3 Response Structure

**Successs:**
```xml
<?xml version="1.0"?>
<methodResponse>
    <params>
        <param>
            <value><int>19</int></value>
        </param>
    </params>
</methodResponse>
```

**Error:**
```xml
<?xml version="1.0"?>
<methodResponse>
    <fault>
        <value>
            <struct>
                <member>
                    <n>faultCode</n>
                    <value><int>-32601</int></value>
                </member>
                <member>
                    <n>faultString</n>
                    <value><string>Method not found</string></value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse>
```

### 3.4 XML-RPC Data Types

| XML Tag | Type | Example |
|---------|------|---------|
| `<int>` or `<i4>` | Integer | `<int>42</int>` |
| `<double>` | Float | `<double>3.14</double>` |
| `<string>` | String | `<string>hello</string>` |
| `<boolean>` | Boolean | `<boolean>1</boolean>` |
| `<base64>` | Binary | `<base64>SGVsbG8=</base64>` |
| `<dateTime.iso8601>` | DateTime | `<dateTime.iso8601>20250115T10:30:00</dateTime.iso8601>` |
| `<array>` | Array | `<array><data>...</data></array>` |
| `<struct>` | Object/Map | `<struct><member>...</member></struct>` |

### 3.5 Introspection

XML-RPC defines standard methods for API discovery:

| Method | Returns |
|--------|---------|
| `system.listMethods` | Array with all available methods |
| `system.methodSignature` | Method signatures |
| `system.methodHelp` | Text documentation for method |

```xml
<methodCall>
    <methodName>system.listMethods</methodName>
    <params></params>
</methodCall>
```

---

## 4. gRPC with Protocol Buffers

### 4.1 Characteristics

gRPC (Google RPC) is the high-performance framework developed by Google.

| Aspect | Value |
|--------|-------|
| **Serialisation** | Protocol Buffers (binary) |
| **Transport** | HTTP/2 mandatory |
| **Streaming** | Unary, server, client, bidirectional |
| **Code generation** | Automatic from .proto files |
| **Performance** | 2-10x faster than JSON-RPC |

### 4.2 Protocol Buffers

Service definition in `.proto` file:

```protobuf
syntax = "proto3";

package calculator;

service Calculator {
    // Unary RPC
    rpc Subtract(SubtractRequest) returns (SubtractResponse);
    
    // Server streaming
    rpc GetPrimes(RangeRequest) returns (stream PrimeNumber);
    
    // Bidirectional streaming
    rpc Chat(stream Message) returns (stream Message);
}

message SubtractRequest {
    int32 minuend = 1;
    int32 subtrahend = 2;
}

message SubtractResponse {
    int32 result = 1;
}

message RangeRequest {
    int32 start = 1;
    int32 end = 2;
}

message PrimeNumber {
    int32 value = 1;
}

message Message {
    string content = 1;
    string sender = 2;
}
```

### 4.3 gRPC Call Types

| Type | Client | Server | Use case |
|------|--------|--------|----------|
| **Unary** | 1 request | 1 response | CRUD operations |
| **Server streaming** | 1 request | stream responses | Download file, list items |
| **Client streaming** | stream requests | 1 response | Upload file, aggregation |
| **Bidirectional** | stream | stream | Chat, real-time sync |

### 4.4 Protocol Buffers Advantages

- **Small size**: ~3-10x smaller than JSON
- **Parsing speed**: ~5-100x faster
- **Strict schema**: Compile-time errors
- **Evolution**: Backward compatibility with field numbers

### 4.5 Python Example (grpcio)

**Server:**
```python
import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    def Subtract(self, request, context):
        result = request.minuend - request.subtrahend
        return calculator_pb2.SubtractResponse(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

**Client:**
```python
import grpc
import calculator_pb2
import calculator_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = calculator_pb2_grpc.CalculatorStub(channel)

request = calculator_pb2.SubtractRequest(minuend=42, subtrahend=23)
response = stub.Subtract(request)
print(f"Result: {response.result}")  # Result: 19
```

---

## 5. JSON-RPC vs XML-RPC vs gRPC Comparison

| Aspect | JSON-RPC | XML-RPC | gRPC |
|--------|----------|---------|------|
| **Format** | JSON (text) | XML (text) | Protobuf (binary) |
| **Overhead** | ~50-100 bytes | ~200-500 bytes | ~20-50 bytes |
| **Transport** | HTTP/WS/TCP | HTTP POST | HTTP/2 |
| **Schema** | Optional | No | Mandatory (.proto) |
| **Streaming** | Not native | No | Yes, bidirectional |
| **Browser** | Yes | Yes | grpc-web (proxy) |
| **Debugging** | Easy (human-readable) | Easy | Requires tools |
| **Performance** | Environmentm | Low | High |
| **Typing** | Dynamic | Dynamic | Static |

### When to Use Each?

| Situation | Recommendation |
|-----------|----------------|
| Public API, simplicity | JSON-RPC |
| Legacy PHP/WordPress system | XML-RPC |
| Internal microservices | gRPC |
| Native browser client | JSON-RPC |
| Real-time bidirectional | gRPC streaming |
| Limited bandwidth | gRPC |
| Rapid prototyping | JSON-RPC |

---

## 6. Python Implementation

### 6.1 JSON-RPC Server

```python
"""
JSON-RPC 2.0 Server - Educational Implementation
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class JSONRPCHandler(BaseHTTPRequestHandler):
    methods = {}
    
    @classmethod
    def register(cls, name, func):
        cls.methods[name] = func
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self.send_error_response(-32700, "Parse error", None)
            return
        
        # Handle batch requests
        if isinstance(request, list):
            responses = [self.handle_single(req) for req in request]
            responses = [r for r in responses if r is not None]
            self.send_response_json(responses)
        else:
            response = self.handle_single(request)
            if response:
                self.send_response_json(response)
    
    def handle_single(self, request):
        # Validate request
        if not isinstance(request, dict):
            return self.make_error(-32600, "Invalid Request", None)
        
        if request.get('jsonrpc') != '2.0':
            return self.make_error(-32600, "Invalid Request", request.get('id'))
        
        method = request.get('method')
        if not method or not isinstance(method, str):
            return self.make_error(-32600, "Invalid Request", request.get('id'))
        
        # Check if notification (no id)
        is_notification = 'id' not in request
        req_id = request.get('id')
        
        # Find method
        if method not in self.methods:
            if is_notification:
                return None
            return self.make_error(-32601, "Method not found", req_id)
        
        # Execute
        params = request.get('params', [])
        try:
            if isinstance(params, list):
                result = self.methods[method](*params)
            else:
                result = self.methods[method](**params)
        except TypeError as e:
            if is_notification:
                return None
            return self.make_error(-32602, f"Invalid params: {e}", req_id)
        except Exception as e:
            if is_notification:
                return None
            return self.make_error(-32603, f"Internal error: {e}", req_id)
        
        if is_notification:
            return None
        
        return {"jsonrpc": "2.0", "result": result, "id": req_id}
    
    def make_error(self, code, message, req_id):
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": req_id
        }
    
    def send_response_json(self, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def send_error_response(self, code, message, req_id):
        self.send_response_json(self.make_error(code, message, req_id))

# Register methods
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return a / b if b != 0 else None

JSONRPCHandler.register('add', add)
JSONRPCHandler.register('subtract', subtract)
JSONRPCHandler.register('multiply', multiply)
JSONRPCHandler.register('divide', divide)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), JSONRPCHandler)
    print("JSON-RPC server running on http://localhost:8000")
    server.serve_forever()
```

### 6.2 JSON-RPC Client

```python
"""
JSON-RPC 2.0 Client - Educational Implementation
"""
import json
import urllib.request

class JSONRPCClient:
    def __init__(self, url):
        self.url = url
        self._id = 0
    
    def _next_id(self):
        self._id += 1
        return self._id
    
    def call(self, method, *args, **kwargs):
        """Make a single RPC call."""
        params = args if args else kwargs if kwargs else None
        
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id()
        }
        if params:
            request["params"] = params
        
        response = self._send(request)
        
        if "error" in response:
            raise Exception(f"RPC Error {response['error']['code']}: {response['error']['message']}")
        
        return response.get("result")
    
    def batch(self, calls):
        """
        Make multiple RPC calls in a single request.
        calls: list of (method, *args) or (method, **kwargs) tuples
        """
        requests = []
        for call in calls:
            method = call[0]
            params = call[1:] if len(call) > 1 else None
            
            req = {
                "jsonrpc": "2.0",
                "method": method,
                "id": self._next_id()
            }
            if params:
                req["params"] = list(params)
            requests.append(req)
        
        responses = self._send(requests)
        
        # Sort responses by id to match request order
        responses.sort(key=lambda r: r.get("id", 0))
        
        results = []
        for r in responses:
            if "error" in r:
                results.append(Exception(f"RPC Error: {r['error']['message']}"))
            else:
                results.append(r.get("result"))
        
        return results
    
    def notify(self, method, *args, **kwargs):
        """Send a notification (no response expected)."""
        params = args if args else kwargs if kwargs else None
        
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            request["params"] = params
        
        # Send without expecting response
        self._send(request, expect_response=False)
    
    def _send(self, data, expect_response=True):
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            if expect_response:
                return json.loads(response.read().decode('utf-8'))
            return None

# Usage example
if __name__ == '__main__':
    client = JSONRPCClient('http://localhost:8000')
    
    # Single calls
    print(f"add(2, 3) = {client.call('add', 2, 3)}")
    print(f"subtract(10, 4) = {client.call('subtract', 10, 4)}")
    
    # Batch call
    results = client.batch([
        ('add', 1, 2),
        ('multiply', 3, 4),
        ('divide', 10, 2)
    ])
    print(f"Batch results: {results}")
```

---

## 7. Traffic Analysis with Wireshark

### 7.1 Useful Filters

```wireshark
# All HTTP POST traffic (RPC calls)
http.request.method == "POST"

# JSON-RPC requests
http contains "jsonrpc"

# XML-RPC requests
http contains "methodCall"

# JSON-RPC error responses
http contains "error"

# Traffic on specific port
tcp.port == 8000
```

### 7.2 What to Observe

1. **Request headers**: Content-Type (application/json vs text/xml)
2. **Payload size**: Compare JSON vs XML for the same request
3. **Response time**: Latency per call
4. **Batch efficiency**: One batch request vs multiple single ones

---

## What We Learned

- **RPC** abstracts function calls over the network
- **JSON-RPC 2.0** is simple, lightweight, ideal for public APIs
- **XML-RPC** is more verbose but offers introspection
- **gRPC** offers maximum performance with Protocol Buffers
- **Batch requests** significantly reduce overhead
- Choice depends on context: simplicity vs performance vs compatibility

---

## How It Helps Us

| Situation | Technology |
|-----------|------------|
| Blockchain API | JSON-RPC |
| Internal microservices | gRPC |
| Legacy integration | XML-RPC |
| Real-time bidirectional | gRPC streaming |
| Browser-first API | JSON-RPC |
| Mobile app backend | gRPC (smaller payloads) |

---

## Bibliography

1. JSON-RPC 2.0 Specification – https://www.jsonrpc.org/specification
2. gRPC Documentation – https://grpc.io/docs/
3. Protocol Buffers Language Guide – https://protobuf.dev/
4. Birrell, A. D., & Nelson, B. J. (1984). Implementing remote procedure calls. ACM TOCS.

---

*Document generated for educational use | Revolvix&Hypotheticalandrei*
