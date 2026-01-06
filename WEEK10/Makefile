# Makefile – Week 10: HTTP/HTTPS, REST, SOAP + Network Services
# Computer Networks, ASE Bucharest 2025-2026
# Revolvix&Hypotheticalandrei

SHELL := /bin/bash
.PHONY: help check setup demo run-demo run-lab docker-up docker-down docker-build docker-debug docker-logs \
        mininet-cli mininet-test mininet-clean tcpdump capture clean reset verify slides selftest \
        dns-test ssh-test ftp-test https-test rest-test all run-all smoke-test artifacts

# Colours for output (portable)
ESC := $(shell printf '\033')
GREEN := $(ESC)[0;32m
YELLOW := $(ESC)[0;33m
RED := $(ESC)[0;31m
BLUE := $(ESC)[0;34m
CYAN := $(ESC)[0;36m
NC := $(ESC)[0m

# Directories
ROOT_DIR    := $(shell pwd)
DOCKER_DIR  := $(ROOT_DIR)/docker
PYTHON_DIR  := $(ROOT_DIR)/python
MININET_DIR := $(ROOT_DIR)/mininet
SLIDES_DIR  := $(ROOT_DIR)/slides
DOCS_DIR    := $(ROOT_DIR)/docs
SCRIPTS_DIR := $(ROOT_DIR)/scripts

# Python interpreter selection (prefer the local virtual environment if present)
VENV_DIR := $(ROOT_DIR)/.venv
PYTHON := $(shell if [ -x "$(VENV_DIR)/bin/python" ]; then echo "$(VENV_DIR)/bin/python"; else command -v python3; fi)
PIP := $(shell if [ -x "$(VENV_DIR)/bin/pip" ]; then echo "$(VENV_DIR)/bin/pip"; else command -v pip3; fi)
CERTS_DIR   := $(ROOT_DIR)/certs
PCAP_DIR    := $(ROOT_DIR)/pcap

# Service ports
DNS_PORT    := 5353
SSH_PORT    := 2222
FTP_PORT    := 2121
HTTPS_PORT  := 8443
HTTP_PORT   := 8000

# Timestamp for logs
TS := $(shell date +%Y%m%d_%H%M%S)

#=============================================================================
# HELP
#=============================================================================

help:
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  WEEK 10 – HTTP/HTTPS, REST, SOAP + Network Services (DNS, SSH, FTP)          ║$(NC)"
	@echo "$(GREEN)║  Computer Networks | ASE Bucharest | 2025-2026                                ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)═══ MAIN COMMANDS ═══$(NC)"
	@echo "  $(CYAN)make check$(NC)         Check dependencies and environment"
	@echo "  $(CYAN)make setup$(NC)         Complete installation (venv + dependencies)"
	@echo "  $(CYAN)make demo$(NC)          Run complete demonstration"
	@echo "  $(CYAN)make verify$(NC)        Verify everything works"
	@echo "  $(CYAN)make all$(NC)           Setup + Complete demo"
	@echo ""
	@echo "$(YELLOW)═══ DOCKER COMPOSE (SEMINAR) ═══$(NC)"
	@echo "  $(CYAN)make docker-up$(NC)     Start services (DNS, SSH, FTP, Web)"
	@echo "  $(CYAN)make docker-down$(NC)   Stop services"
	@echo "  $(CYAN)make docker-build$(NC)  Rebuild images"
	@echo "  $(CYAN)make docker-debug$(NC)  Enter debug container"
	@echo "  $(CYAN)make docker-logs$(NC)   Display service logs"
	@echo ""
	@echo "$(YELLOW)═══ INDIVIDUAL SERVICE TESTS ═══$(NC)"
	@echo "  $(CYAN)make dns-test$(NC)      Test DNS (Docker implicit + custom)"
	@echo "  $(CYAN)make ssh-test$(NC)      Test SSH + Paramiko"
	@echo "  $(CYAN)make ftp-test$(NC)      Test FTP programmatically"
	@echo "  $(CYAN)make https-test$(NC)    Test local HTTPS server"
	@echo "  $(CYAN)make rest-test$(NC)     Test REST levels"
	@echo ""
	@echo "$(YELLOW)═══ MININET (ADVANCED LAB) ═══$(NC)"
	@echo "  $(CYAN)make mininet-cli$(NC)   Start Mininet CLI"
	@echo "  $(CYAN)make mininet-test$(NC)  Run automated test"
	@echo "  $(CYAN)make mininet-clean$(NC) Mininet cleanup"
	@echo ""
	@echo "$(YELLOW)═══ CAPTURES AND DIAGNOSTICS ═══$(NC)"
	@echo "  $(CYAN)make capture$(NC)       Traffic capture with tshark (service ports)"
	@echo "  $(CYAN)make tcpdump$(NC)       Capture with tcpdump (alternative)"
	@echo "  $(CYAN)make slides$(NC)        Open HTML presentations"
	@echo "  $(CYAN)make selftest$(NC)      Run Python self-test"
	@echo ""
	@echo "$(YELLOW)═══ CLEANUP ═══$(NC)"
	@echo "  $(CYAN)make clean$(NC)         Clean temporary files"
	@echo "  $(CYAN)make reset$(NC)         Complete reset (including Docker volumes)"
	@echo ""
	@echo "$(YELLOW)═══ STANDARD AUTOMATIONS ═══$(NC)"
	@echo "  $(CYAN)make run-all$(NC)       Complete automated demo (generates artifacts/)"
	@echo "  $(CYAN)make smoke-test$(NC)    Verify generated artefacts"
	@echo ""

#=============================================================================
# CHECK DEPENDENCIES
#=============================================================================

check:
	@echo ""
	@echo "$(YELLOW)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║              DEPENDENCY VERIFICATION                       ║$(NC)"
	@echo "$(YELLOW)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@printf "%-20s" "Python 3.11+:" && (python3 -c "import sys; assert sys.version_info >= (3,11)" 2>/dev/null && python3 --version | cut -d' ' -f2 && echo -n "") || echo "$(RED)MISSING or < 3.11$(NC)"
	@printf "%-20s" "Docker:" && (docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',') || echo "$(RED)MISSING$(NC)"
	@printf "%-20s" "Docker Compose:" && (docker compose version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) || echo "$(RED)MISSING$(NC)"
	@printf "%-20s" "openssl:" && (openssl version 2>/dev/null | cut -d' ' -f2) || echo "$(RED)REQUIRED$(NC)"
	@printf "%-20s" "curl:" && (curl --version 2>/dev/null | head -1 | cut -d' ' -f2) || echo "$(YELLOW)RECOMMENDED$(NC)"
	@printf "%-20s" "dig:" && (dig -v 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "present") || echo "$(YELLOW)RECOMMENDED$(NC)"
	@printf "%-20s" "tshark:" && (tshark --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) || echo "$(YELLOW)OPTIONAL$(NC)"
	@printf "%-20s" "Mininet:" && (mn --version 2>/dev/null) || echo "$(YELLOW)OPTIONAL$(NC)"
	@echo ""
	@echo "$(GREEN)Verification complete.$(NC)"
	@echo ""

#=============================================================================
# SETUP
#=============================================================================

setup:
	@echo "$(YELLOW)Complete installation...$(NC)"
	@echo ""
	@# Create virtual environment if not exists
	@if [ ! -d ".venv" ]; then \
		echo "$(CYAN)Creating virtual environment...$(NC)"; \
		python3 -m venv .venv; \
	fi
	@echo "$(CYAN)Installing Python dependencies...$(NC)"
	@. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo ""
	@echo "$(CYAN)Generating self-signed certificates...$(NC)"
	@mkdir -p $(CERTS_DIR)
	@if [ ! -f $(CERTS_DIR)/server.crt ]; then \
		openssl req -x509 -newkey rsa:2048 -nodes \
			-keyout $(CERTS_DIR)/server.key -out $(CERTS_DIR)/server.crt \
			-days 30 -subj "/CN=lab.network.local/O=ASE-CSIE/C=RO" \
			-addext "subjectAltName=DNS:lab.network.local,IP:127.0.0.1" 2>/dev/null || \
			openssl req -x509 -newkey rsa:2048 -nodes \
			-keyout $(CERTS_DIR)/server.key -out $(CERTS_DIR)/server.crt \
			-days 30 -subj "/CN=lab.network.local/O=ASE-CSIE/C=RO" 2>/dev/null; \
		echo "$(GREEN)Certificates generated: $(CERTS_DIR)/server.crt$(NC)"; \
	else \
		echo "Certificates already exist."; \
	fi
	@echo ""
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "Activate virtual environment with: $(CYAN)source .venv/bin/activate$(NC)"

#=============================================================================
# DOCKER COMPOSE
#=============================================================================

docker-up:
	@echo "$(YELLOW)Starting Docker services...$(NC)"
	@cd $(DOCKER_DIR) && docker compose up -d --build
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║              SERVICES STARTED                              ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(CYAN)Web demo:$(NC)     http://localhost:$(HTTP_PORT)"
	@echo "  $(CYAN)Custom DNS:$(NC)   dig @localhost -p $(DNS_PORT) myservice.lab.local"
	@echo "  $(CYAN)SSH server:$(NC)   ssh labuser@localhost -p $(SSH_PORT) (password: labpass)"
	@echo "  $(CYAN)FTP server:$(NC)   ftp localhost $(FTP_PORT) (user: labftp/labftp)"
	@echo ""
	@echo "Debug container: $(YELLOW)make docker-debug$(NC)"
	@echo ""

docker-down:
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	@cd $(DOCKER_DIR) && docker compose down
	@echo "$(GREEN)Services stopped.$(NC)"

docker-build:
	@echo "$(YELLOW)Rebuilding Docker images (no cache)...$(NC)"
	@cd $(DOCKER_DIR) && docker compose build --no-cache

docker-debug:
	@echo "$(YELLOW)Entering debug container...$(NC)"
	@echo ""
	@echo "$(CYAN)Useful commands in container:$(NC)"
	@echo "  dig web                                    # Docker implicit DNS"
	@echo "  dig @dns-server -p 5353 myservice.lab.local  # Custom DNS"
	@echo "  curl http://web:8000                      # Test web"
	@echo "  ssh labuser@ssh-server                    # SSH (password: labpass)"
	@echo "  lftp -u labftp,labftp ftp-server:2121    # FTP"
	@echo ""
	@cd $(DOCKER_DIR) && docker compose exec debug sh

docker-logs:
	@cd $(DOCKER_DIR) && docker compose logs -f --tail=50

#=============================================================================
# INDIVIDUAL SERVICE TESTS
#=============================================================================

dns-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ DNS TEST ═══$(NC)"
	@echo ""
	@echo "$(CYAN)1. Docker implicit DNS (resolving 'web'):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig web +short 2>/dev/null || echo "  (debug container not running)"
	@echo ""
	@echo "$(CYAN)2. Custom DNS (myservice.lab.local):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig @dns-server -p 5353 myservice.lab.local +short 2>/dev/null || echo "  (DNS service not responding)"
	@echo ""
	@echo "$(CYAN)3. Custom DNS (api.lab.local):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig @dns-server -p 5353 api.lab.local +short 2>/dev/null || echo "  (record does not exist)"
	@echo ""
	@echo "$(GREEN)DNS test complete.$(NC)"

ssh-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ SSH + PARAMIKO TEST ═══$(NC)"
	@echo ""
	@cd $(DOCKER_DIR) && docker compose exec ssh-client python3 /app/paramiko_client.py 2>/dev/null || echo "$(RED)Error running Paramiko$(NC)"
	@echo ""
	@echo "$(GREEN)SSH test complete.$(NC)"

ftp-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ FTP TEST ═══$(NC)"
	@echo ""
	@python3 -c "\
from ftplib import FTP; \
import sys; \
try: \
    f = FTP(); \
    f.connect('127.0.0.1', $(FTP_PORT), timeout=5); \
    f.login('labftp', 'labftp'); \
    print('  Connected to FTP'); \
    print('  Current directory:', f.pwd()); \
    print('  Files:', f.nlst()); \
    f.quit(); \
    print('  FTP OK'); \
except Exception as e: \
    print('  FTP Error:', e); \
    sys.exit(1)" || echo "$(RED)FTP test failed$(NC)"
	@echo ""
	@echo "$(GREEN)FTP test complete.$(NC)"

https-test:
	@echo ""
	@echo "$(YELLOW)═══ LOCAL HTTPS TEST ═══$(NC)"
	@echo ""
	@if [ -f $(PYTHON_DIR)/exercises/ex_10_01_https.py ]; then \
		cd $(ROOT_DIR) && $(PYTHON) $(PYTHON_DIR)/exercises/ex_10_01_https.py selftest; \
	else \
		echo "$(RED)File ex_10_01_https.py does not exist$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)HTTPS test complete.$(NC)"

rest-test:
	@echo ""
	@echo "$(YELLOW)═══ REST MATURITY LEVELS TEST ═══$(NC)"
	@echo ""
	@if [ -f $(PYTHON_DIR)/exercises/ex_10_02_rest_levels.py ]; then \
		cd $(ROOT_DIR) && $(PYTHON) $(PYTHON_DIR)/exercises/ex_10_02_rest_levels.py selftest; \
	else \
		echo "$(RED)File ex_10_02_rest_levels.py does not exist$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)REST test complete.$(NC)"

#=============================================================================
# MININET
#=============================================================================

mininet-cli:
	@echo "$(YELLOW)Starting Mininet CLI...$(NC)"
	@echo ""
	@echo "$(CYAN)In CLI, run:$(NC)"
	@echo "  h1 python3 -m http.server 8000 &"
	@echo "  h2 curl http://10.0.0.1:8000/"
	@echo ""
	@if [ -f $(MININET_DIR)/topologies/topo_10_base.py ]; then \
		sudo python3 $(MININET_DIR)/topologies/topo_10_base.py --cli; \
	else \
		echo "$(RED)File topo_10_base.py does not exist$(NC)"; \
		echo "Alternative: sudo mn --topo single,3"; \
	fi

mininet-test:
	@echo "$(YELLOW)Running automated Mininet test...$(NC)"
	@if [ -f $(MININET_DIR)/topologies/topo_10_base.py ]; then \
		sudo python3 $(MININET_DIR)/topologies/topo_10_base.py --test; \
	else \
		echo "$(RED)File topo_10_base.py does not exist$(NC)"; \
	fi

mininet-clean:
	@echo "$(YELLOW)Cleaning Mininet...$(NC)"
	@sudo mn -c 2>/dev/null || true
	@echo "$(GREEN)Mininet cleaned.$(NC)"

#=============================================================================
# CAPTURE & DIAGNOSTICS
#=============================================================================

capture:
	@echo "$(YELLOW)Capturing traffic with tshark...$(NC)"
	@echo "Press Ctrl+C to stop."
	@mkdir -p $(PCAP_DIR)
	@tshark -i any -f "tcp port $(HTTP_PORT) or tcp port $(HTTPS_PORT) or tcp port $(SSH_PORT) or tcp port $(FTP_PORT) or udp port $(DNS_PORT)" \
		-w $(PCAP_DIR)/capture_$(TS).pcap 2>/dev/null || \
		echo "$(RED)tshark not available. Try: make tcpdump$(NC)"

tcpdump:
	@echo "$(YELLOW)Capturing traffic with tcpdump...$(NC)"
	@echo "Press Ctrl+C to stop."
	@mkdir -p $(PCAP_DIR)
	@sudo tcpdump -i any -nn "tcp port $(HTTP_PORT) or tcp port $(HTTPS_PORT) or tcp port $(SSH_PORT) or tcp port $(FTP_PORT) or udp port $(DNS_PORT)" \
		-w $(PCAP_DIR)/capture_$(TS).pcap -v

slides:
	@echo "$(YELLOW)Opening HTML presentations...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(SLIDES_DIR)/theory.html 2>/dev/null & \
		sleep 0.5; \
		xdg-open $(SLIDES_DIR)/seminar.html 2>/dev/null & \
		sleep 0.5; \
		xdg-open $(SLIDES_DIR)/lab.html 2>/dev/null & \
	elif command -v open >/dev/null 2>&1; then \
		open $(SLIDES_DIR)/theory.html; \
		open $(SLIDES_DIR)/seminar.html; \
		open $(SLIDES_DIR)/lab.html; \
	else \
		echo "Open manually:"; \
		echo "  $(SLIDES_DIR)/theory.html"; \
		echo "  $(SLIDES_DIR)/seminar.html"; \
		echo "  $(SLIDES_DIR)/lab.html"; \
	fi

selftest: https-test rest-test
	@echo "$(GREEN)Self-tests completed.$(NC)"

#=============================================================================
# VERIFY
#=============================================================================

verify: check
	@echo ""
	@echo "$(YELLOW)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║              COMPLETE VERIFICATION                         ║$(NC)"
	@echo "$(YELLOW)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)1. Checking file structure...$(NC)"
	@test -f $(ROOT_DIR)/Makefile && echo "  ✓ Makefile" || echo "  ✗ Makefile missing"
	@test -f $(ROOT_DIR)/requirements.txt && echo "  ✓ requirements.txt" || echo "  ✗ requirements.txt missing"
	@test -d $(DOCKER_DIR) && echo "  ✓ docker/" || echo "  ✗ docker/ missing"
	@test -d $(PYTHON_DIR) && echo "  ✓ python/" || echo "  ✗ python/ missing"
	@test -d $(SLIDES_DIR) && echo "  ✓ slides/" || echo "  ✗ slides/ missing"
	@echo ""
	@echo "$(CYAN)2. Checking Docker...$(NC)"
	@docker info >/dev/null 2>&1 && echo "  ✓ Docker daemon running" || echo "  ✗ Docker daemon not running"
	@echo ""
	@echo "$(CYAN)3. Checking available ports...$(NC)"
	@ss -tulpn 2>/dev/null | grep -q ":$(DNS_PORT) " && echo "  ⚠ Port $(DNS_PORT) occupied" || echo "  ✓ Port $(DNS_PORT) available"
	@ss -tulpn 2>/dev/null | grep -q ":$(SSH_PORT) " && echo "  ⚠ Port $(SSH_PORT) occupied" || echo "  ✓ Port $(SSH_PORT) available"
	@ss -tulpn 2>/dev/null | grep -q ":$(FTP_PORT) " && echo "  ⚠ Port $(FTP_PORT) occupied" || echo "  ✓ Port $(FTP_PORT) available"
	@echo ""
	@echo "$(GREEN)Verification complete.$(NC)"

#=============================================================================
# COMPLETE DEMO
#=============================================================================

run-demo: demo
demo: check docker-up
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║                         NETWORK SERVICES DEMO                                  ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@sleep 2
	@$(MAKE) dns-test
	@echo ""
	@sleep 1
	@$(MAKE) ftp-test
	@echo ""
	@sleep 1
	@echo "$(YELLOW)For SSH, run: make ssh-test$(NC)"
	@echo "$(YELLOW)For local HTTPS, run: make https-test$(NC)"
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  Demo complete. Services running in background.                               ║$(NC)"
	@echo "$(GREEN)║  Stop: make docker-down                                                        ║$(NC)"
	@echo "$(GREEN)║  Debug container: make docker-debug                                            ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"

run-lab: demo
	@echo ""
	@echo "$(CYAN)Lab steps:$(NC)"
	@echo "  1. make docker-debug    → enter container"
	@echo "  2. dig web              → test implicit DNS"
	@echo "  3. dig @dns-server -p 5353 myservice.lab.local"
	@echo "  4. curl http://web:8000 → test HTTP"
	@echo "  5. ssh labuser@ssh-server → test SSH"
	@echo ""

#=============================================================================
# CLEANUP
#=============================================================================

clean:
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf $(PCAP_DIR)/*.pcap 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete.$(NC)"

reset: clean docker-down mininet-clean
	@echo "$(YELLOW)Complete reset...$(NC)"
	@cd $(DOCKER_DIR) && docker compose down -v 2>/dev/null || true
	@rm -rf $(CERTS_DIR)/*.crt $(CERTS_DIR)/*.key 2>/dev/null || true
	@rm -rf .venv 2>/dev/null || true
	@echo "$(GREEN)Reset complete.$(NC)"

#=============================================================================
# AUTOMATED DEMO + SMOKE TEST (CROSS-CUTTING STANDARD)
#=============================================================================

run-all: artifacts
	@echo "$(YELLOW)Running complete automated demo...$(NC)"
	@$(SCRIPTS_DIR)/run_all.sh
	@echo "$(GREEN)Automated demo completed.$(NC)"

smoke-test:
	@echo "$(YELLOW)Running smoke test...$(NC)"
	@$(ROOT_DIR)/tests/smoke_test.sh
	@echo ""

artifacts:
	@mkdir -p $(ROOT_DIR)/artifacts

#=============================================================================
# ALL
#=============================================================================

all: setup demo
	@echo ""
	@echo "$(GREEN)Installation and demo complete!$(NC)"
