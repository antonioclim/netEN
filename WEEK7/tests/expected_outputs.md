# Expected outputs – Week 6

This document provides examples of outputs you should see when the demos and tests run correctly. Exact values may differ (timestamps, PIDs, ephemeral ports), but the structure and key messages should match.

## NAT demo

### Start the topology

```bash
make nat-demo
```

You should see Mininet initialisation lines (creating network, adding hosts and switches) followed by NAT configuration steps.

### NAT observer – server side

Typical server messages:

```
=== NAT Observer Server ===
Listening on 0.0.0.0:8080
[CONN] Client from 192.168.1.1:45231
[CONN] Client from 192.168.1.1:45232
[CONN] Client from 192.168.1.1:45233
---
Observation: the same source IP (NAT) with different source ports (PAT).
```

### NAT observer – client side

Typical client messages:

```
Connected to 10.0.6.100:8080
Sent: hello-1
Received: ok
```

## SDN demo

### Start controller and topology

```bash
make sdn-demo
```

You should see:

- controller start confirmation
- switch connection messages
- successful connectivity checks (`ping` or an equivalent check)

### Flow inspection

If Open vSwitch is available:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

You should see at least one flow entry installed by the controller.
