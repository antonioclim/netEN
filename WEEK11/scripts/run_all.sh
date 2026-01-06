#!/usr/bin/env bash
# Week 11: Automated demo runner (Docker + Nginx load balancing)
#
# What it does
#   1) Cleans previous artefacts and any Week 11 Docker containers
#   2) Starts the Nginx load balancer stack (3 backends)
#   3) Sends a small burst of requests and reports observed round-robin behaviour
#   4) Optionally captures traffic into artifacts/demo.pcap when capture permissions allow
#   5) Writes artifacts/demo.log and artifacts/validation.txt
#   6) Stops the stack so the environment remains clean
#
# Notes
#   - This script is designed to be run WITHOUT sudo.
#   - Packet capture requires elevated privileges. The script will only use sudo when
#     non-interactive sudo is available (sudo -n). Otherwise it will skip capture and
#     tell you how to generate a capture with make capture.

set -euo pipefail

CAPTURE_MODE="auto"   # auto | off
KEEP_CONTAINERS="0"   # 0 | 1

usage() {
  cat <<'USAGE'
Usage: scripts/run_all.sh [options]

Options
  --no-capture         Do not attempt any traffic capture (no demo.pcap)
  --keep-containers    Keep Docker containers running after completion
  -h, --help           Show this help

Notes
  - The default capture mode is 'auto': the script will attempt a capture when permitted.
  - If capture privileges are missing, the demo still runs and the PCAP may be empty.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --no-capture) CAPTURE_MODE="off" ;;
    --keep-containers) KEEP_CONTAINERS="1" ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done


ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTEFACTS_DIR="$ROOT_DIR/artifacts"
LOG_FILE="$ARTEFACTS_DIR/demo.log"
PCAP_FILE="$ARTEFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTEFACTS_DIR/validation.txt"

NGINX_PORT="8080"
NGINX_URL="http://127.0.0.1:${NGINX_PORT}/"
HEALTH_URL="http://127.0.0.1:${NGINX_PORT}/health"

ORIG_USER="${SUDO_USER:-$USER}"
ORIG_UID="$(id -u "$ORIG_USER" 2>/dev/null || echo 0)"
ORIG_GID="$(id -g "$ORIG_USER" 2>/dev/null || echo 0)"

# Console colours (terminal only)
NC='\033[0m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'

CAPTURE_PID=""
CAPTURE_TOOL=""
STACK_STARTED="0"

log() {
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S')"

  local colour="$NC"
  case "$level" in
    OK) colour="$GREEN";;
    INFO) colour="$BLUE";;
    WARN) colour="$YELLOW";;
    ERROR) colour="$RED";;
  esac

  # Console (coloured)
  echo -e "${colour}[${ts}] [${level}]${NC} ${msg}"
  # File (plain)
  echo "[${ts}] [${level}] ${msg}" >> "$LOG_FILE"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log ERROR "Missing required command: $cmd"
    exit 1
  fi
}

choose_docker_compose() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    echo "docker compose"
    return 0
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
    return 0
  fi
  return 1
}

docker_compose() {
  local dc="$1"; shift
  ( cd "$ROOT_DIR/docker/nginx_compose" && $dc "$@" )
}

force_down_stack() {
  local dc="$1"

  # Best effort
  docker_compose "$dc" down --remove-orphans >/dev/null 2>&1 || true

  # Hard fallback in case compose cannot stop containers cleanly
  for c in s11_nginx_lb s11_backend_1 s11_backend_2 s11_backend_3; do
    docker rm -f "$c" >/dev/null 2>&1 || true
  done
  docker network rm s11_net >/dev/null 2>&1 || true
}

start_capture() {
  # Capture is optional. We try a non-privileged capture first.
  # If that fails, we only use sudo when sudo -n is available.

  rm -f "$PCAP_FILE" 2>/dev/null || true

  local filter="tcp port ${NGINX_PORT}"
  local duration_seconds="20"

  if command -v tshark >/dev/null 2>&1; then
    # Try non-privileged capture
    if tshark -i any -f "$filter" -a duration:"$duration_seconds" -w "$PCAP_FILE" >/dev/null 2>&1 & then
      CAPTURE_PID="$!"
      CAPTURE_TOOL="tshark"
      log OK "Packet capture started with tshark (PID: $CAPTURE_PID)"
      return 0
    fi

    if sudo -n true >/dev/null 2>&1; then
      sudo tshark -i any -f "$filter" -a duration:"$duration_seconds" -w "$PCAP_FILE" >/dev/null 2>&1 &
      CAPTURE_PID="$!"
      CAPTURE_TOOL="sudo tshark"
      log OK "Packet capture started with sudo tshark (PID: $CAPTURE_PID)"
      return 0
    fi

    log WARN "tshark is installed but capture permissions are missing. Skipping capture."
    log WARN "To generate a capture manually: sudo make capture"
    return 0
  fi

  if command -v tcpdump >/dev/null 2>&1; then
    if tcpdump -i any -w "$PCAP_FILE" "tcp port ${NGINX_PORT}" >/dev/null 2>&1 & then
      CAPTURE_PID="$!"
      CAPTURE_TOOL="tcpdump"
      log OK "Packet capture started with tcpdump (PID: $CAPTURE_PID)"
      return 0
    fi

    if sudo -n true >/dev/null 2>&1; then
      sudo tcpdump -i any -w "$PCAP_FILE" "tcp port ${NGINX_PORT}" >/dev/null 2>&1 &
      CAPTURE_PID="$!"
      CAPTURE_TOOL="sudo tcpdump"
      log OK "Packet capture started with sudo tcpdump (PID: $CAPTURE_PID)"
      return 0
    fi

    log WARN "tcpdump is installed but capture permissions are missing. Skipping capture."
    log WARN "To generate a capture manually: sudo make capture"
    return 0
  fi

  log WARN "No capture tool available (tshark or tcpdump). Skipping capture."
}

stop_capture() {
  if [ -n "$CAPTURE_PID" ]; then
    log INFO "Stopping capture ($CAPTURE_TOOL, PID: $CAPTURE_PID)..."
    kill "$CAPTURE_PID" >/dev/null 2>&1 || true
    wait "$CAPTURE_PID" >/dev/null 2>&1 || true
    CAPTURE_PID=""
  fi

  # Ensure user can read the pcap even when capture was executed with sudo.
  if [ -f "$PCAP_FILE" ]; then
    sudo chown "$ORIG_UID:$ORIG_GID" "$PCAP_FILE" >/dev/null 2>&1 || true
  fi
}

cleanup_on_exit() {
  # Always attempt to stop capture. Containers are stopped unless --keep-containers was used.
  stop_capture || true

  if [ "$KEEP_CONTAINERS" != "1" ] && [ "$STACK_STARTED" = "1" ]; then
    local dc
    dc="$(choose_docker_compose 2>/dev/null || true)"
    if [ -n "$dc" ]; then
      force_down_stack "$dc" || true
    fi
  fi

  # Ensure the artefacts are readable by the invoking user
  sudo chown -R "$ORIG_UID:$ORIG_GID" "$ARTEFACTS_DIR" >/dev/null 2>&1 || true
}
trap cleanup_on_exit EXIT

mkdir -p "$ARTEFACTS_DIR"
: > "$LOG_FILE"

log INFO "Preparing artefacts directory: $ARTEFACTS_DIR"

# Dependencies
require_cmd curl

if ! command -v docker >/dev/null 2>&1; then
  log ERROR "Docker is not installed. Install Docker and try again."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  log ERROR "Docker daemon is not reachable. Check that the Docker service is running and your user has access."
  log ERROR "Tip: sudo usermod -aG docker $USER then log out and back in."
  exit 1
fi

DC_BIN="$(choose_docker_compose)"
log OK "Using Docker Compose: $DC_BIN"

log INFO "Cleaning previous configuration (Docker stack and temporary files)..."
"$ROOT_DIR/scripts/cleanup.sh" >/dev/null 2>&1 || true
force_down_stack "$DC_BIN" || true
log OK "Environment cleaned"

# Optional capture
if [ "$CAPTURE_MODE" = "off" ]; then
  log INFO "Traffic capture disabled (--no-capture)"
else
  start_capture
fi

log INFO "Starting Nginx load balancer demo stack on ${NGINX_URL}..."
docker_compose "$DC_BIN" up -d
STACK_STARTED="1"
log OK "Stack started"

log INFO "Waiting for ${NGINX_URL} to return HTTP 200..."
ready="0"
for i in $(seq 1 30); do
  code="$(curl -s -o /dev/null -w "%{http_code}" "$NGINX_URL" || true)"
  if [ "$code" = "200" ]; then
    ready="1"
    break
  fi
  sleep 1
done

if [ "$ready" != "1" ]; then
  log ERROR "Load balancer did not become ready (still not returning HTTP 200)."
  log ERROR "Last Nginx logs (tail):"
  docker_compose "$DC_BIN" logs --tail=80 nginx 2>/dev/null | tail -n 80 | while read -r l; do log WARN "$l"; done
  exit 1
fi

log OK "Load balancer is ready"

# Identify backend container IPs (best effort, used for nicer validation)
B1_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_1 2>/dev/null || true)"
B2_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_2 2>/dev/null || true)"
B3_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' s11_backend_3 2>/dev/null || true)"

log INFO "Backend IPs (Docker network): backend-1=${B1_IP:-unknown}, backend-2=${B2_IP:-unknown}, backend-3=${B3_IP:-unknown}"

hits_b1=0
hits_b2=0
hits_b3=0
hits_unknown=0

log INFO "Sending 12 requests and recording X-Served-By..."
for i in $(seq 1 12); do
  headers="$(curl -s -D - -o /dev/null "$NGINX_URL" || true)"
  status="$(echo "$headers" | head -n 1 | awk '{print $2}')"
  served_by="$(echo "$headers" | awk -F': ' 'tolower($1)=="x-served-by"{print $2}' | tr -d '\r')"
  body_first_line="$(curl -s "$NGINX_URL" | head -n 1 | tr -d '\r')"

  if [ "$status" != "200" ]; then
    log WARN "Request $i: HTTP $status (unexpected). served_by=${served_by:-n/a} body='${body_first_line}'"
  else
    log OK "Request $i: HTTP $status served_by=${served_by:-n/a} body='${body_first_line}'"
  fi

  case "$served_by" in
    "${B1_IP}:"*) hits_b1=$((hits_b1 + 1));;
    "${B2_IP}:"*) hits_b2=$((hits_b2 + 1));;
    "${B3_IP}:"*) hits_b3=$((hits_b3 + 1));;
    *) hits_unknown=$((hits_unknown + 1));;
  esac

  sleep 0.2
done

health="$(curl -s "$HEALTH_URL" || true)"
if echo "$health" | grep -qi "ok"; then
  log OK "Health endpoint: $health"
  health_ok="YES"
else
  log WARN "Health endpoint returned unexpected output: $health"
  health_ok="NO"
fi

# Finalise capture
stop_capture

pcap_ok="NO"
pcap_size="0"
if [ -f "$PCAP_FILE" ]; then
  pcap_size="$(stat -c%s "$PCAP_FILE" 2>/dev/null || echo 0)"
  if [ "$pcap_size" -gt 0 ]; then
    pcap_ok="YES"
    log OK "Capture saved: $PCAP_FILE (${pcap_size} bytes)"
  else
    log WARN "Capture file exists but is empty: $PCAP_FILE"
  fi
else
  # Create an explicit placeholder to avoid confusing missing artefacts
  : > "$PCAP_FILE"
  pcap_size="0"
  log WARN "No capture produced. Placeholder created: $PCAP_FILE"
fi

rr_ok="NO"
if [ "$hits_b1" -gt 0 ] && [ "$hits_b2" -gt 0 ] && [ "$hits_b3" -gt 0 ]; then
  rr_ok="YES"
fi

log INFO "Round-robin distribution: backend-1=$hits_b1, backend-2=$hits_b2, backend-3=$hits_b3, unknown=$hits_unknown"

# Write validation summary
{
  echo "NGINX_DEMO: PASS"
  echo "HEALTH_ENDPOINT_OK: $health_ok"
  echo "RR_BACKEND_1_HITS: $hits_b1"
  echo "RR_BACKEND_2_HITS: $hits_b2"
  echo "RR_BACKEND_3_HITS: $hits_b3"
  echo "RR_UNKNOWN_HITS: $hits_unknown"
  echo "RR_DISTRIBUTION_OK: $rr_ok"
  echo "PCAP_GENERATED: $pcap_ok"
  echo "PCAP_SIZE_BYTES: $pcap_size"
} > "$VALIDATION_FILE"

log OK "Validation written: $VALIDATION_FILE"
log OK "Demo log written: $LOG_FILE"
log OK "Run completed. The Docker stack will now be stopped."

# The EXIT trap performs stack teardown.
