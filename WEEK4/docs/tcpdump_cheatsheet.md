# tcpdump cheatsheet (loopback and ports)

Packet capture may require elevated permissions.
If capture fails, use `--quick` and continue with the rest of the demo.

## Common patterns

Capture TCP ports used in Week 4:

- `tcpdump -i lo -w artifacts/demo.pcap "port 5400 or port 5401 or port 5402"`

Readable console output:

- `tcpdump -i lo -n "port 5400 or port 5401 or port 5402"`

Limit number of packets:

- `tcpdump -i lo -c 50 -n "port 5400"`

## Tips

- Use `-n` to avoid DNS lookups
- Use quotes around the filter expression
- Stop capture with `Ctrl+C`
