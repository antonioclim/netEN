# ==============================================================================
# Makefile - Starterkit S13: IoT and Security in Computer Networks
# ==============================================================================
# Automations for demonstrations, exercises and infrastructure management
# Usage: make <target> [VARIABILE=value]
# ==============================================================================

.PHONY: help setup setup-mininet test lint clean clean-all \
        docker-up docker-down docker-logs docker-status \
        demo-offensive demo-defensive demo-mqtt-plain demo-mqtt-tls \
        scan mqtt-pub mqtt-sub exploit-ftp \
        mininet-base mininet-extended mininet-clean \
        capture-start capture-stop

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SHELL := /bin/bash
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := docker/docker-compose.yml
# Fall back to root docker-compose.yml if docker/docker-compose.yml is missing
ifeq ($(wildcard $(DOCKER_COMPOSE_FILE)),)
DOCKER_COMPOSE_FILE := docker-compose.yml
endif

# Directories
ROOT_DIR := $(shell pwd)
PYTHON_DIR := $(ROOT_DIR)/python
SCRIPTS_DIR := $(ROOT_DIR)/scripts
CONFIGS_DIR := $(ROOT_DIR)/configs
CERTS_DIR := $(CONFIGS_DIR)/certs
MININET_DIR := $(ROOT_DIR)/mininet

# Docker network
DOCKER_NETWORK := pentestnet
DOCKER_SUBNET := 172.20.0.0/24

# Default IPs
TARGET ?= 172.20.0.10
BROKER_IP ?= 10.0.0.100
MQTT_PORT_PLAIN ?= 1883
MQTT_PORT_TLS ?= 8883
TOPIC ?= home/kitchen/telemetry

# Colours for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# ==============================================================================
# HELP
# ==============================================================================

help:
	@echo -e "$(BLUE)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║     Starterkit S13 - IoT and Security in Computer Networks     ║$(NC)"
	@echo -e "$(BLUE)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(GREEN)SETUP:$(NC)"
	@echo "  make setup              - Install dependencies + certificateses"
	@echo "  make setup-mininet      - Complete setup for Mininet (sudo)"
	@echo ""
	@echo -e "$(GREEN)DOCKER:$(NC)"
	@echo "  make docker-up          - Start vulnerable containers"
	@echo "  make docker-down        - Stop and clean containers"
	@echo "  make docker-logs        - View container logs"
	@echo "  make docker-status      - Container status"
	@echo ""
	@echo -e "$(GREEN)DEMONSTRATIONS (secvente automate):$(NC)"
	@echo "  make demo-offensive     - Scan → Enum → Exploit (complete)"
	@echo "  make demo-defensive     - TLS → ACL → Segmentare"
	@echo "  make demo-mqtt-plain    - MQTT without encryption"
	@echo "  make demo-mqtt-tls      - MQTT with TLS"
	@echo ""
	@echo -e "$(GREEN)EXERCISES INDIVIDUALE:$(NC)"
	@echo "  make scan TARGET=IP     - Port Scanning (default: $(TARGET))"
	@echo "  make mqtt-pub TOPIC=X   - Publish message MQTT"
	@echo "  make mqtt-sub TOPIC=X   - Subscribe at topic MQTT"
	@echo "  make exploit-ftp        - Exploit vsftpd backdoor"
	@echo ""
	@echo -e "$(GREEN)MININET (requires sudo):$(NC)"
	@echo "  make mininet-base       - Base topology"
	@echo "  make mininet-extended   - Segmented topology"
	@echo "  make mininet-clean      - Mininet cleanup"
	@echo ""
	@echo -e "$(GREEN)CAPTURA TRAFIC:$(NC)"
	@echo "  make capture-start IF=X - Start capture (default: any)"
	@echo "  make capture-stop       - Stop capture"
	@echo ""
	@echo -e "$(GREEN)UTILITARE:$(NC)"
	@echo "  make test               - Complete smoke test"
	@echo "  make lint               - Python syntax verification"
	@echo "  make clean              - Temporary files cleanup"
	@echo "  make clean-all          - Complete reset"
	@echo ""

# ==============================================================================
# SETUP
# ==============================================================================

setup: _check-python _install-python-deps _generate-certs
	@echo -e "$(GREEN)[✓] Complete setup!$(NC)"
	@echo "    Running 'make test' for verification."

_check-python:
	@echo -e "$(BLUE)[*] Python verification...$(NC)"
	@$(PYTHON) --version || (echo -e "$(RED)[✗] Python3 is not installed$(NC)" && exit 1)

_install-python-deps:
	@echo -e "$(BLUE)[*] Install Python dependencies...$(NC)"
	@$(PIP) install -q --upgrade pip
	@$(PIP) install -q -r requirements.txt
	@echo -e "$(GREEN)[✓] Python dependencies installed$(NC)"

_generate-certs:
	@echo -e "$(BLUE)[*] Generate TLS certificateses...$(NC)"
	@mkdir -p $(CERTS_DIR)
	@if [ ! -f $(CERTS_DIR)/ca.crt ]; then \
		openssl req -x509 -nodes -newkey rsa:2048 \
			-keyout $(CERTS_DIR)/ca.key \
			-out $(CERTS_DIR)/ca.crt \
			-subj "/CN=IoT-Lab-CA" \
			-days 365 2>/dev/null; \
		echo -e "$(GREEN)[✓] CA generated$(NC)"; \
	fi
	@if [ ! -f $(CERTS_DIR)/server.crt ]; then \
		openssl req -nodes -newkey rsa:2048 \
			-keyout $(CERTS_DIR)/server.key \
			-out $(CERTS_DIR)/server.csr \
			-subj "/CN=broker" 2>/dev/null; \
		openssl x509 -req \
			-in $(CERTS_DIR)/server.csr \
			-CA $(CERTS_DIR)/ca.crt \
			-CAkey $(CERTS_DIR)/ca.key \
			-CAcreateserial \
			-out $(CERTS_DIR)/server.crt \
			-days 365 2>/dev/null; \
		rm -f $(CERTS_DIR)/server.csr; \
		echo -e "$(GREEN)[✓] Certificateses server generate$(NC)"; \
	fi

setup-mininet: setup
	@echo -e "$(BLUE)[*] Installation Mininet and dependencies...$(NC)"
	@sudo apt-get update -qq
	@sudo apt-get install -y -qq mininet openvswitch-switch mosquitto mosquitto-clients tcpdump tshark
	@sudo service openvswitch-switch start || true
	@echo -e "$(GREEN)[✓] Setup Mininet complete$(NC)"

# ==============================================================================
# DOCKER
# ==============================================================================

docker-up:
	@echo -e "$(BLUE)[*] Start vulnerable containers...$(NC)"
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d
	@sleep 3
	@echo -e "$(GREEN)[✓] Containere pornite:$(NC)"
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

docker-down:
	@echo -e "$(BLUE)[*] Stop containere...$(NC)"
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v --remove-orphans
	@echo -e "$(GREEN)[✓] Containere oprite$(NC)"

docker-logs:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

docker-status:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

# ==============================================================================
# DEMONSTRATIONS AUTOMATE
# ==============================================================================

demo-offensive: docker-up
	@echo ""
	@echo -e "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(YELLOW)║            DEMO OFENSIV - Fluxul complete of pentest            ║$(NC)"
	@echo -e "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 1: Discovery network (Host Discovery)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Scan the Docker subnet $(DOCKER_SUBNET) for active hosts...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.1-15 --mode discovery --timeout 0.5
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 2: Port Scanning (Port Scanning)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Identifym servicesle on hostsle descoperite...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.10 --ports 1-1024 --timeout 0.3
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.12 --ports 20-25,2121,6200 --timeout 0.3
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 3: Service enumeration (Service Enumeration)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Extragem information about versiuni and configurari...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/banner_grabber.py --target 172.20.0.12 --port 2121
	@$(PYTHON) $(PYTHON_DIR)/exploits/banner_grabber.py --target 172.20.0.10 --port 80 --http
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 4: Verification vulnerabilities (Vulnerability Check)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Cautam vulnerabilities cunoscute...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_04_vuln_checker.py --target 172.20.0.12 --port 2121 --service ftp
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 5: Controlled Exploitation (Controlled Exploitation)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Demonstram exploatarea vulnerabilitiesi vsftpd 2.3.4...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/ftp_backdoor_vsftpd.py --target 172.20.0.12 --ftp-port 2121 --backdoor-port 6200 --command "id; whoami; uname -a"
	@echo ""
	@echo -e "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(GREEN)║                    DEMO OFENSIV COMPLETE!                       ║$(NC)"
	@echo -e "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"

demo-defensive:
	@echo ""
	@echo -e "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(YELLOW)║           DEMO DEFENSIV - Masuri of protection IoT             ║$(NC)"
	@echo -e "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(RED)  ⚠  This demo necesita Mininet (sudo make setup-mininet)$(NC)"
	@echo ""
	@bash $(SCRIPTS_DIR)/run_demo_defensive.sh

demo-mqtt-plain:
	@echo -e "$(BLUE)[*] Demo MQTT in clar (NESECURIZAT)...$(NC)"
	@echo -e "$(RED)  ⚠  Trafficul is vizibil in capture!$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC) --count 3

demo-mqtt-tls:
	@echo -e "$(BLUE)[*] Demo MQTT with TLS (SECURIZAT)...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_TLS) --topic $(TOPIC) --count 3 --tls on --cafile $(CERTS_DIR)/ca.crt --username sensor1 --password sensor1pass

# ==============================================================================
# EXERCISES INDIVIDUALE
# ==============================================================================

scan:
	@echo -e "$(BLUE)[*] Port Scanning on $(TARGET)...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target $(TARGET) --ports 1-1024 --timeout 0.3 --json-out /tmp/scan_$(shell date +%Y%m%d_%H%M%S).json

mqtt-pub:
	@echo -e "$(BLUE)[*] MQTT publish on topic '$(TOPIC)'...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC) --count 1

mqtt-sub:
	@echo -e "$(BLUE)[*] Subscribe at topic '$(TOPIC)'...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role controller --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC)

exploit-ftp:
	@echo -e "$(BLUE)[*] Exploit vsftpd 2.3.4 backdoor...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/ftp_backdoor_vsftpd.py --target 172.20.0.12 --ftp-port 2121 --backdoor-port 6200 --command "id"

# ==============================================================================
# MININET
# ==============================================================================

mininet-base:
	@echo -e "$(BLUE)[*] Start topology Mininet baza...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topologies/topo_base.py --mode plain --cli

mininet-extended:
	@echo -e "$(BLUE)[*] Start topology Mininet segmentata...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topologies/topo_segmented.py --mode tls --policy restricted --cli

mininet-clean:
	@echo -e "$(BLUE)[*] Mininet cleanup...$(NC)"
	@sudo pkill -f mosquitto || true
	@sudo pkill -f mgmt_http || true
	@sudo mn -c 2>/dev/null || true
	@echo -e "$(GREEN)[✓] Mininet curatat$(NC)"

# ==============================================================================
# CAPTURA TRAFIC
# ==============================================================================

IF ?= any
PCAP_FILE ?= /tmp/capture_$(shell date +%Y%m%d_%H%M%S).pcap

capture-start:
	@echo -e "$(BLUE)[*] Start capture on interface '$(IF)'...$(NC)"
	@sudo tcpdump -i $(IF) -w $(PCAP_FILE) -n 'tcp port 1883 or tcp port 8883 or tcp port 2121' &
	@echo -e "$(GREEN)[✓] Capture started: $(PCAP_FILE)$(NC)"
	@echo "    Stop with: make capture-stop"

capture-stop:
	@echo -e "$(BLUE)[*] Stop capture...$(NC)"
	@sudo pkill -f tcpdump || true
	@echo -e "$(GREEN)[✓] Capture stopped$(NC)"

# ==============================================================================
# TESTS
# ==============================================================================

test: _test-syntax _test-imports
	@echo -e "$(GREEN)[✓] All tests passed!$(NC)"

_test-syntax:
	@echo -e "$(BLUE)[*] Python syntax verification...$(NC)"
	@$(PYTHON) -m py_compile $(PYTHON_DIR)/exercises/*.py $(PYTHON_DIR)/utils/*.py $(PYTHON_DIR)/exploits/*.py
	@echo -e "$(GREEN)[✓] Correct syntax$(NC)"

_test-imports:
	@echo -e "$(BLUE)[*] Import verification...$(NC)"
	@$(PYTHON) -c "import socket, json, argparse, time; print('  Standard libs: OK')"
	@$(PYTHON) -c "import paho.mqtt.client; print('  paho-mqtt: OK')" || echo -e "$(YELLOW)  [!] paho-mqtt is not installed$(NC)"
	@echo -e "$(GREEN)[✓] Imports verified$(NC)"

lint:
	@echo -e "$(BLUE)[*] Python linting...$(NC)"
	@$(PYTHON) -m py_compile $(PYTHON_DIR)/**/*.py

# ==============================================================================
# CLEANUP
# ==============================================================================

clean:
	@echo -e "$(BLUE)[*] Temporary files cleanup...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f /tmp/scan_*.json /tmp/capture_*.pcap /tmp/mqtt_*.pcap
	@echo -e "$(GREEN)[✓] Cleanup completa$(NC)"

clean-all: clean docker-down mininet-clean
	@echo -e "$(BLUE)[*] Complete reset...$(NC)"
	@rm -rf $(CERTS_DIR)/*
	@echo -e "$(GREEN)[✓] Complete reset$(NC)"

# ==============================================================================
# FIN
# ==============================================================================
