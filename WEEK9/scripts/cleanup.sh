#!/bin/bash
# =============================================================================
# cleanup.sh – Complete cleanup for Starterkit S9
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  Cleanup Starterkit S9                                            ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}"

# 1. Stop processes
echo -e "\n${YELLOW}[1/5] Stopping processes...${NC}"
pkill -f "ex_9_02_pseudo_ftp" 2>/dev/null && echo "  ✓ Stopped: pseudo_ftp" || true
pkill -f "ftp_demo" 2>/dev/null && echo "  ✓ Stopped: ftp_demo" || true
pkill -f "tcpdump" 2>/dev/null && echo "  ✓ Stopped: tcpdump" || true

# 2. Docker cleanup (if available)
echo -e "\n${YELLOW}[2/5] Docker cleanup...${NC}"
if command -v docker-compose &> /dev/null && [ -f "docker/docker-compose.yml" ]; then
    cd docker && docker-compose down -v 2>/dev/null && cd .. && echo "  ✓ Docker stopped" || true
else
    echo "  - Docker not configured"
fi

# 3. Mininet cleanup (if root)
echo -e "\n${YELLOW}[3/5] Mininet cleanup...${NC}"
if [ "$(id -u)" -eq 0 ]; then
    mn -c 2>/dev/null && echo "  ✓ Mininet cleaned" || true
else
    echo "  - Requires root for mn -c"
fi

# 4. Temporary files cleanup
echo -e "\n${YELLOW}[4/5] Temporary files cleanup...${NC}"
rm -rf __pycache__ python/**/__pycache__ .pytest_cache 2>/dev/null && echo "  ✓ Python cache" || true
rm -f *.pyc python/**/*.pyc 2>/dev/null && echo "  ✓ .pyc files" || true
rm -f client-files/*.txt client-files/*.bin 2>/dev/null && echo "  ✓ Client files" || true

# 5. Artefacts cleanup (optional)
echo -e "\n${YELLOW}[5/5] Artefacts cleanup...${NC}"
if [ "${1:-}" = "--all" ]; then
    rm -rf artifacts/* 2>/dev/null && echo "  ✓ Artefacts deleted" || true
    rm -rf server-files/* 2>/dev/null && echo "  ✓ Server files deleted" || true
else
    echo "  - Artefacts kept (use --all for complete deletion)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Cleanup complete!${NC}"
echo -e "${GREEN}  For total deletion: ./scripts/cleanup.sh --all${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
