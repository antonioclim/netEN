#!/usr/bin/env bash
# ==============================================================================
# smoke_test.sh - Quick validation for Week 4 starter kit
# ==============================================================================
# Checks
# 1) Python availability
# 2) Python syntax (py_compile) for key modules
# 3) Core protocol utilities (CRC32, framing helpers)
# 4) Artefacts presence after demo (if demo was executed)
#
# Usage
#   ./tests/smoke_test.sh           # full smoke test
#   ./tests/smoke_test.sh --quick   # syntax and utility checks only
#
# Default ports (Week 4): 5400, 5401 and 5402
# ==============================================================================

set -euo pipefail

QUICK=false
if [ "${1:-}" = "--quick" ]; then
  QUICK=true
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

ok()   { echo -e "${GREEN}[OK]${NC}   $1"; pass=$((pass+1)); }
bad()  { echo -e "${RED}[FAIL]${NC} $1"; fail=$((fail+1)); }
note() { echo -e "${YELLOW}[WARN]${NC} $1"; warn=$((warn+1)); }

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "Week 4 smoke test"
echo "============================================================"

# ------------------------------------------------------------------------------
# 1) Python availability
# ------------------------------------------------------------------------------
echo
echo "1) Python environment"
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import sys
print("Python:", sys.version.split()[0])
PY
  ok "python3 is available"
else
  bad "python3 is missing"
fi

# ------------------------------------------------------------------------------
# 2) Syntax checks
# ------------------------------------------------------------------------------
echo
echo "2) Python syntax checks (py_compile)"
py_compile() {
  local f="$1"
  if python3 -m py_compile "$f" >/dev/null 2>&1; then
    ok "Syntax OK: $f"
  else
    bad "Syntax error: $f"
  fi
}

py_compile python/utils/proto_common.py
py_compile python/apps/text_proto_server.py
py_compile python/apps/text_proto_client.py
py_compile python/apps/binary_proto_server.py
py_compile python/apps/binary_proto_client.py
py_compile python/apps/udp_sensor_server.py
py_compile python/apps/udp_sensor_client.py

# ------------------------------------------------------------------------------
# 3) Utility checks
# ------------------------------------------------------------------------------
echo
echo "3) Utility checks (CRC32, pack and unpack)"
if python3 - <<'PY'
import sys
sys.path.insert(0, "python/utils")
from proto_common import crc32, pack_udp_sensor, unpack_udp_sensor, encode_kv, decode_kv

data = b"Hello World"
expected = 0x4A17B156
actual = crc32(data)
assert actual == expected, f"CRC32 mismatch: {actual:08x} != {expected:08x}"

# UDP sensor pack and unpack round-trip
msg = pack_udp_sensor(sensor_id=1001, temp_c=23.5, location="Lab_A1")
seq, sensor_id, temp_c, location = unpack_udp_sensor(msg)
assert sensor_id == 1001
assert abs(temp_c - 23.5) < 1e-6
assert location == "Lab_A1"

# Key-value encoding round-trip
kv = encode_kv("name", "Alice")
k, v = decode_kv(kv)
assert (k, v) == ("name", "Alice")

print("PASS")
PY
then
  ok "CRC32 and framing utilities behave as expected"
else
  bad "CRC32 or framing utilities failed"
fi

# ------------------------------------------------------------------------------
# 4) Expected outputs reference
# ------------------------------------------------------------------------------
echo
echo "4) Documentation checks"
if [ -f tests/expected_outputs.md ]; then
  ok "tests/expected_outputs.md is present"
else
  bad "tests/expected_outputs.md is missing"
fi

# ------------------------------------------------------------------------------
# 5) Artefacts (if demo ran)
# ------------------------------------------------------------------------------
if [ "$QUICK" = false ]; then
  echo
  echo "5) Artefacts produced by demo (best effort)"
  if [ -f artifacts/demo.log ]; then
    lines="$(wc -l < artifacts/demo.log 2>/dev/null || echo 0)"
    if [ "${lines:-0}" -ge 20 ]; then
      ok "artifacts/demo.log exists and looks non-trivial ($lines lines)"
    else
      note "artifacts/demo.log exists but looks short ($lines lines)"
    fi
  else
    note "artifacts/demo.log is missing (run: ./scripts/run_all.sh)"
  fi

  if [ -f artifacts/validation.txt ]; then
    if grep -q "TEXT protocol: OK" artifacts/validation.txt 2>/dev/null \
      && grep -q "BINARY protocol: OK" artifacts/validation.txt 2>/dev/null \
      && grep -q "UDP sensor: OK" artifacts/validation.txt 2>/dev/null; then
      ok "artifacts/validation.txt contains the expected summary markers"
    else
      note "artifacts/validation.txt exists but markers are missing or incomplete"
    fi
  else
    note "artifacts/validation.txt is missing (run: ./scripts/run_all.sh)"
  fi

  if [ -f artifacts/demo.pcap ]; then
    ok "artifacts/demo.pcap exists (may be empty in --quick mode or without permissions)"
  else
    note "artifacts/demo.pcap is missing (capture may have been skipped)"
  fi
fi

echo
echo "------------------------------------------------------------"
echo "Summary: $pass passed, $warn warnings, $fail failed"
echo "------------------------------------------------------------"

if [ "$fail" -gt 0 ]; then
  exit 1
fi
exit 0
