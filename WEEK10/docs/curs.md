# Lecture 10 – Application layer protocols and semantics

This lecture focuses on how application protocols behave over TCP and TLS and how protocol semantics affect reliability, security and observability.

## Topics

- HTTP over TCP and HTTPS over TLS
- Method semantics: safe, idempotent and cacheable
- Status codes and edge cases (401 vs 403, 404 vs 405)
- REST as an architectural style and the Richardson maturity model
- SOAP and when it still matters
- When HTTP is not enough: WebSocket and long-lived connections

## Suggested demonstrations

- Capture an HTTP exchange and compare it to HTTPS using `tcpdump` or `tshark`
- Show how headers affect caching and intermediaries
- Discuss how REST constraints support evolvability and operational simplicity
