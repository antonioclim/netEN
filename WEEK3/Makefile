# ============================================================================
# Makefile — Starter Kit Week 3: Network programming (UDP broadcast and multicast, TCP tunnelling)
# ============================================================================
# Usage:
#   make help         - Show available targets
#   make setup        - Install dependencies (may require sudo)
#   make run-demo     - Run the main demos
#   make run-lab      - Start interactive lab mode (where applicable)
#   make capture      - Capture network traffic
#   make verify       - Verify the environment
#   make clean        - Clean temporary files and processes
#   make reset        - Full reset (clean + reconfigure)
#
# Standard aliases (for cross-week consistency):
#   make demo         - Alias for run-demo
#   make test         - Run smoke tests
#   make docker-demo  - Run the Docker compose demo
#   make docker-clean - Stop Docker compose and clean resources
# ============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset \
        run-all run-all-quick \
        demo-broadcast demo-multicast demo-tunnel demo-multiclient \
        docker-build docker-run docker-compose-up docker-compose-down \
        docker-demo docker-clean \
        lint test mininet-base mininet-extended pack \
        capture-broadcast capture-multicast

# ════════════════════════════════════════════════════════════════════════════
# VARIABILE CONFIGURABILE — WEEK 3 Standard
# ════════════════════════════════════════════════════════════════════════════
PYTHON := python3
MININET_CLI := sudo python3
DOCKER_IMAGE := s3-networking
DOCKER_TAG := latest

# WEEK 3: Plan Porturi Standard
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5300
WEEK := 3
WEEK_PORT_BASE := 5300
PORT_BROADCAST := 5307
PORT_MULTICAST := 5301
PORT_TUNNEL_LISTEN := 5390
PORT_TUNNEL_TARGET := 5380
PORT_MULTICLIENT := 5333
MULTICAST_GROUP := 239.3.3.3

# Directoare
LOG_DIR := logs
PCAP_DIR := pcap
ARTIFACTS_DIR := artifacts

# Culori for output (ANSI)
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# ════════════════════════════════════════════════════════════════════════════
# HELP (target implicit)
# ════════════════════════════════════════════════════════════════════════════
help:
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  $(BOLD)Starter Kit S3 — WEEK 3: Broadcast/Multicast UDP + TCP Tunnel$(NC)$(CYAN)    ║$(NC)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Setup and Verification:$(NC)"
	@echo "  make setup              Installing system + Python dependencies"
	@echo "  make verify             Environment verification (Python, Mininet, tools)"
	@echo "  make test               Run complete smoke test"
	@echo "  make lint               Verify cod Python (flake8)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Automatic Demo (produces artefacts):$(NC)"
	@echo "  make run-all            Demo COMPLET → artifacts/demo.{log,pcap}, validation.txt"
	@echo "  make run-all-quick      Demo RAPID (localhost only, fara Mininet)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Individual Demos (requires Mininet):$(NC)"
	@echo "  make run-demo           Run all demo-urile secvential"
	@echo "  make demo-broadcast     Demo UDP broadcast (base topology)"
	@echo "  make demo-multicast     Demo UDP multicast (base topology)"
	@echo "  make demo-tunnel        Demo TCP tunnel (extended topology)"
	@echo "  make demo-multiclient   Demo server TCP multi-threaded (localhost)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Interactive Lab:$(NC)"
	@echo "  make run-lab            Alias for mininet-base (interactive CLI)"
	@echo "  make mininet-base       Starting base topology (3 hosturi, 1 switch)"
	@echo "  make mininet-extended   Starting extended topology (2 subretele)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Traffic Captures:$(NC)"
	@echo "  make capture            Captura generica (broadcast + multicast)"
	@echo "  make capture-broadcast  tcpdump capture for broadcast"
	@echo "  make capture-multicast  tcpdump capture for multicast + IGMP"
	@echo ""
	@echo "$(GREEN)$(BOLD)Docker (alternative to Mininet):$(NC)"
	@echo "  make docker-build       Build image Docker"
	@echo "  make docker-run         Run container interactiv"
	@echo "  make docker-demo        Run demo with docker-compose (recommended)"
	@echo "  make docker-clean       Stop and remove docker resources"
	@echo "  make docker-compose-up  Starting stack multi-container (detached)"
	@echo "  make docker-compose-down Stopping stack"
	@echo ""
	@echo "$(GREEN)$(BOLD)Cleanup si Reset:$(NC)"
	@echo "  make clean              Cleanup Mininet + procese + temp"
	@echo "  make reset              Complete reset (clean + verify)"
	@echo "  make pack               Create archive .zip for distributie"
	@echo ""
	@echo "$(YELLOW)Porturi WEEK 3: BCAST=$(PORT_BROADCAST) MCAST=$(PORT_MULTICAST) TUNNEL=$(PORT_TUNNEL_LISTEN)$(NC)"
	@echo "$(YELLOW)Note: Most commands require sudo permissions for Mininet.$(NC)"
	@echo ""

# ════════════════════════════════════════════════════════════════════════════
# SETUP — Installing dependencies
# ════════════════════════════════════════════════════════════════════════════
setup:
	@echo "$(CYAN)[SETUP] Installing system and Python dependencies...$(NC)"
	@bash scripts/setup.sh
	@echo "$(GREEN)[OK] Setup complete. Run 'make verify' to verify.$(NC)"

setup-python:
	@echo "$(CYAN)[SETUP] Installing dependencies Python...$(NC)"
	@$(PYTHON) -m pip install --break-system-packages -r requirements.txt 2>/dev/null || \
	$(PYTHON) -m pip install -r requirements.txt
	@echo "$(GREEN)[OK] Python dependencies installed.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# VERIFY — Environment verification
# ════════════════════════════════════════════════════════════════════════════
verify:
	@echo "$(CYAN)[VERIFY] Verifying work environment...$(NC)"
	@bash scripts/verify.sh
	@echo "$(GREEN)[OK] Mediul este configurat corect.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# TEST — Smoke test
# ════════════════════════════════════════════════════════════════════════════
test:
	@echo "$(CYAN)[TEST] Run smoke test...$(NC)"
	@bash tests/smoke_test.sh
	@echo "$(GREEN)[OK] Smoke test complete.$(NC)"

test-python:
	@echo "$(CYAN)[TEST] Verify sintaxa Python...$(NC)"
	@$(PYTHON) -m py_compile python/examples/*.py
	@$(PYTHON) -m py_compile python/templates/*.py 2>/dev/null || true
	@$(PYTHON) -m py_compile python/utils/*.py
	@echo "$(GREEN)[OK] Sintaxa Python valida.$(NC)"

lint:
	@echo "$(CYAN)[LINT] Verify cod Python...$(NC)"
	@$(PYTHON) -m flake8 python/ --max-line-length=120 --ignore=E501,W503 || true
	@echo "$(GREEN)[OK] Lint complete.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-ALL — Complete automatic demo (produces artefacts)
# ════════════════════════════════════════════════════════════════════════════
run-all:
	@echo "$(CYAN)[RUN-ALL] Complete automatic demo WEEK $(WEEK)...$(NC)"
	@bash scripts/run_all.sh
	@echo "$(GREEN)[OK] Artefacts generated in $(ARTIFACTS_DIR)/$(NC)"

run-all-quick:
	@echo "$(CYAN)[RUN-ALL] Quick demo (localhost only)...$(NC)"
	@bash scripts/run_all.sh --quick
	@echo "$(GREEN)[OK] Quick demo complete.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-DEMO — Run demo-uri
# ════════════════════════════════════════════════════════════════════════════
run-demo: demo-broadcast demo-multicast demo-tunnel demo-multiclient
	@echo "$(GREEN)[OK] all demo-urile au rulat cu succes.$(NC)"

demo-broadcast:
	@echo "$(CYAN)[DEMO] UDP Broadcast...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Starting base topology cu test broadcast...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_base.py --test broadcast 2>&1 | tee $(LOG_DIR)/demo_broadcast.log
	@echo "$(GREEN)[OK] Demo broadcast complete. Log: $(LOG_DIR)/demo_broadcast.log$(NC)"

demo-multicast:
	@echo "$(CYAN)[DEMO] UDP Multicast...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Starting base topology cu test multicast...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_base.py --test multicast 2>&1 | tee $(LOG_DIR)/demo_multicast.log
	@echo "$(GREEN)[OK] Demo multicast complete. Log: $(LOG_DIR)/demo_multicast.log$(NC)"

demo-tunnel:
	@echo "$(CYAN)[DEMO] TCP Tunnel...$(NC)"
	@mkdir -p $(LOG_DIR)
	@echo "$(YELLOW)Starting extended topology cu test tunnel...$(NC)"
	$(MININET_CLI) mininet/topologies/topo_extended.py --test tunnel 2>&1 | tee $(LOG_DIR)/demo_tunnel.log
	@echo "$(GREEN)[OK] Demo tunnel complete. Log: $(LOG_DIR)/demo_tunnel.log$(NC)"

demo-multiclient:
	@echo "$(CYAN)[DEMO] Server TCP Multiclient (localhost)...$(NC)"
	@echo "$(YELLOW)Starting server in background for 10 secunde...$(NC)"
	@timeout 10 $(PYTHON) python/examples/ex05_tcp_multiclient.py &
	@sleep 1
	@echo "test1" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "test2" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "test3" | nc -w 1 127.0.0.1 $(PORT_MULTICLIENT) || true
	@echo "$(GREEN)[OK] Demo multiclient complete.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RUN-LAB — lab interactiv
# ════════════════════════════════════════════════════════════════════════════
run-lab: mininet-base

mininet-base:
	@echo "$(CYAN)[MININET] Starting BASE topology (interactive CLI)...$(NC)"
	@echo ""
	@echo "$(YELLOW)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  Topologie: h1 ─── s1 ─── h2 ─── h3  (10.0.0.0/24)               ║$(NC)"
	@echo "$(YELLOW)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Useful commands in CLI mininet>:$(NC)"
	@echo "  h1 python3 python/examples/ex01_udp_broadcast.py send --count 5"
	@echo "  h2 python3 python/examples/ex01_udp_broadcast.py recv --count 5"
	@echo "  h3 tcpdump -ni h3-eth0 'udp port $(PORT_BROADCAST)'"
	@echo "  pingall"
	@echo "  exit"
	@echo ""
	$(MININET_CLI) mininet/topologies/topo_base.py --cli

mininet-extended:
	@echo "$(CYAN)[MININET] Starting EXTENDED topology (interactive CLI)...$(NC)"
	@echo ""
	@echo "$(YELLOW)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  netA: a1,a2 ─── sA ─── r1 ─── sB ─── b1,b2 :netB               ║$(NC)"
	@echo "$(YELLOW)║  10.0.1.0/24           .254 .254           10.0.2.0/24          ║$(NC)"
	@echo "$(YELLOW)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Useful commands for TCP tunnel:$(NC)"
	@echo "  b1 python3 python/examples/ex04_echo_server.py --listen 0.0.0.0:8080"
	@echo "  r1 python3 python/examples/ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 10.0.2.1:8080"
	@echo "  a1 bash -lc 'echo test | nc 10.0.1.254 9090 -w 2'"
	@echo ""
	$(MININET_CLI) mininet/topologies/topo_extended.py --cli

# ════════════════════════════════════════════════════════════════════════════
# CAPTURE — Capturi de trafic
# ════════════════════════════════════════════════════════════════════════════
capture: capture-broadcast capture-multicast
	@echo "$(GREEN)[OK] Capturi complete in $(PCAP_DIR)/$(NC)"

capture-broadcast:
	@echo "$(CYAN)[CAPTURE] Starting captura broadcast...$(NC)"
	@mkdir -p $(PCAP_DIR)
	@bash scripts/capture_traffic.sh broadcast $(PORT_BROADCAST) 10

capture-multicast:
	@echo "$(CYAN)[CAPTURE] Starting captura multicast + IGMP...$(NC)"
	@mkdir -p $(PCAP_DIR)
	@bash scripts/capture_traffic.sh multicast $(PORT_MULTICAST) 10

# ════════════════════════════════════════════════════════════════════════════
# DOCKER
# ════════════════════════════════════════════════════════════════════════════
docker-build:
	@echo "$(CYAN)[DOCKER] Build image $(DOCKER_IMAGE):$(DOCKER_TAG)...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f docker/Dockerfile .
	@echo "$(GREEN)[OK] Imagine construita: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-run:
	@echo "$(CYAN)[DOCKER] Run container interactiv...$(NC)"
	docker run -it --rm --privileged \
		-v $(PWD):/app \
		--workdir /app \
		--name s3-networking-dev \
		$(DOCKER_IMAGE):$(DOCKER_TAG) bash

docker-compose-up:
	@echo "$(CYAN)[DOCKER] Starting stack docker-compose...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d
	@echo "$(GREEN)[OK] Stack started. Verificati: docker-compose -f docker/docker-compose.yml ps$(NC)"

docker-compose-down:
	@echo "$(CYAN)[DOCKER] Stopping stack docker-compose...$(NC)"
	docker-compose -f docker/docker-compose.yml down

# Standard aliases for cross-week consistency
docker-demo:
	@echo "$(CYAN)[DOCKER] Running demo with docker-compose...$(NC)"
	@echo "$(YELLOW)Starting server and router in background...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d server router
	@echo "$(YELLOW)Waiting for services to start...$(NC)"
	@sleep 3
	@echo "$(YELLOW)Testing TCP tunnel: client → router:9090 → server:8080$(NC)"
	@echo "HELLO_FROM_DOCKER" | docker-compose -f docker/docker-compose.yml run --rm client \
		bash -c "nc -w 2 router 9090" || echo "[INFO] Test completed"
	@echo ""
	@echo "$(YELLOW)Testing direct to server: client → server:8080$(NC)"
	@echo "DIRECT_TEST" | docker-compose -f docker/docker-compose.yml run --rm client \
		bash -c "nc -w 2 server 8080" || echo "[INFO] Test completed"
	@echo ""
	@echo "$(GREEN)[OK] Docker demo complete. Stopping services...$(NC)"
	docker-compose -f docker/docker-compose.yml down

docker-clean:
	@echo "$(CYAN)[DOCKER] Stopping and removing docker-compose resources...$(NC)"
	docker-compose -f docker/docker-compose.yml down -v --remove-orphans
	@echo "$(GREEN)[OK] Docker cleanup complete.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# CLEAN — Cleanup
# ════════════════════════════════════════════════════════════════════════════
clean:
	@echo "$(CYAN)[CLEAN] Cleanup...$(NC)"
	@bash scripts/cleanup.sh
	@rm -rf $(LOG_DIR) __pycache__ python/__pycache__ python/*/__pycache__
	@rm -f *.pcap *.pcapng
	@echo "$(GREEN)[OK] Cleanup complete.$(NC)"

clean-docker:
	@echo "$(CYAN)[CLEAN] Cleanup Docker...$(NC)"
	docker-compose -f docker/docker-compose.yml down -v 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "$(GREEN)[OK] Docker cleanup complete.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# RESET — Complete reset
# ════════════════════════════════════════════════════════════════════════════
reset: clean
	@echo "$(CYAN)[RESET] Environment verification after cleanup...$(NC)"
	@bash scripts/verify.sh
	@echo "$(GREEN)[OK] Complete reset.$(NC)"

# ════════════════════════════════════════════════════════════════════════════
# PACK — Create archive
# ════════════════════════════════════════════════════════════════════════════
pack:
	@echo "$(CYAN)[PACK] Create archive WEEK3_EN(last)GPT.zip...$(NC)"
	@cd .. && zip -r WEEK3_EN(last)GPT.zip WEEK3 \
		-x "*.pyc" -x "__pycache__/*" -x "__pycache__/**" -x "__MACOSX/*" -x ".DS_Store" -x "Thumbs.db"
	@mv ../WEEK3_EN(last)GPT.zip . 2>/dev/null || true
	@echo "$(GREEN)[OK] Archive created: WEEK3_EN(last)GPT.zip$(NC)"
