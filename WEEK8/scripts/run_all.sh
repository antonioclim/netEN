#!/bin/bash
set -euo pipefail
# ═══════════════════════════════════════════════════════════════════════════════
# run_all.sh - Automatic Demo for Week 8
# Internet Services: Server HTTP + Reverse Proxy
# ═══════════════════════════════════════════════════════════════════════════════
#
# Produce artefacts In artifacts/:
#   - demo.log:        Complete logs ale demo-ului
#   - demo.pcap:       Traffic capture HTTP/proxy (if tcpdump available)
#   - validation.txt:  Validation results
#
# Usage:
#   ./scripts/run_all.sh          # Complete run
#   ./scripts/run_all.sh --quick  # Quick run (without capture)
#
# Author: Computer Networks, ASE Bucharest
# Hypotheticalandrei & Rezolvix | MIT License
# ═══════════════════════════════════════════════════════════════════════════════

set -o pipefail

# Do not generate Python bytecode artefacts
export PYTHONDONTWRITEBYTECODE=1

# ─────────────────────────────────────────────────────────────────────────────
# Configuration according to cross-cutting standard WEEK=8
# ─────────────────────────────────────────────────────────────────────────────
WEEK=8
NETWORK="10.0.${WEEK}.0/24"
HTTP_PORT=${HTTP_PORT:-8080}
PROXY_PORT=${PROXY_PORT:-8888}
BACKEND_PORT_A=${BACKEND_PORT_A:-9001}
BACKEND_PORT_B=${BACKEND_PORT_B:-9002}
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 5800

# ─────────────────────────────────────────────────────────────────────────────
# Port availability pre-check (avoid confusing bind errors)
# ─────────────────────────────────────────────────────────────────────────────
port_is_free() {
    local port="$1"
    if command -v ss >/dev/null 2>&1; then
        if ss -ltnH "sport = :${port}" 2>/dev/null | grep -q .; then
            return 1
        fi
    fi
    return 0
}

for p in "$HTTP_PORT" "$PROXY_PORT" "$BACKEND_PORT_A" "$BACKEND_PORT_B"; do
    if ! port_is_free "$p"; then
        echo "ERROR: Port ${p} is already in use. Stop the conflicting process or override ports via environment variables."
        echo "Hint: HTTP_PORT=18080 PROXY_PORT=18888 BACKEND_PORT_A=19001 BACKEND_PORT_B=19002 ./scripts/run_all.sh --quick"
        exit 2
    fi
done

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"
WWW_DIR="$PROJECT_DIR/www"
PYTHON_DIR="$PROJECT_DIR/python"

# Output artefacts
LOG_FILE="$ARTIFACTS_DIR/demo.log"
PCAP_FILE="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Flags
QUICK_MODE=false
TCPDUMP_PID=""
HTTP_SERVER_PID=""
BACKEND_A_PID=""
BACKEND_B_PID=""
PROXY_PID=""

# ─────────────────────────────────────────────────────────────────────────────
# Functii helper
# ─────────────────────────────────────────────────────────────────────────────
log() {
    local level="$1"
    shift
    local msg="$*"
    local ts
    ts=$(date '+%H:%M:%S')
    
    case "$level" in
        INFO)  color="$GREEN" ;;
        WARN)  color="$YELLOW" ;;
        ERROR) color="$RED" ;;
        STEP)  color="$BLUE" ;;
        *)     color="$NC" ;;
    esac
    
    echo -e "[$ts] ${color}[$level]${NC} $msg"
    echo "[$ts] [$level] $msg" >> "$LOG_FILE"
}

cleanup() {
    log INFO "Cleaning up processes..."
    
    # Stopping tcpdump (requires sudo for SIGTERM)
    if [ -n "$TCPDUMP_PID" ]; then
        sudo kill "$TCPDUMP_PID" 2>/dev/null || true
    fi
    
    # Stopping servere Python
    [ -n "$HTTP_SERVER_PID" ] && kill "$HTTP_SERVER_PID" 2>/dev/null || true
    [ -n "$BACKEND_A_PID" ] && kill "$BACKEND_A_PID" 2>/dev/null || true
    [ -n "$BACKEND_B_PID" ] && kill "$BACKEND_B_PID" 2>/dev/null || true
    [ -n "$PROXY_PID" ] && kill "$PROXY_PID" 2>/dev/null || true
    
    # Cleanup general
    pkill -f "demo_http_server.py.*$HTTP_PORT" 2>/dev/null || true
    pkill -f "demo_http_server.py.*$BACKEND_PORT_A" 2>/dev/null || true
    pkill -f "demo_http_server.py.*$BACKEND_PORT_B" 2>/dev/null || true
    pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
    
    sleep 0.5
    log INFO "Cleanup complete"
}

trap cleanup EXIT

wait_for_port() {
    local port="$1"
    local max_attempts="${2:-30}"
    local attempt=0
    
    while ! nc -z 127.0.0.1 "$port" 2>/dev/null; do
        ((attempt++))
        if [ "$attempt" -ge "$max_attempts" ]; then
            return 1
        fi
        sleep 0.2
    done
    return 0
}

check_http_response() {
    local url="$1"
    local expected_code="$2"
    local actual_code
    
    actual_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$actual_code" = "$expected_code" ]; then
        return 0
    else
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Parsare argumente
# ─────────────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--quick]"
            echo "  --quick, -q  Quick run (without capture pcap)"
            exit 0
            ;;
        *)
            echo "Optiune necunoscuta: $1"
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────────────────────────────────────
# Initializare
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p "$ARTIFACTS_DIR"
> "$LOG_FILE"
> "$VALIDATION_FILE"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Automatic Demo - Week 8: Server HTTP + Reverse Proxy${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

log INFO "Demo automat started"
log INFO "Configuration: WEEK=$WEEK, HTTP_PORT=$HTTP_PORT, PROXY_PORT=$PROXY_PORT"
log INFO "Artefacte In: $ARTIFACTS_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Checking preconditions
# ─────────────────────────────────────────────────────────────────────────────
log STEP "[1/8] Checking preconditions..."

PREREQS_OK=true

if ! command -v python3 &>/dev/null; then
    log ERROR "Python 3 missing!"
    PREREQS_OK=false
fi

if ! command -v curl &>/dev/null; then
    log ERROR "curl missing!"
    PREREQS_OK=false
fi

if ! command -v nc &>/dev/null; then
    log WARN "netcat missing (optional)"
fi

HAS_TCPDUMP=false
if command -v tcpdump &>/dev/null; then
    HAS_TCPDUMP=true
    log INFO "  tcpdump available"
else
    log WARN "  tcpdump inavailable (nu se va genera demo.pcap)"
fi

if [ ! -f "$PYTHON_DIR/demos/demo_http_server.py" ]; then
    log ERROR "demo_http_server.py missing!"
    PREREQS_OK=false
fi

if [ "$PREREQS_OK" = false ]; then
    log ERROR "Preconditions neindeplinite. Ruleaza: ./scripts/setup.sh"
    exit 1
fi

log INFO "  Preconditions OK"
echo "PREREQS: PASS" >> "$VALIDATION_FILE"

# ─────────────────────────────────────────────────────────────────────────────
# Starting capture (if tcpdump available and nu e quick mode)
# ─────────────────────────────────────────────────────────────────────────────
if [ "$QUICK_MODE" = false ] && [ "$HAS_TCPDUMP" = true ]; then
    log STEP "[2/8] Starting capture tcpdump..."
    
    # Captura pe toate porturile relevante
    sudo tcpdump -i lo "port $HTTP_PORT or port $BACKEND_PORT_A or port $BACKEND_PORT_B or port $PROXY_PORT" \
        -nn -w "$PCAP_FILE" -c 200 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    
    if kill -0 "$TCPDUMP_PID" 2>/dev/null; then
        log INFO "  Captura starteda (PID: $TCPDUMP_PID)"
    else
        log WARN "  Nu s-a putut porni tcpdump (poate requires sudo)"
        TCPDUMP_PID=""
    fi
else
    log STEP "[2/8] Skipping capture (quick mode or tcpdump inavailable)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# DEMO 1: Server HTTP simple
# ─────────────────────────────────────────────────────────────────────────────
log STEP "[3/8] Demo 1: Server HTTP simple..."

cd "$PROJECT_DIR"
python3 "$PYTHON_DIR/demos/demo_http_server.py" \
    --host 127.0.0.1 \
    --port "$HTTP_PORT" \
    --www "$WWW_DIR" \
    --id "http-demo" \
    --mode threaded &
HTTP_SERVER_PID=$!
sleep 1

if wait_for_port "$HTTP_PORT" 20; then
    log INFO "  HTTP server started on port $HTTP_PORT"
    
    # Test GET /
    if check_http_response "http://127.0.0.1:$HTTP_PORT/" "200"; then
        log INFO "  ✓ GET / → 200 OK"
        echo "HTTP_GET_ROOT: PASS" >> "$VALIDATION_FILE"
    else
        log ERROR "  ✗ GET / failed"
        echo "HTTP_GET_ROOT: FAIL" >> "$VALIDATION_FILE"
    fi
    
    # Test GET /not-found
    if check_http_response "http://127.0.0.1:$HTTP_PORT/not-found" "404"; then
        log INFO "  ✓ GET /not-found → 404"
        echo "HTTP_GET_404: PASS" >> "$VALIDATION_FILE"
    else
        log ERROR "  ✗ GET /not-found failed"
        echo "HTTP_GET_404: FAIL" >> "$VALIDATION_FILE"
    fi
    
    # Salvare headers response
    curl -s -D - "http://127.0.0.1:$HTTP_PORT/" -o /dev/null >> "$LOG_FILE" 2>&1
    
else
    log ERROR "  Server HTTP nu a started!"
    echo "HTTP_SERVER_START: FAIL" >> "$VALIDATION_FILE"
fi

# Stopping server simple
kill "$HTTP_SERVER_PID" 2>/dev/null || true
HTTP_SERVER_PID=""
sleep 0.5

# ─────────────────────────────────────────────────────────────────────────────
# DEMO 2: Reverse Proxy cu Load Balancing
# ─────────────────────────────────────────────────────────────────────────────
log STEP "[4/8] Demo 2: Starting backends..."

# Backend A
python3 "$PYTHON_DIR/demos/demo_http_server.py" \
    --host 127.0.0.1 \
    --port "$BACKEND_PORT_A" \
    --www "$WWW_DIR" \
    --id "backend-A" \
    --mode threaded &
BACKEND_A_PID=$!

# Backend B
python3 "$PYTHON_DIR/demos/demo_http_server.py" \
    --host 127.0.0.1 \
    --port "$BACKEND_PORT_B" \
    --www "$WWW_DIR" \
    --id "backend-B" \
    --mode threaded &
BACKEND_B_PID=$!

sleep 1

if wait_for_port "$BACKEND_PORT_A" 20 && wait_for_port "$BACKEND_PORT_B" 20; then
    log INFO "  Backend A started on port $BACKEND_PORT_A"
    log INFO "  Backend B started on port $BACKEND_PORT_B"
    echo "BACKENDS_START: PASS" >> "$VALIDATION_FILE"
else
    log ERROR "  Backends nu au started!"
    echo "BACKENDS_START: FAIL" >> "$VALIDATION_FILE"
fi

# ─────────────────────────────────────────────────────────────────────────────
log STEP "[5/8] Starting Reverse Proxy..."

python3 "$PYTHON_DIR/demos/demo_reverse_proxy.py" \
    --listen-host 127.0.0.1 \
    --listen-port "$PROXY_PORT" \
    --backends "127.0.0.1:$BACKEND_PORT_A,127.0.0.1:$BACKEND_PORT_B" &
PROXY_PID=$!
sleep 1

if wait_for_port "$PROXY_PORT" 20; then
    log INFO "  Reverse Proxy started pe port $PROXY_PORT"
    echo "PROXY_START: PASS" >> "$VALIDATION_FILE"
else
    log ERROR "  Proxy did not start!"
    echo "PROXY_START: FAIL" >> "$VALIDATION_FILE"
fi

# ─────────────────────────────────────────────────────────────────────────────
log STEP "[6/8] Test Round-Robin Load Balancing..."

BACKEND_A_COUNT=0
BACKEND_B_COUNT=0

for i in {1..6}; do
    SERVED_BY=$(curl -s -D - "http://127.0.0.1:$PROXY_PORT/" -o /dev/null 2>/dev/null | grep -i "X-Served-By" | cut -d: -f2 | tr -d ' \r\n')
    
    if [ -n "$SERVED_BY" ]; then
        log INFO "  Request $i → $SERVED_BY"
        echo "ROUND_ROBIN_$i: $SERVED_BY" >> "$LOG_FILE"
        
        case "$SERVED_BY" in
            *backend-A*|*9001*) ((++BACKEND_A_COUNT)) ;;
            *backend-B*|*9002*) ((++BACKEND_B_COUNT)) ;;
        esac
    else
        log WARN "  Request $i → Missing X-Served-By header"
    fi
    
    sleep 0.2
done

log INFO "  Distribution: Backend-A=$BACKEND_A_COUNT, Backend-B=$BACKEND_B_COUNT"

# Verification round-robin balanced (tolerance: difference max 2)
DIFF=$((BACKEND_A_COUNT - BACKEND_B_COUNT))
DIFF=${DIFF#-}  # Valoare absoluta

if [ "$DIFF" -le 2 ] && [ "$BACKEND_A_COUNT" -gt 0 ] && [ "$BACKEND_B_COUNT" -gt 0 ]; then
    log INFO "  ✓ Round-Robin functioneaza corect"
    echo "ROUND_ROBIN_BALANCED: PASS" >> "$VALIDATION_FILE"
else
    log WARN "  Round-Robin dezbalanced or partial"
    echo "ROUND_ROBIN_BALANCED: PARTIAL (A=$BACKEND_A_COUNT, B=$BACKEND_B_COUNT)" >> "$VALIDATION_FILE"
fi

# ─────────────────────────────────────────────────────────────────────────────
log STEP "[7/8] Test X-Forwarded-For header..."

# Verificam ca proxy-ul adauga header-ele corecte
HEADERS=$(curl -s -D - "http://127.0.0.1:$PROXY_PORT/" -o /dev/null 2>/dev/null)

if echo "$HEADERS" | grep -qi "X-Request-ID"; then
    log INFO "  ✓ X-Request-ID present"
    echo "X_REQUEST_ID: PASS" >> "$VALIDATION_FILE"
else
    log WARN "  X-Request-ID lipsa"
    echo "X_REQUEST_ID: MISSING" >> "$VALIDATION_FILE"
fi

if echo "$HEADERS" | grep -qi "X-Served-By"; then
    log INFO "  ✓ X-Served-By present"
    echo "X_SERVED_BY: PASS" >> "$VALIDATION_FILE"
else
    log WARN "  X-Served-By lipsa"
    echo "X_SERVED_BY: MISSING" >> "$VALIDATION_FILE"
fi

# ─────────────────────────────────────────────────────────────────────────────
log STEP "[8/8] Finalisation and summary..."

# Stopping capture
if [ -n "$TCPDUMP_PID" ]; then
    sleep 1
    sudo kill "$TCPDUMP_PID" 2>/dev/null || true
    TCPDUMP_PID=""
    sleep 0.5
    
    if [ -f "$PCAP_FILE" ] && [ -s "$PCAP_FILE" ]; then
        PCAP_SIZE=$(stat -f%z "$PCAP_FILE" 2>/dev/null || stat -c%s "$PCAP_FILE" 2>/dev/null || echo "0")
        log INFO "  Captura salvata: $PCAP_FILE ($PCAP_SIZE bytes)"
        echo "PCAP_GENERATED: PASS ($PCAP_SIZE bytes)" >> "$VALIDATION_FILE"
    else
        log WARN "  Captura goala or lipsa"
        echo "PCAP_GENERATED: EMPTY" >> "$VALIDATION_FILE"
    fi
else
    # Creare pcap placeholder if nu exista
    if [ ! -f "$PCAP_FILE" ]; then
        touch "$PCAP_FILE"
        log INFO "  Captura: placeholder (tcpdump unavailable)"
        echo "PCAP_GENERATED: PLACEHOLDER" >> "$VALIDATION_FILE"
    fi
fi

# Adaugare sumar In validation.txt
echo "" >> "$VALIDATION_FILE"
echo "===== SUMAR =====" >> "$VALIDATION_FILE"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')" >> "$VALIDATION_FILE"
echo "WEEK: $WEEK" >> "$VALIDATION_FILE"
echo "HTTP_PORT: $HTTP_PORT" >> "$VALIDATION_FILE"
echo "PROXY_PORT: $PROXY_PORT" >> "$VALIDATION_FILE"
echo "BACKENDS: $BACKEND_PORT_A, $BACKEND_PORT_B" >> "$VALIDATION_FILE"

# Calcul rezultat Final
PASS_COUNT=$(grep -c ": PASS" "$VALIDATION_FILE" 2>/dev/null || echo "0")
FAIL_COUNT=$(grep -c ": FAIL" "$VALIDATION_FILE" 2>/dev/null || echo "0")
# Ensure they are integers
PASS_COUNT=${PASS_COUNT//[^0-9]/}
FAIL_COUNT=${FAIL_COUNT//[^0-9]/}
PASS_COUNT=${PASS_COUNT:-0}
FAIL_COUNT=${FAIL_COUNT:-0}

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Demo summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Generated artefacts:"
echo -e "    ${GREEN}✓${NC} $LOG_FILE"
echo -e "    ${GREEN}✓${NC} $VALIDATION_FILE"
[ -f "$PCAP_FILE" ] && echo -e "    ${GREEN}✓${NC} $PCAP_FILE"
echo ""
echo -e "  Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"
echo ""

log INFO "Demo completed"
echo "DEMO_COMPLETED: SUCCESS" >> "$VALIDATION_FILE"

# Return exit code
if [ "$FAIL_COUNT" -eq 0 ]; then
    exit 0
else
    exit 1
fi
