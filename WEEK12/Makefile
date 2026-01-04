# =============================================================================
# Makefile – StarterKit Week 12: E-mail & RPC
# ASE-CSIE, Computer Networks
# Revolvix&Hypotheticalandrei
# =============================================================================

.PHONY: help setup run-demo run-lab capture verify clean reset \
        smtp-server smtp-send smtp-list \
        jsonrpc-server jsonrpc-client \
        xmlrpc-server xmlrpc-client \
        grpc-server grpc-client proto-gen \
        benchmark-rpc \
        docker-up docker-down docker-shell \
        mininet-run selftest

# -----------------------------------------------------------------------------
# Default configuration
# -----------------------------------------------------------------------------
PYTHON := python3
SHELL := /bin/bash

# Ports
SMTP_PORT := 1025
JSONRPC_PORT := 8080
XMLRPC_PORT := 8000
GRPC_PORT := 50051
HOST := 127.0.0.1

# Directories
SPOOL := ./spool
PCAP_DIR := ./pcap

# SMTP parameters
FROM := sender@test.local
TO := recipient@test.local
SUBJ := Test S12 Email
BODY := Test message generated from Makefile - Week 12

# -----------------------------------------------------------------------------
# Help (default target)
# -----------------------------------------------------------------------------
help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════════╗"
	@echo "║   StarterKit Week 12: E-mail & RPC                                    ║"
	@echo "║   ASE-CSIE, Computer Networks                                         ║"
	@echo "╚═══════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "SETUP & VERIFICATION:"
	@echo "  make setup          - Install Python dependencies"
	@echo "  make verify         - Check installation and dependencies"
	@echo "  make selftest       - Run self-test on all modules"
	@echo "  make clean          - Clean temporary files"
	@echo "  make reset          - Complete reset (clean + recreate spool)"
	@echo ""
	@echo "MAIN DEMOS:"
	@echo "  make run-demo       - Run main demo (SMTP + RPC)"
	@echo "  make run-lab        - Run complete lab scenario"
	@echo "  make capture        - Capture packets with tshark"
	@echo ""
	@echo "SMTP (E-MAIL):"
	@echo "  make smtp-server    - Start SMTP server on port $(SMTP_PORT)"
	@echo "  make smtp-send      - Send email (TO=x@y SUBJ='...' BODY='...')"
	@echo "  make smtp-list      - List messages from spool"
	@echo ""
	@echo "JSON-RPC:"
	@echo "  make jsonrpc-server - Start JSON-RPC server on port $(JSONRPC_PORT)"
	@echo "  make jsonrpc-client - Run JSON-RPC client"
	@echo ""
	@echo "XML-RPC:"
	@echo "  make xmlrpc-server  - Start XML-RPC server on port $(XMLRPC_PORT)"
	@echo "  make xmlrpc-client  - Run XML-RPC client"
	@echo ""
	@echo "gRPC:"
	@echo "  make proto-gen      - Generate Python code from calculator.proto"
	@echo "  make grpc-server    - Start gRPC server on port $(GRPC_PORT)"
	@echo "  make grpc-client    - Run gRPC client"
	@echo ""
	@echo "BENCHMARK & ANALYSIS:"
	@echo "  make benchmark-rpc  - Comparative benchmark JSON/XML/gRPC"
	@echo "  make capture-smtp   - Capture SMTP traffic"
	@echo "  make capture-rpc    - Capture JSON-RPC traffic"
	@echo ""
	@echo "DOCKER:"
	@echo "  make docker-up      - Start containers"
	@echo "  make docker-down    - Stop containers"
	@echo "  make docker-shell   - Interactive shell in container"
	@echo ""
	@echo "MININET:"
	@echo "  make mininet-run    - Start Mininet topology"
	@echo ""

# -----------------------------------------------------------------------------
# Setup & Verification
# -----------------------------------------------------------------------------
setup:
	@echo "[SETUP] Installing Python dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "[SETUP] Checking grpcio-tools (optional)..."
	$(PYTHON) -m pip install grpcio grpcio-tools 2>/dev/null || true
	@mkdir -p $(SPOOL) $(PCAP_DIR)
	@echo "[SETUP] ✓ Installation complete!"

verify:
	@echo "[VERIFY] Checking environment..."
	@echo ""
	@echo "Python:"
	@$(PYTHON) --version
	@echo ""
	@echo "Standard modules:"
	@$(PYTHON) -c "import json, http.server, xmlrpc.server, smtplib; print('  ✓ Standard library OK')"
	@echo ""
	@echo "External modules:"
	@$(PYTHON) -c "import grpc; print('  ✓ grpcio OK')" 2>/dev/null || echo "  ⚠ grpcio MISSING (optional)"
	@echo ""
	@echo "File structure:"
	@test -f src/email/smtp_server.py && echo "  ✓ smtp_server.py" || echo "  ✗ smtp_server.py MISSING"
	@test -f src/rpc/jsonrpc/jsonrpc_server.py && echo "  ✓ jsonrpc_server.py" || echo "  ✗ jsonrpc_server.py MISSING"
	@test -f exercises/ex_01_smtp.py && echo "  ✓ ex_01_smtp.py" || echo "  ✗ ex_01_smtp.py MISSING"
	@test -f exercises/ex_02_rpc.py && echo "  ✓ ex_02_rpc.py" || echo "  ✗ ex_02_rpc.py MISSING"
	@echo ""
	@echo "[VERIFY] ✓ Verification complete!"

selftest:
	@echo "[SELFTEST] Running auto-tests..."
	$(PYTHON) exercises/ex_01_smtp.py --selftest
	$(PYTHON) exercises/ex_02_rpc.py --selftest
	@echo "[SELFTEST] ✓ All tests passed!"

clean:
	@echo "[CLEAN] Deleting temporary files..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	rm -rf .pytest_cache .mypy_cache
	rm -rf src/rpc/grpc/*_pb2.py src/rpc/grpc/*_pb2_grpc.py
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "[CLEAN] ✓ Cleaning complete!"

reset: clean
	@echo "[RESET] Recreating directories..."
	rm -rf $(SPOOL)
	mkdir -p $(SPOOL) $(PCAP_DIR)
	@echo "[RESET] ✓ Complete reset!"

# -----------------------------------------------------------------------------
# Main demos
# -----------------------------------------------------------------------------
run-demo:
	@echo "[DEMO] Starting main demonstration..."
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "Demo 1: SMTP Server"
	@echo "═══════════════════════════════════════════════════════════"
	@mkdir -p $(SPOOL)
	$(PYTHON) src/email/smtp_server.py --port $(SMTP_PORT) --spool $(SPOOL) --demo &
	@sleep 2
	@echo ""
	@echo "Demo 2: Sending test email"
	$(PYTHON) src/email/smtp_client.py --host $(HOST) --port $(SMTP_PORT) \
		--from "$(FROM)" --to "$(TO)" --subject "$(SUBJ)" --body "$(BODY)"
	@echo ""
	@echo "[DEMO] ✓ Demonstration complete! Check $(SPOOL)/"
	@pkill -f "smtp_server.py" 2>/dev/null || true

run-lab:
	@echo "[LAB] Starting complete lab scenario..."
	./scripts/run_demos.sh

capture:
	@echo "[CAPTURE] Capturing traffic..."
	./scripts/capture.sh

# -----------------------------------------------------------------------------
# SMTP Targets
# -----------------------------------------------------------------------------
smtp-server:
	@echo "[SMTP] Starting server on port $(SMTP_PORT)..."
	@mkdir -p $(SPOOL)
	$(PYTHON) src/email/smtp_server.py \
		--listen 0.0.0.0 \
		--port $(SMTP_PORT) \
		--spool $(SPOOL)

smtp-send:
	@echo "[SMTP] Sending email to $(TO)..."
	$(PYTHON) src/email/smtp_client.py \
		--host $(HOST) \
		--port $(SMTP_PORT) \
		--from "$(FROM)" \
		--to "$(TO)" \
		--subject "$(SUBJ)" \
		--body "$(BODY)"

smtp-list:
	@echo "[SMTP] Listing messages from $(SPOOL)..."
	@ls -la $(SPOOL)/ 2>/dev/null || echo "Spool empty or non-existent"
	@echo ""
	@for f in $(SPOOL)/*.eml 2>/dev/null; do \
		if [ -f "$$f" ]; then \
			echo "═══ $$f ═══"; \
			head -20 "$$f"; \
			echo "..."; \
		fi \
	done

# -----------------------------------------------------------------------------
# JSON-RPC Targets
# -----------------------------------------------------------------------------
jsonrpc-server:
	@echo "[JSON-RPC] Starting server on port $(JSONRPC_PORT)..."
	$(PYTHON) src/rpc/jsonrpc/jsonrpc_server.py \
		--listen 0.0.0.0 \
		--port $(JSONRPC_PORT)

jsonrpc-client:
	@echo "[JSON-RPC] Running client to $(HOST):$(JSONRPC_PORT)..."
	$(PYTHON) src/rpc/jsonrpc/jsonrpc_client.py \
		--host $(HOST) \
		--port $(JSONRPC_PORT)

# -----------------------------------------------------------------------------
# XML-RPC Targets
# -----------------------------------------------------------------------------
xmlrpc-server:
	@echo "[XML-RPC] Starting server on port $(XMLRPC_PORT)..."
	$(PYTHON) src/rpc/xmlrpc/xmlrpc_server.py \
		--listen 0.0.0.0 \
		--port $(XMLRPC_PORT)

xmlrpc-client:
	@echo "[XML-RPC] Running client to $(HOST):$(XMLRPC_PORT)..."
	$(PYTHON) src/rpc/xmlrpc/xmlrpc_client.py \
		--host $(HOST) \
		--port $(XMLRPC_PORT)

# -----------------------------------------------------------------------------
# gRPC Targets
# -----------------------------------------------------------------------------
proto-gen:
	@echo "[gRPC] Generating code from calculator.proto..."
	cd src/rpc/grpc && $(PYTHON) -m grpc_tools.protoc \
		-I. \
		--python_out=. \
		--grpc_python_out=. \
		calculator.proto
	@echo "[gRPC] ✓ Files generated: calculator_pb2.py, calculator_pb2_grpc.py"

grpc-server: proto-gen
	@echo "[gRPC] Starting server on port $(GRPC_PORT)..."
	$(PYTHON) src/rpc/grpc/grpc_server.py \
		--port $(GRPC_PORT)

grpc-client:
	@echo "[gRPC] Running client to $(HOST):$(GRPC_PORT)..."
	$(PYTHON) src/rpc/grpc/grpc_client.py \
		--host $(HOST) \
		--port $(GRPC_PORT)

# -----------------------------------------------------------------------------
# Benchmark
# -----------------------------------------------------------------------------
benchmark-rpc:
	@echo "[BENCHMARK] Comparing JSON-RPC vs XML-RPC vs gRPC..."
	@echo ""
	@echo "⚠ Make sure servers are running in separate terminals!"
	@echo "  Terminal 1: make jsonrpc-server"
	@echo "  Terminal 2: make xmlrpc-server"
	@echo "  Terminal 3: make grpc-server (optional)"
	@echo ""
	./scripts/benchmark_rpc.sh 2>/dev/null || $(PYTHON) -c "\
import time, json, urllib.request; \
print('Simplified benchmark:'); \
start = time.time(); \
for i in range(100): \
    try: \
        req = urllib.request.Request('http://127.0.0.1:$(JSONRPC_PORT)', \
            data=json.dumps({'jsonrpc':'2.0','method':'add','params':[1,2],'id':i}).encode(), \
            headers={'Content-Type':'application/json'}); \
        urllib.request.urlopen(req, timeout=1); \
    except: pass; \
print(f'JSON-RPC: 100 calls in {time.time()-start:.2f}s')"

# -----------------------------------------------------------------------------
# Traffic capture
# -----------------------------------------------------------------------------
capture-smtp:
	@echo "[CAPTURE] Capturing SMTP traffic on port $(SMTP_PORT)..."
	sudo tcpdump -i lo -nn -A port $(SMTP_PORT) -c 50

capture-rpc:
	@echo "[CAPTURE] Capturing JSON-RPC traffic on port $(JSONRPC_PORT)..."
	sudo tcpdump -i lo -nn -A port $(JSONRPC_PORT) -c 30

# -----------------------------------------------------------------------------
# Docker Targets
# -----------------------------------------------------------------------------
docker-up:
	@echo "[DOCKER] Starting containers..."
	docker compose -f docker/docker-compose.yml up -d
	@echo "[DOCKER] ✓ Containers started. Check: docker ps"

docker-down:
	@echo "[DOCKER] Stopping containers..."
	docker compose -f docker/docker-compose.yml down
	@echo "[DOCKER] ✓ Containers stopped."

docker-shell:
	@echo "[DOCKER] Interactive shell..."
	docker compose -f docker/docker-compose.yml exec lab bash 2>/dev/null || \
		docker run -it --rm -v $$(pwd):/app -w /app python:3.11-slim bash

# -----------------------------------------------------------------------------
# Mininet Target
# -----------------------------------------------------------------------------
mininet-run:
	@echo "[MININET] Starting topology..."
	sudo $(PYTHON) mininet/topo_s12.py --cli
