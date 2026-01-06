# =============================================================================
# Makefile – Starterkit Week 9: Session (L5), Presentation (L6), File Protocols
# Computer Networks | ASE-CSIE | 2025
# =============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Configurable Variables
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := $(PYTHON) -m pip
HOST := 127.0.0.1
PORT := 3333
FTP_PORT := 2121
USER := test
PASS := 12345
ROOT_DIR := server-files
CLIENT_DIR := client-files
FILE := hello.txt

# Colours for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
CYAN := \033[0;36m
RED := \033[0;31m
NC := \033[0m

# -----------------------------------------------------------------------------
# Main Targets
# -----------------------------------------------------------------------------

.PHONY: help
help: ## Display this help message
	@echo -e "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(CYAN)║  Starterkit S9 - Computer Networks (ASE-CSIE)                    ║$(NC)"
	@echo -e "$(CYAN)║  Session Layer (L5), Presentation Layer (L6)                     ║$(NC)"
	@echo -e "$(CYAN)║  File Protocols                                                  ║$(NC)"
	@echo -e "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(YELLOW)Usage examples:$(NC)"
	@echo "  make setup              # Complete installation"
	@echo "  make server             # Start the pseudo-FTP server"
	@echo "  make client-get FILE=test.txt  # Download a file"
	@echo "  make docker-up          # Start the Docker stack"
	@echo "  make verify             # Verify environment is OK"

# -----------------------------------------------------------------------------
# Setup and Cleanup
# -----------------------------------------------------------------------------

.PHONY: setup
setup: setup-dirs setup-deps setup-files ## Complete installation (dependencies + directories + test files)
	@echo -e "$(GREEN)✓ Setup complete!$(NC)"

.PHONY: setup-dirs
setup-dirs: ## Create necessary directories
	@mkdir -p $(ROOT_DIR) $(CLIENT_DIR) pcap
	@echo -e "$(GREEN)✓ Directories created: $(ROOT_DIR), $(CLIENT_DIR), pcap$(NC)"

.PHONY: setup-deps
setup-deps: ## Install Python dependencies
	@$(PIP) install --break-system-packages -q -r requirements.txt 2>/dev/null || \
		$(PIP) install -q -r requirements.txt 2>/dev/null || \
		echo "Manual dependency installation: pip install pyftpdlib"
	@echo -e "$(GREEN)✓ Python dependencies installed$(NC)"

.PHONY: setup-files
setup-files: setup-dirs ## Create test files
	@echo "Hello S9 - File protocols!" > $(ROOT_DIR)/hello.txt
	@echo "Test file with UTF-8: Romania ✓" > $(ROOT_DIR)/utf8_test.txt
	@echo "Binary test content" > $(ROOT_DIR)/test.bin
	@dd if=/dev/urandom of=$(ROOT_DIR)/random_100k.bin bs=1024 count=100 2>/dev/null || true
	@echo -e "$(GREEN)✓ Test files created in $(ROOT_DIR)/$(NC)"

.PHONY: clean
clean: ## Clean temporary files
	@rm -rf $(CLIENT_DIR)/*.txt $(CLIENT_DIR)/*.bin __pycache__ python/**/__pycache__
	@rm -f *.pcap *.log
	@echo -e "$(YELLOW)✓ Temporary files cleaned$(NC)"

.PHONY: reset
reset: clean docker-down ## Complete reset (includes Docker and Mininet)
	@rm -rf $(ROOT_DIR) $(CLIENT_DIR)
	@sudo mn -c 2>/dev/null || true
	@pkill -f "ex_9_02" 2>/dev/null || true
	@pkill -f "pseudo_ftp" 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Complete reset$(NC)"

# -----------------------------------------------------------------------------
# Exercise 1: Endianness and Framing (L6)
# -----------------------------------------------------------------------------

.PHONY: ex1
ex1: ## Run the endianness exercise (selftest)
	@echo -e "$(CYAN)═══ Exercise 1: Endianness and Binary Framing (L6) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_01_endianness.py --selftest

.PHONY: ex1-demo
ex1-demo: ## Endianness demo with detailed output
	@echo -e "$(CYAN)═══ Demo Endianness: Big-Endian vs Little-Endian ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_01_endianness.py --demo

.PHONY: run-demo
run-demo: ex1-demo ## Alias for demo

# -----------------------------------------------------------------------------
# Pseudo-FTP Server
# -----------------------------------------------------------------------------

.PHONY: server
server: setup-files ## Start the pseudo-FTP server
	@echo -e "$(GREEN)═══ Pseudo-FTP Server on $(HOST):$(PORT) ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C to stop$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py server \
		--host $(HOST) --port $(PORT) --root $(ROOT_DIR)

.PHONY: server-bg
server-bg: setup-files ## Start the server in background
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py server \
		--host $(HOST) --port $(PORT) --root $(ROOT_DIR) &
	@sleep 0.5
	@echo -e "$(GREEN)✓ Server started in background on $(HOST):$(PORT)$(NC)"

# -----------------------------------------------------------------------------
# Pseudo-FTP Client
# -----------------------------------------------------------------------------

.PHONY: client-list
client-list: ## List files on server
	@echo -e "$(CYAN)═══ LIST ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) list

.PHONY: client-get
client-get: setup-dirs ## Download a file (usage: make client-get FILE=hello.txt)
	@echo -e "$(CYAN)═══ GET $(FILE) (passive mode) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --mode passive get $(FILE)

.PHONY: client-get-active
client-get-active: setup-dirs ## Download a file in active mode
	@echo -e "$(CYAN)═══ GET $(FILE) (active mode) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --mode active get $(FILE)

.PHONY: client-put
client-put: ## Upload a file to server
	@echo -e "$(CYAN)═══ PUT $(FILE) ═══$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--mode passive put $(FILE)

.PHONY: client-interactive
client-interactive: ## Start the client in interactive mode
	@echo -e "$(CYAN)═══ Interactive Client ═══$(NC)"
	@echo -e "$(YELLOW)Commands: list, pwd, cwd <dir>, get <file>, put <file>, quit$(NC)"
	@$(PYTHON) python/exercises/ex_9_02_pseudo_ftp.py client \
		--host $(HOST) --port $(PORT) --user $(USER) --password $(PASS) \
		--local-dir $(CLIENT_DIR) --interactive

.PHONY: run-lab
run-lab: server-bg client-list ## Run complete lab (server + list)
	@echo -e "$(GREEN)✓ Demonstrative lab complete$(NC)"

# -----------------------------------------------------------------------------
# Real FTP (pyftpdlib)
# -----------------------------------------------------------------------------

.PHONY: ftp-server
ftp-server: setup-files ## Start the real FTP server (pyftpdlib)
	@echo -e "$(GREEN)═══ FTP Server (pyftpdlib) on $(HOST):$(FTP_PORT) ═══$(NC)"
	@$(PYTHON) python/exercises/ftp_demo_server.py \
		--host $(HOST) --port $(FTP_PORT) --root $(ROOT_DIR) \
		--user $(USER) --password $(PASS)

.PHONY: ftp-client
ftp-client: ## FTP Client (ftplib)
	@echo -e "$(CYAN)═══ FTP Client ═══$(NC)"
	@$(PYTHON) python/exercises/ftp_demo_client.py \
		--host $(HOST) --port $(FTP_PORT) --user $(USER) --password $(PASS) list

# -----------------------------------------------------------------------------
# Complete Demo
# -----------------------------------------------------------------------------

.PHONY: demo
demo: setup ## Complete step-by-step demo
	@echo -e "$(CYAN)╔══════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(CYAN)║                    COMPLETE DEMO S9                              ║$(NC)"
	@echo -e "$(CYAN)╚══════════════════════════════════════════════════════════════════╝$(NC)"
	@bash ./scripts/run_demo.sh

.PHONY: run-all
run-all: setup ## Automated non-interactive demo (produces artifacts/)
	@echo -e "$(CYAN)═══ Automated demo (run_all.sh) ═══$(NC)"
	@bash ./scripts/run_all.sh

.PHONY: demo-encoding
demo-encoding: ## Demo encoding and data representation (L6)
	@echo -e "$(CYAN)═══ Demo: UTF-8, MIME, Base64, Gzip ═══$(NC)"
	@$(PYTHON) -c "\
import base64, gzip, json; \
text = 'Romania: country ✓'; \
print(f'Original: {text}'); \
print(f'UTF-8 bytes: {text.encode(\"utf-8\")}'); \
print(f'Base64: {base64.b64encode(text.encode()).decode()}'); \
compressed = gzip.compress(text.encode()); \
print(f'Gzip ({len(compressed)} bytes vs {len(text.encode())} original)'); \
print(f'JSON: {json.dumps({\"msg\": text})}'); \
"

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

.PHONY: docker-build
docker-build: ## Build Docker images
	@echo -e "$(CYAN)═══ Building Docker images ═══$(NC)"
	@cd docker && docker-compose build

.PHONY: docker-up
docker-up: setup-files ## Start the Docker stack (server + clients)
	@echo -e "$(GREEN)═══ Starting Docker stack ═══$(NC)"
	@cd docker && docker-compose up -d
	@echo -e "$(GREEN)✓ Stack started. Check with: docker-compose ps$(NC)"

.PHONY: docker-test
docker-test: docker-up ## Run multi-client test in Docker
	@echo -e "$(CYAN)═══ Docker multi-client test ═══$(NC)"
	@sleep 2
	@cd docker && docker-compose logs

.PHONY: docker-logs
docker-logs: ## Display Docker logs
	@cd docker && docker-compose logs -f

.PHONY: docker-down
docker-down: ## Stop and remove Docker containers
	@cd docker && docker-compose down -v 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Docker stack stopped$(NC)"

# -----------------------------------------------------------------------------
# Mininet (requires sudo)
# -----------------------------------------------------------------------------

.PHONY: mininet-base
mininet-base: setup-files ## Basic Mininet topology (1 server, 1 client)
	@echo -e "$(GREEN)═══ Mininet: Basic Topology ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_base.py --cli

.PHONY: mininet-test
mininet-test: setup-files ## Automated Mininet test (1 server, 3 clients)
	@echo -e "$(GREEN)═══ Mininet: Concurrency Test ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_extended.py --test

.PHONY: mininet-cli
mininet-cli: setup-files ## Interactive Mininet CLI with extended topology
	@echo -e "$(GREEN)═══ Mininet CLI (extended topology) ═══$(NC)"
	@sudo -E $(PYTHON) mininet/topologies/topo_extended.py --cli

.PHONY: mininet-clean
mininet-clean: ## Clean Mininet resources
	@sudo mn -c 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Mininet cleaned$(NC)"

# -----------------------------------------------------------------------------
# Traffic Capture
# -----------------------------------------------------------------------------

.PHONY: capture
capture: ## Live traffic capture on port 3333
	@echo -e "$(CYAN)═══ tcpdump on port $(PORT) ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C to stop$(NC)"
	@sudo tcpdump -i any "tcp port $(PORT)" -nn -vv

.PHONY: capture-save
capture-save: ## Save capture to .pcap file
	@echo -e "$(CYAN)═══ Saving capture to pcap/s9_capture.pcap ═══$(NC)"
	@echo -e "$(YELLOW)Ctrl+C to stop and save$(NC)"
	@sudo tcpdump -i any "tcp port $(PORT)" -w pcap/s9_capture.pcap
	@echo -e "$(GREEN)✓ Capture saved$(NC)"

.PHONY: capture-read
capture-read: ## Read an existing capture
	@tcpdump -r pcap/s9_capture.pcap -nn -vv 2>/dev/null | head -100 || \
		echo "No file pcap/s9_capture.pcap exists"

# -----------------------------------------------------------------------------
# Verification and Tests
# -----------------------------------------------------------------------------

.PHONY: verify
verify: ## Verify environment is OK
	@echo -e "$(CYAN)═══ Environment Verification ═══$(NC)"
	@bash ./tests/verify.sh

.PHONY: test
test: ex1 ## Run all tests
	@echo -e "$(GREEN)✓ All tests passed!$(NC)"

.PHONY: smoke
smoke: setup ## Quick functionality test
	@echo -e "$(CYAN)═══ Smoke Test ═══$(NC)"
	@bash ./tests/smoke_test.sh

# -----------------------------------------------------------------------------
# Presentations and Documentation
# -----------------------------------------------------------------------------

.PHONY: slides-view
slides-view: ## Display the slide outline
	@cat slides/curs_outline.txt

.PHONY: html-open
html-open: ## Open the interactive HTML presentation
	@xdg-open html_prezentari/theory.html 2>/dev/null || \
		open html_prezentari/theory.html 2>/dev/null || \
		echo "Open manually: html_prezentari/theory.html"

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

.PHONY: check-ports
check-ports: ## Check ports in use
	@echo -e "$(CYAN)═══ Ports in use ═══$(NC)"
	@ss -lntp 2>/dev/null | grep -E "$(PORT)|$(FTP_PORT)" || echo "No active ports"

.PHONY: kill-servers
kill-servers: ## Stop all background servers
	@pkill -f "ex_9_02" 2>/dev/null || true
	@pkill -f "ftp_demo" 2>/dev/null || true
	@pkill -f "pseudo_ftp" 2>/dev/null || true
	@echo -e "$(YELLOW)✓ Servers stopped$(NC)"

.PHONY: tree
tree: ## Display project structure
	@tree -L 3 --dirsfirst -I '__pycache__|*.pyc|server-files|client-files' 2>/dev/null || \
		find . -type d -name '__pycache__' -prune -o -type f -print | head -50

# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================


# -----------------------------------------------------------------------------
# Smoke tests
# -----------------------------------------------------------------------------

.PHONY: smoke-test
smoke-test: run-all ## Run the smoke test suite (runs run-all then validates artefacts)
	@bash ./tests/smoke_test.sh
