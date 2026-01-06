# ==============================================================================
# Week 13 - IoT and Security in Computer Networks
# ==============================================================================
# This Makefile is designed to be "canonical": a small set of predictable targets
# and consistent scripts that work on Ubuntu 24.04.
#
# Key goals:
#   - Everything in British English
#   - No "externally-managed-environment" (PEP 668) issues: we use a local venv
#   - Docker services run with stable defaults but ports can be overridden
#   - Logs and artefacts are written under ./artifacts/
# ==============================================================================

SHELL := /bin/bash

# ------------------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------------------
ROOT_DIR        := $(shell pwd)
SCRIPTS_DIR     := $(ROOT_DIR)/scripts
PYTHON_DIR      := $(ROOT_DIR)/python
DOCKER_DIR      := $(ROOT_DIR)/docker
CONFIGS_DIR     := $(ROOT_DIR)/configs
CERTS_DIR       := $(CONFIGS_DIR)/certs
ARTIFACTS_DIR   := $(ROOT_DIR)/artifacts

VENV_DIR        := $(ROOT_DIR)/.venv
SYS_PYTHON      := python3
VENV_PYTHON     := $(VENV_DIR)/bin/python
VENV_PIP        := $(VENV_DIR)/bin/pip

# Use venv Python when available, otherwise fall back to system Python
PY              := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(SYS_PYTHON))

# Docker compose (project uses docker/docker-compose.yml by default)
DOCKER_COMPOSE  ?= docker compose
COMPOSE_FILE    := $(DOCKER_DIR)/docker-compose.yml
ENV_FILE        := $(ROOT_DIR)/.env

# ------------------------------------------------------------------------------
# Defaults (override like: make scan TARGET=127.0.0.1 PORTS=1-10000)
# ------------------------------------------------------------------------------
# Hostnames for demos running on the host
TARGET          ?= 127.0.0.1
BROKER_HOST     ?= 127.0.0.1

# Ports (host-side). docker-compose.yml uses these via .env
DVWA_HOST_PORT      ?= 8080
VSFTPD_HOST_PORT    ?= 2121
VSFTPD_BACKDOOR_HOST_PORT ?= 6200
MQTT_PLAIN_PORT     ?= 1883
MQTT_TLS_PORT       ?= 8883

# Demo defaults
PORTS           ?= 21,22,80,443,1883,8883,8080,2121,$(VSFTPD_BACKDOOR_HOST_PORT)
TOPIC           ?= iot/sensors/temperature
MESSAGE         ?= {"sensor":"temp","value":24.3}

# ------------------------------------------------------------------------------
# Output helpers
# ------------------------------------------------------------------------------
define _banner
	@printf "\n========================================================================\n"
	@printf "  %s\n" "$(1)"
	@printf "========================================================================\n\n"
endef

.PHONY: help setup verify venv python-deps certs env \
        docker-up docker-down docker-status docker-logs \
        run-all scan demo-offensive demo-defensive \
        demo-mqtt-plain demo-mqtt-tls mqtt-pub mqtt-sub \
        exploit-ftp \
        mininet-base mininet-extended mininet-clean \
        capture-start capture-stop \
        test lint clean clean-all reset

help:
	$(call _banner,Week 13 - IoT and Security (targets))
	@printf "Configuration:\n"
	@printf "  make setup                Prepare venv, certificates and artefact directories\n"
	@printf "  make verify               Verify tools, Python modules and kit structure\n\n"
	@printf "Docker lab:\n"
	@printf "  make docker-up            Start vulnerable services (DVWA, MQTT broker, vsftpd)\n"
	@printf "  make docker-down          Stop services and remove containers and networks\n"
	@printf "  make docker-status        Show container status\n"
	@printf "  make docker-logs          Tail container logs\n\n"
	@printf "Demos:\n"
	@printf "  make run-all             Full automated run (produces artefacts)\n"
	@printf "  make demo-offensive       Port scan and safe exploitation demonstrations\n"
	@printf "  make demo-defensive       Defensive checks (sniffing and vulnerability checks)\n"
	@printf "  make demo-mqtt-plain      MQTT plaintext publish demo\n"
	@printf "  make demo-mqtt-tls        MQTT TLS publish demo (requires certs)\n\n"
	@printf "Tools:\n"
	@printf "  make scan                 Run the Python port scanner\n"
	@printf "  make mqtt-pub             Publish MQTT message (plain)\n"
	@printf "  make mqtt-sub             Subscribe to MQTT topic (plain)\n"
	@printf "  make exploit-ftp          Safe demonstration of an FTP backdoor check\n\n"
	@printf "Mininet:\n"
	@printf "  make mininet-base         Start base topology (requires sudo)\n"
	@printf "  make mininet-extended     Start extended topology (requires sudo)\n"
	@printf "  make mininet-clean        Clean Mininet and OVS artefacts (requires sudo)\n\n"
	@printf "Capture:\n"
	@printf "  make capture-start IFACE=eth0  Start tcpdump capture (requires sudo)\n"
	@printf "  make capture-stop              Stop capture\n\n"
	@printf "Housekeeping:\n"
	@printf "  make test                Run smoke tests (non-destructive)\n"
	@printf "  make lint                Quick Python syntax checks\n"
	@printf "  make clean               Remove temporary files (keeps Docker)\n"
	@printf "  make reset               Full reset (includes Docker and captures)\n\n"

setup: venv python-deps certs env
	$(call _banner,Setup complete)
	@printf "Next steps:\n"
	@printf "  1. make verify\n"
	@printf "  2. make docker-up\n"
	@printf "  3. make demo-offensive   or   make demo-defensive\n\n"

verify:
	@$(SCRIPTS_DIR)/verify.sh

venv:
	$(call _banner,Creating Python virtual environment)
	@mkdir -p "$(ARTIFACTS_DIR)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(SYS_PYTHON) -m venv --system-site-packages "$(VENV_DIR)"; \
	fi
	@$(VENV_PIP) -q install --upgrade pip wheel setuptools >/dev/null
	@printf "✓ venv ready: %s\n" "$(VENV_DIR)"

python-deps:
	$(call _banner,Installing Python dependencies)
	@$(VENV_PIP) -q install -r requirements.txt
	@printf "✓ Python dependencies installed\n"

certs:
	$(call _banner,Generating MQTT TLS certificates)
	@mkdir -p "$(CERTS_DIR)"
	@if [ ! -f "$(CERTS_DIR)/ca.crt" ]; then \
		openssl req -x509 -newkey rsa:2048 -days 365 -nodes \
			-subj "/CN=Week13-CA" \
			-keyout "$(CERTS_DIR)/ca.key" \
			-out "$(CERTS_DIR)/ca.crt" >/dev/null 2>&1; \
	fi
	@if [ ! -f "$(CERTS_DIR)/server.crt" ]; then \
		openssl req -newkey rsa:2048 -nodes \
			-subj "/CN=week13-mqtt" \
			-keyout "$(CERTS_DIR)/server.key" \
			-out "$(CERTS_DIR)/server.csr" >/dev/null 2>&1; \
		openssl x509 -req -days 365 \
			-in "$(CERTS_DIR)/server.csr" \
			-CA "$(CERTS_DIR)/ca.crt" \
			-CAkey "$(CERTS_DIR)/ca.key" \
			-CAcreateserial \
			-out "$(CERTS_DIR)/server.crt" >/dev/null 2>&1; \
		rm -f "$(CERTS_DIR)/server.csr" "$(CERTS_DIR)/ca.srl"; \
	fi
	@printf "✓ Certificates available under %s\n" "$(CERTS_DIR)"

env:
	$(call _banner,Preparing Docker environment file)
	@$(SCRIPTS_DIR)/generate_env.sh "$(ENV_FILE)" "$(DVWA_HOST_PORT)" "$(VSFTPD_HOST_PORT)" "$(MQTT_PLAIN_PORT)" "$(MQTT_TLS_PORT)"
	@printf "✓ .env ready: %s\n" "$(ENV_FILE)"
	@printf "  DVWA:    http://127.0.0.1:$$(grep -E '^DVWA_HOST_PORT=' "$(ENV_FILE)" | cut -d= -f2)/\n"
	@printf "  vsftpd:  127.0.0.1:$$(grep -E '^VSFTPD_HOST_PORT=' "$(ENV_FILE)" | cut -d= -f2)\n"
	@printf "  vsftpd backdoor: 127.0.0.1:$$(grep -E '^VSFTPD_BACKDOOR_HOST_PORT=' "$(ENV_FILE)" | cut -d= -f2)\n"
	@printf "  MQTT:    127.0.0.1:$$(grep -E '^MQTT_PLAIN_PORT=' "$(ENV_FILE)" | cut -d= -f2) (plain)\n"
	@printf "  MQTT:    127.0.0.1:$$(grep -E '^MQTT_TLS_PORT=' "$(ENV_FILE)" | cut -d= -f2) (TLS)\n"

docker-up: env
	$(call _banner,Starting Docker lab services)
	@mkdir -p "$(ARTIFACTS_DIR)"
	@$(DOCKER_COMPOSE) --env-file "$(ENV_FILE)" -f "$(COMPOSE_FILE)" up -d --remove-orphans
	@$(DOCKER_COMPOSE) --env-file "$(ENV_FILE)" -f "$(COMPOSE_FILE)" ps
	@printf "\nTip: if Docker commands fail, try: sudo make docker-up\n\n"

docker-down:
	$(call _banner,Stopping Docker lab services)
	-@$(DOCKER_COMPOSE) --env-file "$(ENV_FILE)" -f "$(COMPOSE_FILE)" down -v --remove-orphans

docker-status:
	@$(DOCKER_COMPOSE) --env-file "$(ENV_FILE)" -f "$(COMPOSE_FILE)" ps

docker-logs:
	@$(DOCKER_COMPOSE) --env-file "$(ENV_FILE)" -f "$(COMPOSE_FILE)" logs -f --tail=200

# ------------------------------------------------------------------------------
# Demos and tools
# ------------------------------------------------------------------------------
scan:
	$(call _banner,Port scan)
	@mkdir -p "$(ARTIFACTS_DIR)"
	@$(PY) "$(PYTHON_DIR)/exercises/ex_01_port_scanner.py" \
		--target "$(TARGET)" \
		--ports "$(PORTS)" \
		--mode scan \
		--json-out "$(ARTIFACTS_DIR)/scan_results.json"
	@printf "\n✓ Results: %s\n\n" "$(ARTIFACTS_DIR)/scan_results.json"

demo-mqtt-plain:
	$(call _banner,MQTT plaintext demo)
	@$(PY) "$(PYTHON_DIR)/exercises/ex_02_mqtt_client.py" \
		--broker "$(BROKER_HOST)" \
		--port "$$(grep -E '^MQTT_PLAIN_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(MQTT_PLAIN_PORT))" \
		--mode publish \
		--topic "$(TOPIC)" \
		--message "$(MESSAGE)" \
		--count 3 \
		--qos 0

demo-mqtt-tls:
	$(call _banner,MQTT TLS demo)
	@$(PY) "$(PYTHON_DIR)/exercises/ex_02_mqtt_client.py" \
		--broker "$(BROKER_HOST)" \
		--port "$$(grep -E '^MQTT_TLS_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(MQTT_TLS_PORT))" \
		--mode publish \
		--topic "$(TOPIC)" \
		--message "$(MESSAGE)" \
		--count 3 \
		--qos 0 \
		--tls \
		--cafile "$(CERTS_DIR)/ca.crt"

mqtt-pub:
	$(call _banner,MQTT publish)
	@$(PY) "$(PYTHON_DIR)/exercises/ex_02_mqtt_client.py" \
		--broker "$(BROKER_HOST)" \
		--port "$$(grep -E '^MQTT_PLAIN_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(MQTT_PLAIN_PORT))" \
		--mode publish \
		--topic "$(TOPIC)" \
		--message "$(MESSAGE)" \
		--count 1

mqtt-sub:
	$(call _banner,MQTT subscribe)
	@$(PY) "$(PYTHON_DIR)/exercises/ex_02_mqtt_client.py" \
		--broker "$(BROKER_HOST)" \
		--port "$$(grep -E '^MQTT_PLAIN_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(MQTT_PLAIN_PORT))" \
		--mode subscribe \
		--topic "$(TOPIC)" \
		--timeout 20

exploit-ftp:
	$(call _banner,FTP backdoor check demonstration)
	@$(PY) "$(PYTHON_DIR)/exploits/ftp_backdoor_vsftpd.py" \
		--target "$(TARGET)" \
		--ftp-port "$$(grep -E '^VSFTPD_HOST_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(VSFTPD_HOST_PORT))" \
		--backdoor-port "$$(grep -E '^VSFTPD_BACKDOOR_HOST_PORT=' "$(ENV_FILE)" 2>/dev/null | cut -d= -f2 || echo $(VSFTPD_BACKDOOR_HOST_PORT))" \
		--command "id" || true
	@printf "\nNote: this is an educational stub. It demonstrates detection of an exposed port and safe handling.\n\n"

demo-offensive: docker-up scan exploit-ftp
	$(call _banner,Offensive demo complete)
	@printf "Artefacts are available in %s\n\n" "$(ARTIFACTS_DIR)"

demo-defensive: docker-up demo-mqtt-plain
	$(call _banner,Defensive demo complete)
	@printf "Try: sudo make capture-start IFACE=any and then re-run demo-mqtt-plain\n\n"

run-all: setup docker-up
	$(call _banner,Full automated run)
	@$(SCRIPTS_DIR)/run_all.sh
	@printf "\n✓ Automated run complete. See %s\n\n" "$(ARTIFACTS_DIR)"

# ------------------------------------------------------------------------------
# Mininet
# ------------------------------------------------------------------------------
mininet-base:
	$(call _banner,Mininet base topology)
	@sudo "$(PY)" "$(ROOT_DIR)/mininet/topologies/topo_base.py"

mininet-extended:
	$(call _banner,Mininet extended topology)
	@sudo "$(PY)" "$(ROOT_DIR)/mininet/topologies/topo_segmented.py"

mininet-clean:
	$(call _banner,Cleaning Mininet and OVS)
	@sudo timeout 12 mn -c >/dev/null 2>&1 || true
	@sudo timeout 12 ovs-vsctl --if-exists del-br s1 >/dev/null 2>&1 || true
	@sudo timeout 12 ovs-vsctl --if-exists del-br s2 >/dev/null 2>&1 || true
	@printf "✓ Cleanup complete.\n"

# ------------------------------------------------------------------------------
# Capture helpers
# ------------------------------------------------------------------------------
CAPTURE_FILE ?= $(ARTIFACTS_DIR)/capture.pcap
IFACE ?= any

capture-start:
	$(call _banner,Starting tcpdump capture)
	@mkdir -p "$(ARTIFACTS_DIR)"
	@sudo tcpdump -i "$(IFACE)" -w "$(CAPTURE_FILE)" >/dev/null 2>&1 &
	@echo $$! > "$(ARTIFACTS_DIR)/tcpdump.pid"
	@printf "✓ Capturing on %s to %s\n" "$(IFACE)" "$(CAPTURE_FILE)"

capture-stop:
	$(call _banner,Stopping tcpdump capture)
	@if [ -f "$(ARTIFACTS_DIR)/tcpdump.pid" ]; then \
		sudo kill "$$(cat "$(ARTIFACTS_DIR)/tcpdump.pid")" >/dev/null 2>&1 || true; \
		rm -f "$(ARTIFACTS_DIR)/tcpdump.pid"; \
		printf "✓ Capture stopped: %s\n" "$(CAPTURE_FILE)"; \
	else \
		printf "No capture PID file found.\n"; \
	fi

# ------------------------------------------------------------------------------
# Quality checks and cleanup
# ------------------------------------------------------------------------------
test:
	@$(SCRIPTS_DIR)/smoke_test.sh

lint:
	$(call _banner,Python syntax check)
	@$(PY) -m compileall -q "$(PYTHON_DIR)"

clean:
	$(call _banner,Cleaning temporary files)
	@find "$(ROOT_DIR)" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -f "$(ARTIFACTS_DIR)/tcpdump.pid" 2>/dev/null || true
	@rm -f "$(ARTIFACTS_DIR)"/capture*.pcap 2>/dev/null || true
	@printf "✓ Clean complete.\n"

reset: docker-down mininet-clean clean
	$(call _banner,Reset complete)
	@rm -f /tmp/demo_capture.pcap 2>/dev/null || true
	@printf "✓ Full reset complete.\n"

clean-all: reset
	@rm -rf "$(VENV_DIR)"
	@rm -rf "$(CERTS_DIR)"
	@rm -f "$(ENV_FILE)"
	@printf "✓ Removed venv, certificates and .env\n"
