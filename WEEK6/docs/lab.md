# Week 6 Lab Tasks

Complete the tasks using the provided scripts and Mininet topologies.

## 1. Baseline demo

Run:

```bash
make demo
```

Inspect:

- `artifacts/demo.log`
- `artifacts/validation.txt`

Write down:

- which topology was used
- which IP plan was applied
- which ports were used for demo services

## 2. NAT and PAT

Run the NAT demo script (host-run):

```bash
./scripts/run_nat_demo.sh
```

Explain, in 5 to 10 lines:

- what is translated (source IP, source port)
- where you expect to see translations in logs or captures

## 3. ARP and DHCP signals

Using `tcpdump` or `tshark` on the correct interface, capture the relevant frames:

```bash
sudo tcpdump -n -e -i any arp or port 67 or port 68
```

Report:

- one ARP request and response pair
- DHCP traffic if present in the scenario

## 4. SDN policy

Run:

```bash
./scripts/run_sdn_demo.sh
```

Identify:

- which controller script is used
- one policy decision that changes forwarding behaviour

## 5. Clean up

Run:

```bash
./scripts/cleanup.sh
```

Confirm that Mininet state was cleared and that rerunning the demo starts from a clean baseline.
