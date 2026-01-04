# Week 10: HTTP, HTTPS, REST, SOAP and Network Services (DNS, SSH and FTP)

## Computer Networks | ASE Bucharest | 2025–2026

This kit is designed for a Linux CLI-only minimal VM. It provides a reproducible demonstration of common application-layer protocols and three classic services, packaged with Docker Compose and optional Mininet scenarios.


---


## 🚀 Quick Clone & Setup

To clone **only this week's content** directly into `~/WEEK10` and make all scripts executable, run the following commands:

### Option A: One-liner (recommended)

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK10 && cd WEEK10 && git sparse-checkout set WEEK10 && shopt -s dotglob && mv WEEK10/* . && rmdir WEEK10 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Option B: Step-by-step (for understanding)

```bash
# 1. Navigate to home directory
cd ~

# 2. Clone repository with sparse checkout (downloads only metadata initially)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK10

# 3. Enter the cloned directory
cd WEEK10

# 4. Configure sparse checkout to fetch only WEEK10
git sparse-checkout set WEEK10

# 5. Move contents up one level (flatten structure)
shopt -s dotglob
mv WEEK10/* .
rmdir WEEK10

# 6. Make all shell scripts and Python files executable
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verify the setup
ls -la
ls -la scripts/
```

### Option C: Without Git history (lightweight)

If you don't need Git history and want the smallest possible download:

```bash
cd ~ && mkdir -p WEEK10 && cd WEEK10 && curl -L https://github.com/antonioclim/netEN/archive/refs/heads/main.tar.gz | tar -xz --strip-components=2 netEN-main/WEEK10 && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Verify Installation

After cloning, verify that scripts are executable:

```bash
cd ~/WEEK10
ls -la scripts/*.sh      # Should show 'x' permission
file scripts/*.sh        # Should show "shell script"
./scripts/setup.sh --help 2>/dev/null || head -5 scripts/setup.sh
```

---

## Quickstart

1. Unzip the archive and change into the week folder:

   ```bash
   cd WEEK10
   ```

2. Verify prerequisites:

   ```bash
   make check
   ```

3. Create the Python environment and install dependencies:

   ```bash
   make setup
   ```

4. Run the end-to-end demo (writes logs into `artifacts/`):

   ```bash
   make demo
   ```

5. Validate the outputs:

   ```bash
   make smoke-test
   ```

## Verification

After `make demo`, you should have at least:

- `artifacts/demo.log` containing lines for DNS, SSH and FTP checks
- `artifacts/validation.txt` summarising passed validations
- `artifacts/demo.pcap` if packet capture is enabled by the demo

Run:

```bash
./tests/smoke_test.sh
```

and confirm it exits with code `0`.

## Reset to zero

```bash
make clean
./scripts/cleanup.sh
```

If you used Mininet, the cleanup script also runs `mn -c`.

## Troubleshooting

1. **Docker is missing**: install Docker Engine and the Compose plugin, then re-run `make check`.
2. **Permission denied when running scripts**: run `chmod +x scripts/*.sh tests/*.sh` then retry.
3. **Ports already in use**: stop conflicting services or adjust ports in `docker/docker-compose.yml`.
4. **DNS queries fail**: check that the DNS container is up and that UDP port 53 is reachable from your host.
5. **SSH authentication fails**: confirm the provided test user and keys match the configuration in `docker/ssh-server/`.
6. **FTP login fails**: check the FTP server logs via `make docker-logs` and confirm passive ports are not blocked.
7. **Mininet errors**: ensure Mininet is installed, run `sudo mn -c` and re-run `make mininet-test`.
8. **No artefacts created**: check `artifacts/` permissions and confirm you ran the demo from the `WEEK10/` directory.

## Student deliverable and success criteria

Deliver `artifacts/demo.log` and `artifacts/validation.txt`. You are successful if:

- the smoke test passes
- you can explain the difference between HTTP and HTTPS at the TLS layer
- you can justify REST method semantics (safe, idempotent and cacheable)
- you can demonstrate a DNS query, an SSH session and an FTP transfer using the provided services

## Licence and attribution

Materials created for the Computer Networks course, ASE Bucharest.

© 2025 Computer Networks teaching team
