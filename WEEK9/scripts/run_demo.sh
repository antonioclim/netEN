#!/bin/bash
# Demo complet for Starterkit S9

set -euo pipefail
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}═══ Demo Complet S9 ═══${NC}"
echo ""

# 1. Exercise endianness
echo -e "${GREEN}[1/3] Exercise L6 - Endianness${NC}"
python3 python/exercises/ex_9_01_endianness.py --selftest
echo ""

# 2. Demo encoding
echo -e "${GREEN}[2/3] Demo L6 - Encoding${NC}"
python3 -c "
import base64, gzip, json
text = 'Unicode: sample ✓'
print(f'Original: {text}')
print(f'UTF-8 bytes: {text.encode(\"utf-8\")}')
print(f'Base64: {base64.b64encode(text.encode()).decode()}')
compressed = gzip.compress(text.encode())
print(f'Gzip: {len(compressed)} bytes (vs {len(text.encode())} original)')
"
echo ""

# 3. Final message
echo -e "${GREEN}[3/3] For pseudo-FTP demo:${NC}"
echo "  Terminal 1: make server"
echo "  Terminal 2: make client-list"
echo ""
echo -e "${CYAN}═══ Demo complet! ═══${NC}"
