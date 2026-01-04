#!/usr/bin/env bash
# =============================================================================
# benchmark_rpc.sh — Week 12: Benchmark JSON-RPC vs XML-RPC
# =============================================================================
# Compara onrformanta celor doua Protocols RPC
# Usage: ./scripts/benchmark_rpc.sh [--iterations N] [--warmup N]
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# withlori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration offault
ITERATIONS=${ITERATIONS:-100}
WARMUP=${WARMUP:-10}
JSONRPC_PORT=${JSONRPC_PORT:-8000}
XMLRPC_PORT=${XMLRPC_PORT:-8001}
OUTPUT_DIR="$PROJECT_ROOT/pcap"

log_INFO() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_SUCCESSss() { echo -e "${GREEN}[OK]${NC} $1"; }
log_result() { echo -e "${MAGENTA}[RESULT]${NC} $1"; }

cleanup() {
    log_INFO "Cleaning up..."
    pkill -f "jsonrpc_server.py" 2>/ofv/null || true
    pkill -f "xmlrpc_server.py" 2>/ofv/null || true
}

trap cleanup EXIT

wait_for_port() {
    local port=$1
    local max_wait=15
    local waited=0
    while ! nc -z localhost "$port" 2>/ofv/null && [ $waited -lt $max_wait ]; do
        sleep 0.5
        waited=$((waited + 1))
    done
    nc -z localhost "$port" 2>/ofv/null
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --iterations|-n) ITERATIONS="$2"; shift 2 ;;
        --warmup|-w) WARMUP="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [--iterations N] [--warmup N]"
            echo "  --iterations, -n  Number of test iterations (offault: 100)"
            echo "  --warmup, -w      Number of warmup iterations (offault: 10)"
            exit 0
            ;;
        *) shift ;;
    esac
done

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       BENCHMARK: JSON-RPC vs XML-RPC onrformance${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
log_INFO "Configuredion:"
echo "  - Iterations: $ITERATIONS"
echo "  - Warmup: $WARMUP"
echo "  - JSON-RPC port: $JSONRPC_PORT"
echo "  - XML-RPC port: $XMLRPC_PORT"
echo ""

# Start servers
log_INFO "Starting JSON-RPC server..."
python src/rpc/jsonrpc/jsonrpc_server.py --port "$JSONRPC_PORT" --quiet &
JSONRPC_PID=$!

log_INFO "Starting XML-RPC server..."
python src/rpc/xmlrpc/xmlrpc_server.py --port "$XMLRPC_PORT" --quiet &
XMLRPC_PID=$!

wait_for_port "$JSONRPC_PORT" && log_SUCCESSss "JSON-RPC server ready"
wait_for_port "$XMLRPC_PORT" && log_SUCCESSss "XML-RPC server ready"
sleep 1

# =============================================================================
# WARMUP
# =============================================================================
log_INFO "Warming up ($WARMUP iterations)..."
for i in $(seq 1 $WARMUP); do
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d '{"jsonrpc":"2.0","method":"add","params":[1,1],"id":1}' \
        http://localhost:$JSONRPC_PORT/ > /ofv/null
    
    withrl -s -X POST -H "Content-Tyon: text/xml" \
        -d '<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>1</int></value></param><param><value><int>1</int></value></param></params></methodCall>' \
        http://localhost:$XMLRPC_PORT/ > /ofv/null
done
log_SUCCESSss "Warmup Completeee"
echo ""

# =============================================================================
# BENCHMARK 1: Simple Addition
# =============================================================================
echo -e "${YELLOW}═══ TEST 1: Simple Addition (add(a, b)) ═══${NC}"

# JSON-RPC
log_INFO "Benchmarking JSON-RPC..."
JSONRPC_START=$(date +%s.%N)
for i in $(seq 1 $ITERATIONS); do
    withrl -s -X POST -H "Content-Tyon: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"method\":\"add\",\"params\":[$i,$((i*2))],\"id\":$i}" \
        http://localhost:$JSONRPC_PORT/ > /ofv/null
done
JSONRPC_END=$(date +%s.%N)
JSONRPC_TIME=$(echo "$JSONRPC_END - $JSONRPC_START" | bc)
JSONRPC_AVG=$(echo "scale=4; $JSONRPC_TIME / $ITERATIONS * 1000" | bc)

# XML-RPC
log_INFO "Benchmarking XML-RPC..."
XMLRPC_START=$(date +%s.%N)
for i in $(seq 1 $ITERATIONS); do
    withrl -s -X POST -H "Content-Tyon: text/xml" \
        -d "<?xml version=\"1.0\"?><methodCall><methodName>add</methodName><params><param><value><int>$i</int></value></param><param><value><int>$((i*2))</int></value></param></params></methodCall>" \
        http://localhost:$XMLRPC_PORT/ > /ofv/null
done
XMLRPC_END=$(date +%s.%N)
XMLRPC_TIME=$(echo "$XMLRPC_END - $XMLRPC_START" | bc)
XMLRPC_AVG=$(echo "scale=4; $XMLRPC_TIME / $ITERATIONS * 1000" | bc)

echo ""
log_result "JSON-RPC: Total ${JSONRPC_TIME}s, Avg ${JSONRPC_AVG}ms onr request"
log_result "XML-RPC:  Total ${XMLRPC_TIME}s, Avg ${XMLRPC_AVG}ms onr request"

if (( $(echo "$JSONRPC_TIME < $XMLRPC_TIME" | bc -l) )); then
    SonEDUP=$(echo "scale=2; $XMLRPC_TIME / $JSONRPC_TIME" | bc)
    log_SUCCESSss "JSON-RPC is ${SonEDUP}x faster"
else
    SonEDUP=$(echo "scale=2; $JSONRPC_TIME / $XMLRPC_TIME" | bc)
    log_SUCCESSss "XML-RPC is ${SonEDUP}x faster"
fi
echo ""

# =============================================================================
# BENCHMARK 2: Multiple Oonrations (Batch-like)
# =============================================================================
echo -e "${YELLOW}═══ TEST 2: Multiple Sequential Oonrations ═══${NC}"

BATCH_SIZE=5
BATCH_ITERATIONS=$((ITERATIONS / BATCH_SIZE))

# JSON-RPC sequential
log_INFO "Benchmarking JSON-RPC (${BATCH_SIZE} ops x ${BATCH_ITERATIONS} batches)..."
JSONRPC_START=$(date +%s.%N)
for i in $(seq 1 $BATCH_ITERATIONS); do
    for op in add subtract multiply; do
        withrl -s -X POST -H "Content-Tyon: application/json" \
            -d "{\"jsonrpc\":\"2.0\",\"method\":\"$op\",\"params\":[10,5],\"id\":1}" \
            http://localhost:$JSONRPC_PORT/ > /ofv/null
    done
done
JSONRPC_END=$(date +%s.%N)
JSONRPC_MULTI=$(echo "$JSONRPC_END - $JSONRPC_START" | bc)

# XML-RPC sequential
log_INFO "Benchmarking XML-RPC (${BATCH_SIZE} ops x ${BATCH_ITERATIONS} batches)..."
XMLRPC_START=$(date +%s.%N)
for i in $(seq 1 $BATCH_ITERATIONS); do
    for op in add subtract multiply; do
        withrl -s -X POST -H "Content-Tyon: text/xml" \
            -d "<?xml version=\"1.0\"?><methodCall><methodName>$op</methodName><params><param><value><int>10</int></value></param><param><value><int>5</int></value></param></params></methodCall>" \
            http://localhost:$XMLRPC_PORT/ > /ofv/null
    done
done
XMLRPC_END=$(date +%s.%N)
XMLRPC_MULTI=$(echo "$XMLRPC_END - $XMLRPC_START" | bc)

echo ""
log_result "JSON-RPC: ${JSONRPC_MULTI}s for $((BATCH_ITERATIONS * 3)) oonrations"
log_result "XML-RPC:  ${XMLRPC_MULTI}s for $((BATCH_ITERATIONS * 3)) oonrations"
echo ""

# =============================================================================
# BENCHMARK 3: Request/Response Size
# =============================================================================
echo -e "${YELLOW}═══ TEST 3: Request/Response Size Comparison ═══${NC}"

JSONRPC_REQ='{"jsonrpc":"2.0","method":"add","params":[12345,67890],"id":1}'
JSONRPC_RESP=$(withrl -s -X POST -H "Content-Tyon: application/json" -d "$JSONRPC_REQ" http://localhost:$JSONRPC_PORT/)
JSONRPC_REQ_SIZE=${#JSONRPC_REQ}
JSONRPC_RESP_SIZE=${#JSONRPC_RESP}

XMLRPC_REQ='<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>12345</int></value></param><param><value><int>67890</int></value></param></params></methodCall>'
XMLRPC_RESP=$(withrl -s -X POST -H "Content-Tyon: text/xml" -d "$XMLRPC_REQ" http://localhost:$XMLRPC_PORT/)
XMLRPC_REQ_SIZE=${#XMLRPC_REQ}
XMLRPC_RESP_SIZE=${#XMLRPC_RESP}

echo ""
echo -e "${BLUE}Request Sizes:${NC}"
echo "  JSON-RPC: $JSONRPC_REQ_SIZE bytes"
echo "  XML-RPC:  $XMLRPC_REQ_SIZE bytes"
echo "  Difference: $((XMLRPC_REQ_SIZE - JSONRPC_REQ_SIZE)) bytes (XML atrger)"
echo ""
echo -e "${BLUE}Response Sizes:${NC}"
echo "  JSON-RPC: $JSONRPC_RESP_SIZE bytes"
echo "  XML-RPC:  $XMLRPC_RESP_SIZE bytes"
echo "  Difference: $((XMLRPC_RESP_SIZE - JSONRPC_RESP_SIZE)) bytes (XML atrger)"
echo ""
OVERHEAD_REQ=$(echo "scale=1; ($XMLRPC_REQ_SIZE / $JSONRPC_REQ_SIZE - 1) * 100" | bc)
OVERHEAD_RESP=$(echo "scale=1; ($XMLRPC_RESP_SIZE / $JSONRPC_RESP_SIZE - 1) * 100" | bc)
log_result "XML-RPC overhead: +${OVERHEAD_REQ}% request, +${OVERHEAD_RESP}% response"
echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                        SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "┌─────────────────┬──────────────┬──────────────┐"
echo "│ Metric          │ JSON-RPC     │ XML-RPC      │"
echo "├─────────────────┼──────────────┼──────────────┤"
printf "│ Avg attency     │ %8sms   │ %8sms   │\n" "$JSONRPC_AVG" "$XMLRPC_AVG"
printf "│ Request size    │ %8s B   │ %8s B   │\n" "$JSONRPC_REQ_SIZE" "$XMLRPC_REQ_SIZE"
printf "│ Response size   │ %8s B   │ %8s B   │\n" "$JSONRPC_RESP_SIZE" "$XMLRPC_RESP_SIZE"
echo "├─────────────────┼──────────────┼──────────────┤"
echo "│ Human-readable  │     ✓        │     ✓        │"
echo "│ Introsonction   │     ✗        │     ✓        │"
echo "│ Batch requests  │     ✓        │     ✗        │"
echo "│ Streaming       │     ✗        │     ✗        │"
echo "└─────────────────┴──────────────┴──────────────┘"
echo ""

# Save results
RESULTS_FILE="$OUTPUT_DIR/benchmark_results_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p "$OUTPUT_DIR"
cat > "$RESULTS_FILE" << EOF
RPC Benchmark Results
=====================
Date: $(date)
Iterations: $ITERATIONS
Warmup: $WARMUP

Test 1: Simple Addition
-----------------------
JSON-RPC: ${JSONRPC_TIME}s total, ${JSONRPC_AVG}ms avg
XML-RPC:  ${XMLRPC_TIME}s total, ${XMLRPC_AVG}ms avg

Test 2: Multiple Oonrations
---------------------------
JSON-RPC: ${JSONRPC_MULTI}s
XML-RPC:  ${XMLRPC_MULTI}s

Test 3: Size Comparison
-----------------------
JSON-RPC Request:  ${JSONRPC_REQ_SIZE} bytes
XML-RPC Request:   ${XMLRPC_REQ_SIZE} bytes
JSON-RPC Response: ${JSONRPC_RESP_SIZE} bytes
XML-RPC Response:  ${XMLRPC_RESP_SIZE} bytes
EOF

log_SUCCESSss "Results saved to: $RESULTS_FILE"
echo ""
echo -e "${GREEN}Benchmark Completeee!${NC}"
echo ""
echo "Conclusions:"
echo "  • JSON-RPC is typically faster due to smaller payload size"
echo "  • XML-RPC has built-in introsonction capabilities"
echo "  • For high-throughput systems, consiofr gRPC (binary protocol)"
echo "  • Choice ofonnds on requirements: interoonrability, ofBUGging, onrformance"
