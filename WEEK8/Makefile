# ═══════════════════════════════════════════════════════════════════════════════
# Makefile - Computer Networks - Week 8
# Transport Layer (TCP/UDP/TLS) + HTTP Server + Reverse Proxy
# ═══════════════════════════════════════════════════════════════════════════════
#
# Quick usage:
#   make help              - Display all available commands
#   make setup             - Install required dependencies
#   make run-demo          - Run the main demo
#   make run-lab           - Start the interactive laboratory
#   make capture           - Capture packets for analysis
#   make verify            - Verify environment is OK
#   make clean             - Clean temporary files
#   make reset             - Complete reset
#
# Author: Computer Networks, ASE Bucharest, 2025
# Revolvix&Hypotheticalandrei
# ═══════════════════════════════════════════════════════════════════════════════

# Configuration
PYTHON     := python3
SHELL      := /bin/bash
.SHELLFLAGS := -o pipefail -c

# Ports (according to standard WEEK=8)
HTTP_PORT       ?= 8080
BACKEND_PORT_A  ?= 9001
BACKEND_PORT_B  ?= 9002
PROXY_PORT      ?= 8888
WEEK_PORT_BASE  := 5800

# Directories
SRC_DIR    := python
DEMO_DIR   := $(SRC_DIR)/demos
EXER_DIR   := $(SRC_DIR)/exercises
SCEN_DIR   := scenarios
DOCS_DIR   := docs
OUT_DIR    := output
WWW_DIR    := www
PCAP_DIR   := pcap

# Colours for output
ESC     := $(shell printf '\033')
GREEN   := $(ESC)[0;32m
YELLOW  := $(ESC)[0;33m
BLUE    := $(ESC)[0;34m
RED     := $(ESC)[0;31m
CYAN    := $(ESC)[0;36m
MAGENTA := $(ESC)[0;35m
BOLD    := $(ESC)[1m
NC      := $(ESC)[0m

# ═══════════════════════════════════════════════════════════════════════════════
# Main target: help
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: help
help:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Computer Networks - Week 8$(NC)"
	@echo "$(BLUE)  Transport Layer (TCP/UDP/TLS) + HTTP Server + Reverse Proxy$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)🔧 Configuration:$(NC)"
	@echo "  make setup              - Install system dependencies"
	@echo "  make verify             - Verify everything is installed correctly"
	@echo ""
	@echo "$(GREEN)$(BOLD)🚀 Demos (server + client):$(NC)"
	@echo "  make run-all            - Complete automatic demo + artefacts"
	@echo "  make run-all-quick      - Automatic demo (without pcap capture)"
	@echo "  make run-demo           - Complete demo HTTP server + proxy"
	@echo "  make demo-http          - Simple HTTP server demo"
	@echo "  make demo-proxy         - Reverse proxy demo with 2 backends"
	@echo ""
	@echo "$(GREEN)$(BOLD)🔬 Laboratory:$(NC)"
	@echo "  make run-lab            - Start the laboratory environment"
	@echo "  make http-server        - Start HTTP server on port $(HTTP_PORT)"
	@echo "  make proxy-server       - Start reverse proxy"
	@echo "  make backend-a          - Start backend A on port $(BACKEND_PORT_A)"
	@echo "  make backend-b          - Start backend B on port $(BACKEND_PORT_B)"
	@echo ""
	@echo "$(GREEN)$(BOLD)📡 Captures and analysis:$(NC)"
	@echo "  make capture            - Complete HTTP traffic capture"
	@echo "  make capture-handshake  - TCP three-way handshake capture"
	@echo "  make capture-proxy      - Client→proxy→backend traffic capture"
	@echo "  make analyze            - Analyse last capture"
	@echo ""
	@echo "$(GREEN)$(BOLD)🐳 Docker:$(NC)"
	@echo "  make docker-build       - Build Docker image"
	@echo "  make docker-up          - Start complete stack"
	@echo "  make docker-down        - Stop stack"
	@echo "  make docker-logs        - Display logs"
	@echo ""
	@echo "$(GREEN)$(BOLD)📝 Tests:$(NC)"
	@echo "  make test-ex1           - Test exercise 1 (HTTP server)"
	@echo "  make test-ex2           - Test exercise 2 (Reverse proxy)"
	@echo "  make test-all           - Test all exercises"
	@echo "  make smoke-test         - Quick functionality test"
	@echo ""
	@echo "$(GREEN)$(BOLD)🧹 Cleanup:$(NC)"
	@echo "  make clean              - Delete temporary files"
	@echo "  make reset              - Complete reset (includes captures)"
	@echo "  make kill-servers       - Stop all active servers"
	@echo ""
	@echo "$(YELLOW)Note: Some commands require sudo permissions (tcpdump).$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Setup and verification
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: setup
setup:
	@echo "$(BLUE)[setup]$(NC) Installing system dependencies..."
	@./scripts/setup.sh
	@echo "$(GREEN)[setup]$(NC) Completed!"

.PHONY: verify
verify:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Working Environment Verification$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Essential:$(NC)"
	@echo -n "  Python 3:     " && ($(PYTHON) --version 2>/dev/null && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ MISSING$(NC)"
	@echo -n "  curl:         " && (which curl > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ MISSING$(NC)"
	@echo -n "  netcat:       " && (which nc > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(RED)✗ MISSING$(NC)"
	@echo ""
	@echo "$(CYAN)Traffic analysis:$(NC)"
	@echo -n "  tcpdump:      " && (which tcpdump > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo -n "  tshark:       " && (which tshark > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo -n "  wireshark:    " && (which wireshark > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo ""
	@echo "$(CYAN)Infrastructure:$(NC)"
	@echo -n "  docker:       " && (which docker > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo -n "  nginx:        " && (which nginx > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo -n "  mininet:      " && (which mn > /dev/null 2>&1 && echo "$(GREEN)✓$(NC)") || echo "$(YELLOW)○ optional$(NC)"
	@echo ""
	@echo "$(CYAN)Kit file verification:$(NC)"
	@test -f $(DEMO_DIR)/demo_http_server.py && echo "  demo_http_server.py:    $(GREEN)✓$(NC)" || echo "  demo_http_server.py:    $(RED)✗$(NC)"
	@test -f $(DEMO_DIR)/demo_reverse_proxy.py && echo "  demo_reverse_proxy.py:  $(GREEN)✓$(NC)" || echo "  demo_reverse_proxy.py:  $(RED)✗$(NC)"
	@test -d $(WWW_DIR) && echo "  www/:                   $(GREEN)✓$(NC)" || echo "  www/:                   $(RED)✗$(NC)"
	@echo ""
	@echo "$(GREEN)[verify]$(NC) Verification complete!"

# ═══════════════════════════════════════════════════════════════════════════════
# Create directories
# ═══════════════════════════════════════════════════════════════════════════════
$(OUT_DIR):
	@mkdir -p $(OUT_DIR)

$(PCAP_DIR):
	@mkdir -p $(PCAP_DIR)

# ═══════════════════════════════════════════════════════════════════════════════
# Complete demos
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: run-all
run-all:
	@echo "$(BLUE)[run-all]$(NC) Running complete automatic demo..."
	@./scripts/run_all.sh

.PHONY: run-all-quick
run-all-quick:
	@echo "$(BLUE)[run-all]$(NC) Running automatic demo (without capture)..."
	@./scripts/run_all.sh --quick

.PHONY: run-demo
run-demo: demo-http demo-proxy
	@echo ""
	@echo "$(GREEN)All demos completed successfully!$(NC)"

.PHONY: demo-http
demo-http: $(OUT_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Demo: Minimal HTTP Server (Socket)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/5]$(NC) Starting HTTP server on port $(HTTP_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(HTTP_PORT) --www $(WWW_DIR) --id demo &
	@sleep 1
	@curl -sS -D - -o /dev/null http://127.0.0.1:$(HTTP_PORT)/ | grep -qi '^Server: ASE-S8-Server' || (echo "$(RED)[ERROR]$(NC) HTTP server did not start correctly on port $(HTTP_PORT). Is the port already in use?"; $(MAKE) kill-servers >/dev/null 2>&1; exit 1)
	@echo ""
	@echo "$(YELLOW)[2/5]$(NC) Test: GET / (index.html)"
	@curl -s http://127.0.0.1:$(HTTP_PORT)/ | head -5
	@echo ""
	@echo "$(YELLOW)[3/5]$(NC) Test: Response headers"
	@curl -s -D - http://127.0.0.1:$(HTTP_PORT)/ -o /dev/null | head -8
	@echo ""
	@echo "$(YELLOW)[4/5]$(NC) Test: GET /not-found (→ 404)"
	@curl -s -D - http://127.0.0.1:$(HTTP_PORT)/not-found -o /dev/null | head -1
	@echo ""
	@echo "$(YELLOW)[5/5]$(NC) Stopping server..."
	@-pkill -f "[d]emo_http_server.py.*$(HTTP_PORT)" 2>/dev/null || true
	@sleep 0.5
	@echo ""
	@echo "$(GREEN)HTTP demo completed successfully!$(NC)"

.PHONY: demo-proxy
demo-proxy: $(OUT_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Demo: Reverse Proxy with Round-Robin$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/6]$(NC) Starting Backend A on port $(BACKEND_PORT_A)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend-A &
	@sleep 0.5
	@curl -sS -D - -o /dev/null http://127.0.0.1:$(BACKEND_PORT_A)/ | grep -qi '^X-Backend: backend-A' || (echo "$(RED)[ERROR]$(NC) Backend A did not start correctly on port $(BACKEND_PORT_A). Is the port already in use?"; $(MAKE) kill-servers >/dev/null 2>&1; exit 1)
	@echo ""
	@echo "$(YELLOW)[2/6]$(NC) Starting Backend B on port $(BACKEND_PORT_B)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_B) --www $(WWW_DIR) --id backend-B &
	@sleep 0.5
	@curl -sS -D - -o /dev/null http://127.0.0.1:$(BACKEND_PORT_B)/ | grep -qi '^X-Backend: backend-B' || (echo "$(RED)[ERROR]$(NC) Backend B did not start correctly on port $(BACKEND_PORT_B). Is the port already in use?"; $(MAKE) kill-servers >/dev/null 2>&1; exit 1)
	@echo ""
	@echo "$(YELLOW)[3/6]$(NC) Starting Reverse Proxy on port $(PROXY_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) \
		--backends 127.0.0.1:$(BACKEND_PORT_A),127.0.0.1:$(BACKEND_PORT_B) &
	@sleep 1
	@curl -sS -D - -o /dev/null http://127.0.0.1:$(PROXY_PORT)/ | grep -qi '^X-Request-ID:' || (echo "$(RED)[ERROR]$(NC) Reverse proxy did not start correctly on port $(PROXY_PORT). Is the port already in use?"; $(MAKE) kill-servers >/dev/null 2>&1; exit 1)
	@# Warm-up request to keep the visible sequence starting with backend-A
	@curl -sS -o /dev/null http://127.0.0.1:$(PROXY_PORT)/ || true
	@echo ""
	@echo "$(YELLOW)[4/6]$(NC) Test: 6 requests through proxy (observe alternation)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@for i in 1 2 3 4 5 6; do \
		echo -n "  Request $$i: "; \
		curl -s http://127.0.0.1:$(PROXY_PORT)/ -D - -o /dev/null 2>/dev/null | grep -E "X-Served-By|X-Backend" | head -1; \
	done
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(YELLOW)[5/6]$(NC) Stopping all servers..."
	@-pkill -f "[d]emo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "[d]emo_http_server.py.*$(BACKEND_PORT_A)" 2>/dev/null || true
	@-pkill -f "[d]emo_http_server.py.*$(BACKEND_PORT_B)" 2>/dev/null || true
	@sleep 0.5
	@echo ""
	@echo "$(GREEN)Reverse Proxy demo completed successfully!$(NC)"
	@echo "$(MAGENTA)Observe: Backends alternate (A, B, A, B...) - Round-Robin!$(NC)"

# ═══════════════════════════════════════════════════════════════════════════════
# Individual servers
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: http-server
http-server:
	@echo "$(BLUE)[http-server]$(NC) Starting HTTP server on port $(HTTP_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 0.0.0.0 --port $(HTTP_PORT) --www $(WWW_DIR)

.PHONY: proxy-server
proxy-server:
	@echo "$(BLUE)[proxy]$(NC) Starting reverse proxy on port $(PROXY_PORT)..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) \
		--backends 127.0.0.1:$(BACKEND_PORT_A),127.0.0.1:$(BACKEND_PORT_B)

.PHONY: backend-a
backend-a:
	@echo "$(BLUE)[backend-a]$(NC) Starting Backend A on port $(BACKEND_PORT_A)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend-A

.PHONY: backend-b
backend-b:
	@echo "$(BLUE)[backend-b]$(NC) Starting Backend B on port $(BACKEND_PORT_B)..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_B) --www $(WWW_DIR) --id backend-B

# ═══════════════════════════════════════════════════════════════════════════════
# Interactive laboratory
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: run-lab
run-lab:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Interactive Laboratory - Week 8$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(CYAN)Recommended steps:$(NC)"
	@echo ""
	@echo "  1. Open 4 terminals"
	@echo ""
	@echo "  2. Terminal 1 - Backend A:"
	@echo "     $(GREEN)make backend-a$(NC)"
	@echo ""
	@echo "  3. Terminal 2 - Backend B:"
	@echo "     $(GREEN)make backend-b$(NC)"
	@echo ""
	@echo "  4. Terminal 3 - Reverse Proxy:"
	@echo "     $(GREEN)make proxy-server$(NC)"
	@echo ""
	@echo "  5. Terminal 4 - Client (tests):"
	@echo "     $(GREEN)curl -v http://localhost:8080/$(NC)"
	@echo "     $(GREEN)for i in {1..6}; do curl -s localhost:8080/ -D - | grep X-Served-By; done$(NC)"
	@echo ""
	@echo "$(YELLOW)For tcpdump capture:$(NC)"
	@echo "     $(GREEN)sudo tcpdump -i lo 'port 8080 or port 9001 or port 9002' -nn -A$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Packet captures
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: capture
capture: capture-handshake
	@echo "$(GREEN)Capture completed!$(NC)"

.PHONY: capture-handshake
capture-handshake: $(PCAP_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Capture: TCP Three-Way Handshake$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/5]$(NC) Starting server..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(HTTP_PORT) --www $(WWW_DIR) &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[2/5]$(NC) Starting tcpdump capture..."
	@sudo tcpdump -i lo port $(HTTP_PORT) -nn -c 20 -w $(PCAP_DIR)/handshake.pcap 2>/dev/null &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[3/5]$(NC) Generating traffic (curl)..."
	@curl -s http://127.0.0.1:$(HTTP_PORT)/ > /dev/null 2>&1 || true
	@sleep 2
	@echo ""
	@echo "$(YELLOW)[4/5]$(NC) Stopping capture and server..."
	@-sudo pkill -f "[t]cpdump.*$(HTTP_PORT)" 2>/dev/null || true
	@-pkill -f "[d]emo_http_server.py.*$(HTTP_PORT)" 2>/dev/null || true
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[5/5]$(NC) Handshake analysis:"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@-sudo tcpdump -r $(PCAP_DIR)/handshake.pcap -nn 2>/dev/null | head -20 || echo "  (requires sudo permissions to read)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(GREEN)TCP flags:$(NC)"
	@echo "  [S]    = SYN (connection initiation)"
	@echo "  [S.]   = SYN-ACK (confirmation + acceptance)"
	@echo "  [.]    = ACK (confirmation)"
	@echo "  [P.]   = PSH-ACK (data + confirmation)"
	@echo "  [F.]   = FIN-ACK (closure)"
	@echo ""
	@echo "$(MAGENTA)Capture saved to: $(PCAP_DIR)/handshake.pcap$(NC)"

.PHONY: capture-proxy
capture-proxy: $(PCAP_DIR)
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)$(BOLD)  Capture: Client → Proxy → Backend$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/6]$(NC) Starting backend..."
	@$(PYTHON) $(DEMO_DIR)/demo_http_server.py --host 127.0.0.1 --port $(BACKEND_PORT_A) --www $(WWW_DIR) --id backend &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[2/6]$(NC) Starting proxy..."
	@$(PYTHON) $(DEMO_DIR)/demo_reverse_proxy.py --listen-port $(PROXY_PORT) --backends 127.0.0.1:$(BACKEND_PORT_A) &
	@sleep 0.5
	@echo ""
	@echo "$(YELLOW)[3/6]$(NC) Starting capture..."
	@sudo tcpdump -i lo '(port $(PROXY_PORT) or port $(BACKEND_PORT_A))' -nn -w $(PCAP_DIR)/proxy_capture.pcap -c 40 2>/dev/null &
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[4/6]$(NC) Generating traffic..."
	@curl -s http://127.0.0.1:$(PROXY_PORT)/ > /dev/null
	@sleep 2
	@echo ""
	@echo "$(YELLOW)[5/6]$(NC) Stopping processes..."
	@-sudo pkill -f "[t]cpdump.*$(PROXY_PORT)" 2>/dev/null || true
	@-pkill -f "[d]emo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "[d]emo_http_server.py.*$(BACKEND_PORT_A)" 2>/dev/null || true
	@sleep 1
	@echo ""
	@echo "$(YELLOW)[6/6]$(NC) Analysis:"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@-sudo tcpdump -r $(PCAP_DIR)/proxy_capture.pcap -nn 2>/dev/null | head -30 || echo "  (requires sudo)"
	@echo "$(CYAN)───────────────────────────────────────────────────────────────────────$(NC)"
	@echo ""
	@echo "$(GREEN)Observe the 2 TCP connections:$(NC)"
	@echo "  - Client (ephemeral port) → Proxy ($(PROXY_PORT))"
	@echo "  - Proxy (ephemeral port) → Backend ($(BACKEND_PORT_A))"

.PHONY: analyze
.PHONY: analyse
analyse: analyze

analyze:
	@echo "$(BLUE)[analyze]$(NC) Analysing existing captures..."
	@ls -to $(PCAP_DIR)/*.pcap 2>/dev/null || echo "  No captures exist. Run: make capture"

# ═══════════════════════════════════════════════════════════════════════════════
# Docker
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: docker-build
docker-build:
	@echo "$(BLUE)[docker]$(NC) Building image..."
	@docker build -t retele-s8 -f docker/Dockerfile .
	@echo "$(GREEN)[docker]$(NC) Image built: retele-s8"

.PHONY: docker-up
docker-up:
	@echo "$(BLUE)[docker]$(NC) Starting stack..."
	@cd docker && docker-compose up -d
	@echo "$(GREEN)[docker]$(NC) Stack started!"
	@echo "  - Nginx: http://localhost:80"
	@echo "  - Backend A: http://localhost:$(BACKEND_PORT_A)"
	@echo "  - Backend B: http://localhost:$(BACKEND_PORT_B)"

.PHONY: docker-down
docker-down:
	@echo "$(BLUE)[docker]$(NC) Stopping stack..."
	@cd docker && docker-compose down
	@echo "$(GREEN)[docker]$(NC) Stack stopped"

.PHONY: docker-logs
docker-logs:
	@cd docker && docker-compose logs -f

# ═══════════════════════════════════════════════════════════════════════════════
# Testing
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: test-ex1
test-ex1:
	@echo "$(BLUE)[test]$(NC) Testing Exercise 1 - HTTP Server"
	@$(PYTHON) $(EXER_DIR)/ex_01_http_server.py --selftest 2>/dev/null || echo "$(YELLOW)TODO: Complete the exercise$(NC)"

.PHONY: test-ex2
test-ex2:
	@echo "$(BLUE)[test]$(NC) Testing Exercise 2 - Reverse Proxy"
	@$(PYTHON) $(EXER_DIR)/ex_02_reverse_proxy.py --selftest 2>/dev/null || echo "$(YELLOW)TODO: Complete the exercise$(NC)"

.PHONY: test-all
test-all: test-ex1 test-ex2
	@echo "$(GREEN)All tests run!$(NC)"

.PHONY: smoke-test
smoke-test:
	@echo "$(BLUE)[test]$(NC) Smoke test..."
	@./tests/smoke_test.sh

# ═══════════════════════════════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════════════════════════════
.PHONY: clean
clean:
	@echo "$(BLUE)[clean]$(NC) Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f *.log
	@echo "$(GREEN)[clean]$(NC) Temporary files deleted"

.PHONY: reset
reset: clean kill-servers
	@echo "$(BLUE)[reset]$(NC) Complete reset..."
	@rm -rf $(OUT_DIR)
	@rm -f $(PCAP_DIR)/*.pcap
	@echo "$(GREEN)[reset]$(NC) Complete reset performed"

.PHONY: kill-servers
kill-servers:
	@echo "$(BLUE)[kill]$(NC) Stopping servers..."
	@-pkill -f "[d]emo_http_server.py" 2>/dev/null || true
	@-pkill -f "[d]emo_reverse_proxy.py" 2>/dev/null || true
	@-pkill -f "[e]x_01_http_server.py" 2>/dev/null || true
	@-pkill -f "[e]x_02_reverse_proxy.py" 2>/dev/null || true
	@-sudo pkill -f "[t]cpdump" 2>/dev/null || true
	@echo "$(GREEN)[kill]$(NC) Servers stopped"

# ═══════════════════════════════════════════════════════════════════════════════
# Default
# ═══════════════════════════════════════════════════════════════════════════════
.DEFAULT_GOAL := help
