#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

usage() {
  echo "Usage: $0 start|stop [IFACE=any] [CAPTURE_FILE=artifacts/capture.pcap]"
}

cmd="${1:-}"
shift || true

case "${cmd}" in
  start)
    exec make capture-start "$@"
    ;;
  stop)
    exec make capture-stop "$@"
    ;;
  *)
    usage
    exit 2
    ;;
esac
