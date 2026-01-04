# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /work

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
     iproute2 iputils-ping netcat-openbsd tcpdump \
  && rm -rf /var/lib/apt/lists/*

CMD ["bash", "-lc", "python -m pip install -U pip && python -m pip install -r requirements.txt && bash scripts/run_all.sh --quick --no-capture && bash tests/smoke_test.sh"]
