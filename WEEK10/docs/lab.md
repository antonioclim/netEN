# Lab 10 – Mininet validation tasks

The Mininet portion of Week 10 provides a controlled network where students can reproduce service discovery and connectivity tests.

## What to run

1. Clean Mininet state:

```bash
sudo mn -c
```

2. Run the lab demo:

```bash
make mininet-test
```

3. Enter the Mininet CLI:

```bash
make mininet-cli
```

## What to verify

- host connectivity using `ping`
- service reachability using `nc` or `curl`
- traffic capture where relevant using `tcpdump` or `tshark`

See `mininet/scenarios/scenario_10_tasks.md` for the step-by-step tasks.
