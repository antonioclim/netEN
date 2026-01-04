# Mininet cheatsheet (quick reference)

Mininet is optional in this week.
Use it only if a scenario explicitly requires a virtual topology.

## Install and check

- `mn --version`
- `sudo mn --test pingall`

## Clean up

Always clean up before and after experiments:

- `sudo mn -c`

## Useful commands inside Mininet CLI

- `nodes`  
- `net`  
- `dump`  
- `pingall`  
- `h1 ping -c 1 h2`

## Running a Python topology

If the kit contains a topology script:

- `sudo python3 mininet/<script>.py`

If you see stale interfaces or namespaces, run `sudo mn -c` and retry.
