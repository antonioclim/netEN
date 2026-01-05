# ============================================================================
# Makefile – Week 6: Computer Networks
# NAT/PAT · ARP · DHCP · NDP · ICMP · SDN/OpenFlow
# ASE-CSIE, Business Informatics
# ============================================================================

.PHONY: all setup check clean help \
        nat-demo sdn-demo routing-demo run-all \
        controller-start controller-stop controller-status \
        smoke-test docker-build docker-run slides \
        install-deps verify-tools capture verify reset

# Colours for terminal output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
CYAN   := \033[0;36m
BOLD   := \033[1m
RESET  := \033[0m

# Paths
SCRIPTS_DIR    := scripts
TOPO_DIR       := mininet/topologies
CONTROLLER_DIR := seminar/python/controllers
APPS_DIR       := seminar/python/apps
SLIDES_DIR     := slides
TESTS_DIR      := tests
PCAP_DIR       := pcap

# Controller settings
CONTROLLER_PY  := $(CONTROLLER_DIR)/sdn_policy_controller.py
CONTROLLER_PID := /tmp/osken_controller.pid

# Use sudo only when not already running as root
SUDO := $(shell [ "$$(id -u)" -eq 0 ] && echo "" || echo "sudo")
OFP_PORT       := 6633

# ============================================================================
# DEFAULT & HELP
# ============================================================================

all: help

help:
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Starterkit S6 – NAT/PAT, SDN, Traffic Analysis$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)Installation & Verification:$(RESET)"
	@echo "  $(GREEN)make setup$(RESET)        – Install all dependencies"
	@echo "  $(GREEN)make check$(RESET)        – Verify available tools"
	@echo "  $(GREEN)make verify-tools$(RESET) – Verify detailed tool versions"
	@echo ""
	@echo "$(BOLD)Interactive Demos:$(RESET)"
	@echo "  $(GREEN)make nat-demo$(RESET)     – Start NAT topology with PAT"
	@echo "  $(GREEN)make sdn-demo$(RESET)     – Start controller + SDN topology"
	@echo "  $(GREEN)make routing-demo$(RESET) – Triangle topology for routing"
	@echo "  $(GREEN)make run-all$(RESET)      – Automated demo (artifacts/)"
	@echo ""
	@echo "$(BOLD)SDN Controller:$(RESET)"
	@echo "  $(GREEN)make controller-start$(RESET)  – Start OS-Ken in background"
	@echo "  $(GREEN)make controller-stop$(RESET)   – Stop controller"
	@echo "  $(GREEN)make controller-status$(RESET) – Check controller status"
	@echo ""
	@echo "$(BOLD)Capture & Verification:$(RESET)"
	@echo "  $(GREEN)make capture$(RESET)      – Start packet capture"
	@echo "  $(GREEN)make verify$(RESET)       – Verify that demos function"
	@echo ""
	@echo "$(BOLD)Tests & Validation:$(RESET)"
	@echo "  $(GREEN)make smoke-test$(RESET)   – Run validation tests"
	@echo ""
	@echo "$(BOLD)Docker (complete isolation):$(RESET)"
	@echo "  $(GREEN)make docker-build$(RESET) – Build Docker image"
	@echo "  $(GREEN)make docker-run$(RESET)   – Run interactive container"
	@echo ""
	@echo "$(BOLD)Presentation & Cleanup:$(RESET)"
	@echo "  $(GREEN)make slides$(RESET)       – Open interactive presentation"
	@echo "  $(GREEN)make clean$(RESET)        – Clean Mininet/OVS artefacts"
	@echo "  $(GREEN)make reset$(RESET)        – Complete reset (clean + kill processes)"
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""

# ============================================================================
# SETUP & DEPENDENCIES
# ============================================================================

setup:
	@echo "$(CYAN)>>> Installing system dependencies...$(RESET)"
	@chmod +x $(SCRIPTS_DIR)/setup.sh 2>/dev/null || true
	@if [ -f $(SCRIPTS_DIR)/setup.sh ]; then \
		$(SUDO) $(SCRIPTS_DIR)/setup.sh; \
	else \
		echo "$(YELLOW)setup.sh does not exist, manual installation:$(RESET)"; \
		$(SUDO) apt-get update; \
		$(SUDO) apt-get install -y python3 python3-pip mininet openvswitch-switch tcpdump tshark iptables; \
		pip3 install --break-system-packages os-ken scapy; \
	fi
	@echo "$(GREEN)✓ Setup complete!$(RESET)"

install-deps:
	@echo "$(CYAN)>>> Installing Python packages...$(RESET)"
	@pip3 install --break-system-packages os-ken scapy
	@echo "$(GREEN)✓ Python packages installed.$(RESET)"

check:
	@echo ""
	@echo "$(BOLD)Verifying required tools:$(RESET)"
	@echo ""
	@command -v python3 >/dev/null && echo "  $(GREEN)✓$(RESET) python3" || echo "  $(RED)✗$(RESET) python3"
	@command -v mn >/dev/null && echo "  $(GREEN)✓$(RESET) mininet (mn)" || echo "  $(RED)✗$(RESET) mininet"
	@command -v ovs-vsctl >/dev/null && echo "  $(GREEN)✓$(RESET) openvswitch" || echo "  $(RED)✗$(RESET) openvswitch"
	@command -v tcpdump >/dev/null && echo "  $(GREEN)✓$(RESET) tcpdump" || echo "  $(RED)✗$(RESET) tcpdump"
	@command -v tshark >/dev/null && echo "  $(GREEN)✓$(RESET) tshark" || echo "  $(RED)✗$(RESET) tshark"
	@command -v iptables >/dev/null && echo "  $(GREEN)✓$(RESET) iptables" || echo "  $(RED)✗$(RESET) iptables"
	@command -v osken-manager >/dev/null 2>&1 && echo "  $(GREEN)✓$(RESET) osken-manager (binary)" || echo "  $(YELLOW)!$(RESET) osken-manager (not in PATH, expected with os-ken < 4.0.0)"
	@echo ""
	@python3 -c "import os_ken" 2>/dev/null && echo "  $(GREEN)✓$(RESET) os_ken (Python)" || echo "  $(RED)✗$(RESET) os_ken module"
	@python3 -c "import scapy" 2>/dev/null && echo "  $(GREEN)✓$(RESET) scapy (Python)" || echo "  $(RED)✗$(RESET) scapy module"
	@echo ""

verify-tools:
	@echo "$(BOLD)Tool versions:$(RESET)"
	@echo ""
	@python3 --version 2>/dev/null || echo "python3: not found"
	@mn --version 2>/dev/null || echo "mininet: not found"
	@ovs-vsctl --version 2>/dev/null | head -1 || echo "ovs: not found"
	@tcpdump --version 2>/dev/null | head -1 || echo "tcpdump: not found"
	@tshark --version 2>/dev/null | head -1 || echo "tshark: not found"
	@pip3 show os-ken 2>/dev/null | grep -E "^(Name|Version)" || echo "os-ken: not installed"
	@echo ""

# ============================================================================
# NAT/PAT DEMO
# ============================================================================

nat-demo: clean
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  NAT/PAT Demo – Observing address translation$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topology:$(RESET)"
	@echo "  h1 (192.168.1.10) ──┐"
	@echo "                      ├── rnat ── h3 (203.0.113.2)"
	@echo "  h2 (192.168.1.20) ──┘    │"
	@echo "                       MASQUERADE"
	@echo ""
	@echo "$(YELLOW)Suggested exercises:$(RESET)"
	@echo "  1. $(BOLD)h1 ping h3$(RESET) or $(BOLD)h1 ping 203.0.113.2$(RESET)"
	@echo "  2. $(BOLD)rnat iptables -t nat -L -n -v$(RESET) – view NAT rules"
	@echo "  3. Start $(BOLD)nat_observer$(RESET) on h3, then connect from h1/h2"
	@echo ""
	@echo "$(GREEN)>>> Starting topology...$(RESET)"
	@echo ""
	@sudo python3 $(TOPO_DIR)/topo_nat.py --cli

# ============================================================================
# SDN / OPENFLOW DEMO
# ============================================================================

sdn-demo: clean controller-start
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  SDN/OpenFlow Demo – Centralised control$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topology:$(RESET)"
	@echo "  h1 (10.0.6.11) ──┐"
	@echo "  h2 (10.0.6.12) ──┼── s1 (OVS) ←→ Controller (6633)"
	@echo "  h3 (10.0.6.13) ──┘"
	@echo ""
	@echo "$(YELLOW)Suggested exercises:$(RESET)"
	@echo "  1. $(BOLD)h1 ping 10.0.6.12$(RESET) – verify permitted connectivity"
	@echo "  2. $(BOLD)h1 ping 10.0.6.13$(RESET) – verify blocked traffic"
	@echo "  3. $(BOLD)sh ovs-ofctl -O OpenFlow13 dump-flows s1$(RESET) – view flows"
	@echo ""
	@echo "$(GREEN)>>> Starting topology with active controller...$(RESET)"
	@echo ""
	@sleep 2
	@sudo python3 $(TOPO_DIR)/topo_sdn.py --cli

# ============================================================================
# RUN-ALL (Automated demo non-interactive)
# ============================================================================

run-all:
	@echo "$(CYAN)>>> Automated demo (produces artifacts/)...$(RESET)"
	@chmod +x $(SCRIPTS_DIR)/run_all.sh 2>/dev/null || true
	@sudo $(SCRIPTS_DIR)/run_all.sh

# ============================================================================
# CONTROLLER SDN
# ============================================================================

controller-start:
	@if [ -f $(CONTROLLER_PID) ] && kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
		echo "$(YELLOW)Controller already running (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
	else \
		echo "$(CYAN)>>> Starting OS-Ken controller in background...$(RESET)"; \
	echo "$(YELLOW)OS-Ken 4.0.0 removed osken-manager and os_ken.cmd.*. SDN demo will install OVS flows directly.$(RESET)"; \
		echo $$! > $(CONTROLLER_PID); \
		sleep 2; \
		if kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
			echo "$(GREEN)✓ Controller started (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
		else \
			echo "$(YELLOW)Controller start skipped (CLI removed in os-ken 4.0.0).$(RESET)"; \
		fi \
	fi

controller-stop:
	@if [ -f $(CONTROLLER_PID) ]; then \
		echo "$(CYAN)>>> Stopping controller...$(RESET)"; \
		$(SUDO) kill $$(cat $(CONTROLLER_PID)) 2>/dev/null || true; \
		rm -f $(CONTROLLER_PID); \
		echo "$(GREEN)✓ Controller stopped.$(RESET)"; \
	else \
		echo "$(YELLOW)Controller not running.$(RESET)"; \
	fi

controller-status:
	@if [ -f $(CONTROLLER_PID) ] && $(SUDO) kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
		echo "$(GREEN)✓ Controller active (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
		echo "  Log: /tmp/osken.log"; \
	else \
		echo "$(YELLOW)✗ Controller inactive$(RESET)"; \
	fi

# ============================================================================
# ROUTING DEMO
# ============================================================================

routing-demo: clean
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Routing Demo – Triangle topology$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topology:$(RESET)"
	@echo "          r1 (10.0.1.1)"
	@echo "         /  \\"
	@echo "        /    \\"
	@echo "    r2 ────── r3"
	@echo "  (10.0.2.1)  (10.0.3.1)"
	@echo ""
	@echo "$(YELLOW)Suggested exercises:$(RESET)"
	@echo "  1. $(BOLD)r1 ip route$(RESET) – verify configured routes"
	@echo "  2. $(BOLD)r1 traceroute -n 10.0.3.1$(RESET) – path towards r3"
	@echo "  3. Disable r1-r3: $(BOLD)r1 ip link set r1-eth1 down$(RESET)"
	@echo "  4. Rerun traceroute – observe alternative route"
	@echo ""
	@echo "$(GREEN)>>> Starting topology...$(RESET)"
	@echo ""
	@sudo python3 $(TOPO_DIR)/topo_triangle.py --cli 2>/dev/null || \
		echo "$(YELLOW)topo_triangle.py does not exist in this kit$(RESET)"

# ============================================================================
# CAPTURE & VERIFY
# ============================================================================

capture:
	@mkdir -p $(PCAP_DIR)
	@echo "$(CYAN)>>> Directory pcap/ prepared for captures$(RESET)"
	@echo "Use: tcpdump -w $(PCAP_DIR)/capture.pcap -i <interface>"

verify:
	@echo "$(CYAN)>>> Verifying functionality...$(RESET)"
	@echo "Run: make smoke-test"

# ============================================================================
# TESTING
# ============================================================================

smoke-test:
	@echo "$(CYAN)>>> Running validation tests...$(RESET)"
	@if [ -f $(TESTS_DIR)/smoke_test.sh ]; then \
		chmod +x $(TESTS_DIR)/smoke_test.sh; \
		$(TESTS_DIR)/smoke_test.sh; \
	else \
		echo "$(YELLOW)smoke_test.sh does not exist, running inline test:$(RESET)"; \
		echo "Testing NAT topology..."; \
		$(SUDO) python3 $(TOPO_DIR)/topo_nat.py --test || true; \
	fi

# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	@echo "$(CYAN)>>> Building Docker image...$(RESET)"
	@if [ -f docker/Dockerfile ]; then \
		docker build -t netlab-s6:latest -f docker/Dockerfile .; \
		echo "$(GREEN)✓ Image built: netlab-s6:latest$(RESET)"; \
	else \
		echo "$(YELLOW)Dockerfile does not exist$(RESET)"; \
	fi

docker-run:
	@echo "$(CYAN)>>> Starting Docker container interactively...$(RESET)"
	@docker run -it --rm --privileged \
		--name netlab-s6 \
		-v $(PWD):/workspace \
		-w /workspace \
		-p 6633:6633 \
		-p 6653:6653 \
		netlab-s6:latest \
		/bin/bash || echo "$(YELLOW)Docker image does not exist. Run: make docker-build$(RESET)"

docker-clean:
	@echo "$(CYAN)>>> Cleaning containers and images...$(RESET)"
	@docker rm -f netlab-s6 2>/dev/null || true
	@docker rmi netlab-s6:latest 2>/dev/null || true
	@echo "$(GREEN)✓ Docker cleanup complete.$(RESET)"

# ============================================================================
# SLIDES
# ============================================================================

slides:
	@echo "$(CYAN)>>> Opening interactive presentation...$(RESET)"
	@if command -v xdg-open >/dev/null; then \
		xdg-open $(SLIDES_DIR)/theory.html 2>/dev/null || \
		echo "$(YELLOW)Open manually: $(SLIDES_DIR)/theory.html$(RESET)"; \
	elif command -v open >/dev/null; then \
		open $(SLIDES_DIR)/theory.html; \
	else \
		echo "$(YELLOW)Open manually: $(SLIDES_DIR)/theory.html$(RESET)"; \
	fi

# ============================================================================
# CLEANUP
# ============================================================================

clean: controller-stop
	@echo "$(CYAN)>>> Cleaning Mininet/OVS artefacts...$(RESET)"
	@timeout 15s $(SUDO) mn -c 2>/dev/null || true
	@$(SUDO) ovs-vsctl --if-exists del-br s1 2>/dev/null || true
	@$(SUDO) ovs-vsctl --if-exists del-br s2 2>/dev/null || true
	@rm -f $(CONTROLLER_PID)
	@echo "$(GREEN)✓ Cleanup complete.$(RESET)"

reset: clean docker-clean
	@echo "$(CYAN)>>> Complete reset (including Docker)...$(RESET)"
	@$(SUDO) rm -f /tmp/osken.log /tmp/*.pcap 2>/dev/null || true
	@$(SUDO) systemctl restart openvswitch-switch 2>/dev/null || true
	@echo "$(GREEN)✓ Complete reset.$(RESET)"

deep-clean: reset
	@$(SUDO) rm -f /tmp/osken.log /tmp/*.pcap 2>/dev/null || true
	@echo "$(GREEN)✓ Deep cleanup complete.$(RESET)"
