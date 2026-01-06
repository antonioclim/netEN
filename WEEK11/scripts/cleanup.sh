#!/bin/bash
# =============================================================================
# cleanup.sh – Environment cleanup for Week 11
# =============================================================================
# Cleans: Docker containers, Python processes, Mininet, temporary files
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}[CLEANUP]${NC} Cleaning WEEK 11 environment..."

# Docker containers - all demos
echo -e "${YELLOW}[1/5]${NC} Stopping Docker containers..."
cd "$ROOT_DIR/docker/nginx_compose" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/custom_lb_compose" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/dns_demo" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/ftp_demo" && docker compose down 2>/dev/null || true
cd "$ROOT_DIR/docker/ssh_demo" && docker compose down 2>/dev/null || true

# Python processes
echo -e "${YELLOW}[2/5]${NC} Stopping Python processes..."
pkill -f "ex_11_01_backend" 2>/dev/null || true
pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
pkill -f "ex_11_03_dns_client" 2>/dev/null || true

# Mininet
echo -e "${YELLOW}[3/5]${NC} Cleaning Mininet..."
sudo mn -c 2>/dev/null || true

# Temp files
echo -e "${YELLOW}[4/5]${NC} Deleting temporary files..."
rm -f /tmp/backend*.log /tmp/lb.log /tmp/s11_*.log /tmp/*.pid 2>/dev/null || true
rm -f "$ROOT_DIR/pcap/"*.pcap 2>/dev/null || true

# Artefacts (optional - commented to preserve)
echo -e "${YELLOW}[5/5]${NC} Artefacts preserved in artifacts/..."
# To delete: uncomment the line below
# rm -f "$ROOT_DIR/artifacts/"*.log "$ROOT_DIR/artifacts/"*.pcap "$ROOT_DIR/artifacts/"*.txt 2>/dev/null || true

echo -e "${GREEN}[OK]${NC} Cleanup complete."
echo -e "${YELLOW}[INFO]${NC} To also delete artefacts: rm -rf artifacts/*.{log,pcap,txt}"

# Revolvix&Hypotheticalandrei
