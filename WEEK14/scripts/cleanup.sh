#!/bin/bash
# cleanup.sh — Cleans processes and Mininet network
# Run: sudo bash scripts/cleanup.sh

echo "=============================================="
echo "  Cleanup W14"
echo "=============================================="

# Stop starterkit processes
echo "[*] Stopping starterkit processes..."
pkill -f "backend_server.py" 2>/dev/null || true
pkill -f "lb_proxy.py" 2>/dev/null || true
pkill -f "tcp_echo_server.py" 2>/dev/null || true
pkill -f "tcp_echo_client.py" 2>/dev/null || true
pkill -f "http_client.py" 2>/dev/null || true
pkill -f "run_demo.py" 2>/dev/null || true
pkill -f "topo_14" 2>/dev/null || true

# Stop tcpdump
echo "[*] Stopping tcpdump..."
pkill -f "tcpdump" 2>/dev/null || true

# Clean Mininet
echo "[*] Cleaning Mininet..."
if command -v mn &> /dev/null; then
    mn -c 2>/dev/null || true
fi

# Stop OVS orphan bridges (optional)
echo "[*] Checking OVS..."
if command -v ovs-vsctl &> /dev/null; then
    for br in $(ovs-vsctl list-br 2>/dev/null); do
        if [[ "$br" == s* ]]; then
            echo "    Deleting bridge: $br"
            ovs-vsctl del-br "$br" 2>/dev/null || true
        fi
    done
fi

# Free common ports (W14 port plan)
echo "[*] Checking ports..."
for port in 8080 9090 9091; do
    pid=$(ss -lntp 2>/dev/null | grep ":$port " | awk '{print $NF}' | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$pid" ]; then
        echo "    Freeing port $port (PID: $pid)"
        kill "$pid" 2>/dev/null || true
    fi
done

sleep 1

echo ""
echo "=============================================="
echo "  Cleanup completed!"
echo "=============================================="
