# Teaching checklist – Week 10

## Before the session

### 1–2 days before

- [ ] Pull Docker images if you are using pre-built images: `docker compose pull`
- [ ] Run a full infrastructure test on the demonstration machine
- [ ] Prepare a fallback plan (VM snapshot or cached images)
- [ ] Ensure slides and supporting materials are up to date
- [ ] Prepare the example files used in the demo

### 30 minutes before

- [ ] Start the Docker infrastructure: `make docker-up`
- [ ] Confirm all services are running: `docker compose ps`
- [ ] Quick test for DNS, SSH and FTP
- [ ] Open the required terminals (3–4)

## During the session

- [ ] Keep `artifacts/demo.log` visible while running the demo
- [ ] Highlight where outputs are produced and how students should validate them
- [ ] Use `make docker-logs` to explain service failures when they occur

## After the session

- [ ] Run `make docker-down`
- [ ] Run `./scripts/cleanup.sh`
- [ ] Archive `artifacts/` for reference or assessment
