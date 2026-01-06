#!/bin/bash
# =============================================================================
# Setup script for Starterkit S9
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Setup Starterkit S9 - Computer Networks                       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"

# 1. Check Python
echo -e "\n${YELLOW}[1/4] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYVER=$(python3 --version)
    echo -e "${GREEN}✓ $PYVER${NC}"
else
    echo "Python3 is not installed!"
    exit 1
fi

# 2. Install Python dependencies
echo -e "\n${YELLOW}[2/4] Installing Python dependencies...${NC}"
python3 -m pip install --break-system-packages -q -r requirements.txt 2>/dev/null || \
    python3 -m pip install -q -r requirements.txt 2>/dev/null || \
    echo "Note: Install pyftpdlib manually if needed"
echo -e "${GREEN}✓ Dependencies installed${NC}"

# 3. Create directories
echo -e "\n${YELLOW}[3/4] Creating directories...${NC}"
mkdir -p server-files client-files pcap
echo -e "${GREEN}✓ Directories created${NC}"

# 4. Create test files
echo -e "\n${YELLOW}[4/4] Creating test files...${NC}"
echo "Hello S9 - File protocols!" > server-files/hello.txt
echo "Test file with UTF-8: Romania ✓" > server-files/utf8_test.txt
echo "Binary test content" > server-files/test.bin
dd if=/dev/urandom of=server-files/random_100k.bin bs=1024 count=100 2>/dev/null || true
echo -e "${GREEN}✓ Test files created${NC}"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete! Useful commands:${NC}"
echo -e "${GREEN}    make server         - Start the server${NC}"
echo -e "${GREEN}    make client-list    - List files${NC}"
echo -e "${GREEN}    make help           - All commands${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
