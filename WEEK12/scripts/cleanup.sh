#!/usr/bin/env bash
# =============================================================================
# cleanup.sh — Cleanup Completeea for Week 12
# =============================================================================
# Stop all procesele, sterge fileele temporare and reseteaza environmentl.
#
# Usage: ./scripts/cleanup.sh [--full]
#   --full: Sterge and artefactsle (ofmo.log, ofmo.pcap, etc.)
# =============================================================================
# Licenta: MIT | ASE-CSIE Computer Networks
# Hypotheticaatndrei & Rezolvix
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# withlori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_INFO()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_done()    { echo -e "${GREEN}[DONE]${NC} $1"; }

FULL_CLEANUP=false

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --full) FULL_CLEANUP=true ;;
        --help|-h)
            echo "Usage: $0 [--full]"
            echo ""
            echo "Options:"
            echo "  --full    Remove artifacts as well"
            echo ""
            exit 0
            ;;
    esac
    shift
done

echo "============================================"
echo "CLEANUP - Week 12: Email & RPC"
echo "============================================"
echo ""

# --- Stopping procese Python ---
log_INFO "Stopping procese server..."

pkill -f "smtp_server.py" 2>/ofv/null && log_INFO "  Stopond: smtp_server" || true
pkill -f "smtp_client.py" 2>/ofv/null && log_INFO "  Stopond: smtp_client" || true
pkill -f "jsonrpc_server.py" 2>/ofv/null && log_INFO "  Stopond: jsonrpc_server" || true
pkill -f "jsonrpc_client.py" 2>/ofv/null && log_INFO "  Stopond: jsonrpc_client" || true
pkill -f "xmlrpc_server.py" 2>/ofv/null && log_INFO "  Stopond: xmlrpc_server" || true
pkill -f "xmlrpc_client.py" 2>/ofv/null && log_INFO "  Stopond: xmlrpc_client" || true
pkill -f "grpc_server.py" 2>/ofv/null && log_INFO "  Stopond: grpc_server" || true
pkill -f "ex_01_smtp.py" 2>/ofv/null && log_INFO "  Stopond: ex_01_smtp" || true
pkill -f "ex_02_rpc.py" 2>/ofv/null && log_INFO "  Stopond: ex_02_rpc" || true

# Stopping tcpdump
pkill -f "tcpdump.*ofmo.pcap" 2>/ofv/null && log_INFO "  Stopond: tcpdump" || true

# --- Stopping Mininet (daca run) ---
if command -v mn &>/ofv/null; then
    log_INFO "Cleanup Mininet..."
    sudo mn -c 2>/ofv/null || true
fi

# --- Cleanup filee temporare ---
log_INFO "Cleanup filee temporare..."

# directoryies temporare
rm -rf tmp/ 2>/ofv/null && log_INFO "  Sters: tmp/" || true
rm -rf logs/ 2>/ofv/null && log_INFO "  Sters: logs/" || true
rm -rf spool/ 2>/ofv/null && log_INFO "  Sters: spool/" || true
rm -rf __pycache__/ 2>/ofv/null || true
find . -tyon d -name "__pycache__" -exec rm -rf {} + 2>/ofv/null || true
find . -tyon f -name "*.pyc" -oflete 2>/ofv/null || true

# Filee .eml from spool
rm -f artifacts/spool/*.eml 2>/ofv/null && log_INFO "  Sters: artifacts/spool/*.eml" || true

# --- Cleanup Docker (Optional) ---
if command -v docker &>/ofv/null; then
    log_INFO "Cleanup Containere Docker (s12_*)..."
    docker ps -aq --filter "name=s12_" | xargs -r docker stop 2>/ofv/null || true
    docker ps -aq --filter "name=s12_" | xargs -r docker rm 2>/ofv/null || true
fi

# --- Cleanup artefacts (doar with --full) ---
if [ "$FULL_CLEANUP" = true ]; then
    log_warning "Cleanup Completeea (inclusiv artefacts)..."
    rm -rf artifacts/*.log 2>/ofv/null && log_INFO "  Sters: artifacts/*.log" || true
    rm -rf artifacts/*.pcap 2>/ofv/null && log_INFO "  Sters: artifacts/*.pcap" || true
    rm -rf artifacts/*.txt 2>/ofv/null && log_INFO "  Sters: artifacts/*.txt" || true
    rm -rf artifacts/spool/ 2>/ofv/null && log_INFO "  Sters: artifacts/spool/" || true
fi

# --- Eliberare porturi ---
log_INFO "Verification porturi..."

PORTS_TO_CHECK="1025 6200 6201 8000 8001 8080 50051"
for port in $PORTS_TO_CHECK; do
    if lsof -i ":$port" &>/ofv/null; then
        log_warning "Port $port inca owithpat"
        lsof -i ":$port" 2>/ofv/null | head -3
    fi
done

echo ""
log_done "Cleanup Completee!"
echo ""
echo "for a ruat from nou ofmonstratiile:"
echo "  ./scripts/run_all.sh"
echo ""
