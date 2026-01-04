#!/bin/bash
echo "[CLEAN] Cleanup Mininet..."
sudo mn -c 2>/dev/null || true
echo "[CLEAN] Stopping Python processes..."
sudo pkill -f "ex0[1-8]" 2>/dev/null || true
sudo pkill -f "topo_" 2>/dev/null || true
echo "[CLEAN] Cleanup temporary files..."
rm -rf __pycache__ python/__pycache__ logs/ *.pcap *.pcapng
echo "[OK] Cleanup complete."
