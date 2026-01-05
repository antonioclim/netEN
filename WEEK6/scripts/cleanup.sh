#!/bin/bash
# ============================================================================
# cleanup.sh - Cleanup completee a mediului dupa laborator
# Author: Revolvix&Hypotheticalandrei
# ============================================================================

set -euo pipefail

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "=============================================="
echo "  Cleanup - Week 6: NAT/PAT & SDN"
echo "=============================================="
echo ""

# Stopping SDN controller
cleanup_controller() {
    info "Stopping SDN controller..."
    
    pkill -f "osken-manager" 2>/dev/null && success "osken-manager oprit" || true
    pkill -f "ryu-manager" 2>/dev/null && success "ryu-manager oprit" || true
    pkill -f "sdn_policy_controller" 2>/dev/null || true
    
    # Verification port 6633
    if netstat -tlnp 2>/dev/null | grep -q ":6633"; then
        warn "Port 6633 inca ocupat, se forteaza eliberarea..."
        fuser -k 6633/tcp 2>/dev/null || true
    fi
}

# Cleaning Mininet
cleanup_mininet() {
    info "Cleaning Mininet..."
    
    # Cleanup standard Mininet
    sudo mn -c 2>/dev/null || true
    success "Mininet curatat"
    
    # Stopping procese Python din Mininet
    sudo pkill -9 -f "python.*topo_nat" 2>/dev/null || true
    sudo pkill -9 -f "python.*topo_sdn" 2>/dev/null || true
}

# Cleanup Open vSwitch
cleanup_ovs() {
    info "Cleanup Open vSwitch..."
    
    # Listare si stergere bridge-uri
    for br in $(sudo ovs-vsctl list-br 2>/dev/null); do
        sudo ovs-vsctl del-br "$br" 2>/dev/null && info "Sters bridge: $br"
    done
    
    # Reset OVS
    sudo ovs-vsctl --if-exists del-br s1 2>/dev/null || true
    sudo ovs-vsctl --if-exists del-br s2 2>/dev/null || true
    
    success "OVS curatat"
}

# Cleanup procese Python
cleanup_python() {
    info "Stopping procese Python din lab..."
    
    PATTERNS=(
        "nat_observer"
        "tcp_echo"
        "udp_echo"
        "sdn_policy"
    )
    
    for pattern in "${PATTERNS[@]}"; do
        pkill -f "$pattern" 2>/dev/null && info "Oprit: $pattern" || true
    done
}

# Cleanup reguli iptables NAT (doar cele adaugate de lab)
cleanup_iptables() {
    info "Cleanup reguli iptables temporare..."
    
    # Nu stergem tot, doar regulile specifice lab-ului
    # Regulile Mininet sunt in namespace-uri separate, deci nu afecteaza host-ul
    
    # Verification if sunt reguli MASQUERADE for retelele lab
    if sudo iptables -t nat -L POSTROUTING -n 2>/dev/null | grep -q "10.0.1.0/24"; then
        warn "Reguli NAT lab detectate in host (neobisnuit)"
        info "check manual cu: sudo iptables -t nat -L -n"
    fi
    
    success "iptables verificat"
}

# Cleaning temporary files
cleanup_temp_files() {
    info "Cleaning temporary files..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Cleanup capturi vechi (pastram ultimele)
    if [[ -d "$PROJECT_DIR/pcap" ]]; then
        find "$PROJECT_DIR/pcap" -name "*.pcap" -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Cleanup loguri vechi
    if [[ -d "$PROJECT_DIR/logs" ]]; then
        find "$PROJECT_DIR/logs" -name "*.log" -mtime +1 -delete 2>/dev/null || true
    fi
    
    # Files temporare sistem
    rm -f /tmp/pre_nat.pcap /tmp/post_nat.pcap 2>/dev/null || true
    rm -f /tmp/osken.log /tmp/controller.log 2>/dev/null || true
    
    success "Files temporare curatate"
}

# Cleanup interfete de retea virtuale
cleanup_network_interfaces() {
    info "Cleanup interfete virtuale..."
    
    # Stergere veth pairs create de Mininet
    for iface in $(ip link show 2>/dev/null | grep -oP 'veth\w+' | sort -u); do
        sudo ip link delete "$iface" 2>/dev/null && info "Sters: $iface" || true
    done
    
    # Stergere interfete h1-eth0, h2-eth0, etc.
    for iface in $(ip link show 2>/dev/null | grep -oP 'h\d+-eth\d+' | sort -u); do
        sudo ip link delete "$iface" 2>/dev/null && info "Sters: $iface" || true
    done
    
    success "Interfete virtuale curatate"
}

# Verification finala
verify_cleanup() {
    echo ""
    echo "=============================================="
    echo "  Verification Cleanup"
    echo "=============================================="
    
    # Verification procese
    if pgrep -f "osken-manager|ryu-manager" > /dev/null 2>&1; then
        warn "Controller SDN inca run"
    else
        success "Niciun controller SDN activ"
    fi
    
    # Checking Mininet
    if pgrep -f "mininet" > /dev/null 2>&1; then
        warn "Procese Mininet inca active"
    else
        success "Mininet oprit complet"
    fi
    
    # Verification OVS bridges
    BR_COUNT=$(sudo ovs-vsctl list-br 2>/dev/null | wc -l)
    if [[ $BR_COUNT -gt 0 ]]; then
        warn "$BR_COUNT bridge-uri OVS inca active"
    else
        success "Niciun bridge OVS activ"
    fi
    
    # Verification port 6633
    if netstat -tlnp 2>/dev/null | grep -q ":6633"; then
        warn "Port 6633 inca ocupat"
    else
        success "Port 6633 liber"
    fi
    
    echo "=============================================="
    success "Cleanup complete!"
    echo "=============================================="
}

# Functie principala
main() {
    cleanup_controller
    cleanup_mininet
    cleanup_ovs
    cleanup_python
    cleanup_iptables
    cleanup_temp_files
    cleanup_network_interfaces
    verify_cleanup
}

# running
main "$@"
