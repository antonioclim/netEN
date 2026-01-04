# =============================================================================
# Makefile – StarterKit Week 11 (Computer Networks)
# =============================================================================
# Complete automation: setup, run-demo, run-lab, capture, verify, clean, reset
# Usage: make help
# =============================================================================

.PHONY: help setup setup-full run-demo run-lab capture verify clean reset \
        demo-nginx demo-nginx-stop demo-custom-lb demo-custom-lb-stop \
        demo-mininet demo-mininet-cli demo-dns demo-ftp demo-ssh demo-all \
        backends-start backends-stop lb-start lb-stop \
        benchmark benchmark-heavy test capture-traffic

SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
PYTHON := python3
DOCKER_COMPOSE := docker compose

# Ports
LB_PORT := 8080
B1_PORT := 8001
B2_PORT := 8002
B3_PORT := 8003

# Colours
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m

# =============================================================================
# HELP
# =============================================================================

help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════════╗"
	@echo "║     StarterKit Week 11 – Computer Networks                               ║"
	@echo "║     Application Protocols (FTP/DNS/SSH) + Load Balancing                 ║"
	@echo "╚══════════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "$(GREEN)SETUP & VERIFICATION$(NC)"
	@echo "  make setup          Baseline installation (Python deps, tools)"
	@echo "  make setup-full     Complete installation (+ Docker + Mininet)"
	@echo "  make verify         Environment verification (all components)"
	@echo ""
	@echo "$(GREEN)AUTOMATIC DEMO (STANDARD)$(NC)"
	@echo "  make run-all        Complete automatic demo → artifacts/*.{log,pcap,txt}"
	@echo "  make smoke-test     Artefact and syntax verification"
	@echo ""
	@echo "$(GREEN)MAIN DEMOS$(NC)"
	@echo "  make run-demo       Run complete demonstration (seminar)"
	@echo "  make run-lab        Run laboratory step by step"
	@echo "  make demo-all       Run all demos sequentially"
	@echo ""
	@echo "$(BLUE)─── Seminar Demos (Load Balancing) ───$(NC)"
	@echo "  make demo-nginx     Nginx reverse proxy demo (Docker)"
	@echo "  make demo-custom-lb Custom Python LB demo (Docker)"
	@echo "  make demo-mininet   Mininet topology demo with LB"
	@echo ""
	@echo "$(BLUE)─── Lecture Demos (Application Protocols) ───$(NC)"
	@echo "  make demo-dns       Educational DNS client demo"
	@echo "  make demo-ftp       Active/passive FTP demo (Docker)"
	@echo "  make demo-ssh       SSH provisioning demo (Docker)"
	@echo ""
	@echo "$(GREEN)PYTHON EXERCISES (standalone)$(NC)"
	@echo "  make backends-start Start 3 local HTTP backends"
	@echo "  make backends-stop  Stop backends"
	@echo "  make lb-start       Start load balancer (round-robin)"
	@echo "  make lb-start-lc    Start load balancer (least_conn)"
	@echo "  make lb-start-ip    Start load balancer (ip_hash)"
	@echo "  make lb-stop        Stop load balancer"
	@echo ""
	@echo "$(GREEN)TESTS & BENCHMARK$(NC)"
	@echo "  make test           Run smoke tests"
	@echo "  make benchmark      Apache Bench (1000 req, 10 concurrent)"
	@echo "  make benchmark-heavy Heavy benchmark (10000 req, 50 concurrent)"
	@echo ""
	@echo "$(GREEN)INSTRUMENTATION$(NC)"
	@echo "  make capture        Simplified traffic capture"
	@echo "  make capture-traffic tcpdump capture on port 8080"
	@echo ""
	@echo "$(GREEN)CLEANUP$(NC)"
	@echo "  make clean          Stop containers + Mininet cleanup"
	@echo "  make reset          Complete cleanup + delete Docker images"
	@echo ""

# =============================================================================
# SETUP & VERIFY
# =============================================================================

setup:
	@echo "$(GREEN)[SETUP]$(NC) Installing baseline dependencies..."
	@bash $(ROOT_DIR)/scripts/setup.sh
	@echo "$(GREEN)[OK]$(NC) Baseline setup complete."

setup-full:
	@echo "$(GREEN)[SETUP]$(NC) Complete installation (all components)..."
	@bash $(ROOT_DIR)/scripts/setup.sh --full
	@echo "$(GREEN)[OK]$(NC) Complete setup finished."

verify:
	@echo "$(GREEN)[VERIFY]$(NC) Verifying environment..."
	@bash $(ROOT_DIR)/scripts/verify.sh
	@echo "$(GREEN)[OK]$(NC) Verification complete."

# =============================================================================
# AUTOMATIC STANDARD DEMO (run-all, smoke-test)
# =============================================================================

run-all:
	@echo "$(GREEN)[RUN-ALL]$(NC) Complete automatic demo..."
	@bash $(ROOT_DIR)/scripts/run_all.sh
	@echo "$(GREEN)[OK]$(NC) Artefacts generated in artifacts/"

run-all-no-capture:
	@echo "$(GREEN)[RUN-ALL]$(NC) Automatic demo without capture..."
	@bash $(ROOT_DIR)/scripts/run_all.sh --no-capture
	@echo "$(GREEN)[OK]$(NC) Artefacts generated in artifacts/"

smoke-test:
	@echo "$(GREEN)[SMOKE-TEST]$(NC) Verifying artefacts and syntax..."
	@bash $(ROOT_DIR)/tests/smoke_test.sh
	@echo "$(GREEN)[OK]$(NC) Smoke test complete."

# =============================================================================
# MAIN DEMO (run-demo, run-lab)
# =============================================================================

run-demo: demo-nginx
	@echo ""
	@echo "$(GREEN)[DEMO]$(NC) Complete seminar demo."
	@echo "$(YELLOW)[INFO]$(NC) Nginx stack running. Test with: curl http://localhost:$(LB_PORT)/"
	@echo "$(YELLOW)[INFO]$(NC) To stop: make clean"

run-lab:
	@echo "$(GREEN)[LAB]$(NC) Step by step laboratory..."
	@echo ""
	@echo "$(BLUE)═══ STEP 0: Environment verification ═══$(NC)"
	@make verify || (echo "$(RED)[!] Run 'make setup' first$(NC)" && exit 1)
	@echo ""
	@echo "$(BLUE)═══ STEP 1: Nginx Demo ═══$(NC)"
	@echo "Start demo with: make demo-nginx"
	@echo "Test with: curl http://localhost:8080/"
	@echo ""
	@echo "$(BLUE)═══ STEP 2: Custom LB Demo ═══$(NC)"
	@echo "Stop Nginx: make demo-nginx-stop"
	@echo "Start custom LB: make demo-custom-lb"
	@echo ""
	@echo "$(BLUE)═══ STEP 3: Python Exercises ═══$(NC)"
	@echo "make backends-start && make lb-start"
	@echo "curl http://localhost:8080/ (repeat multiple times)"
	@echo ""
	@echo "$(BLUE)═══ STEP 4: Mininet (requires sudo) ═══$(NC)"
	@echo "make demo-mininet"
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) See docs/lab.md for detailed instructions."

# =============================================================================
# DOCKER DEMOS (SEMINAR)
# =============================================================================

demo-nginx:
	@echo "$(GREEN)[DEMO]$(NC) Starting Nginx reverse proxy..."
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) up -d
	@sleep 3
	@echo ""
	@echo "$(YELLOW)[TEST]$(NC) Sending 9 requests (expecting round-robin):"
	@for i in 1 2 3 4 5 6 7 8 9; do \
		response=$$(curl -s http://localhost:$(LB_PORT)/ 2>/dev/null | head -1); \
		echo "  Request $$i: $$response"; \
	done
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) Nginx stack running on port $(LB_PORT)"
	@echo "$(GREEN)[INFO]$(NC) Logs: cd docker/nginx_compose && docker compose logs -f"

demo-nginx-stop:
	@echo "$(YELLOW)[STOP]$(NC) Stopping Nginx stack..."
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Nginx stopped."

demo-custom-lb:
	@echo "$(GREEN)[DEMO]$(NC) Starting custom Python LB in Docker..."
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) up -d --build
	@sleep 4
	@echo ""
	@echo "$(YELLOW)[TEST]$(NC) Sending 9 requests:"
	@for i in 1 2 3 4 5 6 7 8 9; do \
		response=$$(curl -s http://localhost:$(LB_PORT)/ 2>/dev/null | head -1); \
		echo "  Request $$i: $$response"; \
	done
	@echo ""
	@echo "$(GREEN)[INFO]$(NC) Custom LB stack running on port $(LB_PORT)"

demo-custom-lb-stop:
	@echo "$(YELLOW)[STOP]$(NC) Stopping custom LB stack..."
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Custom LB stopped."

# =============================================================================
# DOCKER DEMOS (LECTURE - Protocols)
# =============================================================================

demo-dns:
	@echo "$(GREEN)[DEMO]$(NC) Educational DNS client..."
	@echo ""
	@echo "$(BLUE)─── A Query for google.com ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query google.com --type A 2>/dev/null || \
		echo "$(YELLOW)[INFO]$(NC) Install dnspython: pip3 install dnspython"
	@echo ""
	@echo "$(BLUE)─── MX Query for google.com ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query google.com --type MX 2>/dev/null || true
	@echo ""
	@echo "$(BLUE)─── NS Query for ase.ro ───$(NC)"
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_03_dns_client.py --query ase.ro --type NS 2>/dev/null || true

demo-ftp:
	@echo "$(GREEN)[DEMO]$(NC) FTP Demo (requires Docker)..."
	@if [ -d "$(ROOT_DIR)/docker/ftp_demo" ] && [ -f "$(ROOT_DIR)/docker/ftp_demo/docker-compose.yml" ]; then \
		cd $(ROOT_DIR)/docker/ftp_demo && $(DOCKER_COMPOSE) up -d; \
		sleep 3; \
		echo "$(YELLOW)[INFO]$(NC) FTP server started. Connect: ftp localhost 2121"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) FTP Demo: see docker/ftp_demo/README.md"; \
	fi

demo-ssh:
	@echo "$(GREEN)[DEMO]$(NC) SSH Provisioning Demo..."
	@if [ -d "$(ROOT_DIR)/docker/ssh_demo" ] && [ -f "$(ROOT_DIR)/docker/ssh_demo/docker-compose.yml" ]; then \
		cd $(ROOT_DIR)/docker/ssh_demo && $(DOCKER_COMPOSE) up -d; \
		sleep 3; \
		echo "$(YELLOW)[INFO]$(NC) SSH containers started. See docker/ssh_demo/README.md"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) SSH Demo: see docker/ssh_demo/README.md"; \
	fi

# =============================================================================
# MININET DEMO
# =============================================================================

demo-mininet:
	@echo "$(GREEN)[DEMO]$(NC) Prior Mininet cleanup..."
	@sudo mn -c 2>/dev/null || true
	@echo "$(GREEN)[DEMO]$(NC) Starting Mininet topology with automatic test..."
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_base.py --test
	@echo "$(GREEN)[OK]$(NC) Mininet demo finished."

demo-mininet-cli:
	@echo "$(GREEN)[DEMO]$(NC) Entering Mininet CLI (exit to quit)..."
	@sudo mn -c 2>/dev/null || true
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_base.py --cli

demo-mininet-extended:
	@echo "$(GREEN)[DEMO]$(NC) Extended topology with failover..."
	@sudo mn -c 2>/dev/null || true
	@cd $(ROOT_DIR) && sudo $(PYTHON) mininet/topologies/topo_11_extended.py --test

# =============================================================================
# DEMO ALL
# =============================================================================

demo-all: 
	@echo "$(GREEN)[DEMO-ALL]$(NC) Running all demos..."
	@echo ""
	@echo "$(BLUE)═══ 1. Nginx Demo ═══$(NC)"
	@make demo-nginx
	@sleep 3
	@make demo-nginx-stop
	@echo ""
	@echo "$(BLUE)═══ 2. Custom LB Demo ═══$(NC)"
	@make demo-custom-lb
	@sleep 3
	@make demo-custom-lb-stop
	@echo ""
	@echo "$(BLUE)═══ 3. DNS Demo ═══$(NC)"
	@make demo-dns
	@echo ""
	@echo "$(GREEN)[OK]$(NC) All Docker demos finished."
	@echo "$(YELLOW)[INFO]$(NC) For Mininet: make demo-mininet (requires sudo)"

# =============================================================================
# STANDALONE PYTHON EXERCISES
# =============================================================================

backends-start:
	@echo "$(GREEN)[START]$(NC) Starting 3 local HTTP backends..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 1 --port $(B1_PORT) > /tmp/backend1.log 2>&1 &
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 2 --port $(B2_PORT) > /tmp/backend2.log 2>&1 &
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_01_backend.py --id 3 --port $(B3_PORT) > /tmp/backend3.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) Backends started on ports $(B1_PORT), $(B2_PORT), $(B3_PORT)"
	@echo "$(YELLOW)[INFO]$(NC) Logs in /tmp/backend{1,2,3}.log"
	@echo "$(YELLOW)[INFO]$(NC) Test: curl http://localhost:$(B1_PORT)/"

backends-stop:
	@echo "$(YELLOW)[STOP]$(NC) Stopping backends..."
	@pkill -f "ex_11_01_backend" 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Backends stopped."

lb-start:
	@echo "$(GREEN)[START]$(NC) Starting load balancer (round-robin)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo rr > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB started on port $(LB_PORT) (algorithm: round-robin)"
	@echo "$(YELLOW)[INFO]$(NC) Test: curl http://localhost:$(LB_PORT)/"

lb-start-lc:
	@echo "$(GREEN)[START]$(NC) Starting load balancer (least_conn)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo least_conn > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB started on port $(LB_PORT) (algorithm: least_conn)"

lb-start-ip:
	@echo "$(GREEN)[START]$(NC) Starting load balancer (ip_hash)..."
	@$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py \
		--listen 0.0.0.0:$(LB_PORT) \
		--backends 127.0.0.1:$(B1_PORT),127.0.0.1:$(B2_PORT),127.0.0.1:$(B3_PORT) \
		--algo ip_hash > /tmp/lb.log 2>&1 &
	@sleep 1
	@echo "$(GREEN)[OK]$(NC) LB started on port $(LB_PORT) (algorithm: ip_hash)"

lb-stop:
	@echo "$(YELLOW)[STOP]$(NC) Stopping load balancer..."
	@pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) LB stopped."

# =============================================================================
# TESTS & BENCHMARK
# =============================================================================

test:
	@echo "$(GREEN)[TEST]$(NC) Running smoke tests..."
	@bash $(ROOT_DIR)/scripts/verify.sh --smoke
	@echo "$(GREEN)[OK]$(NC) Smoke tests complete."

benchmark:
	@echo "$(GREEN)[BENCH]$(NC) Apache Bench: 1000 requests, 10 concurrent..."
	@if command -v ab &> /dev/null; then \
		ab -n 1000 -c 10 http://127.0.0.1:$(LB_PORT)/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed)"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) ab not installed. Running Python load generator..."; \
		$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py loadgen --url http://127.0.0.1:$(LB_PORT)/ --n 1000 --c 10; \
	fi

benchmark-heavy:
	@echo "$(GREEN)[BENCH]$(NC) Heavy benchmark: 10000 requests, 50 concurrent..."
	@if command -v ab &> /dev/null; then \
		ab -n 10000 -c 50 http://127.0.0.1:$(LB_PORT)/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed)"; \
	else \
		$(PYTHON) $(ROOT_DIR)/python/exercises/ex_11_02_loadbalancer.py loadgen --url http://127.0.0.1:$(LB_PORT)/ --n 10000 --c 50; \
	fi

# =============================================================================
# INSTRUMENTATION
# =============================================================================

capture:
	@echo "$(GREEN)[CAPTURE]$(NC) Simplified traffic capture..."
	@bash $(ROOT_DIR)/scripts/capture.sh

capture-traffic:
	@echo "$(GREEN)[CAPTURE]$(NC) tcpdump on port $(LB_PORT) (Ctrl+C to stop)..."
	@if command -v tcpdump &> /dev/null; then \
		sudo tcpdump -i any -n tcp port $(LB_PORT) -c 20; \
	elif command -v tshark &> /dev/null; then \
		sudo tshark -i any -f "tcp port $(LB_PORT)" -c 20; \
	else \
		echo "$(RED)[!]$(NC) Neither tcpdump nor tshark are installed."; \
	fi

# =============================================================================
# CLEANUP
# =============================================================================

clean:
	@echo "$(YELLOW)[CLEAN]$(NC) Complete cleanup..."
	@# Docker stacks
	@cd $(ROOT_DIR)/docker/nginx_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/custom_lb_compose && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/ftp_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/dns_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@cd $(ROOT_DIR)/docker/ssh_demo && $(DOCKER_COMPOSE) down 2>/dev/null || true
	@# Python processes
	@pkill -f "ex_11_01_backend" 2>/dev/null || true
	@pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
	@# Mininet
	@sudo mn -c 2>/dev/null || true
	@# Temporary files
	@rm -f /tmp/backend*.log /tmp/lb.log /tmp/s11_*.log /tmp/*.pid 2>/dev/null || true
	@rm -f $(ROOT_DIR)/pcap/*.pcap 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Cleanup finished."

reset: clean
	@echo "$(YELLOW)[RESET]$(NC) Complete reset + delete Docker images..."
	@docker system prune -f 2>/dev/null || true
	@docker volume prune -f 2>/dev/null || true
	@echo "$(GREEN)[OK]$(NC) Complete reset finished."

# =============================================================================
# FOOTER
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================
