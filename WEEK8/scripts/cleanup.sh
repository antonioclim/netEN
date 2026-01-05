#!/bin/bash
set -euo pipefail
# ═══════════════════════════════════════════════════════════════════════════════
# cleanup.sh - Week 8 Environment Cleanup
# ═══════════════════════════════════════════════════════════════════════════════
#
# Stops all processes and cleans temporary files.
# Includes Mininet cleanup if applicable.
#
# Author: Computer Networks, ASE Bucharest
# Hypotheticalandrei & Rezolvix | MIT License
# ═══════════════════════════════════════════════════════════════════════════════

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  Cleanup - Week 8                                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Stop Python servers
echo "[cleanup] Stopping HTTP servers..."
pkill -f "demo_http_server.py" 2>/dev/null || true
pkill -f "demo_reverse_proxy.py" 2>/dev/null || true
pkill -f "ex01_http_server.py" 2>/dev/null || true
pkill -f "ex02_reverse_proxy.py" 2>/dev/null || true
pkill -f "ex03_post_support.py" 2>/dev/null || true
pkill -f "ex04_rate_limiting.py" 2>/dev/null || true
pkill -f "ex05_caching_proxy.py" 2>/dev/null || true

# Stop tcpdump (if running)
echo "[cleanup] Stopping tcpdump..."
sudo pkill -f "tcpdump" 2>/dev/null || true

# Release used ports
echo "[cleanup] Releasing ports 8080, 8888, 9001, 9002..."
for port in 8080 8888 9001 9002 5800 5801 5802; do
    fuser -k "$port/tcp" 2>/dev/null || true
done

# Docker cleanup (if applicable)
if command -v docker &>/dev/null; then
    echo "[cleanup] Checking Docker containers..."
    if docker ps -q --filter "label=com.ase.project=seminar8" | grep -q .; then
        echo "[cleanup] Stopping seminar8 containers..."
        docker stop $(docker ps -q --filter "label=com.ase.project=seminar8") 2>/dev/null || true
    fi
fi

# Mininet cleanup (if installed)
if command -v mn &>/dev/null; then
    echo "[cleanup] Mininet cleanup..."
    sudo mn -c 2>/dev/null || true
fi

# Clean temporary files
echo "[cleanup] Cleaning temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "[cleanup] Cleanup complete!"
