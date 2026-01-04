# ==============================================================================
# Makefile - Computer Networks starter kit, Week 1
# ==============================================================================
# Targets are designed for reproducible execution on a Linux CLI-only VM.
# ==============================================================================

SHELL := /bin/bash
PYTHON := python3

.PHONY: help setup demo test verify clean docker-demo docker-clean

help:
	@echo "Available targets:"
	@echo "  make setup        Check prerequisites (and optionally install via sudo)"
	@echo "  make demo         Run the end-to-end demo (host)"
	@echo "  make test         Run the smoke test"
	@echo "  make verify       Run static checks (py_compile, bash -n, compose config)"
	@echo "  make clean        Reset generated artefacts and environment state"
	@echo "  make docker-demo  Run the demo via Docker compose (optional)"
	@echo "  make docker-clean Stop Docker services and remove volumes (optional)"

setup:
	@bash scripts/setup.sh

demo:
	@bash scripts/run_all.sh

test:
	@bash tests/smoke_test.sh

verify:
	@bash scripts/verify.sh --verbose

clean:
	@bash scripts/cleanup.sh

docker-demo:
	@if command -v docker >/dev/null 2>&1; then \
		docker compose -f docker/docker-compose.yml config -q; \
		docker compose -f docker/docker-compose.yml up --build --abort-on-container-exit; \
	else \
		echo "Docker is not available, skipping docker-demo"; \
	fi

docker-clean:
	@if command -v docker >/dev/null 2>&1; then \
		docker compose -f docker/docker-compose.yml down -v; \
	else \
		echo "Docker is not available, skipping docker-clean"; \
	fi

.PHONY: all
all: setup verify demo test
