# Week 7 Docker Compose demo (optional)

This folder contains an optional Docker Compose demonstration.
It is not required for the main Week 7 Mininet lab, but it can be useful to compare host networking and container networking.

## Requirements
- Docker Engine
- Docker Compose (either `docker compose` or `docker-compose`)

## Run
From the kit root:

```bash
./scripts/run_all.sh --docker-only
```

Or directly:

```bash
cd docker
docker compose up --build --abort-on-container-exit --remove-orphans
```

Outputs are written to `artifacts/` on the host, for example:
- `artifacts/docker_tcp_server.log`
- `artifacts/docker_tcp_client.log`
- `artifacts/docker_udp_receiver.log`
- `artifacts/docker_udp_sender.log`

## Notes
- The Docker demo uses the same Python applications as the Mininet demo.
- It does not attempt packet capture inside containers to keep the setup light.
- Use it only on your own machine and only for this lab.
