# WEEK 9 — Application-layer framing and a Pseudo-FTP protocol

This week focuses on *application-layer* protocol design, with an emphasis on **framing**, **endianness**, **integrity checks** and a minimal **file transfer protocol** (Pseudo-FTP) that uses a control channel and a separate data channel.

The kit is designed to be runnable in three ways:

- **Single-command automated demo** (recommended): runs all exercises, launches a Pseudo-FTP server and client, optionally captures traffic and produces validation artefacts.
- **Manual multi-terminal demo**: you start the server in one terminal and drive clients from another terminal, optionally with packet capture in a third terminal.
- **Docker and Mininet scenarios**: multi-client concurrency and topology experiments.

---

## Learning outcomes

By the end of WEEK 9 you should be able to:

1. Explain why a TCP byte stream still needs **application-layer framing**.
2. Distinguish **big-endian** and **little-endian** representations and justify using **network byte order** for on-the-wire formats.
3. Implement and reason about a **length-prefixed** binary protocol with integrity validation (CRC32 and optional SHA-256).
4. Describe and demonstrate the difference between **passive** and **active** data connections in FTP-style designs.
5. Capture and inspect traffic to validate protocol behaviour and message boundaries.

---

## Repository layout

- `python/exercises/`
  - `ex_9_01_endianness.py` — endianness and message framing exercise and self-test
  - `ex_9_02_pseudo_ftp.py` — Pseudo-FTP server and client (control + data channels)
- `python/utils/net_utils.py` — shared framing utilities (header format, CRC32, gzip flag, optional SHA-256)
- `scripts/`
  - `setup.sh` — prepares folders and demo files
  - `run_demo.sh` — guided interactive demo
  - `run_all.sh` — automated full run that generates validation artefacts
  - `capture_traffic.sh` — tcpdump helper
- `tests/`
  - `verify.sh` — environment checks
  - `smoke_test.sh` — validates that the automated run produced expected outputs
- `docs/lab.md` — laboratory worksheet

---

## Requirements

Minimum:

- Linux (recommended for the full experience)
- `python3` (3.10+ recommended)
- GNU `make`

Optional but strongly recommended:

- `tcpdump` and Wireshark (or `tshark`) for capture and inspection
- Docker and Docker Compose for the containerised scenario
- Mininet for topology experiments (requires `sudo`)

---

## Quick start

From the WEEK9 directory:

```bash
make setup
make verify
```

Notes:

- If you run `make` from a different directory, use `-C`:

  ```bash
  make -C ~/WEEK9 setup
  ```

- Scripts are invoked via `bash` from the Makefile, so executable bits are not required.

---

## One-command automated demo

This is the fastest way to validate the whole week.

```bash
make run-all
```

What it does:

- prepares demo folders and server-side files
- runs the endianness and framing self-test
- starts a Pseudo-FTP server and runs client actions (LIST, GET, gzip GET)
- optionally captures traffic (if `tcpdump` is available)
- writes results to:

  - `artifacts/demo.log`
  - `artifacts/validation.txt`
  - `artifacts/demo.pcap` (empty placeholder if capture tools are unavailable)

Port used:

- the automated demo *prefers* port **5900** (chosen to be distinct from the manual default)
- if the port is busy, it automatically tries `5901`, `5902` and so on

To force a specific port:

```bash
PORT=5905 make run-all
```

To validate after the run:

```bash
make smoke-test
```

---

## Manual multi-terminal demo

This section matches typical laboratory workflow and is the most useful for understanding the protocol.

### Terminal 1 — start the server

Default port for the manual workflow is **3333**.

```bash
make server
```

If port `3333` is busy:

```bash
make PORT=3335 server
```

Stop the server with `Ctrl+C`.

### Terminal 2 — list server files

```bash
make client-list
```

You should see a directory listing sourced from `server-files/`.

### Terminal 2 — download a file (passive mode)

```bash
make client-get FILE=hello.txt
```

The file should appear under `client-files/hello.txt`.

### Terminal 2 — download a file (active mode)

```bash
make client-get-active FILE=hello.txt
```

In **active** mode the client opens a listening socket and the server connects back to the client for the data transfer.

### Manual gzip transfer

The client supports `--gzip` for data payload compression. Example (passive mode):

```bash
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
  --host 127.0.0.1 --port 3333 \
  --user test --password 12345 \
  --gzip get utf8_test.txt
```

---

## Packet capture and inspection

### Option A — capture via Makefile (recommended)

Start capture in a separate terminal:

```bash
make capture
```

This uses `tcpdump` and will prompt for `sudo`. The capture is stored under `pcap/`.

While capture is running, perform one or more client actions (LIST, GET, active GET).

Stop capture with `Ctrl+C`.

Open the `.pcap` in Wireshark and inspect:

- one TCP connection for the **control channel** (server port 3333 in the manual workflow)
- one TCP connection for the **data channel** (passive port range or client-chosen port in active mode)
- the framed payload header (see `python/utils/net_utils.py`)

### Option B — use the automated artefact

After `make run-all`, open:

- `artifacts/demo.pcap`

---

## Docker scenario

If you have Docker and Compose installed:

```bash
make docker-build
make docker-up
make docker-test
make docker-down
```

This spins up services under `docker/` and runs a multi-client workload.

---

## Mininet scenario

Mininet requires `sudo` and is useful for topology experiments and concurrency.

```bash
make mininet-base
make mininet-test
make mininet-graph
```

---

## Troubleshooting

### “No rule to make target …”

You are not in the WEEK9 directory. Use:

```bash
cd ~/WEEK9
make client-list
```

or:

```bash
make -C ~/WEEK9 client-list
```

### “Address already in use”

A different process is already listening on the selected port.

- For the manual workflow, override `PORT`, for example `make PORT=3335 server`
- For the automated workflow, either set `PORT=5905 make run-all` or let the script auto-select

### Permission errors when capturing traffic

Packet capture usually requires `sudo`. Use `make capture` and enter your password when prompted.

---

## Further reading

- Stevens et al. (2003). *UNIX Network Programming, Volume 1: The Sockets Networking API* (3rd ed.). Addison-Wesley.
- Postel (1981). *Transmission Control Protocol*. RFC 793.
- Postel and Reynolds (1985). *File Transfer Protocol*. RFC 959.
