# Course notes – Week 6

## NAT and PAT (NAT overload)

NAT maps one address space to another. In practice it is commonly used to allow multiple private hosts to share a smaller set of public addresses. PAT extends this by also translating transport ports, allowing many internal connections to share a single external address.

Key implications:

- NAT breaks end-to-end addressing and can complicate protocols that embed IP addresses in payloads
- NAT devices must track connection state for translations to remain consistent
- Troubleshooting typically relies on routing inspection, NAT table inspection and packet capture

## SDN overview

Software-Defined Networking separates:

- **Control plane:** decides what forwarding rules should exist
- **Data plane:** forwards packets according to installed rules

This separation enables centralised policy, rapid reconfiguration and stronger observability.
