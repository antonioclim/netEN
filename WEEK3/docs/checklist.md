# Teaching checklist — Week 3

This checklist is for the instructor running Week 3 activities on a Linux VM.

## Before the session (1–2 days)
- Confirm the VM image is representative and fully updated
- Run `make verify` and `./tests/smoke_test.sh`
- Confirm Python examples run and `--help` is informative
- Confirm packet capture works (`tcpdump` or `tshark`)
- If Mininet is used, confirm `sudo mn --test pingall` works

## Immediately before the session
- Start from a clean state: `sudo ./scripts/cleanup.sh`
- Run the non-interactive demo once: `sudo ./scripts/run_all.sh --quick`
- Confirm artefacts exist in `./artifacts`

## During the session
- Emphasise safety and reproducibility: exact commands and exact outputs
- Demonstrate the difference between broadcast and multicast at packet level
- Highlight binding and interface selection issues (multi-homed hosts)
- Encourage students to capture traffic and annotate one or two packets

## After the session
- Ask for a short report with commands, outputs and one traffic capture excerpt
- Re-run `./tests/smoke_test.sh` on a fresh checkout if you publish updates
