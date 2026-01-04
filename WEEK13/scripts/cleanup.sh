#!/bin/bash
set -euo pipefail
set -euo pipefail
# ============================================================================
# cleanup.sh - Script of cleanup for laboratorul S13
# ============================================================================
# Clean all resursele create in timpul laboratorului:
# - Containere Docker
# - Processes Mosquitto
# - Sessions Mininet
# - Files temporare
# - Cache and loguri
#
# Author: Colectivul of Tehnologii Web, ASE-CSIE
# ============================================================================

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TMP_DIR="/tmp/s13_lab"
EVIDENCE_DIR="$PROJECT_DIR/evidence"

# Flags
FORCE=false
DOCKER=true
MININET=true
PROCESSES=true
TEMP_FILES=true
LOGS=false
CERTS=false

# ============================================================================
# Functions of utilitate
# ============================================================================

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           S13 Lab Cleanup Script                               ║"
    echo "║           Computer Networks - ASE-CSIE                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm_action() {
    if [ "$FORCE" = true ]; then
        return 0
    fi
    
    read -p "Are you sure you want to proceed? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# ============================================================================
# Functions of cleanup
# ============================================================================

cleanup_docker() {
    log_info "Cleaning up Docker containers..."
    
    # Stop containere from docker-compose
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        cd "$PROJECT_DIR"
        docker-compose down -v 2>/dev/null || true
    fi
    
    # Stop containere individuale (if exista)
    local containers="dvwa webgoat vsftpd mosquitto attacker"
    for container in $containers; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            log_info "  Stopping container: $container"
            docker stop "$container" 2>/dev/null || true
            docker rm "$container" 2>/dev/null || true
        fi
    done
    
    # Cleanup imagini nefolosite (optional with --deep)
    if [ "$DEEP_CLEAN" = true ]; then
        log_info "  Removing unused Docker images..."
        docker image prune -f 2>/dev/null || true
    fi
    
    # Cleanup networks Docker orfane
    local networks=$(docker network ls --format '{{.Name}}' | grep -E "s13|starterkit" || true)
    for network in $networks; do
        log_info "  Removing network: $network"
        docker network rm "$network" 2>/dev/null || true
    done
    
    log_info "Docker cleanup complete"
}

cleanup_mininet() {
    log_info "Cleaning up Mininet..."
    
    # Verification if Mininet is instalat
    if ! command -v mn &> /dev/null; then
        log_warn "Mininet not installed, skipping..."
        return 0
    fi
    
    # Cleanup standard Mininet
    sudo mn -c 2>/dev/null || true
    
    # Stop Open vSwitch controllers
    sudo pkill -f "controller" 2>/dev/null || true
    sudo pkill -f "ovs-controller" 2>/dev/null || true
    
    # Cleanup switch-uri OVS
    for ovs in $(sudo ovs-vsctl list-br 2>/dev/null || true); do
        log_info "  Removing OVS bridge: $ovs"
        sudo ovs-vsctl del-br "$ovs" 2>/dev/null || true
    done
    
    # Cleanup interfaces virtuale
    for iface in $(ip link show 2>/dev/null | grep -oP 's\d+-eth\d+' || true); do
        log_info "  Removing interface: $iface"
        sudo ip link delete "$iface" 2>/dev/null || true
    done
    
    log_info "Mininet cleanup complete"
}

cleanup_processes() {
    log_info "Cleaning up running processes..."
    
    # Lista of processes of oprit
    local processes=(
        "mosquitto"
        "tcpdump"
        "tshark"
        "ex_01_port_scanner"
        "ex_02_mqtt_client"
        "ex_03_packet_sniffer"
        "ex_04_vuln_checker"
        "ftp_backdoor"
        "banner_grabber"
        "report_generator"
    )
    
    for proc in "${processes[@]}"; do
        local pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_info "  Stopping process: $proc (PIDs: $pids)"
            sudo pkill -f "$proc" 2>/dev/null || true
        fi
    done
    
    # Asteptare for terminare gratioasa
    sleep 1
    
    # Force kill if inca exista
    for proc in "${processes[@]}"; do
        local pids=$(pgrep -f "$proc" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            log_warn "  Force killing: $proc"
            sudo pkill -9 -f "$proc" 2>/dev/null || true
        fi
    done
    
    log_info "Process cleanup complete"
}

cleanup_temp_files() {
    log_info "Cleaning up temporary files..."
    
    # Directories temporare
    local temp_dirs=(
        "$TMP_DIR"
        "/tmp/mqtt_*"
        "/tmp/scan_*"
        "/tmp/capture_*"
        "/tmp/evidence_*"
    )
    
    for dir in "${temp_dirs[@]}"; do
        if ls $dir 2>/dev/null 1>&2; then
            log_info "  Removing: $dir"
            rm -rf $dir 2>/dev/null || true
        fi
    done
    
    # Files temporare in project dir
    if [ -d "$PROJECT_DIR" ]; then
        find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true
        find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$PROJECT_DIR" -name "*.log" -delete 2>/dev/null || true
        find "$PROJECT_DIR" -name "*.pcap" -delete 2>/dev/null || true
    fi
    
    log_info "Temporary files cleanup complete"
}

cleanup_logs() {
    log_info "Cleaning up logs..."
    
    # Loguri Mosquitto
    if [ -d "/var/log/mosquitto" ]; then
        log_info "  Clearing Mosquitto logs"
        sudo rm -f /var/log/mosquitto/*.log 2>/dev/null || true
    fi
    
    # Loguri locale
    if [ -d "$PROJECT_DIR/logs" ]; then
        log_info "  Clearing project logs"
        rm -rf "$PROJECT_DIR/logs"/* 2>/dev/null || true
    fi
    
    log_info "Logs cleanup complete"
}

cleanup_certificates() {
    log_info "Cleaning up certificates..."
    
    local cert_dirs=(
        "$PROJECT_DIR/configs/certs"
        "/etc/mosquitto/certs"
    )
    
    for dir in "${cert_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_warn "  Removing certificates from: $dir"
            rm -f "$dir"/*.crt "$dir"/*.key "$dir"/*.csr "$dir"/*.srl 2>/dev/null || true
        fi
    done
    
    log_info "Certificateses cleanup complete"
}

cleanup_evidence() {
    log_info "Cleaning up evidence directory..."
    
    if [ -d "$EVIDENCE_DIR" ]; then
        if confirm_action; then
            rm -rf "$EVIDENCE_DIR"/*
            log_info "Evidence directory cleared"
        else
            log_warn "Skipping evidence cleanup"
        fi
    fi
}

# ============================================================================
# Checkri post-cleanup
# ============================================================================

verify_cleanup() {
    log_info "Verifying cleanup..."
    
    local issues=0
    
    # Docker verification
    local running=$(docker ps -q 2>/dev/null | wc -l)
    if [ "$running" -gt 0 ]; then
        log_warn "  $running Docker containers still running"
        ((issues++))
    else
        log_info "  ✓ No Docker containers running"
    fi
    
    # Verification processes
    for proc in mosquitto tcpdump; do
        if pgrep -f "$proc" &>/dev/null; then
            log_warn "  Process still running: $proc"
            ((issues++))
        fi
    done
    
    # Verification ports
    for port in 21 80 1883 8080 8883; do
        if ss -tulpn 2>/dev/null | grep -q ":$port "; then
            log_warn "  Port $port still in use"
            ((issues++))
        fi
    done
    
    if [ "$issues" -eq 0 ]; then
        log_info "  ✓ All resources cleaned successsfully"
    else
        log_warn "  $issues issues found, may require manual cleanup"
    fi
}

# ============================================================================
# Help and parsare arguments
# ============================================================================

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Cleanup script for Week 13 Lab environment"
    echo ""
    echo "Options:"
    echo "  -f, --force       Skip confirmation prompts"
    echo "  -a, --all         Clean everything (including certs and logs)"
    echo "  --docker          Clean only Docker resources"
    echo "  --mininet         Clean only Mininet resources"
    echo "  --processes       Kill only running processes"
    echo "  --temp            Clean only temporary files"
    echo "  --logs            Clean log files"
    echo "  --certs           Remove generated certificates"
    echo "  --deep            Deep clean (remove unused Docker images)"
    echo "  --verify          Only verify current state, don't clean"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Standard cleanup"
    echo "  $0 -f --all       # Full cleanup without prompts"
    echo "  $0 --docker       # Only cleanup Docker"
    echo "  $0 --verify       # Check what's running"
}

parse_args() {
    SELECTIVE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                FORCE=true
                shift
                ;;
            -a|--all)
                LOGS=true
                CERTS=true
                shift
                ;;
            --docker)
                SELECTIVE=true
                DOCKER=true
                MININET=false
                PROCESSES=false
                TEMP_FILES=false
                shift
                ;;
            --mininet)
                SELECTIVE=true
                DOCKER=false
                MININET=true
                PROCESSES=false
                TEMP_FILES=false
                shift
                ;;
            --processes)
                SELECTIVE=true
                DOCKER=false
                MININET=false
                PROCESSES=true
                TEMP_FILES=false
                shift
                ;;
            --temp)
                SELECTIVE=true
                DOCKER=false
                MININET=false
                PROCESSES=false
                TEMP_FILES=true
                shift
                ;;
            --logs)
                LOGS=true
                shift
                ;;
            --certs)
                CERTS=true
                shift
                ;;
            --deep)
                DEEP_CLEAN=true
                shift
                ;;
            --verify)
                VERIFY_ONLY=true
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
    print_banner
    parse_args "$@"
    
    # Only verification
    if [ "$VERIFY_ONLY" = true ]; then
        verify_cleanup
        exit 0
    fi
    
    echo -e "${YELLOW}This will clean up the lab environment.${NC}"
    echo ""
    
    if ! confirm_action; then
        log_info "Cleanup cancelled"
        exit 0
    fi
    
    echo ""
    
    # Execution cleanup
    [ "$DOCKER" = true ] && cleanup_docker
    [ "$MININET" = true ] && cleanup_mininet
    [ "$PROCESSES" = true ] && cleanup_processes
    [ "$TEMP_FILES" = true ] && cleanup_temp_files
    [ "$LOGS" = true ] && cleanup_logs
    [ "$CERTS" = true ] && cleanup_certificates
    
    echo ""
    verify_cleanup
    
    echo ""
    log_info "Cleanup complete!"
    echo -e "${GREEN}Environment is ready for fresh start.${NC}"
}

# Rulare
main "$@"
