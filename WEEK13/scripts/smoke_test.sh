#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

banner() {
  printf "\n========================================================================\n"
  printf "  %s\n" "$1"
  printf "========================================================================\n"
}

require_file() {
  local rel="$1"
  if [ -f "${ROOT_DIR}/${rel}" ]; then
    printf "  ✓ %s\n" "${rel}"
  else
    printf "  ✗ %s (missing)\n" "${rel}"
    return 1
  fi
}

require_dir() {
  local rel="$1"
  if [ -d "${ROOT_DIR}/${rel}" ]; then
    printf "  ✓ %s/\n" "${rel}"
  else
    printf "  ✗ %s/ (missing)\n" "${rel}"
    return 1
  fi
}

banner "Week 13 - Smoke test (non-destructive)"

fail=0

printf "\nStructure:\n"
require_file "Makefile" || fail=1
require_file "README.md" || fail=1
require_file "requirements.txt" || fail=1
require_file ".gitignore" || true
require_dir "python" || fail=1
require_dir "docker" || fail=1
require_dir "configs" || fail=1
require_dir "scripts" || fail=1

printf "\nKey scripts:\n"
require_file "scripts/verify.sh" || fail=1
require_file "scripts/run_all.sh" || fail=1
require_file "scripts/generate_env.sh" || fail=1
require_file "docker/docker-compose.yml" || fail=1

printf "\nMakefile targets (basic check):\n"
for tgt in setup verify docker-up docker-down scan demo-offensive demo-defensive demo-mqtt-plain demo-mqtt-tls exploit-ftp run-all; do
  if grep -Eq "^${tgt}:" "${ROOT_DIR}/Makefile"; then
    printf "  ✓ %s\n" "${tgt}"
  else
    printf "  ✗ %s (missing)\n" "${tgt}"
    fail=1
  fi
done

printf "\nPython syntax (compileall):\n"
if python3 -m compileall -q "${ROOT_DIR}/python" >/dev/null 2>&1; then
  printf "  ✓ compileall\n"
else
  printf "  ✗ compileall\n"
  fail=1
fi

printf "\nResult:\n"
if [ "${fail}" -eq 0 ]; then
  printf "  ✓ Smoke test passed\n\n"
else
  printf "  ✗ Smoke test failed\n\n"
  exit 1
fi
