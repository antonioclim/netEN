#!/bin/bash
# =============================================================================
# run_all.sh – Automated demo for Starterkit S9
# File protocols: FTP-style server / mini file-transfer + multi-client
# =============================================================================
# 
# Produces:
#   - artifacts/demo.log      (complete demo logs)
#   - artifacts/demo.pcap     (traffic capture)
#   - artifacts/validation.txt (validation results)
#
# Run: ./scripts/run_all.sh (no interactive input)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Configuration
PORT="${PORT:-5900}"  # Default port for automated demo (falls back if busy)
HOST="127.0.0.1"
USER="test"
PASS="12345"

# If the preferred port is already in use, walk upwards until we find a free one.
if command -v ss >/dev/null 2>&1; then
  while ss -lnt "sport = :${PORT}" 2>/dev/null | grep -q LISTEN; do
    PORT=$((PORT + 1))
  done
elif command -v lsof >/dev/null 2>&1; then
  while lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; do
    PORT=$((PORT + 1))
  done
fi
TIMEOUT=10

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Directories
mkdir -p artifacts server-files client-files

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}[CLEANUP] Stopping processes...${NC}"
    pkill -f "ex_9_02_pseudo_ftp.py.*--port $PORT" 2>/dev/null || true
    pkill -f "tcpdump.*port $PORT" 2>/dev/null || true
    sleep 0.5
}
trap cleanup EXIT

# =============================================================================
# Initialisation
# =============================================================================

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Starterkit S9 – Automated Demo                                   ║${NC}"
echo -e "${CYAN}║  File Protocols (FTP/File Transfer)                               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# Clean old artefacts
rm -f artifacts/demo.log artifacts/demo.pcap artifacts/validation.txt

# Start logging
exec > >(tee -a artifacts/demo.log) 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Demo start"

# =============================================================================
# Step 1: Setup
# =============================================================================

echo -e "\n${YELLOW}[1/6] Environment setup...${NC}"

# Create test files on server
echo "Hello Week 9 - FTP Demo!" > server-files/hello.txt
echo "Test UTF-8: Romania ✓ country" > server-files/utf8_test.txt
echo "Binary content for testing" > server-files/test.bin
dd if=/dev/urandom of=server-files/random_1k.bin bs=1024 count=1 2>/dev/null || true

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 is not installed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 available${NC}"

# =============================================================================
# Step 2: L6 Exercise (endianness)
# =============================================================================

echo -e "\n${YELLOW}[2/6] L6 Exercise - Endianness and Framing...${NC}"
python3 python/exercises/ex_9_01_endianness.py --selftest
echo -e "${GREEN}✓ L6 exercise complete${NC}"

# =============================================================================
# Step 3: Test net_utils.py
# =============================================================================

echo -e "\n${YELLOW}[3/6] Checking common utilities (net_utils.py)...${NC}"
python3 python/utils/net_utils.py
echo -e "${GREEN}✓ net_utils.py OK${NC}"

# =============================================================================
# Step 4: Start traffic capture
# =============================================================================

echo -e "\n${YELLOW}[4/6] Starting traffic capture on port $PORT...${NC}"

# Try tcpdump (requires privileges in some cases)
if command -v tcpdump &> /dev/null; then
    # Run tcpdump in background
    # Note: may require sudo in real environments
    timeout 30 tcpdump -i lo "tcp port $PORT" -w artifacts/demo.pcap -c 100 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 0.5
    
    if kill -0 $TCPDUMP_PID 2>/dev/null; then
        echo -e "${GREEN}✓ tcpdump started (PID: $TCPDUMP_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ tcpdump did not start (requires privileges?)${NC}"
        # Create empty pcap for smoke test
        touch artifacts/demo.pcap
    fi
else
    echo -e "${YELLOW}⚠ tcpdump not installed, creating empty pcap${NC}"
    touch artifacts/demo.pcap
fi

# =============================================================================
# Step 5: Pseudo-FTP Server + Client
# =============================================================================

echo -e "\n${YELLOW}[5/6] Testing Pseudo-FTP (server + client)...${NC}"

# Start server in background
echo "[$(date '+%H:%M:%S')] Starting server on port $PORT..."
python3 python/exercises/ex_9_02_pseudo_ftp.py server \
    --host $HOST --port $PORT --root ./server-files &
SERVER_PID=$!
sleep 1

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}[ERROR] Server did not start!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"

# Test LIST
echo "[$(date '+%H:%M:%S')] Client: LIST..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    list || true

# Test GET (passive mode)
echo "[$(date '+%H:%M:%S')] Client: GET hello.txt (passive)..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    --local-dir ./client-files --mode passive \
    get hello.txt || true

# Check that file was downloaded
if [ -f "client-files/hello.txt" ]; then
    echo -e "${GREEN}✓ File downloaded: client-files/hello.txt${NC}"
    DOWNLOADED_SHA=$(sha256sum client-files/hello.txt | cut -d' ' -f1)
    ORIGINAL_SHA=$(sha256sum server-files/hello.txt | cut -d' ' -f1)
    
    if [ "$DOWNLOADED_SHA" = "$ORIGINAL_SHA" ]; then
        echo -e "${GREEN}✓ SHA256 verified: $DOWNLOADED_SHA${NC}"
    else
        echo -e "${RED}⚠ SHA256 different!${NC}"
    fi
else
    echo -e "${YELLOW}⚠ File was not downloaded${NC}"
fi

# Test GET with compression
echo "[$(date '+%H:%M:%S')] Client: GET utf8_test.txt (passive + gzip)..."
python3 python/exercises/ex_9_02_pseudo_ftp.py client \
    --host $HOST --port $PORT --user $USER --password $PASS \
    --local-dir ./client-files --mode passive --gzip \
    get utf8_test.txt || true

# Stop server
echo "[$(date '+%H:%M:%S')] Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo -e "${GREEN}✓ Pseudo-FTP test complete${NC}"

# =============================================================================
# Step 6: Validation
# =============================================================================

echo -e "\n${YELLOW}[6/6] Validating results...${NC}"

{
    echo "═══════════════════════════════════════════════════════════════"
    echo "  STARTERKIT S9 VALIDATION – $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Test 1: Endianness exercise
    echo "▶ Test 1: L6 Exercise (endianness)"
    if python3 python/exercises/ex_9_01_endianness.py --selftest 2>&1 | grep -q "All tests passed"; then
        echo "   [PASS] L6 Exercise OK"
    else
        echo "   [FAIL] L6 Exercise FAILED"
    fi
    echo ""
    
    # Test 2: net_utils.py
    echo "▶ Test 2: Common utilities (net_utils.py)"
    if python3 python/utils/net_utils.py 2>&1 | grep -q "All tests passed"; then
        echo "   [PASS] net_utils.py OK"
    else
        echo "   [FAIL] net_utils.py FAILED"
    fi
    echo ""
    
    # Test 3: Import pseudo-FTP
    echo "▶ Test 3: Import ex_9_02_pseudo_ftp.py"
    if python3 -c "from python.exercises.ex_9_02_pseudo_ftp import pack_data, unpack_data; print('OK')" 2>&1 | grep -q "OK"; then
        echo "   [PASS] Import OK"
    else
        echo "   [FAIL] Import FAILED"
    fi
    echo ""
    
    # Test 4: Downloaded files
    echo "▶ Test 4: File transfer"
    if [ -f "client-files/hello.txt" ]; then
        echo "   [PASS] hello.txt downloaded"
        echo "   SHA256: $(sha256sum client-files/hello.txt 2>/dev/null | cut -d' ' -f1 || echo 'N/A')"
    else
        echo "   [FAIL] hello.txt was NOT downloaded"
    fi
    echo ""
    
    # Test 5: Artefacts
    echo "▶ Test 5: Generated artefacts"
    [ -f "artifacts/demo.log" ] && echo "   [PASS] demo.log present" || echo "   [FAIL] demo.log missing"
    [ -f "artifacts/demo.pcap" ] && echo "   [PASS] demo.pcap present" || echo "   [FAIL] demo.pcap missing"
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════"
    echo "  VALIDATION COMPLETE"
    echo "═══════════════════════════════════════════════════════════════"
    
} > artifacts/validation.txt

cat artifacts/validation.txt

# =============================================================================
# Final
# =============================================================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Demo complete!                                                   ║${NC}"
echo -e "${GREEN}║                                                                   ║${NC}"
echo -e "${GREEN}║  Generated artefacts:                                             ║${NC}"
echo -e "${GREEN}║    - artifacts/demo.log                                           ║${NC}"
echo -e "${GREEN}║    - artifacts/demo.pcap                                          ║${NC}"
echo -e "${GREEN}║    - artifacts/validation.txt                                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Demo end"
