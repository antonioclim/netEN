#!/bin/bash
set -euo pipefail
set -euo pipefail
# =============================================================================
# clean.sh - Wrapper for cleanup.sh
# =============================================================================
# Pastrat for compatibilitate with scripts existente.
# Canonical: scripts/cleanup.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirectionare catre scriptul principal
exec "$SCRIPT_DIR/cleanup.sh" "$@"
