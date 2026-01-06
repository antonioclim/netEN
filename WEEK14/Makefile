# Makefile — Starterkit Week 14
# Computer Networks / Networking — CSIE/ASE
# Version: 2025-12-31

.PHONY: setup run-demo run-lab capture verify clean reset help smoke-test run-all

SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
ARTIFACTS := $(ROOT_DIR)/artifacts
PYTHON := python3

# Colours for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo -e "$(GREEN)Starterkit W14 — Available commands:$(NC)"
	@echo ""
	@echo "  make setup      - Install dependencies (requires sudo)"
	@echo "  make verify     - Verify environment and dependencies"
	@echo "  make smoke-test - Run smoke tests only"
	@echo "  make run-demo   - Run the complete demo (Mininet + traffic + pcap)"
	@echo "  make run-all    - Alias for run-demo"
	@echo "  make run-lab    - Start topology interactively (Mininet CLI)"
	@echo "  make capture    - Start only tcpdump capture"
	@echo "  make clean      - Stop processes, clean Mininet"
	@echo "  make reset      - Clean + delete all artefacts"
	@echo ""
	@echo -e "$(YELLOW)Note: run-demo and run-lab require sudo.$(NC)"

setup:
	@echo -e "$(GREEN)[setup] Installing dependencies...$(NC)"
	@sudo bash scripts/setup.sh
	@echo -e "$(GREEN)[setup] Installing Python packages...$(NC)"
	@pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
	@echo -e "$(GREEN)[setup] Done.$(NC)"

verify:
	@echo -e "$(GREEN)[verify] Verifying environment...$(NC)"
	@bash scripts/verify.sh
	@bash tests/smoke_test.sh

smoke-test:
	@bash tests/smoke_test.sh

run-demo:
	@echo -e "$(GREEN)[run-demo] Starting automated demo...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@sudo bash scripts/run_all.sh
	@echo -e "$(GREEN)[run-demo] Artefacts generated in: $(ARTIFACTS)$(NC)"
	@ls -la $(ARTIFACTS)/ 2>/dev/null || true

run-all: run-demo

run-lab:
	@echo -e "$(GREEN)[run-lab] Starting interactive topology (Mininet CLI)...$(NC)"
	@echo -e "$(YELLOW)Type 'exit' or Ctrl+D to quit.$(NC)"
	@sudo $(PYTHON) mininet/topologies/topo_14_recap.py --cli

capture:
	@echo -e "$(GREEN)[capture] Starting standalone capture...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@sudo bash scripts/capture.sh $(ARTIFACTS)/manual_capture.pcap

clean:
	@echo -e "$(YELLOW)[clean] Stopping processes and cleaning Mininet...$(NC)"
	@sudo bash scripts/cleanup.sh
	@echo -e "$(GREEN)[clean] Done.$(NC)"

reset: clean
	@echo -e "$(RED)[reset] Deleting artefacts...$(NC)"
	@rm -rf $(ARTIFACTS)
	@echo -e "$(GREEN)[reset] Done.$(NC)"

# Default target
.DEFAULT_GOAL := help
