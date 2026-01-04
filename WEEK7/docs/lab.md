# Lab guide – Week 6

This lab is designed for a minimal Linux VM environment and uses CLI-only tooling.

## Tasks

1. Run the automated demo
2. Inspect artefacts in `artifacts/`
3. Answer the questions in the seminar report template (if provided)

## Commands

```bash
make setup
make demo
make test
make clean
```

## Notes

- If Mininet is not available, `make demo` may fail. In that case use `make test` for static checks and review the troubleshooting section in `README.md`.
- If packet capture is restricted on your VM, disable capture in the configuration and rely on logs and counters.
