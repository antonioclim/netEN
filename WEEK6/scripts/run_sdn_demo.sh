#!/bin/bash
# ============================================================================
# run_sdn_demo.sh - Starting demonstration SDN cu OpenFlow
# Author: Revolvix and contributors
# ============================================================================

set -euo pipefail

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
header() { echo -e "${CYAN}$1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Banner
clear
header "╔══════════════════════════════════════════════════════════╗"
header "║      SDN Demo - Week 6                             ║"
header "║      Software-Defined Networking cu OpenFlow             ║"
header "╚══════════════════════════════════════════════════════════╝"
echo ""

# Verification privilegii
if [[ $EUID -ne 0 ]]; then
    error "This script requires root privileges. Run with: sudo $0"
fi

# Functie pre-cleanup
pre_cleanup() {
    info "Cleaning previous configuration..."
    mn -c 2>/dev/null || true
    pkill -9 -f "topo_sdn.py" 2>/dev/null || true
    pkill -f "python3 -m os_ken.cmd.manager" 2>/dev/null || true
    pkill -f "ryu-manager" 2>/dev/null || true
    
    # Eliberare port 6633
    fuser -k 6633/tcp 2>/dev/null || true
    
    sleep 2
    success "Environment pregatit"
}

# Verification files requirede
check_files() {
    info "Verification files..."
    
    TOPO_FILE="$PROJECT_DIR/seminar/mininet/topologies/topo_sdn.py"
    CONTROLLER_FILE="$PROJECT_DIR/seminar/python/controllers/sdn_policy_controller.py"
    
    if [[ ! -f "$TOPO_FILE" ]]; then
        error "Lipseste: $TOPO_FILE"
    fi
    
    if [[ ! -f "$CONTROLLER_FILE" ]]; then
        error "Lipseste: $CONTROLLER_FILE"
    fi
    
    success "Files gasite"
}

# Verification OS-Ken instalat
check_osken() {
    info "Verification OS-Ken SDN controller..."
    
    if command -v python3 -m os_ken.cmd.manager &> /dev/null; then
        success "python3 -m os_ken.cmd.manager available"
        return 0
    elif command -v ryu-manager &> /dev/null; then
        warn "python3 -m os_ken.cmd.manager nu e available, se foloseste ryu-manager"
        export SDN_MANAGER="ryu-manager"
        return 0
    else
        error "Niciun controller SDN gasit. install cu: pip3 install os-ken"
    fi
}

# Afisare topologie
show_topology() {
    echo ""
    header "┌─────────────────────────────────────────────────────────┐"
    header "│                   TOPOLOGIE SDN                         │"
    header "├─────────────────────────────────────────────────────────┤"
    echo "│                                                         │"
    echo "│              ┌─────────────────────┐                    │"
    echo "│              │   SDN Controller    │                    │"
    echo "│              │     (OS-Ken)        │                    │"
    echo "│              │    port 6633        │                    │"
    echo "│              └─────────┬───────────┘                    │"
    echo "│                        │ OpenFlow 1.3                   │"
    echo "│                        ▼                                │"
    echo "│              ┌─────────────────────┐                    │"
    echo "│              │    OVS Switch (s1)  │                    │"
    echo "│              └─────────────────────┘                    │"
    echo "│                /       |       \\                        │"
    echo "│               /        |        \\                       │"
    echo "│         ┌────┐    ┌────┐    ┌────┐                      │"
    echo "│         │ h1 │    │ h2 │    │ h3 │                      │"
    echo "│         │.1  │    │.2  │    │.3  │                      │"
    echo "│         └────┘    └────┘    └────┘                      │"
    echo "│                                                         │"
    header "├─────────────────────────────────────────────────────────┤"
    echo "│  Policies:                                              │"
    echo -e "│    ${GREEN}✓ h1 ↔ h2${NC}: PERMIT                                  │"
    echo -e "│    ${RED}✗ * → h3${NC} : DROP (default)                         │"
    echo -e "│    ${YELLOW}? UDP → h3${NC}: Configurabil (ALLOW_UDP_TO_H3)         │"
    header "└─────────────────────────────────────────────────────────┘"
    echo ""
}

# Starting controller in background
start_controller() {
    info "Starting SDN controller in background..."
    
    CONTROLLER_FILE="$PROJECT_DIR/seminar/python/controllers/sdn_policy_controller.py"
    LOG_FILE="/tmp/osken_controller.log"
    
    # Determinare manager
    if [[ -n "$SDN_MANAGER" ]]; then
        MANAGER="$SDN_MANAGER"
    else
        MANAGER="python3 -m os_ken.cmd.manager"
    fi
    
    # Starting in background
    nohup $MANAGER "$CONTROLLER_FILE" > "$LOG_FILE" 2>&1 &
    CONTROLLER_PID=$!
    
    echo "$CONTROLLER_PID" > /tmp/sdn_controller.pid
    
    # Asteptare pornire
    sleep 3
    
    # Verification ca run
    if kill -0 $CONTROLLER_PID 2>/dev/null; then
        success "Controller started (PID: $CONTROLLER_PID)"
        info "Log: $LOG_FILE"
    else
        error "Controller-ul nu a pornit. check $LOG_FILE"
    fi
}

# Starting topologie
start_topology() {
    info "Starting SDN topology..."
    
    TOPO_FILE="$PROJECT_DIR/seminar/mininet/topologies/topo_sdn.py"
    
    echo ""
    header "═══════════════════════════════════════════════════════════"
    header "  MININET CLI - Useful commands:"
    header "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  📡 Test politici:"
    echo -e "     ${GREEN}h1 ping -c 2 10.0.6.12${NC}     # Ar trebui sa functioneze"
    echo -e "     ${RED}h1 ping -c 2 -W 2 10.0.6.13${NC} # Ar trebui sa esueze (DROP)"
    echo ""
    echo "  📊 Inspectare flow table:"
    echo "     sh sudo ovs-ofctl dump-flows s1"
    echo ""
    echo "  🔍 Verification conexiune controller:"
    echo "     sh sudo ovs-vsctl show"
    echo ""
    echo "  🖥️ Test UDP (if ALLOW_UDP_TO_H3=True):"
    echo "     h3 python3 $PROJECT_DIR/seminar/python/apps/udp_echo.py server --port 9091 &"
    echo "     h1 python3 $PROJECT_DIR/seminar/python/apps/udp_echo.py client --dst 10.0.6.13 --port 9091"
    echo ""
    echo "  📝 Log controller:"
    echo "     sh tail -f /tmp/osken_controller.log"
    echo ""
    echo "  🚪 Iesire: exit"
    echo ""
    header "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Starting Mininet cu topologia
    python3 "$TOPO_FILE" --cli
}

# Cleanup la iesire
cleanup_on_exit() {
    info "Stopping controller..."
    
    if [[ -f /tmp/sdn_controller.pid ]]; then
        PID=$(cat /tmp/sdn_controller.pid)
        kill $PID 2>/dev/null || true
        rm -f /tmp/sdn_controller.pid
    fi
    
    pkill -f "python3 -m os_ken.cmd.manager" 2>/dev/null || true
    pkill -f "ryu-manager" 2>/dev/null || true
}

# Trap for cleanup
trap cleanup_on_exit EXIT

# Functie principala
main() {
    pre_cleanup
    check_files
    check_osken
    show_topology
    start_controller
    start_topology
}

# running
main "$@"
