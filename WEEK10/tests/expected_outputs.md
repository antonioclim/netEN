# Expected outputs (Week 10)

This document lists short, representative excerpts of output that you should see
when running the main targets. Exact timestamps, IP addresses and container IDs
will differ.

## 1. Environment verification

```bash
make verify
```

Expected (excerpt):

- `python3` detected
- `openssl` detected
- Python packages importable (requests, Flask, paramiko)
- Docker available (if installed)

## 2. HTTPS exercise self-test

```bash
make https-test
```

Expected (excerpt):

- `Self-test: PASS`
- CRUD operations succeed and status codes are correct

## 3. REST levels exercise self-test

```bash
make rest-test
```

Expected (excerpt):

- `Self-test: PASS`
- Level 0..3 endpoints respond with the expected patterns

## 4. Docker stack tests

```bash
make docker-up
make docker-health
make dns-test
make ssh-test
make ftp-test
make docker-down
```

Expected (excerpt):

- `web` answers on `http://localhost:8000/`
- DNS returns `10.10.10.10` for `myservice.lab.local`
- Paramiko client prints a successful SSH command output
- FTP listing shows at least `welcome.txt`

## 5. Fully automated demo

```bash
make run-all
```

Expected (excerpt):

- `HTTP test: PASS`
- `DNS test: PASS`
- `SSH test: PASS`
- `FTP test: PASS`
- `validation.txt` created in `artifacts/`
