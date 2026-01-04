# Week 7 extra exercises (optional)

These exercises are designed to deepen understanding while keeping the kit reproducible.

## Exercise 1: source based policy
Extend `configs/firewall_profiles.json` with a profile that blocks TCP port 9090 only if the source is `h1`.
Hint: use `-s 10.0.7.11` in iptables rules and keep rule order explicit.

## Exercise 2: fail fast vs fail slow
Change `block_tcp_9090` from `REJECT` to `DROP` and observe:
- how the client behaves
- what changes in the capture
- which failure mode is easier to debug and why

## Exercise 3: application layer filter
Use `python/apps/packet_filter.py`:
1) run the TCP server on `h2`
2) run the proxy on `fw` or on a dedicated host
3) connect from `h1` to the proxy and observe logs and captures
4) add an allow list and confirm only the expected source can connect

## Exercise 4: write a micro report
Take one failure (TCP blocked or UDP blocked) and write:
- what you expected
- what you observed (include 3–6 tshark lines)
- what the root cause is
- how you would prevent it in an automated pipeline
