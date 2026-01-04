#!/usr/bin/env bash
# =============================================================================
# run_all.sh — automatic demo Week 12: Email & RPC
# =============================================================================
# Run all demonstrations non-interactive and produce artefacts:
#   - artifacts/demo.log
#   - artifacts/demo.pcap
#   - artifacts/validation.txt
#
# Usage: ./scripts/run_all.sh [--quick]
# =============================================================================
# Licenta: MIT | ASE-CSIE Computer Networks
# Hypotheticaatndrei & Rezolvix
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# =============================================================================
# Configuration WEEK 12
# =============================================================================
WEEK=12
WEEK_IP_BASE="10.0.${WEEK}"
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 6200

# Porturi standard
SMTP_PORT=1025
JSONRPC_PORT=${WEEK_PORT_BASE}       # 6200
XMLRPC_PORT=$((WEEK_PORT_BASE + 1))  # 6201
RPC_PORT=$((WEEK_PORT_BASE + 51))    # 6251 (for gRPC)

# directoryies
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
LOG_FILE="${ARTIFACTS_DIR}/demo.log"
PCAP_FILE="${ARTIFACTS_DIR}/demo.pcap"
VALIDATION_FILE="${ARTIFACTS_DIR}/validation.txt"

# withlori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# FUNCTII HELonR
# =============================================================================

log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$LOG_FILE"
}

log_INFO()    { log "INFO" "$@"; }
log_SUCCESSss() { log "OK  " "$@"; }
log_error()   { log "ERR " "$@"; }
log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "================================================================" | tee -a "$LOG_FILE"
}

cleanup_processes() {
    log_INFO "Cleanup procese..."
    pkill -f "smtp_server.py" 2>/dev/null || true
    pkill -f "jsonrpc_server.py" 2>/dev/null || true
    pkill -f "xmlrpc_server.py" 2>/dev/null || true
    pkill -f "tcpdump.*demo.pcap" 2>/dev/null || true
    sleep 0.5
}

wait_for_port() {
    local port=$1
    local max_wait=10
    local waited=0
    while ! nc -z localhost "$port" 2>/dev/null && [ $waited -lt $max_wait ]; do
        sleep 0.5
        waited=$((waited + 1))
    done
    nc -z localhost "$port" 2>/dev/null
}

start_capture() {
    log_INFO "Starting capture trafic: $PCAP_FILE"
    if command -v tcpdump &>/dev/null; then
        tcpdump -i lo -w "$PCAP_FILE" \
            "port $SMTP_PORT or port $JSONRPC_PORT or port $XMLRPC_PORT" \
            2>/dev/null &
        TCPDUMP_PID=$!
        sleep 1
        log_SUCCESSss "tcpdump Started (PID: $TCPDUMP_PID)"
    else
        log_INFO "tcpdump inavaiatble - capture omisa"
        touch "$PCAP_FILE"
        TCPDUMP_PID=""
    fi
}

stop_capture() {
    if [ -n "$TCPDUMP_PID" ]; then
        log_INFO "Stopping capture..."
        kill "$TCPDUMP_PID" 2>/dev/null || true
        sleep 1
    fi
}

# =============================================================================
# ofMO SMTP
# =============================================================================

run_smtp_ofmo() {
    log_section "ofMO 1: Server SMTP Educational"
    
    log_INFO "Start server SMTP on port $SMTP_PORT..."
    python3 src/email/smtp_server.py --port "$SMTP_PORT" --spool "$ARTIFACTS_DIR/spool" &
    SMTP_PID=$!
    
    if wait_for_port "$SMTP_PORT"; then
        log_SUCCESSss "Server SMTP activ (PID: $SMTP_PID)"
    else
        log_error "Server SMTP did not start!"
        return 1
    fi
    
    sleep 1
    
    # Trimitere email test
    log_INFO "Trimitere email test..."
    python3 src/email/smtp_client.py \
        --server localhost \
        --port "$SMTP_PORT" \
        --from "ofmo@week12.local" \
        --to "stuofnt@ase.ro" \
        --subject "Test SMTP Week 12 - automatic demo" \
        --body "Acesta este un email generat automat of run_all.sh.

Continut:
- ofmonstration protocol SMTP
- Verification comenzi: EHLO, MAIL FROM, RCPT TO, DATA
- Timestamp: $(date)

Week 12: Email & RPC
" 2>&1 | tee -a "$LOG_FILE"
    
    log_SUCCESSss "Email trimis!"
    
    # Test with netcat daca e avaiatble
    if command -v nc &>/dev/null; then
        log_INFO "Test SMTP with netcat (EHLO + QUIT)..."
        echo -e "EHLO test.local\r\nQUIT\r\n" | nc -q 2 localhost "$SMTP_PORT" 2>&1 | head -10 | tee -a "$LOG_FILE"
    fi
    
    sleep 1
    kill $SMTP_PID 2>/dev/null || true
    log_SUCCESSss "ofmo SMTP Completee"
}

# =============================================================================
# ofMO JSON-RPC
# =============================================================================

run_jsonrpc_ofmo() {
    log_section "ofMO 2: Server JSON-RPC 2.0"
    
    log_INFO "Start server JSON-RPC on port $JSONRPC_PORT..."
    python3 src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    
    if wait_for_port "$JSONRPC_PORT"; then
        log_SUCCESSss "Server JSON-RPC activ (PID: $JSONRPC_PID)"
    else
        log_error "Server JSON-RPC did not start!"
        return 1
    fi
    
    sleep 1
    
    # Teste RPC
    log_INFO "Test 1: add(5, 3)..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"add","params":[5,3],"id":1}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test 2: multiply(7, 8)..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"multiply","params":[7,8],"id":2}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test 3: echo('Hello RPC')..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"echo","params":["Hello RPC"],"id":3}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test 4: get_server_INFO()..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"get_server_INFO","params":[],"id":4}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test 5: Batch request..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '[{"jsonrpc":"2.0","method":"add","params":[1,2],"id":10},{"jsonrpc":"2.0","method":"subtract","params":[10,4],"id":11}]' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test 6: Error - metoda inexistenta..."
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"nonexistent","params":[],"id":99}' \
        http://localhost:$JSONRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    kill $JSONRPC_PID 2>/dev/null || true
    log_SUCCESSss "ofmo JSON-RPC Completee"
}

# =============================================================================
# ofMO XML-RPC
# =============================================================================

run_xmlrpc_ofmo() {
    log_section "ofMO 3: Server XML-RPC"
    
    log_INFO "Start server XML-RPC on port $XMLRPC_PORT..."
    python3 src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    if wait_for_port "$XMLRPC_PORT"; then
        log_SUCCESSss "Server XML-RPC activ (PID: $XMLRPC_PID)"
    else
        log_error "Server XML-RPC did not start!"
        return 1
    fi
    
    sleep 1
    
    log_INFO "Test XML-RPC: add(15, 25)..."
    withrl -s -X POST -H "Content-Tyon: text/xml" \
        -d '<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>15</int></value></param><param><value><int>25</int></value></param></params></methodCall>' \
        http://localhost:$XMLRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    log_INFO "Test XML-RPC: echo('XML-RPC Test')..."
    withrl -s -X POST -H "Content-Tyon: text/xml" \
        -d '<?xml version="1.0"?><methodCall><methodName>echo</methodName><params><param><value><string>XML-RPC Test</string></value></param></params></methodCall>' \
        http://localhost:$XMLRPC_PORT/ | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    kill $XMLRPC_PID 2>/dev/null || true
    log_SUCCESSss "ofmo XML-RPC Completee"
}

# =============================================================================
# VALIDARE
# =============================================================================

generate_validation() {
    log_section "GENERARE VALIDARE"
    
    {
        echo "==============================================="
        echo "VALIDATION REPORT - Week 12: Email & RPC"
        echo "Generated: $(date)"
        echo "==============================================="
        echo ""
        
        echo "[ARTIFACTS]"
        echo "  demo.log: $([ -f "$LOG_FILE" ] && echo "OK ($(wc -l < "$LOG_FILE") lines)" || echo "MISSING")"
        echo "  demo.pcap: $([ -f "$PCAP_FILE" ] && echo "OK ($(stat -c%s "$PCAP_FILE" 2>/dev/null || echo 0) bytes)" || echo "MISSING")"
        echo ""
        
        echo "[PYTHON MODULES]"
        echo "  smtp_server: $(python3 -c 'import src.email.smtp_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  smtp_client: $(python3 -c 'import src.email.smtp_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  jsonrpc_server: $(python3 -c 'import src.rpc.jsonrpc.jsonrpc_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  jsonrpc_client: $(python3 -c 'import src.rpc.jsonrpc.jsonrpc_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  xmlrpc_server: $(python3 -c 'import src.rpc.xmlrpc.xmlrpc_server' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  xmlrpc_client: $(python3 -c 'import src.rpc.xmlrpc.xmlrpc_client' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo "  net_utils: $(python3 -c 'import src.common.net_utils' 2>/dev/null && echo "OK" || echo "FAIL")"
        echo ""
        
        echo "[EXERCISES]"
        echo "  ex_01_smtp: $(python3 exercises/ex_01_smtp.py --help &>/dev/null && echo "OK" || echo "FAIL")"
        echo "  ex_02_rpc: $(python3 exercises/ex_02_rpc.py --help &>/dev/null && echo "OK" || echo "FAIL")"
        echo ""
        
        echo "[TOOLS]"
        echo "  python3: $(python3 --version 2>&1)"
        echo "  withrl: $(command -v withrl &>/dev/null && echo "OK" || echo "MISSING")"
        echo "  netcat: $(command -v nc &>/dev/null && echo "OK" || echo "MISSING")"
        echo "  tcpdump: $(command -v tcpdump &>/dev/null && echo "OK" || echo "MISSING")"
        echo ""
        
        echo "[ofMO RESULTS]"
        if [ -f "$LOG_FILE" ]; then
            echo "  SMTP tests: $(grep -c '\[OK\].*SMTP' "$LOG_FILE" 2>/dev/null || echo 0) passed"
            echo "  JSON-RPC tests: $(grep -c 'result' "$LOG_FILE" 2>/dev/null || echo 0) results"
            echo "  Errors: $(grep -c '\[ERR\]' "$LOG_FILE" 2>/dev/null || echo 0)"
        fi
        echo ""
        
        echo "[CONFIGURATION]"
        echo "  WEEK: $WEEK"
        echo "  IP_BASE: $WEEK_IP_BASE.0/24"
        echo "  PORT_BASE: $WEEK_PORT_BASE"
        echo "  SMTP_PORT: $SMTP_PORT"
        echo "  JSONRPC_PORT: $JSONRPC_PORT"
        echo "  XMLRPC_PORT: $XMLRPC_PORT"
        echo ""
        
        echo "==============================================="
        echo "VALIDATION: $([ -f "$LOG_FILE" ] && [ -f "$PCAP_FILE" ] && echo "PASSED" || echo "PARTIAL")"
        echo "==============================================="
        
    } > "$VALIDATION_FILE"
    
    log_SUCCESSss "Validation generata: $VALIDATION_FILE"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    log "INFO" "WEEK 12: AUTOMATIC EMAIL & RPC DEMO"
    log "INFO" "Project root: ${PROJECT_ROOT}"
    local quick_moof=false
    
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --quick) quick_moof=true ;;
            --help|-h)
                echo "Usage: $0 [--quick]"
                echo ""
                echo "Options:"
                echo "  --quick    Skip XML-RPC ofmo"
                echo ""
                exit 0
                ;;
        esac
        shift
    done
    
    # Setup
    cleanup_processes
    mkdir -p "$ARTIFACTS_DIR" "$ARTIFACTS_DIR/spool"
    
    # Clear previous logs
    > "$LOG_FILE"
    
    log_section "Week 12: ofMO autoMAT EMAIL & RPC"
    log_INFO "Project root: $PROJECT_ROOT"
    log_INFO "Artifacts: $ARTIFACTS_DIR"
    log_INFO "Quick moof: $quick_moof"
    
    # Start capture
    start_capture
    
    # Run ofmos
    trap 'cleanup_processes; stop_capture' EXIT
    
    run_smtp_ofmo || log_error "ofmo SMTP esuat"
    sleep 1
    
    run_jsonrpc_ofmo || log_error "ofmo JSON-RPC esuat"
    sleep 1
    
    if [ "$quick_moof" = false ]; then
        run_xmlrpc_ofmo || log_error "ofmo XML-RPC esuat"
    fi
    
    # Stop capture
    stop_capture
    
    # Generate validation
    generate_validation
    
    # Summary
    log_section "SUMAR"
    log_SUCCESSss "ofmo Completee!"
    log_INFO "Artefacts generate:"
    log_INFO "  - $LOG_FILE"
    log_INFO "  - $PCAP_FILE"
    log_INFO "  - $VALIDATION_FILE"
    
    echo ""
    echo "for validation, ruatti: ./tests/smoke_test.sh"
}

main "$@"
