# Week 7 (Networking) — Packet capture, filtering and defensive port probing

This week is about observing real traffic on the wire (TCP and UDP), making filtering decisions explicit and reproducible and turning those decisions into working rules. The focus is a controlled laboratory environment (Mininet in a minimal Linux VM). Any scanning or filtering is strictly for the local lab network created by this kit.


---

## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK7` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK7 && cd WEEK7 && git sparse-checkout set WEEK7 && shopt -s dotglob && mv WEEK7/* . && rmdir WEEK7 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK7

# 3. Enter the cloned directory
cd WEEK7

# 4. Configure sparse checkout to fetch only WEEK7
git sparse-checkout set WEEK7

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK7/* .
rmdir WEEK7

# 6. Make all shell scripts and Python files executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verify the setup
ls -la
ls -la scripts/
```

### Option C: Without Git sparse-checkout (full clone, then copy)

If sparse checkout causes issues, use this alternative:

```bash
cd ~ && git clone --depth 1 https://github.com/antonioclim/netEN.git netEN-temp && mv netEN-temp/WEEK7 ~/WEEK7 && rm -rf netEN-temp && cd ~/WEEK7 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK7
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---
## What you will do
By the end of this week you will be able to:
- capture and inspect TCP and UDP traffic using `tcpdump` and `tshark`
- explain what you see in captures using concrete packet fields (addresses, ports, flags, payload boundaries)
- apply filtering rules (allow or block) and verify their effect with repeatable tests
- generate a small, structured report: evidence (pcap and logs), observations and conclusions

## Quickstart (CLI)
From the kit root directory:

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/run_all.sh
./tests/smoke_test.sh
./scripts/cleanup.sh
```

If you prefer `make`:

```bash
make setup
make demo
make test
make clean
```

Outputs are written to `artifacts/`:
- `artifacts/demo.log`
- `artifacts/demo.pcap` (if `tcpdump` is available)
- `artifacts/validation.txt`
- optional: `artifacts/tshark_summary.txt`

## Requirements
Target VM: Ubuntu or Debian (CLI only), running in VirtualBox with modest resources.

Minimum software:
- Python 3.10+ and `pip`
- Mininet and Open vSwitch (for the Mininet demo)
- `iptables` (or compatible alternative) for filtering demonstrations
- `tcpdump` and `tshark` for traffic capture and analysis

The setup script installs the typical packages on Debian or Ubuntu. If you use a different distribution, install the equivalents manually.

## Student deliverable (60–90 minutes)
1) Run the demo and keep `artifacts/demo.pcap` and `artifacts/demo.log`.
2) Create a new firewall profile that blocks either:
   - TCP port 9090 only from one source host or
   - UDP port 9091 while keeping ICMP working
3) Provide a short note (half a page) describing:
   - which rules you applied
   - how you verified the effect (commands and evidence)
   - one pitfall you hit and how you fixed it

## Troubleshooting (common issues)
1) **Mininet fails with OVS errors**: run `sudo service openvswitch-switch restart` then `sudo mn -c`.
2) **`tshark` cannot capture as non-root**: run the demo with `sudo` or allow capture for the `wireshark` group.
3) **No `demo.pcap` produced**: check that `tcpdump` is installed and available in PATH.
4) **Firewall rules do not seem to apply**: confirm you applied them on the router host (`fw`) and that routing is in place.
5) **TCP client hangs**: use `--timeout` on the client and use `REJECT` instead of `DROP` while debugging.
6) **UDP receiver shows nothing**: confirm the receiver is started first and check the destination IP and port.
7) **`Permission denied` on scripts**: run `chmod +x scripts/*.sh tests/*.sh`.
8) **Leftover namespaces or processes**: run `./scripts/cleanup.sh` then `sudo mn -c`.

## Ethics and scope
Use this kit only in the provided lab environment. Do not run port probing or filtering experiments against systems you do not own or have explicit permission to test.
