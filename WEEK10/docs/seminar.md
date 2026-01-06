# Seminar 10 – Docker Compose services

This seminar is built around three small services started via Docker Compose: DNS, SSH and FTP.

## Ports

- DNS: UDP 5353 (mapped from container UDP 53)
- SSH: TCP 2222
- FTP: TCP 2121 plus passive ports 30000–30009
- HTTP: TCP 8000 if the web demo is enabled

## Run

```bash
make docker-up
make docker-logs
```

## Validate

```bash
./scripts/run_all.sh
./tests/smoke_test.sh
```

## Stop

```bash
make docker-down
./scripts/cleanup.sh
```
