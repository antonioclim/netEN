# Week 7 lab tasks — packet interception and filtering (Mininet)

## Scope and safety
All experiments must run inside the Mininet laboratory network created by this kit. Do not run scanning or filtering against external systems.

## 0) Setup
From the kit root:

```bash
chmod +x scripts/*.sh tests/*.sh
./scripts/setup.sh
```

## 1) Run the automated demo (recommended first)
```bash
./scripts/run_all.sh
./tests/smoke_test.sh
```

Inspect artefacts:
- `artifacts/demo.log`
- `artifacts/validation.txt`
- `artifacts/demo.pcap` (if tcpdump is available)

## 2) Start an interactive Mininet session (base topology)
This topology is good for quick debugging.

```bash
sudo mn --custom mininet/topologies/topo_week7_base.py --topo week7base --mac
```

Inside the Mininet CLI:
- `nodes`
- `h1 ping -c 2 h2`
- `h2 python3 python/apps/tcp_server.py --host 0.0.0.0 --port 9090`
- from another terminal: `sudo mnexec -a $(pgrep -f 'mininet:h1') python3 python/apps/tcp_client.py --host 10.0.7.100 --port 9090 --message hello`

Capture traffic (in a separate terminal):
```bash
sudo tcpdump -i any -nn tcp port 9090
```

Exit Mininet:
- `exit`

Clean:
```bash
sudo mn -c
```

## 3) Filtering topology with a router firewall
Start the topology with router host `fw`:

```bash
sudo mn --custom mininet/topologies/topo_week7_firewall.py --topo week7fw --mac
```

In Mininet CLI:
- `h1 ip route`
- `h2 ip route`
- `fw iptables -L -n -v`

Start servers on `h2`:
```bash
h2 python3 python/apps/tcp_server.py --host 0.0.0.0 --port 9090
h2 python3 python/apps/udp_receiver.py --host 0.0.0.0 --port 9091 --count 999
```

From `h1`, test clients:
```bash
h1 python3 python/apps/tcp_client.py --host 10.0.7.200 --port 9090 --message hello
h1 python3 python/apps/udp_sender.py --host 10.0.7.200 --port 9091 --message hello --count 1
```

## 4) Apply filtering profiles on the router
On `fw`:
```bash
fw python3 python/apps/firewallctl.py --profile baseline
fw python3 python/apps/firewallctl.py --profile block_tcp_9090
fw python3 python/apps/firewallctl.py --profile block_udp_9091
```

Use `h1` to probe ports defensively:
```bash
h1 python3 python/apps/port_probe.py --host 10.0.7.200 --ports 22,80,9090
```

## 5) Evidence with pcaps
Capture on `fw`:
```bash
fw tcpdump -i any -nn -U -w /tmp/week7_fw.pcap tcp or udp
```

Stop capture with Ctrl+C then copy the pcap from the host filesystem if needed.

## 6) Student deliverable
Create a new profile in `configs/firewall_profiles.json` that blocks one traffic class while keeping the rest functional. Provide:
- the updated json file
- a short note with commands you ran and what you observed
- the pcap evidence and a few tshark lines that support your conclusion

## 7) Success criteria
- your profile is reproducible
- your evidence is clear (pcap and logs)
- your explanation uses packet fields rather than speculation
