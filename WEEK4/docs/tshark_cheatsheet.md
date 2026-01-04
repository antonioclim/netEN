# tshark cheatsheet (filters and quick inspection)

`tshark` is the CLI version of Wireshark.
It is optional in this kit.

Read a capture file:

- `tshark -r artifacts/demo.pcap`

Filter by port:

- `tshark -r artifacts/demo.pcap -Y "tcp.port == 5400"`
- `tshark -r artifacts/demo.pcap -Y "udp.port == 5402"`

Show a summary of conversations:

- `tshark -r artifacts/demo.pcap -q -z conv,tcp`
