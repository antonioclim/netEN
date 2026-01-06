# Sample PCAP files – Week 10

This folder describes packet captures used to analyse DNS, SSH and FTP behaviour.

Binary PCAPs may be omitted from some Git workflows. This kit therefore includes scripts that can generate captures in a reproducible way.

## Generate captures

Run the end-to-end demo:

```bash
./scripts/run_all.sh
```

If capture is enabled, the demo writes:

- `artifacts/demo.pcap`

You can also run the capture helper directly:

```bash
./scripts/capture.sh
```

## Inspect

Examples:

```bash
tshark -r artifacts/demo.pcap -q
tcpdump -nn -r artifacts/demo.pcap | head
```
