# Week 6 Seminar Guide

This seminar is structured as a guided demo followed by student tasks.

## Agenda

1. Run the full automated demo (`scripts/run_all.sh`)
2. Inspect artefacts and locate key protocol events
3. Repeat one part of the demo manually to understand what the automation performs
4. Validate results using the smoke test

## Key observations

- NAT changes packet headers, so the same application flow can have different five-tuples at different points in the path
- ARP is local to a broadcast domain, it is not routed
- DHCP is a broadcast-based protocol and can be relayed
- SDN policies can be expressed as code and applied dynamically

## Student checklist

- You can reproduce the demo in a clean VM
- You can explain at least one capture-based observation for NAT and ARP
- You can show the smoke test passing
