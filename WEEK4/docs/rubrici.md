# Assessment rubric (Week 4)

This rubric evaluates correctness, reproducibility and clarity for the Week 4 protocol tasks.

## 1) Reproducible execution (40%)

- The kit runs on a CLI-only Linux VM using the documented commands
- The demo produces the expected artefacts in `artifacts/`
- The smoke test is non-interactive and fails on errors

## 2) Protocol correctness (35%)

- TCP framing is implemented correctly (no partial-frame bugs)
- CRC32 is computed and validated consistently
- Binary packing and unpacking uses a stable format on both ends
- UDP messages are parsed safely and errors are handled

## 3) Code quality (15%)

- Clear structure and consistent naming
- Helpful help text for CLI scripts (argparse)
- Defensive timeouts and explicit exit codes where relevant

## 4) Documentation and troubleshooting (10%)

- README explains how to run, verify and clean up
- Troubleshooting includes at least 8 practical items
