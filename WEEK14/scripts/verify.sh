#!/usr/bin/env bash
# verify.sh — Verifies the environment for Week 14
# Run: bash scripts/verify.sh

set -euo pipefail

echo "=============================================="
echo "  Environment Verification - Week 14"
echo "=============================================="
echo ""

ERRORS=0

check_cmd() {
  local cmd="$1"
  local required="$2"

  if command -v "$cmd" >/dev/null 2>&1; then
    local version
    version=$($cmd --version 2>&1 | head -1 || echo "installed")
    echo "  ✓ $cmd: $version"
  else
    if [[ "$required" == "required" ]]; then
      echo "  ✗ $cmd: MISSING (required)"
      ERRORS=$((ERRORS + 1))
    else
      echo "  ○ $cmd: missing (optional)"
    fi
  fi
}

echo "[*] Python:"
check_cmd python3 required

if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "    Version OK (>= 3.8)"
  else
    echo "    Version too old (requires >= 3.8)"
    ERRORS=$((ERRORS + 1))
  fi

  # Validate that the system Mininet package is importable.
  if python3 -c "import mininet; import mininet.net" >/dev/null 2>&1; then
    echo "    Mininet Python package importable"
  else
    echo "    Mininet Python package import FAILED"
    echo "    This can happen if a local folder shadows the system package."
    ERRORS=$((ERRORS + 1))
  fi
fi

echo ""
echo "[*] Pip:"
check_cmd pip3 required

echo ""
echo "[*] Mininet and Open vSwitch:"
check_cmd mn required
check_cmd ovs-vsctl required

if command -v systemctl >/dev/null 2>&1; then
  if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
    echo "    openvswitch-switch: active"
  else
    echo "    openvswitch-switch: inactive"
    echo "    Run: sudo systemctl start openvswitch-switch"
    ERRORS=$((ERRORS + 1))
  fi
fi

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

echo ""
echo "[*] Permissions:"
if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
  echo "  ✓ Running as root"
else
  echo "  ○ Not running as root (Mininet demos require sudo)"
fi

echo ""
echo "[*] Local TCP ports (host namespace only):"
echo "    This check is informative. Mininet hosts run in separate network namespaces."
for port in 8080 9000; do
  if ss -lnt 2>/dev/null | grep -q ":$port "; then
    echo "  ○ Port $port: in use (host namespace)"
  else
    echo "  ✓ Port $port: free (host namespace)"
  fi
done

echo ""
echo "=============================================="
if [[ $ERRORS -eq 0 ]]; then
  echo "  Verification complete: OK"
  echo "=============================================="
  exit 0
else
  echo "  Verification complete: $ERRORS error(s)"
  echo "=============================================="
  echo ""
  echo "Run 'make setup' to install dependencies."
  exit 1
fi
