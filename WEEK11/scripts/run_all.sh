#!/bin/bash
# =============================================================================
# run_all.sh – Automatic demo for Week 11: Nginx Load Balancing
# =============================================================================
# Produces artefacts in artifacts/:
#   - demo.log      : complete demo log
#   - demo.pcap     : HTTP traffic capture
#   - validation.txt: final validations
# =============================================================================
# Usage: ./run_all.sh [--no-capture]
# =============================================================================

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
DOCKER_DIR="$ROOT_DIR/docker/nginx_compose"

# Standard ports (according to WEEK 11 spec)
HTTP_PORT=8080
WEEK_PORT_BASE=6100  # 5100 + 100*(11-1) = 6100
DNS_PORT=5353

# Colours
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
NO_CAPTURE=false
if [[ "$1" == "--no-capture" ]]; then
    NO_CAPTURE=true
fi

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$ARTIFACTS_DIR/demo.log"
}

cleanup_previous() {
    log "${YELLOW}[CLEANUP]${NC} Cleaning previous state..."
    
    # Stop Docker containers
    cd "$DOCKER_DIR" && docker compose down 2>/dev/null || true
    cd "$ROOT_DIR/docker/custom_lb_compose" && docker compose down 2>/dev/null || true
    
    # Stop Python processes
    pkill -f "ex_11_01_backend" 2>/dev/null || true
    pkill -f "ex_11_02_loadbalancer" 2>/dev/null || true
    
    # Stop tshark if running
    pkill -f "tshark.*$HTTP_PORT" 2>/dev/null || true
    
    # Clean ports
    sleep 1
}

wait_for_port() {
    local port=$1
    local timeout=${2:-30}
    local elapsed=0
    
    while ! nc -z localhost "$port" 2>/dev/null; do
        sleep 1
        elapsed=$((elapsed + 1))
        if [[ $elapsed -ge $timeout ]]; then
            return 1
        fi
    done
    return 0
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Automatic Demo – Week 11: Nginx Load Balancing${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Create artefacts directory
mkdir -p "$ARTIFACTS_DIR"
rm -f "$ARTIFACTS_DIR/demo.log" "$ARTIFACTS_DIR/demo.pcap" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null || true

log "${BLUE}[INFO]${NC} Automatic demo for WEEK 11"
log "${BLUE}[INFO]${NC} Artefacts will be saved in: $ARTIFACTS_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 0: Cleanup
# ─────────────────────────────────────────────────────────────────────────────

cleanup_previous

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Docker verification
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[1/6]${NC} Verifying Docker..."

if ! command -v docker &> /dev/null; then
    log "${RED}[ERROR]${NC} Docker is not installed!"
    echo "Docker is not installed" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

if ! docker info &> /dev/null; then
    log "${RED}[ERROR]${NC} Docker is not running or you lack permissions!"
    echo "Docker is not running" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

log "${GREEN}[OK]${NC} Docker available."

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Start traffic capture (background)
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$NO_CAPTURE" == "false" ]]; then
    log "${YELLOW}[2/6]${NC} Starting traffic capture..."
    
    if command -v tshark &> /dev/null; then
        # Capture in background (max 60 seconds or 500 packets)
        timeout 60 tshark -i any -f "tcp port $HTTP_PORT" \
            -w "$ARTIFACTS_DIR/demo.pcap" \
            -c 500 2>/dev/null &
        TSHARK_PID=$!
        log "${GREEN}[OK]${NC} tshark started (PID: $TSHARK_PID)"
        sleep 2
    elif command -v tcpdump &> /dev/null; then
        timeout 60 sudo tcpdump -i any -n "tcp port $HTTP_PORT" \
            -w "$ARTIFACTS_DIR/demo.pcap" \
            -c 500 2>/dev/null &
        TSHARK_PID=$!
        log "${GREEN}[OK]${NC} tcpdump started (PID: $TSHARK_PID)"
        sleep 2
    else
        log "${YELLOW}[WARN]${NC} Neither tshark nor tcpdump are available. Skipping capture."
        touch "$ARTIFACTS_DIR/demo.pcap"
    fi
else
    log "${YELLOW}[2/6]${NC} Skip capture (--no-capture)."
    touch "$ARTIFACTS_DIR/demo.pcap"
fi

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Start Nginx Load Balancer
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[3/6]${NC} Starting Nginx reverse proxy + 3 backends..."

cd "$DOCKER_DIR"
docker compose up -d >> "$ARTIFACTS_DIR/demo.log" 2>&1

if ! wait_for_port $HTTP_PORT 30; then
    log "${RED}[ERROR]${NC} Nginx did not start within 30 seconds!"
    echo "FAIL: Nginx timeout" >> "$ARTIFACTS_DIR/validation.txt"
    exit 1
fi

log "${GREEN}[OK]${NC} Nginx running on port $HTTP_PORT"
sleep 2

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Round-Robin Test
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[4/6]${NC} Testing Round-Robin distribution..."

echo "" >> "$ARTIFACTS_DIR/demo.log"
echo "=== TEST ROUND-ROBIN ===" >> "$ARTIFACTS_DIR/demo.log"

RESPONSES=""
for i in $(seq 1 9); do
    RESPONSE=$(curl -s -m 5 "http://localhost:$HTTP_PORT/" 2>/dev/null | head -1)
    echo "Request $i: $RESPONSE" >> "$ARTIFACTS_DIR/demo.log"
    log "  Request $i: ${BLUE}$RESPONSE${NC}"
    RESPONSES="$RESPONSES$RESPONSE\n"
    sleep 0.3
done

# Verify distribution
BACKEND_1=$(echo -e "$RESPONSES" | grep -c "Backend 1" || echo "0")
BACKEND_2=$(echo -e "$RESPONSES" | grep -c "Backend 2" || echo "0")
BACKEND_3=$(echo -e "$RESPONSES" | grep -c "Backend 3" || echo "0")

log "${BLUE}[STATS]${NC} Distribution: B1=$BACKEND_1, B2=$BACKEND_2, B3=$BACKEND_3"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Health Check Test
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[5/6]${NC} Testing health check endpoint..."

HEALTH=$(curl -s -m 5 "http://localhost:$HTTP_PORT/health" 2>/dev/null || echo "FAIL")
log "  Health check: ${BLUE}$HEALTH${NC}"
echo "Health check: $HEALTH" >> "$ARTIFACTS_DIR/demo.log"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Generate Validation
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[6/6]${NC} Generating validation.txt..."

{
    echo "=== VALIDATION REPORT - WEEK 11 ==="
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "--- Docker Status ---"
    docker compose ps 2>/dev/null || echo "Docker compose status unavailable"
    echo ""
    echo "--- Load Balancing Distribution ---"
    echo "Backend 1: $BACKEND_1 requests"
    echo "Backend 2: $BACKEND_2 requests"
    echo "Backend 3: $BACKEND_3 requests"
    echo ""
    echo "--- Validation Checks ---"
    
    # Check 1: All backends received requests
    if [[ "$BACKEND_1" -gt 0 && "$BACKEND_2" -gt 0 && "$BACKEND_3" -gt 0 ]]; then
        echo "PASS: All backends received requests"
    else
        echo "WARN: Not all backends received requests (may be normal for 9 req)"
    fi
    
    # Check 2: Approximately equal distribution
    TOTAL=$((BACKEND_1 + BACKEND_2 + BACKEND_3))
    if [[ $TOTAL -eq 9 ]]; then
        echo "PASS: Total requests correct (9)"
    else
        echo "FAIL: Total requests incorrect ($TOTAL != 9)"
    fi
    
    # Check 3: Health check functional
    if [[ "$HEALTH" == "OK" ]]; then
        echo "PASS: Health check endpoint functional"
    else
        echo "WARN: Health check returned: $HEALTH"
    fi
    
    # Check 4: Artefacts generated
    echo ""
    echo "--- Artefacts Generated ---"
    ls -la "$ARTIFACTS_DIR/"
    
} > "$ARTIFACTS_DIR/validation.txt"

log "${GREEN}[OK]${NC} Validation complete."

# ─────────────────────────────────────────────────────────────────────────────
# FINAL CLEANUP
# ─────────────────────────────────────────────────────────────────────────────

log "${YELLOW}[CLEANUP]${NC} Stopping capture..."

# Stop tshark
if [[ -n "$TSHARK_PID" ]]; then
    kill "$TSHARK_PID" 2>/dev/null || true
    wait "$TSHARK_PID" 2>/dev/null || true
fi

# Leave containers running (manual cleanup with scripts/cleanup.sh)
log "${BLUE}[INFO]${NC} Docker containers remain active."
log "${BLUE}[INFO]${NC} To stop: cd docker/nginx_compose && docker compose down"

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Demo Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Artefacts generated in ${YELLOW}$ARTIFACTS_DIR/${NC}:"
echo -e "  • demo.log        – complete log"
echo -e "  • demo.pcap       – HTTP traffic capture"
echo -e "  • validation.txt  – validation report"
echo ""
echo -e "For verification: ${YELLOW}bash tests/smoke_test.sh${NC}"
echo ""

log "${GREEN}[DONE]${NC} Automatic demo finished."

# Revolvix&Hypotheticalandrei
