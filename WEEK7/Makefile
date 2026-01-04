SHELL := /bin/bash

.PHONY: help setup demo test clean docker-demo docx

help:
	@echo "Targets:"
	@echo "  make setup       Install or validate dependencies"
	@echo "  make demo        Run the automated Week 7 demo"
	@echo "  make test        Run smoke tests"
	@echo "  make clean       Cleanup Mininet state and generated artefacts"
	@echo "  make docker-demo Run the optional Docker Compose demo (if Docker is available)"
	@echo "  make docx        Generate the Week 7 DOCX sheet (optional)"

setup:
	@./scripts/setup.sh

demo:
	@./scripts/run_all.sh

test:
	@./tests/smoke_test.sh

clean:
	@./scripts/cleanup.sh

docker-demo:
	@./scripts/run_all.sh --docker-only

docx:
	@python3 generate_docx/generate_docx.py --out docs/Week7_Lab_Sheet.docx
