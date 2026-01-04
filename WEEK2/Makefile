# =============================================================================
# Makefile – Starterkit W2: OSI/TCP-IP Models & Socket Programming
# =============================================================================
# Usage: make <target> | Help: make help
# Author: Revolvix&Hypotheticalandrei
# =============================================================================

SHELL := /bin/bash
.PHONY: help setup verify run-demo run-lab capture clean reset \
        demo-all demo-tcp demo-udp mininet-cli mininet-extended mininet-test \
        tcp-server tcp-client udp-server udp-client \
        capture-tcp capture-udp capture-stop analyze-tcp analyze-udp \
        docker-build docker-shell docker-demo diagrams test

# -----------------------------------------------------------------------------
# VARIABLES
# -----------------------------------------------------------------------------
PYTHON        := python3
MININET_SUDO  := sudo
TSHARK        := tshark
TCPDUMP       := tcpdump
NC            := nc

ROOT_DIR      := $(shell pwd)
EXERCISES_DIR := $(ROOT_DIR)/seminar/python/exercises
TEMPLATES_DIR := $(ROOT_DIR)/seminar/python/templates
CAPTURES_DIR  := $(ROOT_DIR)/seminar/captures
LOGS_DIR      := $(ROOT_DIR)/logs
MININET_DIR   := $(ROOT_DIR)/seminar/mininet
PCAP_DIR      := $(ROOT_DIR)/pcap

EX_TCP        := $(EXERCISES_DIR)/ex_2_01_tcp.py
EX_UDP        := $(EXERCISES_DIR)/ex_2_02_udp.py
TOPO_BASE     := $(MININET_DIR)/topologies/topo_2_base.py
TOPO_EXT      := $(MININET_DIR)/topologies/topo_2_extended.py

TCP_PORT      := 9999
UDP_PORT      := 9998
BIND_ADDR     := 0.0.0.0
MSG           ?= "Hello from Makefile"

DOCKER_IMAGE  := netlab-s2:latest

# Colours for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC_CLR := \033[0m

# =============================================================================
# HELP
# =============================================================================
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════════╗"
	@echo "║  $(GREEN)Starterkit W2$(NC_CLR) – Makefile                                              ║"
	@echo "║  Architectural Models OSI/TCP-IP & Socket Programming                    ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)SETUP & VERIFY$(NC_CLR)                                                         ║"
	@echo "║   make setup              Install packages and dependencies              ║"
	@echo "║   make verify             Verify working environment                     ║"
	@echo "║   make test               Quick smoke test                               ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)DEMONSTRATIONS (REQUIRED)$(NC_CLR)                                               ║"
	@echo "║   make run-demo           Complete demo (TCP + UDP + capture)            ║"
	@echo "║   make run-lab            Run interactive laboratory                     ║"
	@echo "║   make demo-tcp           TCP demo only                                  ║"
	@echo "║   make demo-udp           UDP demo only                                  ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)MININET$(NC_CLR)                                                                 ║"
	@echo "║   make mininet-cli        Interactive Mininet (base topology)            ║"
	@echo "║   make mininet-extended   Topology with router (2 subnets)               ║"
	@echo "║   make mininet-test       Automatic test in Mininet                      ║"
	@echo "║   make mininet-clean      Clean Mininet sessions                         ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)SERVER / CLIENT$(NC_CLR)                                                         ║"
	@echo "║   make tcp-server         TCP server on localhost:$(TCP_PORT)                   ║"
	@echo "║   make tcp-client MSG=x   TCP client with custom message                 ║"
	@echo "║   make udp-server         UDP server on localhost:$(UDP_PORT)                   ║"
	@echo "║   make udp-client         Interactive UDP client                         ║"
	@echo "║   make load-test N=10     Load test with N clients                       ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)CAPTURES & ANALYSIS$(NC_CLR)                                                     ║"
	@echo "║   make capture            Start TCP+UDP capture                          ║"
	@echo "║   make capture-tcp        Start tcpdump TCP only                         ║"
	@echo "║   make capture-udp        Start tcpdump UDP only                         ║"
	@echo "║   make capture-stop       Stop all captures                              ║"
	@echo "║   make analyze-tcp        TCP analysis with tshark                       ║"
	@echo "║   make analyze-udp        UDP analysis with tshark                       ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)DOCKER (OPTIONAL)$(NC_CLR)                                                       ║"
	@echo "║   make docker-build       Build Docker image                             ║"
	@echo "║   make docker-shell       Interactive shell in container                 ║"
	@echo "║   make docker-demo        Run demo in container                          ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)CLEANUP$(NC_CLR)                                                                 ║"
	@echo "║   make clean              Clean active processes                         ║"
	@echo "║   make reset              Complete reset (clean + generated files)       ║"
	@echo "╚══════════════════════════════════════════════════════════════════════════╝"
	@echo ""

# =============================================================================
# SETUP & VERIFY (REQUIRED)
# =============================================================================
setup:
	@echo "$(GREEN)[SETUP]$(NC_CLR) Installing dependencies..."
	@mkdir -p $(CAPTURES_DIR) $(LOGS_DIR) $(PCAP_DIR)
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update -qq && \
		sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
			python3 python3-pip python3-venv \
			mininet openvswitch-switch \
			tcpdump tshark wireshark-common \
			netcat-openbsd iproute2 net-tools curl; \
	fi
	@$(PYTHON) -m pip install --upgrade pip -q 2>/dev/null || true
	@test -f requirements.txt && $(PYTHON) -m pip install -r requirements.txt -q 2>/dev/null || true
	@echo "$(GREEN)[SETUP]$(NC_CLR) ✓ Installation complete"

verify:
	@echo "$(GREEN)[VERIFY]$(NC_CLR) Verifying working environment..."
	@echo ""
	@echo "  System components:"
	@printf "    Python3:    " && $(PYTHON) --version 2>&1 || echo "$(RED)MISSING$(NC_CLR)"
	@printf "    Mininet:    " && ($(MININET_SUDO) mn --version 2>/dev/null || echo "$(RED)MISSING$(NC_CLR)")
	@printf "    tshark:     " && ($(TSHARK) -v 2>&1 | head -n1 || echo "$(RED)MISSING$(NC_CLR)")
	@printf "    tcpdump:    " && ($(TCPDUMP) --version 2>&1 | head -n1 || echo "$(RED)MISSING$(NC_CLR)")
	@printf "    netcat:     " && ($(NC) -h 2>&1 | head -n1 || echo "$(RED)MISSING$(NC_CLR)")
	@echo ""
	@echo "  Exercise files:"
	@test -f $(EX_TCP) && echo "    $(GREEN)✓$(NC_CLR) ex_2_01_tcp.py" || echo "    $(RED)✗$(NC_CLR) ex_2_01_tcp.py MISSING"
	@test -f $(EX_UDP) && echo "    $(GREEN)✓$(NC_CLR) ex_2_02_udp.py" || echo "    $(RED)✗$(NC_CLR) ex_2_02_udp.py MISSING"
	@echo ""
	@echo "  Mininet topologies:"
	@test -f $(TOPO_BASE) && echo "    $(GREEN)✓$(NC_CLR) topo_2_base.py" || echo "    $(RED)✗$(NC_CLR) topo_2_base.py MISSING"
	@test -f $(TOPO_EXT) && echo "    $(GREEN)✓$(NC_CLR) topo_2_extended.py" || echo "    $(RED)✗$(NC_CLR) topo_2_extended.py MISSING"
	@echo ""
	@echo "$(GREEN)[VERIFY]$(NC_CLR) ✓ Verification complete"

test:
	@echo "$(GREEN)[TEST]$(NC_CLR) Smoke test..."
	@chmod +x scripts/verify.sh 2>/dev/null || true
	@./scripts/verify.sh 2>/dev/null || echo "$(YELLOW)[INFO]$(NC_CLR) verify.sh unavailable, running minimal check"
	@$(PYTHON) -c "import socket; print('  Socket module: OK')" 2>/dev/null || echo "$(RED)ERROR$(NC_CLR) Socket module"
	@$(PYTHON) -c "import threading; print('  Threading module: OK')" 2>/dev/null || echo "$(RED)ERROR$(NC_CLR) Threading module"
	@echo "$(GREEN)[TEST]$(NC_CLR) ✓ Smoke test complete"

# =============================================================================
# DEMONSTRATIONS (REQUIRED)
# =============================================================================
run-demo: demo-all

demo-all: clean
	@echo "$(GREEN)[DEMO]$(NC_CLR) Running complete TCP + UDP demonstration..."
	@mkdir -p $(CAPTURES_DIR) $(LOGS_DIR)
	@echo ""
	@echo "  $(YELLOW)Step 1:$(NC_CLR) Starting TCP server..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT) > $(LOGS_DIR)/tcp_server.log 2>&1 &
	@sleep 1
	@echo "  $(YELLOW)Step 2:$(NC_CLR) Starting TCP capture..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/demo_tcp.pcap tcp port $(TCP_PORT) > /dev/null 2>&1 &
	@sleep 0.5
	@echo "  $(YELLOW)Step 3:$(NC_CLR) Sending TCP messages..."
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "Hello TCP #1"
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "Hello TCP #2"
	@sleep 0.5
	@sudo pkill -f "tcpdump.*tcp port" 2>/dev/null || true
	@pkill -f "ex_2_01_tcp.py server" 2>/dev/null || true
	@echo ""
	@echo "  $(YELLOW)Step 4:$(NC_CLR) Starting UDP server..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT) > $(LOGS_DIR)/udp_server.log 2>&1 &
	@sleep 1
	@echo "  $(YELLOW)Step 5:$(NC_CLR) Starting UDP capture..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/demo_udp.pcap udp port $(UDP_PORT) > /dev/null 2>&1 &
	@sleep 0.5
	@echo "  $(YELLOW)Step 6:$(NC_CLR) Sending UDP messages..."
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "ping"
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "upper:hello"
	@sleep 0.5
	@sudo pkill -f "tcpdump.*udp port" 2>/dev/null || true
	@pkill -f "ex_2_02_udp.py server" 2>/dev/null || true
	@echo ""
	@echo "$(GREEN)[DEMO]$(NC_CLR) ✓ Complete demonstration"
	@echo "  Captures available in: $(CAPTURES_DIR)/"
	@echo "  Logs available in: $(LOGS_DIR)/"
	@echo ""
	@echo "  $(YELLOW)Next steps:$(NC_CLR)"
	@echo "    make analyze-tcp    # View TCP handshake"
	@echo "    make analyze-udp    # View UDP traffic"

run-lab:
	@echo "$(GREEN)[LAB]$(NC_CLR) Starting interactive laboratory..."
	@echo "  1. Open a new terminal for the server"
	@echo "  2. Run: make tcp-server"
	@echo "  3. In this terminal, run: make tcp-client MSG=\"your message\""
	@echo ""
	@read -p "Press ENTER to start TCP server in this terminal..."
	@make tcp-server

demo-tcp:
	@echo "$(GREEN)[DEMO-TCP]$(NC_CLR) TCP demonstration..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT) &
	@sleep 1 && $(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "$(MSG)"
	@pkill -f "ex_2_01_tcp.py server" 2>/dev/null || true

demo-udp:
	@echo "$(GREEN)[DEMO-UDP]$(NC_CLR) UDP demonstration..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT) &
	@sleep 1 && $(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "ping"
	@pkill -f "ex_2_02_udp.py server" 2>/dev/null || true

# =============================================================================
# MININET
# =============================================================================
mininet-cli:
	@echo "$(GREEN)[MININET]$(NC_CLR) Starting CLI base topology (3 hosts, 1 switch)..."
	@echo "  Useful commands in Mininet:"
	@echo "    nodes          - node list"
	@echo "    net            - topology"
	@echo "    pingall        - connectivity test"
	@echo "    h1 ping h2     - ping between hosts"
	@echo ""
	@$(MININET_SUDO) $(PYTHON) $(TOPO_BASE) --cli

mininet-extended:
	@echo "$(GREEN)[MININET]$(NC_CLR) Starting CLI extended topology (2 subnets + router)..."
	@$(MININET_SUDO) $(PYTHON) $(TOPO_EXT) --cli

mininet-test:
	@echo "$(GREEN)[MININET]$(NC_CLR) Automatic connectivity test..."
	@$(MININET_SUDO) $(PYTHON) $(TOPO_BASE) --test

mininet-clean:
	@echo "$(GREEN)[MININET]$(NC_CLR) Cleaning previous sessions..."
	@$(MININET_SUDO) mn -c 2>/dev/null || true
	@echo "$(GREEN)[MININET]$(NC_CLR) ✓ Cleaned"

# =============================================================================
# SERVER / CLIENT
# =============================================================================
tcp-server:
	@echo "$(GREEN)[TCP-SERVER]$(NC_CLR) Starting on $(BIND_ADDR):$(TCP_PORT)..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT)

tcp-client:
	@echo "$(GREEN)[TCP-CLIENT]$(NC_CLR) Sending to 127.0.0.1:$(TCP_PORT)..."
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "$(MSG)"

udp-server:
	@echo "$(GREEN)[UDP-SERVER]$(NC_CLR) Starting on $(BIND_ADDR):$(UDP_PORT)..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT)

udp-client:
	@echo "$(GREEN)[UDP-CLIENT]$(NC_CLR) Interactive client to 127.0.0.1:$(UDP_PORT)..."
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --interactive

N ?= 10
load-test:
	@echo "$(GREEN)[LOAD-TEST]$(NC_CLR) Test with $(N) concurrent clients..."
	@$(PYTHON) $(EX_TCP) load --host 127.0.0.1 --port $(TCP_PORT) --clients $(N)

# =============================================================================
# CAPTURES (REQUIRED)
# =============================================================================
capture: capture-tcp capture-udp
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) Active captures for TCP and UDP"

capture-tcp:
	@mkdir -p $(CAPTURES_DIR)
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) TCP on lo:$(TCP_PORT)..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/capture_tcp.pcap tcp port $(TCP_PORT) &
	@echo "  PID: $$(pgrep -f 'tcpdump.*tcp port')"

capture-udp:
	@mkdir -p $(CAPTURES_DIR)
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) UDP on lo:$(UDP_PORT)..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/capture_udp.pcap udp port $(UDP_PORT) &
	@echo "  PID: $$(pgrep -f 'tcpdump.*udp port')"

capture-stop:
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) Stopping captures..."
	@sudo pkill tcpdump 2>/dev/null || echo "$(YELLOW)[INFO]$(NC_CLR) No active tcpdump"

analyze-tcp:
	@echo "$(GREEN)[ANALYZE]$(NC_CLR) TCP capture analysis..."
	@if [ -f $(CAPTURES_DIR)/demo_tcp.pcap ]; then \
		echo ""; \
		echo "  Frame | Source IP    | Port | Dest IP      | Port | Flags"; \
		echo "  ------|--------------|------|--------------|------|------"; \
		$(TSHARK) -r $(CAPTURES_DIR)/demo_tcp.pcap -Y "tcp" -T fields \
			-e frame.number -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.flags.str \
			2>/dev/null | while read line; do echo "  $$line"; done; \
		echo ""; \
		echo "$(GREEN)[ANALYZE]$(NC_CLR) TCP handshake (SYN, SYN-ACK, ACK) identifiable in first 3 packets"; \
	else \
		echo "$(RED)[ERROR]$(NC_CLR) TCP capture missing. Run first: make demo-all"; \
	fi

analyze-udp:
	@echo "$(GREEN)[ANALYZE]$(NC_CLR) UDP capture analysis..."
	@if [ -f $(CAPTURES_DIR)/demo_udp.pcap ]; then \
		echo ""; \
		echo "  Frame | Source IP    | Port | Dest IP      | Port | Length"; \
		echo "  ------|--------------|------|--------------|------|--------"; \
		$(TSHARK) -r $(CAPTURES_DIR)/demo_udp.pcap -Y "udp" -T fields \
			-e frame.number -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e frame.len \
			2>/dev/null | while read line; do echo "  $$line"; done; \
		echo ""; \
		echo "$(GREEN)[ANALYZE]$(NC_CLR) UDP: observe lack of handshake and reduced overhead"; \
	else \
		echo "$(RED)[ERROR]$(NC_CLR) UDP capture missing. Run first: make demo-all"; \
	fi

# =============================================================================
# DOCKER (OPTIONAL)
# =============================================================================
docker-build:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Building image..."
	@docker build -t $(DOCKER_IMAGE) -f docker/Dockerfile .

docker-shell:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Interactive shell..."
	@docker run -it --rm --privileged \
		-v $(ROOT_DIR):/workspace -w /workspace \
		$(DOCKER_IMAGE) /bin/bash

docker-demo:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Running demo with docker compose..."
	@docker compose -f docker/docker-compose.yml up --build --abort-on-container-exit

docker-clean:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Stopping and removing docker compose resources..."
	@docker compose -f docker/docker-compose.yml down -v --remove-orphans

# =============================================================================
# CLEANUP (REQUIRED)
# =============================================================================
clean:
	@echo "$(GREEN)[CLEAN]$(NC_CLR) Cleaning processes..."
	@pkill -f "ex_2_01_tcp.py" 2>/dev/null || true
	@pkill -f "ex_2_02_udp.py" 2>/dev/null || true
	@sudo pkill tcpdump 2>/dev/null || true
	@$(MININET_SUDO) mn -c 2>/dev/null || true
	@echo "$(GREEN)[CLEAN]$(NC_CLR) ✓"

reset: clean
	@echo "$(GREEN)[RESET]$(NC_CLR) Complete reset..."
	@rm -rf $(CAPTURES_DIR)/*.pcap $(LOGS_DIR)/*.log $(PCAP_DIR)/*.pcap
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf *.pyc */*.pyc */*/*.pyc
	@echo "$(GREEN)[RESET]$(NC_CLR) ✓"

# =============================================================================
# DEFAULT
# =============================================================================
.DEFAULT_GOAL := help
