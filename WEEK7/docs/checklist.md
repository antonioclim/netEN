# Teaching checklist – Week 6

## Before the seminar

- Verify the VM boots and has Internet access (if the scenario requires it)
- Verify Mininet works: `sudo mn --test pingall`
- Verify Open vSwitch is available: `sudo ovs-vsctl show`
- Verify Python is available: `python3 --version`
- Verify the kit runs: `make setup` then `make demo`
- Verify tests: `make test`

## During the seminar

- Keep all commands CLI-only and repeatable
- Emphasise evidence collection: logs, counters and captures
- Remind students to reset the environment with `make clean` if the state becomes inconsistent

## After the seminar

- Collect student reports and validate they include the required artefacts and explanations
