# ==============================================================================
# Makefile - Week 4 Starterkit (WEEK 4)
# Custom text/binary application protocol over TCP and UDP
# ==============================================================================
# WEEK 4 port plan: 5400 (TEXT), 5401 (BINARY), 5402 (UDP)
# IP plan (Mininet): 10.0.4.0/24
#
# Usage: make [target]
#   make help       - Display this message
#   make setup      - Install dependencies
#   make run-demo   - Run the main demo
#   make run-lab    - Start servers for laboratory
#   make capture    - Capture network traffic
#   make verify     - Verify the environment is working
#   make clean      - Clean temporary files
#   make reset      - Reset everything to initial state
#
# Licence: MIT - ASE-CSIE Teaching Material
# ==============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset cleanup \
        server-text server-binary server-udp test lint check

# Variables
PYTHON := python3
SUDO := sudo
ROOT := $(shell pwd)
ARTIFACTS := $(ROOT)/artifacts
RESULTS := $(ROOT)/results
PCAP := $(ROOT)/pcap

# ==============================================================================
# WEEK 4 PORT PLAN (Cross-Cutting Standard)
# ==============================================================================
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5100 + 300 = 5400
PORT_TEXT := 5400
PORT_BIN := 5401
PORT_UDP := 5402

# Colours for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
CYAN := \033[0;36m
NC := \033[0m

# ==============================================================================
# Main target: help
# ==============================================================================

help:
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  Week 4 Starterkit - Custom TEXT/BINARY Protocols (WEEK 4)           ║$(NC)"
	@echo "$(CYAN)║  Ports: TEXT=$(PORT_TEXT), BINARY=$(PORT_BIN), UDP=$(PORT_UDP)                           ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)SETUP AND VERIFICATION:$(NC)"
	@echo "  make setup          Install dependencies"
	@echo "  make verify         Verify environment (Python, ports, modules)"
	@echo "  make check          Verify Python syntax"
	@echo "  make lint           Analyse code style"
	@echo ""
	@echo "$(YELLOW)RUN SERVERS:$(NC)"
	@echo "  make server-text    Start TEXT server on port $(PORT_TEXT)"
	@echo "  make server-binary  Start BINARY server on port $(PORT_BIN)"
	@echo "  make server-udp     Start UDP server on port $(PORT_UDP)"
	@echo "  make run-lab        Start all servers (in background)"
	@echo ""
	@echo "$(YELLOW)DEMO AND CAPTURE:$(NC)"
	@echo "  make run-demo       Run complete demo with clients"
	@echo "  make capture        Capture traffic on lo (5 seconds)"
	@echo "  make analyze        Analyse last capture"
	@echo ""
	@echo "$(YELLOW)CLEANUP:$(NC)"
	@echo "  make clean          Delete temporary files"
	@echo "  make cleanup        Stop servers and clean"
	@echo "  make reset          Complete reset (kill servers, clean)"
	@echo ""
	@echo "$(GREEN)QUICK COMMANDS:$(NC)"
	@echo "  make test           Run quick smoke test"
	@echo ""
	@echo "$(GREEN)IP PLAN (Mininet):$(NC)"
	@echo "  Network: 10.0.4.0/24, Gateway: 10.0.4.1, Server: 10.0.4.100"
	@echo ""

# ==============================================================================
# Setup and Installation
# ==============================================================================

setup:
	@echo "$(GREEN)[SETUP] Installing dependencies...$(NC)"
	@chmod +x scripts/*.sh 2>/dev/null || true
	@./scripts/setup.sh || (echo "$(RED)Setup failed!$(NC)" && exit 1)
	@echo "$(GREEN)[SETUP] Complete!$(NC)"

# ==============================================================================
# Environment verification
# ==============================================================================

verify:
	@echo "$(GREEN)[VERIFY] Verifying environment...$(NC)"
	@echo ""
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo ""
	@echo "Required Python modules:"
	@$(PYTHON) -c "import socket; print('  ✓ socket')"
	@$(PYTHON) -c "import struct; print('  ✓ struct')"
	@$(PYTHON) -c "import zlib; print('  ✓ zlib')"
	@$(PYTHON) -c "import threading; print('  ✓ threading')"
	@$(PYTHON) -c "import dataclasses; print('  ✓ dataclasses')"
	@echo ""
	@echo "Verifying free ports (WEEK 4: 5400-5402):"
	@(lsof -i :$(PORT_TEXT) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_TEXT) IN USE") || echo "  ✓ Port $(PORT_TEXT) free"
	@(lsof -i :$(PORT_BIN) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_BIN) IN USE") || echo "  ✓ Port $(PORT_BIN) free"
	@(lsof -i :$(PORT_UDP) > /dev/null 2>&1 && echo "  ⚠ Port $(PORT_UDP) IN USE") || echo "  ✓ Port $(PORT_UDP) free"
	@echo ""
	@echo "$(GREEN)[VERIFY] Verification complete!$(NC)"

check:
	@echo "$(GREEN)[CHECK] Verifying Python syntax...$(NC)"
	@$(PYTHON) -m py_compile python/apps/text_proto_server.py && echo "  ✓ text_proto_server.py"
	@$(PYTHON) -m py_compile python/apps/text_proto_client.py && echo "  ✓ text_proto_client.py"
	@$(PYTHON) -m py_compile python/apps/binary_proto_server.py && echo "  ✓ binary_proto_server.py"
	@$(PYTHON) -m py_compile python/apps/binary_proto_client.py && echo "  ✓ binary_proto_client.py"
	@$(PYTHON) -m py_compile python/apps/udp_sensor_server.py && echo "  ✓ udp_sensor_server.py"
	@$(PYTHON) -m py_compile python/apps/udp_sensor_client.py && echo "  ✓ udp_sensor_client.py"
	@$(PYTHON) -m py_compile python/utils/proto_common.py && echo "  ✓ proto_common.py"
	@$(PYTHON) -m py_compile python/utils/io_utils.py && echo "  ✓ io_utils.py"
	@echo "$(GREEN)[CHECK] All files are valid!$(NC)"

lint:
	@echo "$(GREEN)[LINT] Verifying code style...$(NC)"
	@$(PYTHON) -m pyflakes python/apps/*.py python/utils/*.py 2>/dev/null || true
	@echo "$(GREEN)[LINT] Complete!$(NC)"

# ==============================================================================
# Run Servers
# ==============================================================================

server-text:
	@echo "$(GREEN)[SERVER] Starting TEXT server on port $(PORT_TEXT)...$(NC)"
	@$(PYTHON) python/apps/text_proto_server.py --port $(PORT_TEXT) --verbose

server-binary:
	@echo "$(GREEN)[SERVER] Starting BINARY server on port $(PORT_BIN)...$(NC)"
	@$(PYTHON) python/apps/binary_proto_server.py --port $(PORT_BIN) --verbose

server-udp:
	@echo "$(GREEN)[SERVER] Starting UDP server on port $(PORT_UDP)...$(NC)"
	@$(PYTHON) python/apps/udp_sensor_server.py --port $(PORT_UDP) --verbose

run-lab:
	@echo "$(GREEN)[LAB] Starting servers in background...$(NC)"
	@mkdir -p $(RESULTS) $(ARTIFACTS)
	@$(PYTHON) python/apps/text_proto_server.py --port $(PORT_TEXT) > $(RESULTS)/text_server.log 2>&1 &
	@echo "  TEXT server: port $(PORT_TEXT) (PID: $$!)"
	@$(PYTHON) python/apps/binary_proto_server.py --port $(PORT_BIN) > $(RESULTS)/binary_server.log 2>&1 &
	@echo "  BINARY server: port $(PORT_BIN) (PID: $$!)"
	@$(PYTHON) python/apps/udp_sensor_server.py --port $(PORT_UDP) > $(RESULTS)/udp_server.log 2>&1 &
	@echo "  UDP server: port $(PORT_UDP) (PID: $$!)"
	@echo ""
	@echo "$(GREEN)Servers running in background. Use 'make cleanup' to stop.$(NC)"

# ==============================================================================
# Demo
# ==============================================================================

run-demo:
	@echo "$(GREEN)[DEMO] Running complete demo...$(NC)"
	@mkdir -p $(ARTIFACTS)
	@chmod +x scripts/run_all.sh
	@./scripts/run_all.sh || echo "$(YELLOW)Demo completed with warnings$(NC)"
	@echo "$(GREEN)[DEMO] Complete! Check $(ARTIFACTS)/$(NC)"

# ==============================================================================
# Capture and Analysis
# ==============================================================================

capture:
	@echo "$(GREEN)[CAPTURE] Starting capture on lo (5 seconds)...$(NC)"
	@mkdir -p $(PCAP)
	@$(SUDO) tcpdump -i lo -w $(PCAP)/capture_$$(date +%Y%m%d_%H%M%S).pcap \
		-c 100 port $(PORT_TEXT) or port $(PORT_BIN) or port $(PORT_UDP) &
	@echo "Capture active. Generate traffic then wait 5 seconds."
	@sleep 5
	@echo "$(GREEN)[CAPTURE] Capture complete in $(PCAP)/$(NC)"

analyze:
	@echo "$(GREEN)[ANALYZE] Analysing last capture...$(NC)"
	@LATEST=$$(ls -t $(PCAP)/*.pcap 2>/dev/null | head -1); \
	if [ -n "$$LATEST" ]; then \
		echo "File: $$LATEST"; \
		tshark -r "$$LATEST" -q -z io,stat,1 2>/dev/null || \
		tcpdump -r "$$LATEST" -n | head -20; \
	else \
		echo "$(RED)No captures in $(PCAP)/$(NC)"; \
	fi

# ==============================================================================
# Test
# ==============================================================================

test:
	@echo "$(GREEN)[TEST] Quick smoke test...$(NC)"
	@chmod +x tests/smoke_test.sh
	@./tests/smoke_test.sh

# ==============================================================================
# Cleanup
# ==============================================================================

clean:
	@echo "$(YELLOW)[CLEAN] Cleaning temporary files...$(NC)"
	@rm -rf $(RESULTS)/*.log 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)[CLEAN] Complete!$(NC)"

cleanup:
	@echo "$(YELLOW)[CLEANUP] Stopping servers and cleaning...$(NC)"
	@chmod +x scripts/cleanup.sh
	@./scripts/cleanup.sh
	@echo "$(GREEN)[CLEANUP] Complete!$(NC)"

reset: cleanup clean
	@echo "$(YELLOW)[RESET] Complete reset...$(NC)"
	@rm -rf $(ARTIFACTS)/* 2>/dev/null || true
	@rm -rf $(PCAP)/*.pcap 2>/dev/null || true
	@mkdir -p $(RESULTS) $(PCAP) $(ARTIFACTS)
	@echo "$(GREEN)[RESET] Complete!$(NC)"
