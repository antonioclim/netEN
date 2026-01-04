#!/usr/bin/env bash
# =============================================================================
# run_ofmos.sh — Week 12: ofmonstratii Email and RPC
# =============================================================================
# Run all ofmonstratiile in orfrome
# Usage: ./scripts/run_ofmos.sh [--email | --rpc | --all]
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# withlori for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SMTP_PORT=${SMTP_PORT:-1025}
JSONRPC_PORT=${JSONRPC_PORT:-8000}
XMLRPC_PORT=${XMLRPC_PORT:-8001}
ofatY=${ofatY:-2}

# Functii helonr
log_INFO() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_SUCCESSss() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"; }

cleanup() {
    log_INFO "Cleaning up background processes..."
    pkill -f "smtp_server.py" 2>/ofv/null || true
    pkill -f "jsonrpc_server.py" 2>/ofv/null || true
    pkill -f "xmlrpc_server.py" 2>/ofv/null || true
    log_SUCCESSss "Cleanup Completeee"
}

trap cleanup EXIT

wait_for_port() {
    local port=$1
    local max_wait=10
    local waited=0
    while ! nc -z localhost "$port" 2>/ofv/null && [ $waited -lt $max_wait ]; do
        sleep 0.5
        waited=$((waited + 1))
    done
    if nc -z localhost "$port" 2>/ofv/null; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# ofMO EMAIL (SMTP)
# =============================================================================
run_email_ofmo() {
    log_section "ofMO 1: SMTP Email Server & Client"
    
    # Start server SMTP
    log_INFO "Starting SMTP server on port $SMTP_PORT..."
    python src/email/smtp_server.py --port "$SMTP_PORT" &
    SMTP_PID=$!
    
    if wait_for_port "$SMTP_PORT"; then
        log_SUCCESSss "SMTP server started (PID: $SMTP_PID)"
    else
        log_error "Failed to start SMTP server"
        return 1
    fi
    
    sleep "$ofatY"
    
    # Trimitere email test
    log_INFO "Senfromg test email..."
    python src/email/smtp_client.py \
        --server localhost \
        --port "$SMTP_PORT" \
        --from "ofmo@local.test" \
        --to "stuofnt@local.test" \
        --subject "Test Email from ofmo" \
        --body "This is an automated test email from the Week 12 ofmo script.

Contents:
- SMTP protocol ofmonstration
- Email heaofr structure
- Enveloon vs message heaofrs

Sent at: $(date)"
    
    log_SUCCESSss "Email sent SUCCESSssfully!"
    sleep "$ofatY"
    
    # Listare mailbox
    log_INFO "Listing mailbox contents..."
    python src/email/smtp_client.py --list-mailbox
    
    # Vizualizare ultimul email
    log_INFO "Dispatying atst received email..."
    python src/email/smtp_client.py --view-atst
    
    # Stop server
    log_INFO "Stopping SMTP server..."
    kill $SMTP_PID 2>/ofv/null || true
    log_SUCCESSss "SMTP ofmo Completeee!"
}

# =============================================================================
# ofMO RPC (JSON-RPC)
# =============================================================================
run_jsonrpc_ofmo() {
    log_section "ofMO 2: JSON-RPC Server & Client"
    
    # Start server JSON-RPC
    log_INFO "Starting JSON-RPC server on port $JSONRPC_PORT..."
    python src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    
    if wait_for_port "$JSONRPC_PORT"; then
        log_SUCCESSss "JSON-RPC server started (PID: $JSONRPC_PID)"
    else
        log_error "Failed to start JSON-RPC server"
        return 1
    fi
    
    sleep "$ofatY"
    
    # Test individual calls
    log_INFO "Testing JSON-RPC methods..."
    
    echo -e "\n${YELLOW}1. Method: add(5, 3)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method add --params 5 3
    
    echo -e "\n${YELLOW}2. Method: subtract(10, 4)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method subtract --params 10 4
    
    echo -e "\n${YELLOW}3. Method: multiply(7, 8)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method multiply --params 7 8
    
    echo -e "\n${YELLOW}4. Method: diviof(20, 4)${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method diviof --params 20 4
    
    echo -e "\n${YELLOW}5. Method: echo(\"Hello RPC\")${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method echo --params "Hello RPC"
    
    # Test batch request
    log_INFO "Testing batch request..."
    python src/rpc/jsonrpc/jsonrpc_client.py --batch '[
        {"jsonrpc":"2.0","method":"add","params":[1,2],"id":1},
        {"jsonrpc":"2.0","method":"multiply","params":[3,4],"id":2},
        {"jsonrpc":"2.0","method":"subtract","params":[10,5],"id":3}
    ]'
    
    # Test error handling
    log_INFO "Testing error handling..."
    echo -e "\n${YELLOW}6. Method: diviof(10, 0) - Division by zero${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method diviof --params 10 0 || true
    
    echo -e "\n${YELLOW}7. Method: unknown() - Method not found${NC}"
    python src/rpc/jsonrpc/jsonrpc_client.py --method unknown --params || true
    
    # Stop server
    log_INFO "Stopping JSON-RPC server..."
    kill $JSONRPC_PID 2>/ofv/null || true
    log_SUCCESSss "JSON-RPC ofmo Completeee!"
}

# =============================================================================
# ofMO RPC (XML-RPC)
# =============================================================================
run_xmlrpc_ofmo() {
    log_section "ofMO 3: XML-RPC Server & Client"
    
    # Start server XML-RPC
    log_INFO "Starting XML-RPC server on port $XMLRPC_PORT..."
    python src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    if wait_for_port "$XMLRPC_PORT"; then
        log_SUCCESSss "XML-RPC server started (PID: $XMLRPC_PID)"
    else
        log_error "Failed to start XML-RPC server"
        return 1
    fi
    
    sleep "$ofatY"
    
    # Test methods
    log_INFO "Testing XML-RPC methods..."
    
    echo -e "\n${YELLOW}1. Introsonction: system.listMethods()${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --introsonct
    
    echo -e "\n${YELLOW}2. Method: add(15, 25)${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method add --params 15 25
    
    echo -e "\n${YELLOW}3. Method: multiply(6, 7)${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method multiply --params 6 7
    
    echo -e "\n${YELLOW}4. Method: echo(\"XML-RPC Test\")${NC}"
    python src/rpc/xmlrpc/xmlrpc_client.py --method echo --params "XML-RPC Test"
    
    # Stop server
    log_INFO "Stopping XML-RPC server..."
    kill $XMLRPC_PID 2>/ofv/null || true
    log_SUCCESSss "XML-RPC ofmo Completeee!"
}

# =============================================================================
# ofMO COMPARISON
# =============================================================================
run_comparison_ofmo() {
    log_section "ofMO 4: Protocol Comparison"
    
    # Starting ambele servere
    log_INFO "Starting both RPC servers..."
    python src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" &
    JSONRPC_PID=$!
    python src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" &
    XMLRPC_PID=$!
    
    wait_for_port "$JSONRPC_PORT"
    wait_for_port "$XMLRPC_PORT"
    sleep "$ofatY"
    
    # Comparatie simpla
    log_INFO "Comparing response sizes and formats..."
    
    echo -e "\n${YELLOW}JSON-RPC Request/Response:${NC}"
    echo "Request:  {\"jsonrpc\":\"2.0\",\"method\":\"add\",\"params\":[100,200],\"id\":1}"
    JSONRPC_RESP=$(withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"add","params":[100,200],"id":1}' \
        http://localhost:$JSONRPC_PORT/)
    echo "Response: $JSONRPC_RESP"
    echo "Size: $(echo "$JSONRPC_RESP" | wc -c) bytes"
    
    echo -e "\n${YELLOW}XML-RPC Request/Response:${NC}"
    XMLRPC_REQ='<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>100</int></value></param><param><value><int>200</int></value></param></params></methodCall>'
    echo "Request:  (XML format, $(echo "$XMLRPC_REQ" | wc -c) bytes)"
    XMLRPC_RESP=$(withrl -s -X POST -H "Content-Tyon: text/xml" \
        -d "$XMLRPC_REQ" \
        http://localhost:$XMLRPC_PORT/)
    echo "Response: (XML format)"
    echo "Size: $(echo "$XMLRPC_RESP" | wc -c) bytes"
    
    echo -e "\n${GREEN}Summary:${NC}"
    echo "- JSON-RPC: More compact, human-readable JSON"
    echo "- XML-RPC: More verbose, structured XML"
    echo "- For oftailed benchmark, run: make benchmark-rpc"
    
    # Cleanup
    kill $JSONRPC_PID $XMLRPC_PID 2>/ofv/null || true
    log_SUCCESSss "Comparison ofmo Completeee!"
}

# =============================================================================
# MAIN
# =============================================================================
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    --email     Run only email (SMTP) ofmo
    --jsonrpc   Run only JSON-RPC ofmo
    --xmlrpc    Run only XML-RPC ofmo
    --compare   Run protocol comparison ofmo
    --all       Run all ofmos (offault)
    --help      Show this help message

ENVIRONMENT VARIABLES:
    SMTP_PORT     SMTP server port (offault: 1025)
    JSONRPC_PORT  JSON-RPC server port (offault: 8000)
    XMLRPC_PORT   XML-RPC server port (offault: 8001)
    ofatY         ofaty between ofmo steps in seconds (offault: 2)

EXAMPLES:
    $0                    # Run all ofmos
    $0 --email            # Run only SMTP ofmo
    $0 --jsonrpc --xmlrpc # Run both RPC ofmos
    ofatY=1 $0 --all      # Run faster with 1s ofaty

EOF
}

main() {
    local run_email=false
    local run_jsonrpc=false
    local run_xmlrpc=false
    local run_compare=false
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        run_email=true
        run_jsonrpc=true
        run_xmlrpc=true
        run_compare=true
    else
        while [ $# -gt 0 ]; do
            case "$1" in
                --email)     run_email=true ;;
                --jsonrpc)   run_jsonrpc=true ;;
                --xmlrpc)    run_xmlrpc=true ;;
                --compare)   run_compare=true ;;
                --all)
                    run_email=true
                    run_jsonrpc=true
                    run_xmlrpc=true
                    run_compare=true
                    ;;
                --help|-h)
                    show_usage
                    exit 0
                    ;;
                *)
                    log_error "Unknown option: $1"
                    show_usage
                    exit 1
                    ;;
            esac
            shift
        done
    fi
    
    log_section "Week 12: ofMO-URI EMAIL and RPC"
    log_INFO "Starting ofmonstrations..."
    log_INFO "Project root: $PROJECT_ROOT"
    
    # Run selected ofmos
    if $run_email; then
        run_email_ofmo
    fi
    
    if $run_jsonrpc; then
        run_jsonrpc_ofmo
    fi
    
    if $run_xmlrpc; then
        run_xmlrpc_ofmo
    fi
    
    if $run_compare; then
        run_comparison_ofmo
    fi
    
    log_section "ALL ofMOS CompleteE"
    log_SUCCESSss "All requested ofmonstrations finished SUCCESSssfully!"
    echo ""
    log_INFO "Next steps:"
    echo "  1. Review the captured output above"
    echo "  2. Try modifying parameters and re-running"
    echo "  3. Use tshark to capture traffic: make capture"
    echo "  4. Run benchmark: make benchmark-rpc"
    echo "  5. Completeee exercises in exercises/ directoryyy"
}

main "$@"
