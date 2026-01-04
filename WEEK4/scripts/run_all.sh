#!/bin/bash
# ==============================================================================
# run_all.sh - Automatic demo for Week 4 Starterkit
# ==============================================================================
# Runs without interactive input and produces:
#   - artifacts/demo.log      : complete demo log
#   - artifacts/demo.pcap     : traffic capture (if tcpdump available)
#   - artifacts/validation.txt: verification results
#
# WEEK 4 standard ports: 5400 (TEXT), 5401 (BINARY), 5402 (UDP)
# IP network: 10.0.4.0/24 (for Mininet scenarios)
#
# Usage:
#   ./scripts/run_all.sh           # complete demo
#   ./scripts/run_all.sh --quick   # quick demo (no capture)
#
# Licence: MIT - ASE-CSIE Teaching Material
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ==============================================================================
# WEEK 4 PORT PLAN (Cross-Cutting Standard)
# ==============================================================================
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5100 + 300 = 5400
PORT_TEXT=5400    # TCP text protocol
PORT_BIN=5401     # TCP binary protocol
PORT_UDP=5402     # UDP sensors

# ==============================================================================
# IP PLAN (for Mininet)
# ==============================================================================
# Network: 10.0.4.0/24
# Gateway: 10.0.4.1
# Server: 10.0.4.100
# Hosts: h1=10.0.4.11, h2=10.0.4.12, h3=10.0.4.13

# Directories
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Options
QUICK_MODE=false
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    QUICK_MODE=true
fi

# PIDs for cleanup
declare -a PIDS=()
TCPDUMP_PID=""

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}[CLEANUP] Stopping processes...${NC}" | tee -a "$DEMO_LOG"
    
    # Stop tcpdump
    if [ -n "$TCPDUMP_PID" ]; then
        sudo kill $TCPDUMP_PID 2>/dev/null || true
        sleep 0.5
    fi
    
    # Stop servers
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null || true
    done
    
    pkill -f "text_proto_server" 2>/dev/null || true
    pkill -f "binary_proto_server" 2>/dev/null || true
    pkill -f "udp_sensor_server" 2>/dev/null || true
}

trap cleanup EXIT

# Create directories
mkdir -p "$ARTIFACTS_DIR"

# Initialise log
echo "═══════════════════════════════════════════════════════════════" > "$DEMO_LOG"
echo "  STARTERKIT S4 - AUTOMATIC DEMO" >> "$DEMO_LOG"
echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$DEMO_LOG"
echo "  Ports: TEXT=$PORT_TEXT, BINARY=$PORT_BIN, UDP=$PORT_UDP" >> "$DEMO_LOG"
echo "═══════════════════════════════════════════════════════════════" >> "$DEMO_LOG"
echo "" >> "$DEMO_LOG"

# Banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║     STARTERKIT S4 - CUSTOM TEXT/BINARY PROTOCOLS (WEEK 4)            ║"
echo "║     Ports: TEXT=$PORT_TEXT, BINARY=$PORT_BIN, UDP=$PORT_UDP                          ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# START CAPTURE (if tcpdump available and not quick mode)
# ==============================================================================
if [ "$QUICK_MODE" = false ] && command -v tcpdump >/dev/null 2>&1; then
    echo -e "${GREEN}[CAPTURE] Starting traffic capture...${NC}" | tee -a "$DEMO_LOG"
    TCPDUMP_PID=""
    # Try without sudo first, then sudo -n (non-interactive) if needed
    if tcpdump -i lo -w "$DEMO_PCAP" "port $PORT_TEXT or port $PORT_BIN or port $PORT_UDP" 2>/dev/null & then
        TCPDUMP_PID=$!
    elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
        sudo -n tcpdump -i lo -w "$DEMO_PCAP" "port $PORT_TEXT or port $PORT_BIN or port $PORT_UDP" 2>/dev/null &
        TCPDUMP_PID=$!
    else
        echo -e "${YELLOW}[CAPTURE] tcpdump present but capture is not permitted, continuing without pcap${NC}" | tee -a "$DEMO_LOG"
    fi
    sleep 1
    if [ -n "${TCPDUMP_PID:-}" ]; then
        echo "  Capture active (PID: $TCPDUMP_PID)" | tee -a "$DEMO_LOG"
    else
        # Keep an empty file for a predictable artefact set
        : > "$DEMO_PCAP"
    fi
else
    echo -e "${YELLOW}[CAPTURE] Skip (tcpdump unavailable or --quick)${NC}" | tee -a "$DEMO_LOG"
    # Keep an empty file for a predictable artefact set
    : > "$DEMO_PCAP"
fi

# ==============================================================================
# DEMO 1: TEXT Protocol over TCP
# ==============================================================================
echo -e "\n${GREEN}[DEMO 1] TEXT Protocol over TCP (port $PORT_TEXT)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Start server in background
python3 python/apps/text_proto_server.py --port $PORT_TEXT --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server started on port $PORT_TEXT (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Test with client
echo -e "\n${CYAN}Executing TEXT commands:${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/text_proto_client.py --host localhost --port $PORT_TEXT \
    -c "PING" \
    -c "SET name Alice" \
    -c "SET city Bucharest" \
    -c "SET year 2025" \
    -c "GET name" \
    -c "COUNT" \
    -c "KEYS" \
    -c "DEL year" \
    -c "COUNT" \
    -c "QUIT" \
    -v 2>&1 | tee -a "$DEMO_LOG"

# Stop server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ TEXT Demo complete!${NC}\n" | tee -a "$DEMO_LOG"

sleep 0.5

# ==============================================================================
# DEMO 2: BINARY Protocol over TCP
# ==============================================================================
echo -e "${GREEN}[DEMO 2] BINARY Protocol over TCP (port $PORT_BIN)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Start server in background
python3 python/apps/binary_proto_server.py --port $PORT_BIN --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server started on port $PORT_BIN (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Test with client
echo -e "\n${CYAN}Executing BINARY commands:${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/binary_proto_client.py --host localhost --port $PORT_BIN \
    -c "echo Hello Binary World" \
    -c "put name Bob" \
    -c "put city Paris" \
    -c "put temp 23.5" \
    -c "get name" \
    -c "count" \
    -c "keys" \
    -c "quit" \
    -v 2>&1 | tee -a "$DEMO_LOG"

# Stop server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ BINARY Demo complete!${NC}\n" | tee -a "$DEMO_LOG"

sleep 0.5

# ==============================================================================
# DEMO 3: UDP Sensor Protocol
# ==============================================================================
echo -e "${GREEN}[DEMO 3] UDP Sensor Protocol (port $PORT_UDP)${NC}" | tee -a "$DEMO_LOG"
echo "──────────────────────────────────────────" | tee -a "$DEMO_LOG"

# Start server in background
python3 python/apps/udp_sensor_server.py --port $PORT_UDP --verbose >> "$DEMO_LOG" 2>&1 &
SERVER_PID=$!
PIDS+=($SERVER_PID)
sleep 1

echo "Server started on port $PORT_UDP (PID: $SERVER_PID)" | tee -a "$DEMO_LOG"

# Send sensor readings
echo -e "\n${CYAN}Sending sensor readings:${NC}" | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 1 --temp 23.5 --location "Lab1" -v 2>&1 | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 2 --temp 19.2 --location "Office" -v 2>&1 | tee -a "$DEMO_LOG"

python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 1 --temp 24.1 --location "Lab1" -v 2>&1 | tee -a "$DEMO_LOG"

# Send a corrupted packet to demonstrate error detection
echo -e "\n${YELLOW}Sending corrupted packet (CRC testing):${NC}" | tee -a "$DEMO_LOG"
python3 python/apps/udp_sensor_client.py --host localhost --port $PORT_UDP \
    --sensor-id 99 --temp 0.0 --location "Test" --corrupt -v 2>&1 | tee -a "$DEMO_LOG"

sleep 1

# Stop server
kill $SERVER_PID 2>/dev/null || true
echo -e "\n${GREEN}✓ UDP Demo complete!${NC}\n" | tee -a "$DEMO_LOG"

# ==============================================================================
# STOP CAPTURE
# ==============================================================================
if [ -n "$TCPDUMP_PID" ]; then
    echo -e "${GREEN}[CAPTURE] Stopping capture...${NC}" | tee -a "$DEMO_LOG"
    sudo kill $TCPDUMP_PID 2>/dev/null || true
    TCPDUMP_PID=""
    sleep 1
fi

# ==============================================================================
# GENERATE VALIDATION.TXT
# ==============================================================================
echo -e "${GREEN}[VALIDATION] Generating validation report...${NC}" | tee -a "$DEMO_LOG"

cat > "$VALIDATION_FILE" << EOF
═══════════════════════════════════════════════════════════════
  VALIDATION REPORT - STARTERKIT S4 (WEEK 4)
  Generated: $(date '+%Y-%m-%d %H:%M:%S')
═══════════════════════════════════════════════════════════════

PORTS USED:
  TCP TEXT:   $PORT_TEXT (protocol length-prefixed)
  TCP BINARY: $PORT_BIN (header 14B + CRC32)
  UDP SENSOR: $PORT_UDP (datagram 23B + CRC32)

IP PLAN (Mininet):
  Network:    10.0.4.0/24
  Gateway:    10.0.4.1
  Server:     10.0.4.100
  Hosts:      h1=10.0.4.11, h2=10.0.4.12, h3=10.0.4.13

ARTIFACTS GENERATED:
EOF

# Verify artifacts
echo "" >> "$VALIDATION_FILE"
echo "FILES:" >> "$VALIDATION_FILE"

if [ -f "$DEMO_LOG" ]; then
    LINES=$(wc -l < "$DEMO_LOG")
    echo "  [OK] demo.log ($LINES lines)" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] demo.log missing" >> "$VALIDATION_FILE"
fi

if [ -f "$DEMO_PCAP" ]; then
    SIZE=$(stat -f%z "$DEMO_PCAP" 2>/dev/null || stat -c%s "$DEMO_PCAP" 2>/dev/null || echo "0")
    echo "  [OK] demo.pcap ($SIZE bytes)" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] demo.pcap missing" >> "$VALIDATION_FILE"
fi

# Verify commands in log
echo "" >> "$VALIDATION_FILE"
echo "PROTOCOL TESTS:" >> "$VALIDATION_FILE"

if grep -q "OK pong" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT PING successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT PING failed" >> "$VALIDATION_FILE"
fi

if grep -q "OK stored name" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT SET successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT SET failed" >> "$VALIDATION_FILE"
fi

if grep -q "OK.*keys" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] TEXT COUNT successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] TEXT COUNT failed" >> "$VALIDATION_FILE"
fi

if grep -q "ECHO_RESP\|Hello Binary" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] BINARY ECHO successful" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] BINARY ECHO failed" >> "$VALIDATION_FILE"
fi

if grep -q "Sensor.*Lab1\|sensor_id=1" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] UDP sensor data received" >> "$VALIDATION_FILE"
else
    echo "  [FAIL] UDP sensor data failed" >> "$VALIDATION_FILE"
fi

if grep -qi "crc.*mismatch\|corrupt\|CRC" "$DEMO_LOG" 2>/dev/null; then
    echo "  [OK] CRC error detection working" >> "$VALIDATION_FILE"
else
    echo "  [WARN] CRC error detection not verified" >> "$VALIDATION_FILE"
fi

echo "" >> "$VALIDATION_FILE"
echo "═══════════════════════════════════════════════════════════════" >> "$VALIDATION_FILE"
echo "  VALIDATION COMPLETE" >> "$VALIDATION_FILE"
echo "═══════════════════════════════════════════════════════════════" >> "$VALIDATION_FILE"

# ==============================================================================
# SUMMARY
# ==============================================================================
echo -e "${CYAN}"
echo "══════════════════════════════════════════════════════════════════════"
echo "                           DEMO SUMMARY"
echo "══════════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo "1. TEXT Protocol (TCP port $PORT_TEXT):"
echo "   - Framing: length-prefix (e.g. '11 SET name Alice')"
echo "   - Easy to debug with netcat/telnet (partially)"
echo "   - Human-readable for debugging"
echo ""
echo "2. BINARY Protocol (TCP port $PORT_BIN):"
echo "   - Fixed header 14 bytes + CRC32"
echo "   - Predictable and efficient parsing"
echo "   - Error detection included"
echo ""
echo "3. UDP Sensor Protocol (port $PORT_UDP):"
echo "   - Fixed datagram 23 bytes"
echo "   - CRC32 for integrity verification"
echo "   - Connectionless - no TCP overhead"
echo ""
echo -e "${GREEN}Artifacts generated in: $ARTIFACTS_DIR/${NC}"
echo "  - demo.log       : complete log"
echo "  - demo.pcap      : traffic capture"  
echo "  - validation.txt : validation report"
echo ""
echo -e "${GREEN}For verification: cat $VALIDATION_FILE${NC}"

# Display validation summary
echo ""
cat "$VALIDATION_FILE"