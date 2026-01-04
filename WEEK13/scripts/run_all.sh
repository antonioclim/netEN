#!/usr/bin/env bash
set -euo pipefail
# =============================================================================
# run_all.sh - Demo Automat Week 13 (IoT & Security)
# =============================================================================
# Produce:
#   - artifacts/demo.log        (log complete al demonstratiei)
#   - artifacts/demo.pcap       (capture traffic of network)
#   - artifacts/validation.txt  (results validation)
#
# Running without input interactive. Validat of tests/smoke_test.sh.
#
# Usage:
#   ./scripts/run_all.sh              # Demonstration completa
#   ./scripts/run_all.sh --quick      # Demonstration rapida (without Docker)
#   ./scripts/run_all.sh --mininet    # Demonstration Mininet (requires sudo)
#
# Licence: MIT
# Teaching Staff ASE-CSIE / Hypotheticalandrei & Rezolvix
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# CONSTANTE
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"

# Plan unitar of addresses - WEEK 13
WEEK=13
NETWORK="10.0.${WEEK}.0/24"
GATEWAY="10.0.${WEEK}.1"
HOST1="10.0.${WEEK}.11"
HOST2="10.0.${WEEK}.12"
HOST3="10.0.${WEEK}.13"
SERVER="10.0.${WEEK}.100"

# Plan unitar of ports
TCP_APP_PORT=9090
UDP_APP_PORT=9091
HTTP_PORT=8080
PROXY_PORT=8888
DNS_PORT=5353
FTP_PORT=2121
SSH_PORT=2222
MQTT_PORT=1883
MQTT_TLS_PORT=8883

# Ports specifice saptamanii (baza + 100*(WEEK-1))
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 6300
SCAN_RESULT_PORT=$((WEEK_PORT_BASE + 1))      # 6301

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variables of control
DEMO_MODE="quick"
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$DEMO_LOG"
}

log_info() {
    log "${CYAN}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[✓]${NC} $1"
}

log_warning() {
    log "${YELLOW}[!]${NC} $1"
}

log_error() {
    log "${RED}[✗]${NC} $1"
}

log_section() {
    echo "" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}  $1${NC}" | tee -a "$DEMO_LOG"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$DEMO_LOG"
    echo "" | tee -a "$DEMO_LOG"
}

cleanup_on_exit() {
    log_info "Cleanup at iesire..."
    # Stop eventuale processes of fundal
    pkill -f "tcpdump.*demo.pcap" 2>/dev/null || true
    pkill -f "tshark.*demo.pcap" 2>/dev/null || true
}

trap cleanup_on_exit EXIT

# -----------------------------------------------------------------------------
# INITIALIZARE
# -----------------------------------------------------------------------------

init_demo() {
    log_section "Initializare Demo S13"
    
    # Create directory artifacts
    mkdir -p "$ARTIFACTS_DIR"
    
    # Initializare files
    echo "# Demo Log - Week 13 IoT & Security" > "$DEMO_LOG"
    echo "# Inceput: $(date)" >> "$DEMO_LOG"
    echo "# Network: $NETWORK" >> "$DEMO_LOG"
    echo "" >> "$DEMO_LOG"
    
    echo "# Validation Results - S13" > "$VALIDATION_FILE"
    echo "# Generated: $(date)" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
    
    log_success "Directories and files initializate"
    log_info "Log: $DEMO_LOG"
    log_info "PCAP: $DEMO_PCAP"
    log_info "Validation: $VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# VERIFICATION DEPENDENTE
# -----------------------------------------------------------------------------

check_dependencies() {
    log_section "Verification Dependencies"
    
    local deps_ok=true
    
    # Python
    if command -v python3 &>/dev/null; then
        log_success "Python3: $(python3 --version 2>&1)"
        echo "PASS: Python3 available" >> "$VALIDATION_FILE"
    else
        log_error "Python3 is not installed"
        echo "FAIL: Python3 missing" >> "$VALIDATION_FILE"
        deps_ok=false
    fi
    
    # Python modules verification
    for modules in socket json concurrent.futures; do
        if python3 -c "import $modules" 2>/dev/null; then
            log_success "  Modules $modules: OK"
        else
            log_warning "  Modules $modules: Lipsa"
        fi
    done
    
    # Netcat
    if command -v nc &>/dev/null || command -v netcat &>/dev/null; then
        log_success "Netcat: disponibil"
        echo "PASS: Netcat available" >> "$VALIDATION_FILE"
    else
        log_warning "Netcat: not is disponibil"
        echo "WARN: Netcat missing" >> "$VALIDATION_FILE"
    fi
    
    # tcpdump/tshark for capture
    if command -v tcpdump &>/dev/null; then
        log_success "tcpdump: disponibil"
        echo "PASS: tcpdump available" >> "$VALIDATION_FILE"
    elif command -v tshark &>/dev/null; then
        log_success "tshark: disponibil"
        echo "PASS: tshark available" >> "$VALIDATION_FILE"
    else
        log_warning "tcpdump/tshark: not are disponibile (pcap va fi gol)"
        echo "WARN: No packet capture tool" >> "$VALIDATION_FILE"
    fi
    
    # nmap (optional)
    if command -v nmap &>/dev/null; then
        log_success "nmap: disponibil (optional)"
    else
        log_info "nmap: is not installed (folosim scanner Python)"
    fi
    
    echo "" >> "$VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# CAPTURA TRAFIC
# -----------------------------------------------------------------------------

start_capture() {
    log_info "Start capture traffic..."
    
    # Create pcap gol initial
    touch "$DEMO_PCAP"
    
    if command -v tcpdump &>/dev/null; then
        # Capture on loopback and all interfacesle
        sudo tcpdump -i any -w "$DEMO_PCAP" -c 1000 \
            "port $MQTT_PORT or port $HTTP_PORT or port $FTP_PORT or port $SSH_PORT or icmp" \
            2>/dev/null &
        CAPTURE_PID=$!
        log_success "tcpdump pornit (PID: $CAPTURE_PID)"
    elif command -v tshark &>/dev/null; then
        sudo tshark -i any -w "$DEMO_PCAP" -c 500 \
            -f "port $MQTT_PORT or port $HTTP_PORT or port $FTP_PORT" \
            2>/dev/null &
        CAPTURE_PID=$!
        log_success "tshark pornit (PID: $CAPTURE_PID)"
    else
        log_warning "Not se can porni captura (tcpdump/tshark lipsa)"
        CAPTURE_PID=""
        # Cream un pcap minimal valid (header pcap)
        printf '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > "$DEMO_PCAP"
    fi
}

stop_capture() {
    if [ -n "$CAPTURE_PID" ] && kill -0 "$CAPTURE_PID" 2>/dev/null; then
        log_info "Stop capture..."
        sudo kill "$CAPTURE_PID" 2>/dev/null || true
        sleep 1
    fi
    
    if [ -f "$DEMO_PCAP" ] && [ -s "$DEMO_PCAP" ]; then
        local pcap_size=$(stat -c%s "$DEMO_PCAP" 2>/dev/null || stat -f%z "$DEMO_PCAP" 2>/dev/null || echo "0")
        log_success "Capture saved: $DEMO_PCAP ($pcap_size bytes)"
        echo "PASS: PCAP generated ($pcap_size bytes)" >> "$VALIDATION_FILE"
    else
        # Asigurare pcap minimal valid
        printf '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > "$DEMO_PCAP"
        log_warning "Capture goala (traffic insuficient)"
        echo "WARN: Empty PCAP (minimal traffic)" >> "$VALIDATION_FILE"
    fi
}

# -----------------------------------------------------------------------------
# DEMONSTRATIONS SECURITATE
# -----------------------------------------------------------------------------

demo_port_scanner() {
    log_section "Demo 1: Scanner of Ports"
    
    local scanner="$PROJECT_DIR/python/exercises/ex_01_port_scanner.py"
    local scan_output="$ARTIFACTS_DIR/scan_results.json"
    
    if [ ! -f "$scanner" ]; then
        log_error "Scanner not exista: $scanner"
        echo "FAIL: Port scanner script missing" >> "$VALIDATION_FILE"
        return 1
    fi
    
    log_info "Scanning localhost (ports comune)..."
    
    # Scanning localhost on ports comune
    if python3 "$scanner" --target 127.0.0.1 --ports 22,80,443,8080,1883,3306 \
        --timeout 0.5 --workers 10 --json-out "$scan_output" >> "$DEMO_LOG" 2>&1; then
        log_success "Scanning completa"
        
        if [ -f "$scan_output" ]; then
            local open_ports=$(python3 -c "import json; d=json.load(open('$scan_output')); print(len([p for p in d.get('results',{}).values() if p.get('state')=='open']))" 2>/dev/null || echo "0")
            log_info "Ports opene gasite: $open_ports"
            echo "PASS: Port scan completed, found $open_ports open ports" >> "$VALIDATION_FILE"
        fi
    else
        log_warning "Scanning with errors (normal on systems without services)"
        echo "WARN: Port scan had issues (expected on minimal systems)" >> "$VALIDATION_FILE"
    fi
    
    # Test banner grabbing simple
    log_info "Test banner grabbing on SSH local..."
    local banner_grabber="$PROJECT_DIR/python/exploits/banner_grabber.py"
    if [ -f "$banner_grabber" ]; then
        timeout 5 python3 "$banner_grabber" --target 127.0.0.1 --port 22 >> "$DEMO_LOG" 2>&1 || true
    fi
}

demo_vulnerability_check() {
    log_section "Demo 2: Verification Vulnerabilities"
    
    local vuln_checker="$PROJECT_DIR/python/exercises/ex_04_vuln_checker.py"
    local vuln_output="$ARTIFACTS_DIR/vuln_report.json"
    
    if [ ! -f "$vuln_checker" ]; then
        log_warning "Vulnerability checker not exista, skip"
        echo "SKIP: Vulnerability checker not found" >> "$VALIDATION_FILE"
        return
    fi
    
    log_info "Verification vulnerabilities on localhost..."
    
    if python3 "$vuln_checker" --target 127.0.0.1 --quick \
        --output "$vuln_output" >> "$DEMO_LOG" 2>&1; then
        log_success "Verification complete"
        echo "PASS: Vulnerability check completed" >> "$VALIDATION_FILE"
    else
        log_warning "Verification partiala (unele services indisponibile)"
        echo "WARN: Partial vulnerability check" >> "$VALIDATION_FILE"
    fi
}

demo_packet_sniffer() {
    log_section "Demo 3: Packet Sniffer (conceptual)"
    
    local sniffer="$PROJECT_DIR/python/exercises/ex_03_packet_sniffer.py"
    
    if [ ! -f "$sniffer" ]; then
        log_warning "Packet sniffer not exista, skip"
        echo "SKIP: Packet sniffer not found" >> "$VALIDATION_FILE"
        return
    fi
    
    log_info "Verification sintaxa packet sniffer..."
    
    if python3 -m py_compile "$sniffer" 2>/dev/null; then
        log_success "Sintaxa valida: ex_03_packet_sniffer.py"
        echo "PASS: Packet sniffer syntax OK" >> "$VALIDATION_FILE"
    else
        log_error "Error sintaxa in packet sniffer"
        echo "FAIL: Packet sniffer syntax error" >> "$VALIDATION_FILE"
    fi
    
    # Note: runa efectiva a sniffer-ului necesita root and scapy
    log_info "Note: Runninga sniffer-ului necesita: sudo python3 $sniffer -i eth0"
}

demo_network_simulation() {
    log_section "Demo 4: Simulation Traffic of Network"
    
    log_info "Generation traffic of test on localhost..."
    
    # Ping local
    ping -c 3 127.0.0.1 >> "$DEMO_LOG" 2>&1 || true
    
    # Test connection TCP
    log_info "Test connections TCP..."
    for port in 22 80 443; do
        if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
            log_success "Port $port: open"
        else
            log_info "Port $port: closed/filtered"
        fi
    done
    
    echo "PASS: Network simulation completed" >> "$VALIDATION_FILE"
}

# -----------------------------------------------------------------------------
# VALIDARE FINALA
# -----------------------------------------------------------------------------

validate_results() {
    log_section "Validation Results"
    
    local all_ok=true
    
    # Verification demo.log
    if [ -f "$DEMO_LOG" ] && [ -s "$DEMO_LOG" ]; then
        local log_lines=$(wc -l < "$DEMO_LOG")
        log_success "demo.log: $log_lines linii"
        echo "PASS: demo.log exists ($log_lines lines)" >> "$VALIDATION_FILE"
    else
        log_error "demo.log: lipsa or gol"
        echo "FAIL: demo.log missing or empty" >> "$VALIDATION_FILE"
        all_ok=false
    fi
    
    # Verification demo.pcap
    if [ -f "$DEMO_PCAP" ]; then
        local pcap_size=$(stat -c%s "$DEMO_PCAP" 2>/dev/null || stat -f%z "$DEMO_PCAP" 2>/dev/null || echo "0")
        if [ "$pcap_size" -ge 24 ]; then
            log_success "demo.pcap: $pcap_size bytes"
            echo "PASS: demo.pcap exists ($pcap_size bytes)" >> "$VALIDATION_FILE"
        else
            log_warning "demo.pcap: prea mic ($pcap_size bytes)"
            echo "WARN: demo.pcap too small" >> "$VALIDATION_FILE"
        fi
    else
        log_error "demo.pcap: lipsa"
        echo "FAIL: demo.pcap missing" >> "$VALIDATION_FILE"
        all_ok=false
    fi
    
    # Verification validation.txt
    if [ -f "$VALIDATION_FILE" ] && [ -s "$VALIDATION_FILE" ]; then
        local pass_count=$(grep -c "^PASS:" "$VALIDATION_FILE" || echo "0")
        local fail_count=$(grep -c "^FAIL:" "$VALIDATION_FILE" || echo "0")
        local warn_count=$(grep -c "^WARN:" "$VALIDATION_FILE" || echo "0")
        
        echo "" >> "$VALIDATION_FILE"
        echo "# Summary" >> "$VALIDATION_FILE"
        echo "TOTAL_PASS: $pass_count" >> "$VALIDATION_FILE"
        echo "TOTAL_FAIL: $fail_count" >> "$VALIDATION_FILE"
        echo "TOTAL_WARN: $warn_count" >> "$VALIDATION_FILE"
        
        log_success "validation.txt: PASS=$pass_count, FAIL=$fail_count, WARN=$warn_count"
    fi
    
    echo "" >> "$VALIDATION_FILE"
    echo "# End: $(date)" >> "$VALIDATION_FILE"
    
    if [ "$all_ok" = true ] && [ "$fail_count" -eq 0 ]; then
        log_success "All validarile au trecut!"
        return 0
    else
        log_warning "Unele validari au failed (verificati $VALIDATION_FILE)"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║   DEMO AUTOMAT - Week 13: IoT & Security                  ║"
    echo "║   Computer Networks - ASE-CSIE                              ║"
    echo "║   Network: $NETWORK                                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --quick       Demonstration rapida (without Docker)"
    echo "  --full        Demonstration completa (necesita Docker)"
    echo "  --mininet     Demonstration Mininet (requires sudo)"
    echo "  --help        Afisare this message"
    echo ""
    echo "Output:"
    echo "  artifacts/demo.log        - Log demonstration"
    echo "  artifacts/demo.pcap       - Capture traffic"
    echo "  artifacts/validation.txt  - Results validation"
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                DEMO_MODE="quick"
                shift
                ;;
            --full)
                DEMO_MODE="full"
                shift
                ;;
            --mininet)
                DEMO_MODE="mininet"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log_warning "Option unknowna: $1"
                shift
                ;;
        esac
    done
    
    print_banner
    
    # Change in directorul proiectului
    cd "$PROJECT_DIR"
    
    # Initializare
    init_demo
    
    # Verification dependencies
    check_dependencies
    
    # Start capture
    start_capture
    
    # Running demonstrations
    demo_port_scanner
    demo_vulnerability_check
    demo_packet_sniffer
    demo_network_simulation
    
    # Stop capture
    stop_capture
    
    # Validation finala
    validate_results
    
    log_section "Demo Complete"
    log_success "Artefacte generate in: $ARTIFACTS_DIR/"
    log_info "Verification: ./tests/smoke_test.sh"
    
    echo ""
    echo "Files generate:"
    ls -at "$ARTIFACTS_DIR/" 2>/dev/null || true
}

main "$@"
