#!/bin/bash
# verify.sh — Verifies environment and dependencies for Starterkit W14
# Run: bash scripts/verify.sh

echo "=============================================="
echo "  Environment Verification W14"
echo "=============================================="
echo ""

ERRORS=0

# Function to check command
check_cmd() {
    local cmd=$1
    local required=$2
    
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | head -1 || echo "installed")
        echo "  ✓ $cmd: $version"
    else
        if [ "$required" = "required" ]; then
            echo "  ✗ $cmd: MISSING (required)"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ○ $cmd: missing (optional)"
        fi
    fi
}

# Check Python
echo "[*] Python:"
check_cmd python3 required
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$PY_VERSION >= 3.8" | bc)" -eq 1 ] 2>/dev/null || python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
        echo "    Version OK (>= 3.8)"
    else
        echo "    Version too old (requires >= 3.8)"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check pip
echo ""
echo "[*] Pip:"
check_cmd pip3 required

# Check Mininet
echo ""
echo "[*] Mininet & OVS:"
check_cmd mn required
check_cmd ovs-vsctl required

if command -v ovs-vsctl &> /dev/null; then
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
        echo "    openvswitch-switch: active"
    else
        echo "    openvswitch-switch: INACTIVE"
        echo "    Run: sudo systemctl start openvswitch-switch"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check network tools
echo ""
echo "[*] Network tools:"
check_cmd ip required
check_cmd ping required
check_cmd ss required
check_cmd tcpdump required
check_cmd tshark optional
check_cmd nc optional
check_cmd curl optional
check_cmd ab optional

# Check permissions
echo ""
echo "[*] Permissions:"
if [ "$EUID" -eq 0 ]; then
    echo "  ✓ Running as root"
else
    echo "  ○ Not running as root (demo requires sudo)"
fi

# Check ports
echo ""
echo "[*] Ports (8000, 8080, 9000):"
for port in 8000 8080 9000; do
    if ss -lntp 2>/dev/null | grep -q ":$port "; then
        echo "  ✗ Port $port: OCCUPIED"
        ss -lntp 2>/dev/null | grep ":$port " | head -1
    else
        echo "  ✓ Port $port: free"
    fi
done

# Summary
echo ""
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo "  Verification complete: OK"
    echo "=============================================="
    exit 0
else
    echo "  Verification complete: $ERRORS errors"
    echo "=============================================="
    echo ""
    echo "Run 'sudo bash scripts/setup.sh' to install dependencies."
    exit 1
fi
