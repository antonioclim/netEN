#!/bin/bash
# ovs_reset.sh — Complete Open vSwitch and Mininet reset
# Use when topologies hang at "Waiting for switches to connect"
#
# This script performs a deep cleanup of OVS bridges that remain
# registered in the OVS database after incomplete Mininet shutdowns.
# Standard 'mn -c' only cleans Linux interfaces but leaves OVS
# database entries intact, causing conflicts on next startup.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# Check root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo"
        echo "Usage: sudo $0"
        exit 1
    fi
}

# Kill all Mininet-related processes
kill_mininet_processes() {
    log_info "Stopping Mininet-related processes..."
    
    pkill -9 -f "python.*mininet" 2>/dev/null || true
    pkill -9 -f "python.*topo_5" 2>/dev/null || true
    pkill -9 -f "controller" 2>/dev/null || true
    pkill -9 -f "ovs-testcontroller" 2>/dev/null || true
    
    sleep 1
    log_success "Mininet processes terminated"
}

# Delete all OVS bridges
delete_ovs_bridges() {
    log_info "Removing OVS bridges..."
    
    # Get list of all bridges
    local bridges=$(ovs-vsctl list-br 2>/dev/null || echo "")
    
    if [[ -z "$bridges" ]]; then
        log_info "No OVS bridges found"
        return
    fi
    
    # Delete each bridge
    for br in $bridges; do
        log_info "  Deleting bridge: $br"
        ovs-vsctl --if-exists del-br "$br" 2>/dev/null || true
    done
    
    log_success "OVS bridges removed"
}

# Run standard Mininet cleanup
mininet_cleanup() {
    log_info "Running Mininet cleanup (mn -c)..."
    mn -c 2>/dev/null || true
    log_success "Mininet cleanup complete"
}

# Restart Open vSwitch service
restart_ovs() {
    log_info "Restarting Open vSwitch service..."
    
    systemctl restart openvswitch-switch 2>/dev/null || \
    service openvswitch-switch restart 2>/dev/null || \
    /etc/init.d/openvswitch-switch restart 2>/dev/null || {
        log_warn "Could not restart OVS via systemctl/service"
        log_info "Attempting manual OVS restart..."
        ovs-appctl exit --cleanup 2>/dev/null || true
        sleep 1
    }
    
    sleep 3
    log_success "Open vSwitch restarted"
}

# Verify clean state
verify_clean() {
    log_info "Verifying clean state..."
    
    local bridges=$(ovs-vsctl list-br 2>/dev/null || echo "")
    
    if [[ -z "$bridges" ]]; then
        log_success "OVS is clean (no bridges)"
    else
        log_warn "Remaining bridges: $bridges"
        log_warn "Manual intervention may be required"
        return 1
    fi
    
    # Show OVS status
    echo ""
    log_info "Current OVS status:"
    ovs-vsctl show
    echo ""
    
    return 0
}

# Show usage
show_usage() {
    cat << EOF
Usage: sudo $0 [OPTIONS]

Complete reset of Open vSwitch and Mininet environment.
Use when topologies hang at "Waiting for switches to connect".

Options:
  -h, --help     Show this help message
  -q, --quiet    Minimal output
  -v, --verify   Only verify current state (no changes)

What this script does:
  1. Kills all Mininet-related processes
  2. Deletes all OVS bridges from database
  3. Runs standard Mininet cleanup (mn -c)
  4. Restarts Open vSwitch service
  5. Verifies clean state

After running this script, you can start topologies normally:
  sudo python3 mininet/topologies/topo_5_base.py --cli

EOF
}

# Main execution
main() {
    local quiet=false
    local verify_only=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -v|--verify)
                verify_only=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    check_root
    
    if $verify_only; then
        verify_clean
        exit $?
    fi
    
    echo ""
    echo "================================================"
    echo "  OVS & Mininet Complete Reset"
    echo "================================================"
    echo ""
    
    kill_mininet_processes
    delete_ovs_bridges
    mininet_cleanup
    restart_ovs
    
    echo ""
    if verify_clean; then
        echo "================================================"
        log_success "Reset complete! Environment is ready."
        echo "================================================"
        echo ""
        echo "You can now start topologies:"
        echo "  sudo python3 mininet/topologies/topo_5_base.py --cli"
        echo ""
    else
        echo "================================================"
        log_warn "Reset completed with warnings. Check status above."
        echo "================================================"
        exit 1
    fi
}

main "$@"
