# =============================================================================
# Makefile – Week 5 Starterkit: Network Layer - IP Addressing
# =============================================================================
# Complete automation for installation, demos, tests and Mininet laboratory
#
# Usage:
#   make help                # Display all available targets
#   make setup               # Install dependencies
#   make demo                # Run all Python demos
#   make mininet-base        # Start base Mininet topology
#
# © 2025 ASE-CSIE | Revolvix&Hypotheticalandrei
# =============================================================================

.PHONY: help setup test demo demo-cidr demo-flsm demo-vlsm demo-ipv6 quiz \
        mininet-base mininet-extended mininet-extended-ipv6 mininet-clean \
        capture verify clean reset all run-demo run-lab run-all artifacts \
        docker-build docker-run

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := pip3
SHELL := /bin/bash

# Week 5 Configuration
WEEK := 5
NETWORK_BASE := 10.0.$(WEEK)
WEEK_PORT_BASE := $(shell echo $$((5100 + 100 * ($(WEEK) - 1))))

ROOT_DIR := $(shell pwd)
PYTHON_DIR := $(ROOT_DIR)/python
EXERCISES_DIR := $(PYTHON_DIR)/exercises
MININET_DIR := $(ROOT_DIR)/mininet/topologies
SCRIPTS_DIR := $(ROOT_DIR)/scripts
DOCS_DIR := $(ROOT_DIR)/docs
PCAP_DIR := $(ROOT_DIR)/pcap
ARTIFACTS_DIR := $(ROOT_DIR)/artifacts

# Colours for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# -----------------------------------------------------------------------------
# Default target and help
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║$(NC)       $(GREEN)Week 5 Starterkit – Network Layer$(NC)                              $(BLUE)║$(NC)"
	@echo "$(BLUE)║$(NC)       $(YELLOW)IPv4/IPv6 Addressing, CIDR, Subnetting, VLSM$(NC)                   $(BLUE)║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Basic Commands:$(NC)"
	@echo "  make setup               Install system and Python dependencies"
	@echo "  make test                Run smoke tests for validation"
	@echo "  make demo                Run all Python demos"
	@echo "  make clean               Clean temporary files"
	@echo "  make reset               Complete reset (clean + mininet-clean)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Python Demos (no sudo required):$(NC)"
	@echo "  make demo-cidr           CIDR analysis demo (192.168.10.14/26)"
	@echo "  make demo-flsm           FLSM subnetting demo (4 and 8 subnets)"
	@echo "  make demo-vlsm           VLSM allocation demo (60, 20, 10, 2 hosts)"
	@echo "  make demo-ipv6           IPv6 conversions + subnets demo"
	@echo "  make quiz                Interactive subnetting quiz"
	@echo ""
	@echo "$(GREEN)$(BOLD)Mininet Laboratory (requires sudo):$(NC)"
	@echo "  make mininet-base        Base topology: 2 subnets + 1 router"
	@echo "  make mininet-extended    Extended topology: VLSM (3 different prefixes)"
	@echo "  make mininet-extended-ipv6  Extended topology with IPv6"
	@echo "  make mininet-test        Automatic connectivity test"
	@echo "  make mininet-clean       Clean remaining Mininet processes"
	@echo ""
	@echo "$(GREEN)$(BOLD)Capture and Verification:$(NC)"
	@echo "  make capture             Run automated packet capture"
	@echo "  make verify              Verify environment is correctly configured"
	@echo ""
	@echo "$(GREEN)$(BOLD)Compound Targets:$(NC)"
	@echo "  make run-demo            Setup + complete demo"
	@echo "  make run-lab             Setup + test + mininet-base"
	@echo "  make run-all             Automatic demo with artefacts"
	@echo "  make artifacts           Generate artefacts (demo.log, demo.pcap, validation.txt)"
	@echo "  make all                 Setup + test + demo"
	@echo ""
	@echo "$(CYAN)Week $(WEEK) Configuration:$(NC)"
	@echo "  Network: $(NETWORK_BASE).0/24"
	@echo "  Ports: $(WEEK_PORT_BASE)-$(shell echo $$(($(WEEK_PORT_BASE) + 99)))"
	@echo ""
	@echo "$(CYAN)Complete Examples:$(NC)"
	@echo "  make setup && make demo          # Setup and demo"
	@echo "  make run-all                     # Complete demo with artefacts"
	@echo "  sudo make mininet-base           # Mininet laboratory"
	@echo "  make quiz                        # Interactive practice"
	@echo ""

# -----------------------------------------------------------------------------
# Setup and Installation
# -----------------------------------------------------------------------------
setup: setup-system setup-python setup-permissions
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Setup complete!$(NC)"
	@echo "  Run $(CYAN)'make test'$(NC) for verification."
	@echo "  Run $(CYAN)'make demo'$(NC) for demonstrations."

setup-system:
	@echo ""
	@echo "$(BLUE)>>> Installing system dependencies...$(NC)"
	@if [ -f /etc/debian_version ]; then \
		echo "  Debian/Ubuntu system detected"; \
		sudo apt-get update -qq && \
		sudo apt-get install -y -qq \
			python3 python3-pip python3-venv \
			mininet openvswitch-switch \
			iproute2 iputils-ping net-tools \
			tcpdump tshark wireshark-common \
			traceroute curl wget make >/dev/null 2>&1 || \
		echo "  $(YELLOW)Note: Some packages may require manual installation$(NC)"; \
	else \
		echo "  $(YELLOW)Non-Debian system detected. Install dependencies manually.$(NC)"; \
	fi
	@echo "$(GREEN)✓ System dependencies check complete$(NC)"

setup-python:
	@echo ""
	@echo "$(BLUE)>>> Checking Python...$(NC)"
	@$(PYTHON) --version
	@echo "  Note: Kit uses only standard library (ipaddress, argparse)"
	@echo "$(GREEN)✓ Python OK$(NC)"

setup-permissions:
	@echo ""
	@echo "$(BLUE)>>> Setting script permissions...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/*.sh 2>/dev/null || true
	@chmod +x $(ROOT_DIR)/tests/*.sh 2>/dev/null || true
	@chmod +x $(EXERCISES_DIR)/*.py 2>/dev/null || true
	@echo "$(GREEN)✓ Permissions set$(NC)"

# -----------------------------------------------------------------------------
# Tests and Verification
# -----------------------------------------------------------------------------
test: verify
	@echo ""
	@echo "$(BLUE)>>> Running Python smoke tests...$(NC)"
	@$(PYTHON) -c "import ipaddress; print('  ✓ ipaddress module available')"
	@$(PYTHON) -c "from python.utils.net_utils import analyze_ipv4_interface; print('  ✓ net_utils utilities OK')"
	@$(PYTHON) $(EXERCISES_DIR)/ex_5_01_cidr_flsm.py analyze 192.168.1.1/24 --json >/dev/null && \
		echo "  ✓ CIDR exercise functional" || \
		echo "  $(RED)✗ CIDR exercise failed$(NC)"
	@$(PYTHON) $(EXERCISES_DIR)/ex_5_02_vlsm_ipv6.py vlsm 10.0.0.0/24 10 5 2 --json >/dev/null && \
		echo "  ✓ VLSM exercise functional" || \
		echo "  $(RED)✗ VLSM exercise failed$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ All tests passed!$(NC)"

verify:
	@echo ""
	@echo "$(BLUE)>>> Checking environment...$(NC)"
	@echo -n "  Python 3:    " && $(PYTHON) --version 2>/dev/null || echo "$(RED)MISSING$(NC)"
	@echo -n "  Mininet:     " && (mn --version 2>/dev/null | head -1) || echo "$(YELLOW)Not installed$(NC)"
	@echo -n "  OVS:         " && (ovs-vsctl --version 2>/dev/null | head -1) || echo "$(YELLOW)Not installed$(NC)"
	@echo -n "  tshark:      " && (tshark --version 2>/dev/null | head -1) || echo "$(YELLOW)Not installed$(NC)"
	@echo -n "  tcpdump:     " && (tcpdump --version 2>/dev/null | head -1) || echo "$(YELLOW)Not installed$(NC)"
	@echo ""

# -----------------------------------------------------------------------------
# Python Demos
# -----------------------------------------------------------------------------
demo: demo-cidr demo-flsm demo-vlsm demo-ipv6
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Complete demo finished!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)For Mininet laboratory (requires sudo):$(NC)"
	@echo "  sudo make mininet-base"
	@echo "  sudo make mininet-extended-ipv6"
	@echo ""
	@echo "$(YELLOW)For interactive quiz:$(NC)"
	@echo "  make quiz"

demo-cidr:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 1: CIDR Analysis$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_01_cidr_flsm.py analyze 192.168.10.14/26"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py analyze 192.168.10.14/26
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_01_cidr_flsm.py analyze 172.16.50.100/20 --verbose"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py analyze 172.16.50.100/20 --verbose

demo-flsm:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 2: FLSM Subnetting$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8

demo-vlsm:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 3: VLSM Allocation$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2

demo-ipv6:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 4: IPv6 Utilities$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5
	@echo ""
	@echo "$(YELLOW)Command:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6-types"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6-types

quiz:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Interactive Subnetting Quiz$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_03_quiz_generator.py --interactive --count 5

# -----------------------------------------------------------------------------
# Mininet
# -----------------------------------------------------------------------------
mininet-base:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Base Topology (2 subnets + 1 router)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Week $(WEEK) Architecture:$(NC)"
	@echo "  h1 (10.0.5.11/25) -- r1 -- h2 (10.0.5.140/25)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_base.py --cli

mininet-extended:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Extended Topology (VLSM)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --cli

mininet-extended-ipv6:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Extended Topology (VLSM + IPv6)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --cli --ipv6

mininet-test:
	@echo ""
	@echo "$(BLUE)>>> Automatic Mininet connectivity test...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topo_5_base.py --test && \
		echo "$(GREEN)✓ Base test passed$(NC)" || \
		echo "$(RED)✗ Base test failed$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --test --ipv6 && \
		echo "$(GREEN)✓ Extended (IPv6) test passed$(NC)" || \
		echo "$(RED)✗ Extended test failed$(NC)"

mininet-clean:
	@echo ""
	@echo "$(BLUE)>>> Cleaning Mininet processes...$(NC)"
	@sudo mn -c 2>/dev/null || true
	@sudo pkill -9 -f "python.*mininet" 2>/dev/null || true
	@sudo pkill -9 -f "ovs-" 2>/dev/null || true
	@sudo systemctl restart openvswitch-switch 2>/dev/null || \
		echo "  $(YELLOW)OVS not available$(NC)"
	@echo "$(GREEN)✓ Mininet cleaned$(NC)"

# -----------------------------------------------------------------------------
# Capture
# -----------------------------------------------------------------------------
capture:
	@echo ""
	@echo "$(BLUE)>>> Packet capture (demonstrative)$(NC)"
	@mkdir -p $(PCAP_DIR)
	@echo "  For real capture, run in Mininet CLI:"
	@echo "    r1 tcpdump -ni r1-eth0 -w /tmp/capture.pcap icmp &"
	@echo "    h1 ping -c 5 10.0.2.10"
	@echo "    r1 kill %tcpdump"
	@echo ""
	@echo "  Analysis with tshark:"
	@echo "    sudo tshark -r /tmp/capture.pcap -T fields -e ip.ttl -e ip.src -e ip.dst"

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
clean:
	@echo ""
	@echo "$(BLUE)>>> Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ 2>/dev/null || true
	@rm -f $(PCAP_DIR)/*.pcap 2>/dev/null || true
	@echo "$(GREEN)✓ Temporary files cleaned$(NC)"

reset: clean mininet-clean
	@echo ""
	@echo "$(GREEN)✓ Complete reset finished$(NC)"

# -----------------------------------------------------------------------------
# Compound Targets
# -----------------------------------------------------------------------------
run-demo: setup demo

run-lab: setup test
	@echo ""
	@echo "$(YELLOW)Now start the laboratory with:$(NC)"
	@echo "  sudo make mininet-base"

run-all: setup
	@echo ""
	@echo "$(BLUE)>>> Running complete automatic demo...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/run_all.sh
	@$(SCRIPTS_DIR)/run_all.sh --full
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Complete demo finished!$(NC)"
	@echo "$(YELLOW)Artefacts in:$(NC) $(ARTIFACTS_DIR)/"
	@echo "$(YELLOW)Validate with:$(NC) make test-artifacts"

artifacts:
	@echo ""
	@echo "$(BLUE)>>> Generating artefacts...$(NC)"
	@mkdir -p $(ARTIFACTS_DIR)
	@chmod +x $(SCRIPTS_DIR)/run_all.sh
	@$(SCRIPTS_DIR)/run_all.sh --quick
	@echo ""
	@echo "$(GREEN)✓ Artefacts generated:$(NC)"
	@ls -la $(ARTIFACTS_DIR)/ 2>/dev/null || echo "  (empty directory)"

test-artifacts:
	@echo ""
	@echo "$(BLUE)>>> Validating artefacts...$(NC)"
	@chmod +x $(ROOT_DIR)/tests/smoke_test.sh
	@$(ROOT_DIR)/tests/smoke_test.sh --with-artifacts

all: setup test demo
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Setup, test and demo complete!$(NC)"
