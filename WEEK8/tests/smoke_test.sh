#!/bin/bash
set -euo pipefail

# Do not generate Python bytecode artefacts
export PYTHONDONTWRITEBYTECODE=1
# ═══════════════════════════════════════════════════════════════════════════════
# smoke_test.sh - Quick functionality test (Week 8)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Checks:
#   - Preconditions (Python, curl, kit files)
#   - Functionality server HTTP
#   - Functionality reverse proxy
#   - Artefact existence (demo.log, demo.pcap, validation.txt)
#
# Autor: Computer Networks, ASE Bucharest
# Hypotheticalandrei & Rezolvix | MIT License
# ═══════════════════════════════════════════════════════════════════════════════

# Note: NOT using set -e because arithmetic operations can return non-zero

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
WEEK=8
HTTP_PORT=18080       # Unique port for smoke test
PROXY_PORT=18888
BACKEND_PORT=19001

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Smoke Test - Week 8: HTTP Server and Reverse Proxy               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

PASSED=0
FAILED=0
WARNED=0

cleanup() {
    pkill -f "demo_http_server.py.*$HTTP_PORT" 2>/dev/null || true
    pkill -f "demo_http_server.py.*$BACKEND_PORT" 2>/dev/null || true
    pkill -f "demo_reverse_proxy.py.*$PROXY_PORT" 2>/dev/null || true
}
trap cleanup EXIT

# ─────────────────────────────────────────────────────────────────────────────
# Sectiunea 1: Preconditions
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Preconditions]${NC}"

# Test 1: Python 3
echo -n "  [1] Python 3 available... "
if python3 --version &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 2: Module Python standard
echo -n "  [2] Module Python necesare... "
if python3 -c "import socket, threading, argparse, os, sys" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 3: curl available
echo -n "  [3] curl available... "
if command -v curl &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 4: files kit prezente
echo -n "  [4] files kit prezente... "
if [ -f "python/demos/demo_http_server.py" ] && \
   [ -f "python/demos/demo_reverse_proxy.py" ] && \
   [ -f "python/utils/net_utils.py" ] && \
   [ -f "www/index.html" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Sectiunea 2: Server HTTP
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Server HTTP]${NC}"

# Test 5: Starting server HTTP
echo -n "  [5] Server HTTP starts... "
python3 python/demos/demo_http_server.py \
    --host 127.0.0.1 \
    --port $HTTP_PORT \
    --www www \
    --mode threaded &
SERVER_PID=$!
sleep 1

if kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test 6: GET / → 200 OK
echo -n "  [6] GET / → 200 OK... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$HTTP_PORT/ 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test 7: GET /not-found → 404
echo -n "  [7] GET /not-found → 404... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$HTTP_PORT/not-found 2>/dev/null || echo "000")
if [ "$RESPONSE" = "404" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test 8: Header X-Backend prezent
echo -n "  [8] Header X-Backend prezent... "
HEADER=$(curl -s -D - http://127.0.0.1:$HTTP_PORT/ -o /dev/null 2>/dev/null | grep -i "X-Backend" || echo "")
if [ -n "$HEADER" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Stop server simplu
kill $SERVER_PID 2>/dev/null || true
sleep 0.5

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Sectiunea 3: Reverse Proxy
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Reverse Proxy]${NC}"

# Starting backend
echo -n "  [9] Backend starts... "
python3 python/demos/demo_http_server.py \
    --host 127.0.0.1 \
    --port $BACKEND_PORT \
    --www www \
    --id "test-backend" \
    --mode threaded &
BACKEND_PID=$!
sleep 0.5

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Starting proxy
echo -n "  [10] Reverse proxy starts... "
python3 python/demos/demo_reverse_proxy.py \
    --listen-host 127.0.0.1 \
    --listen-port $PROXY_PORT \
    --backends "127.0.0.1:$BACKEND_PORT" &
PROXY_PID=$!
sleep 0.5

if kill -0 $PROXY_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED+1))
fi

# Test proxy forwarding
echo -n "  [11] Proxy forwarding functioneaza... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PROXY_PORT/ 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗ (got $RESPONSE)${NC}"
    FAILED=$((FAILED+1))
fi

# Test header X-Served-By
echo -n "  [12] Header X-Served-By prezent... "
SERVED_BY=$(curl -s -D - http://127.0.0.1:$PROXY_PORT/ -o /dev/null 2>/dev/null | grep -i "X-Served-By" || echo "")
if [ -n "$SERVED_BY" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (optional)"
    WARNED=$((WARNED+1))
fi

# Cleanup proxy test
kill $PROXY_PID 2>/dev/null || true
kill $BACKEND_PID 2>/dev/null || true
sleep 0.3

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Sectiunea 4: Artefacte (dupa run_all.sh)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${BLUE}[Artefacts]${NC}"

# Test: demo.log exists
echo -n "  [13] artifacts/demo.log exists... "
if [ -f "artifacts/demo.log" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (ruleaza run_all.sh)"
    WARNED=$((WARNED+1))
fi

# Test: validation.txt exists
echo -n "  [14] artifacts/validation.txt exists... "
if [ -f "artifacts/validation.txt" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (ruleaza run_all.sh)"
    WARNED=$((WARNED+1))
fi

# Test: demo.pcap exists
echo -n "  [15] artifacts/demo.pcap exists... "
if [ -f "artifacts/demo.pcap" ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}○${NC} (requires tcpdump)"
    WARNED=$((WARNED+1))
fi

# Cleanup Final
cleanup

# ─────────────────────────────────────────────────────────────────────────────
# Sumar
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}, ${YELLOW}$WARNED warnings${NC}"
echo "═══════════════════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
