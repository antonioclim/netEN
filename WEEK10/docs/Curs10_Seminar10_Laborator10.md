# Week 10 – Lecture, seminar and lab guide

This document links the lecture concepts to the seminar and lab activities included in this kit.

## Lecture

See `docs/curs.md`.

## Seminar (Docker services)

Students work with DNS, SSH and FTP services managed via Docker Compose and verify behaviour using standard CLI tools.

Key commands:

```bash
make docker-up
make docker-logs
make docker-down
```

## Lab (Mininet scenarios)

Students run a small Mininet topology and perform application-layer tests inside the emulated network.

Key commands:

```bash
make mininet-test
make mininet-cli
make mininet-clean
```

## Assessment artefacts

Students must produce:

- `artifacts/demo.log`
- `artifacts/validation.txt`

and a short explanation of what each validation line confirms.
