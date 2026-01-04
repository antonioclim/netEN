# Week 5 Lecture Checklist

This checklist is for the instructor and teaching assistants. It is designed for a Linux CLI-only minimal VM.

## Before the session
- Confirm the kit runs on a clean VM with Python 3.10+ and GNU Make.
- Run the full flow: `make setup`, `make demo` and `make test`.
- Check that `./artifacts/demo.log` and `./artifacts/validation.txt` are produced and readable.
- Confirm that no Python bytecode artefacts are present in the archive (`__pycache__/`, `*.pyc`).
- If you will demonstrate traffic capture, confirm that `tcpdump` or `tshark` is available.

## During the session
- Explain the IP plan for Week 5: `10.0.5.0/24`.
- Demonstrate CIDR, subnet masks, network address, broadcast address and usable host range.
- Use the CLI tool in `python/apps/subnet_calc.py` to compute and verify examples.
- If Mininet is used, run the scenario in `mininet/` and capture a short trace.

## After the session
- Run `make clean` to reset the kit.
- Collect `./artifacts/` and verify against `tests/expected_outputs.md`.
