#!/bin/bash
set -euo pipefail
set -euo pipefail
# =============================================================================
# capture.sh - Wrapper for capture_traffic.sh
# =============================================================================
# Pastrat for compatibilitate with scripts existente.
# Canonical: scripts/capture_traffic.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirectionare catre scriptul principal
exec "$SCRIPT_DIR/capture_traffic.sh" "$@"
