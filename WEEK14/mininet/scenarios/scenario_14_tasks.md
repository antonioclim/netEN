# Week 14 Scenario Tasks

This scenario sheet complements the README and `docs/lab.md`.

## Topology recap
Nodes (10.0.14.0/24):
- `lb`   — 10.0.14.1    load balancer / reverse proxy
- `cli`  — 10.0.14.11   client
- `app1` — 10.0.14.100  backend A
- `app2` — 10.0.14.101  backend B

Switches:
- `s1`, `s2` run Open vSwitch in `failMode=standalone` so no external controller is required.

## Task 0: setup and verification
From the kit root:

```bash
cd ./WEEK14
make setup
make verify
```

Expected outcome:
- `make verify` reports the required tools as installed
- the smoke test passes

## Task 1: baseline connectivity
Start the topology:

```bash
sudo python3 mininet/topologies/topo_14_recap.py --cli
```

Inside the Mininet CLI:

```text
mininet> net
mininet> cli ping -c 2 lb
mininet> cli ping -c 2 app1
mininet> cli ping -c 2 app2
```

Expected outcome:
- all pings succeed

## Task 2: load balancer with round robin
In the Mininet CLI:

1) Start both backends:

```text
mininet> app1 python3 python/apps/backend_server.py --id app1 --host 10.0.14.100 --port 8080 &
mininet> app2 python3 python/apps/backend_server.py --id app2 --host 10.0.14.101 --port 8080 &
```

2) Start the load balancer:

```text
mininet> lb python3 python/apps/lb_proxy.py --listen-host 10.0.14.1 --listen-port 8080 \
            --backends 10.0.14.100:8080 10.0.14.101:8080 --algorithm roundrobin &
```

3) Send requests and observe alternation:

```text
mininet> cli sh -c 'for i in $(seq 1 10); do curl -s -D - http://10.0.14.1:8080/ -o /dev/null | grep -i x-backend; done'
```

Expected outcome:
- the `X-Backend:` value alternates between `10.0.14.100:8080` and `10.0.14.101:8080`

## Task 3: failure injection
While the proxy is running, stop one backend:

```text
mininet> app1 pkill -f backend_server.py
```

Repeat the request loop.

Expected outcome:
- some requests fail or return an error depending on retry behaviour
- requests that go to the remaining backend continue to succeed

Re-start `app1` and confirm recovery.

## Task 4: packet capture and analysis
Start a capture on the load balancer:

```text
mininet> lb tcpdump -ni lb-eth0 -w /tmp/scenario14.pcap &
```

Generate traffic:

```text
mininet> cli sh -c 'for i in $(seq 1 6); do curl -s http://10.0.14.1:8080/ >/dev/null; done'
```

Stop the capture:

```text
mininet> lb pkill -INT tcpdump
```

Analyse:

```text
mininet> lb tshark -r /tmp/scenario14.pcap -q -z conv,tcp
mininet> lb tshark -r /tmp/scenario14.pcap -Y http.request -T fields -e ip.src -e ip.dst -e http.host -e http.request.uri | head
```

Expected outcome:
- TCP conversations exist for `cli↔lb` and `lb↔app1/app2`
- HTTP requests are visible in the capture

## Deliverables
Submit:
1. A short note describing the observed alternation and how you validated it.
2. One capture file (`scenario14.pcap`) or a screenshot of the `tshark -z conv,tcp` output.
3. A short troubleshooting note for one induced failure (Task 3).

