# WEEK 6 Starter Kit — Computer Networks

## NAT/PAT and SDN (Software-Defined Networking)

**Course:** Computer Networks  
**Programme:** Business Informatics (ASE-CSIE)  
**Week:** 6  
**Academic year:** 2025–2026

---

## Scope

This kit supports the Week 6 laboratory work on:

- NAT and PAT (including basic conntrack inspection)
- SDN concepts using Mininet and Open vSwitch
- Traffic observation with tcpdump and Wireshark/TShark

Everything is designed to run on a minimal Ubuntu VM in a CLI-only workflow.

All scripts, comments and runtime messages are in British English and avoid a comma before **and** in prose.

---

## Repository layout

Key paths:

- `scripts/setup.sh` — environment checks and one-time preparation
- `scripts/run_all.sh` — automated SDN and NAT demo pipeline that writes artefacts
- `mininet/topologies/topo_sdn.py` — SDN topology and smoke test
- `mininet/topologies/topo_nat.py` — NAT topology and smoke test
- `seminar/python/controllers/sdn_policy_controller.py` — OS-Ken controller app
- `artifacts/` — generated output (logs, validation summary, capture placeholder)

---

## Quick clone (sparse checkout)

If you want to clone only Week 6 from the repository and place it in `~/WEEK6`, use:

```bash
cd ~

git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK6
cd WEEK6
git sparse-checkout set WEEK6

shopt -s dotglob
mv WEEK6/* .
rmdir WEEK6

find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

You should now be in `~/WEEK6`.

---

## System prerequisites (Ubuntu 24.04)

The kit expects:

- Python 3.12+
- Mininet
- Open vSwitch
- tcpdump and tshark
- iptables and conntrack

If you prefer manual installation:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  mininet openvswitch-switch \
  iproute2 iputils-ping traceroute \
  tcpdump tshark iptables conntrack \
  netcat-openbsd arping bridge-utils
```

Python modules:

```bash
pip3 install --break-system-packages os-ken scapy
```

---

## Recommended workflow

### 1) Setup and verification

From the kit folder:

```bash
cd ./WEEK6
make setup
make check
```

`make setup` runs `scripts/setup.sh`. It prepares folders and performs a final verification. The script is designed to complete successfully even if some optional components are missing, while still reporting the status clearly.

`make check` performs a non-destructive check of tools and Python imports.

### 2) Automated demo pipeline

Run the full pipeline (recommended):

```bash
sudo make run-all
```

This:

1. Cleans any previous Mininet and OVS state
2. Attempts to start the OS-Ken controller on `127.0.0.1:6633`
3. Runs SDN smoke test
4. Runs NAT smoke test
5. Generates an artefact set in `artifacts/`
6. Performs final cleanup

Generated artefacts:

- `artifacts/demo.log` — complete run log
- `artifacts/controller.log` — controller preflight and controller output
- `artifacts/validation.txt` — concise validation summary
- `artifacts/demo.pcap` — capture placeholder (created deterministically)

### 3) Standalone demos

SDN demo:

```bash
sudo make sdn-demo
```

NAT demo:

```bash
sudo make nat-demo
```

Important: `nat-demo` and `sdn-demo` may enter the **Mininet CLI** (`mininet>`). Inside Mininet you cannot run `make ...` targets because that is not a shell. To exit Mininet and return to your terminal, type:

```
exit
```

---

## Cleaning and reset

Safe cleanup:

```bash
make clean
```

If sudo credentials are not cached, the kit prints a warning and performs a best-effort cleanup. For a full cleanup without prompts, run:

```bash
sudo -v
make clean
```

Complete reset:

```bash
make reset
```

---

## Troubleshooting

### `make check` shows OS-Ken missing but Python import works

The check uses Python imports rather than relying on `~/.local/bin` being in `PATH`. If you see:

- `os_ken (Python)` is available
- but the OS-Ken line is missing

then the Makefile in your local copy is outdated. Update the kit and re-run `make check`.

### OS-Ken controller does not start (`SDN_FLOWS_INSTALLED: NO`)

The automated run writes controller diagnostics to:

- `artifacts/controller.log`

Inspect it first:

```bash
sed -n '1,160p' artifacts/controller.log
tail -n 60 artifacts/controller.log
```

Common causes:

- OS-Ken not importable in the Python used under sudo
- port 6633 already in use
- controller app path not found or not executable

### `make clean` or demo targets stop with `Terminated`

This is usually caused by an interrupted sudo prompt or a non-interactive environment. Run:

```bash
sudo -v
make clean
```

and then re-run the demo.

---

## Academic integrity and reproducibility

This kit is intended for educational use within the ASE-CSIE Computer Networks course. If you modify the kit, keep changes traceable and ensure outputs remain reproducible in a minimal VM.



## SDN lab details

### Topology

The SDN topology (`mininet/topologies/topo_sdn.py`) uses:

- hosts: `h1` (10.0.6.11), `h2` (10.0.6.12), `h3` (10.0.6.13)
- switch: `s1` (Open vSwitch)
- controller: OS-Ken on `127.0.0.1:6633`

The smoke test (`--test`) checks two behaviours:

1. `h1 → h2` is permitted  
2. `h1 → h3` is expected to be blocked by policy

If the controller is not running, behaviour may depend on the OVS fail mode and may not match the intended policy. In that situation the kit still reports the ping outcomes and records that flows were not installed.

### Controller policy

The controller app is:

- `seminar/python/controllers/sdn_policy_controller.py`

It installs OpenFlow rules that implement a simple policy set:

- permit ICMP between `h1` and `h2`
- drop traffic towards `h3` (ICMP and TCP by default)
- optionally allow some UDP traffic depending on controller configuration

You can inspect flows at any time (in a separate terminal, outside Mininet):

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

A healthy run typically shows one or more rules with `actions=` and non-zero packet counters after traffic is generated.

### Expected SDN validation

After `sudo make run-all` you should see in `artifacts/validation.txt`:

```
SDN_TEST: PASS
SDN_FLOWS_INSTALLED: YES
```

If `SDN_FLOWS_INSTALLED` is `NO`, open `artifacts/controller.log` and verify:

- `os_ken: import OK`
- the controller is listening on 6633
- there is no traceback from the controller app

---

## NAT/PAT lab details

### Topology

The NAT topology (`mininet/topologies/topo_nat.py`) uses:

- internal hosts: `h1` (192.168.1.10), `h2` (192.168.1.20)
- NAT router: `rnat` (acts as gateway and performs masquerading)
- external host: `h3` (203.0.113.2)
- switches: `s1`, `s2`

The intended observation is that packets from 192.168.1.0/24 are translated at `rnat` before reaching `h3`.

### Suggested interactive observations

When you run:

```bash
sudo make nat-demo
```

you may enter the Mininet CLI. Typical commands:

```text
mininet> h1 ping -c 2 203.0.113.2
mininet> h2 ping -c 2 203.0.113.2
mininet> rnat iptables -t nat -L -n -v
mininet> h3 tcpdump -ni h3-eth0 icmp
```

If you open a second terminal and run `conntrack -L` on the host (outside Mininet), you can correlate NAT state with observed flows.

### Expected NAT validation

After `sudo make run-all` you should see:

```
NAT_TEST: PASS
```

If NAT fails, open `artifacts/demo.log` and search for:

- `iptables -t nat` rules being applied
- IP forwarding state
- route configuration on `h1` and `h2`

---

## Artefacts and logs

### `artifacts/demo.log`

This is the primary execution log. It contains:

- timestamps
- cleanup actions
- controller start attempts
- SDN and NAT smoke test output
- final summary lines

### `artifacts/controller.log`

This file is created on every run. It contains:

- a controller preflight block (Python executable, version, sys.path and import status)
- OS-Ken manager output or traceback if startup fails

If you report a controller-related issue, include the first 120 lines and the last 60 lines of this file.

### `artifacts/validation.txt`

This is a concise result summary intended for automated checking and marking.

---

## Common mistakes

- running `make ...` commands inside the Mininet CLI (`mininet>`)  
  Mininet is not a shell, so Make targets will be unknown there. Exit Mininet first.

- running demo targets without cached sudo credentials  
  If you see `Terminated` during cleanup, run `sudo -v` then re-run.

- installing OS-Ken under a different Python than the one used via sudo  
  Use `pip3` for the same Python version, or install to system site-packages if required.

---

## Optional extension tasks

These are suitable for higher marks or project extensions:

1. Modify the controller policy so that UDP to `h3` is permitted only from `h2`.
2. Add a flow counter check to the SDN smoke test and fail if counters remain zero.
3. Extend NAT topology to include a second external subnet and compare behaviour.
4. Capture and annotate a PCAP showing the pre-NAT and post-NAT addressing.



## Marking and evidence (suggested)

When preparing evidence for assessment, include:

- the exact command transcript used to run the demo, including `sudo make run-all`
- `artifacts/validation.txt`
- a short interpretation of what the validation flags mean
- at least one flow table dump:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1 > artifacts/flows_s1.txt
```

and at least one NAT table dump:

```bash
sudo iptables -t nat -L -n -v > artifacts/iptables_nat.txt
```

A minimal evidence set typically contains:

- `validation.txt`
- `demo.log`
- `controller.log` (even if the controller fails)
- `flows_s1.txt`
- `iptables_nat.txt`

---

## FAQ

### Why does `make setup` not install everything automatically?

The kit supports minimal VMs and aims to keep the installation explicit and reproducible. `make setup` verifies what is present, prepares directories and enables required kernel settings. Package installation is available but can be time-consuming in classroom environments.

### Why does the SDN smoke test sometimes pass without a controller?

Open vSwitch behaviour without a reachable controller depends on configuration and may allow limited connectivity in some circumstances. The validation file reports this explicitly via `SDN_FLOWS_INSTALLED`. The intended SDN learning outcome requires a running controller and installed flows.

### Which port should the controller use?

This kit uses OpenFlow TCP port **6633** by default for compatibility with typical Mininet examples. You can change it by running:

```bash
sudo python3 mininet/topologies/topo_sdn.py --test --controller-port 6634
```

and starting the controller on the same port.

---

## Licence and usage

This starter kit is intended for educational use within the ASE-CSIE Computer Networks course. If you redistribute or adapt it, keep attribution, preserve documentation integrity and do not remove safety notes from cleanup and controller management steps.


---

## Appendix: example outputs

### Example `make check`

A typical environment should report all core tools as available:

```
Verifying required tools:

  ✓ python3
  ✓ mininet (mn)
  ✓ openvswitch
  ✓ tcpdump
  ✓ tshark
  ✓ iptables
  ✓ os-ken (Python)
  ✓ os_ken (Python)
  ✓ scapy (Python)
```

### Example `validation.txt`

```
SDN_TEST: PASS
SDN_FLOWS_INSTALLED: YES
NAT_TEST: PASS
PCAP_GENERATED: YES
```

If your `controller.log` is empty or missing, treat that as a kit integrity issue. This kit version creates it deterministically and logs controller preflight information on every run.
