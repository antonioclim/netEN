#!/usr/bin/env bash
#==============================================================================
# run_all.sh – Automated demo for Week 10 (Network services in containers)
# 
# Runs without input interactiv, produce:
#   - artifacts/demo.log       (log complet al exewithtioni)
#   - artifacts/demo.pcap      (capture trafic)
#   - artifacts/validation.txt (verification automata)
#
# Computer Networks, ASE Bucharest 2025-2026
# Revolvix and HypotheticalAndrei | Licence MIT
#==============================================================================
set -uo pipefail  # Continuam la erori pentru a colecta toate rezultatele

#------------------------------------------------------------------------------
# Constants and paths
#------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$ROOT_DIR/docker"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

# Week-specific constants
WEEK=10
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 6000 pentru Week 10

# Porturi services (conform plan unitar)
DNS_PORT=5353
SSH_PORT=2222
FTP_PORT=2121
HTTP_PORT=8000
PROXY_PORT=8888

# Timestamps
TS=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$ARTIFACTS_DIR/demo.log"
PCAP_FILE="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Colours (for log vizibil)
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

#------------------------------------------------------------------------------
# Functii logging
#------------------------------------------------------------------------------
log() {
    local level="$1"
    shift
    local msg="[$(date '+%H:%M:%S')] [$level] $*"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

log_info()  { log "INFO" "${GREEN}$*${NC}"; }
log_warn()  { log "WARN" "${YELLOW}$*${NC}"; }
log_error() { log "ERROR" "${RED}$*${NC}"; }
log_step()  { log "STEP" "${BLUE}$*${NC}"; }

#------------------------------------------------------------------------------
# Verifytion prerequisite
#------------------------------------------------------------------------------
check_prerequisites() {
    log_step "Verifyre prerequisite..."
    
    local errors=0
    
    if ! command -v docker &>/dev/null; then
        log_error "Docker nu este instalat"
        ((errors++))
    fi
    
    if ! docker compose version &>/dev/null 2>&1; then
        log_error "Docker Compose nu este disponibil"
        ((errors++))
    fi
    
    if ! docker info &>/dev/null 2>&1; then
        log_error "Docker daemon nu ruleaza"
        ((errors++))
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Prerequisite lipsa: $errors erori"
        return 1
    fi
    
    log_info "Toate prerequisitele sunt indeplinite"
    return 0
}

#------------------------------------------------------------------------------
# Setup artefacts
#------------------------------------------------------------------------------
setup_artifacts() {
    log_step "Preparation directoare artefacts..."
    
    mkdir -p "$ARTIFACTS_DIR"
    
    # Curata artefacts vechi
    rm -f "$LOG_FILE" "$PCAP_FILE" "$VALIDATION_FILE" 2>/dev/null || true
    
    # Initializare log
    echo "# Demo Log - Saptamana 10" > "$LOG_FILE"
    echo "# Timestamp: $(date)" >> "$LOG_FILE"
    echo "# Porturi: DNS=$DNS_PORT SSH=$SSH_PORT FTP=$FTP_PORT HTTP=$HTTP_PORT" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    log_info "Artefacts pregatite in $ARTIFACTS_DIR/"
}

#------------------------------------------------------------------------------
# Pornire infrastructure Docker
#------------------------------------------------------------------------------
start_docker_services() {
    log_step "Pornire infrastructure Docker..."
    
    cd "$DOCKER_DIR"
    
    # Oprire eventuala existenta
    docker compose down --remove-orphans 2>/dev/null || true
    
    # Build and start
    log_info "Building images..."
    if docker compose build --quiet 2>>"$LOG_FILE"; then
        log_info "Build complet"
    else
        log_warn "Build cu warnings"
    fi
    
    log_info "Starting containers..."
    if docker compose up -d 2>>"$LOG_FILE"; then
        log_info "Containere pornite"
    else
        log_error "Eroare la pornire containere"
        return 1
    fi
    
    # Asteptare for healthy
    log_info "Asteptare services sa devina healthy (max 60s)..."
    local attempts=0
    local max_attempts=12
    
    while [ $attempts -lt $max_attempts ]; do
        local healthy_count
        healthy_count=$(docker compose ps --format json 2>/dev/null | grep -c '"healthy"' || echo "0")
        
        if [ "$healthy_count" -ge 3 ]; then
            log_info "Services healthy: $healthy_count"
            break
        fi
        
        sleep 5
        ((attempts++))
        log_info "Attempt $attempts/$max_attempts - healthy: $healthy_count"
    done
    
    # Status final
    docker compose ps 2>&1 | tee -a "$LOG_FILE"
    
    cd "$ROOT_DIR"
    return 0
}

#------------------------------------------------------------------------------
# Captura trafic in background
#------------------------------------------------------------------------------
start_capture() {
    log_step "Pornire capture trafic..."
    
    # Verifytion tshark/tcpdump
    if command -v tshark &>/dev/null; then
        log_info "Utilizare tshark pentru capture"
        tshark -i any -f "tcp port $HTTP_PORT or tcp port $SSH_PORT or tcp port $FTP_PORT or udp port $DNS_PORT" \
            -w "$PCAP_FILE" -a duration:120 &>/dev/null &
        CAPTURE_PID=$!
        log_info "Captura pornita (PID: $CAPTURE_PID)"
    elif command -v tcpdump &>/dev/null; then
        log_info "Utilizare tcpdump pentru capture"
        sudo tcpdump -i any -nn \
            "tcp port $HTTP_PORT or tcp port $SSH_PORT or tcp port $FTP_PORT or udp port $DNS_PORT" \
            -w "$PCAP_FILE" -c 1000 &>/dev/null &
        CAPTURE_PID=$!
        log_info "Captura pornita (PID: $CAPTURE_PID)"
    else
        log_warn "tshark/tcpdump indisponibil - capture omisa"
        CAPTURE_PID=""
        # Creaza file placeholder
        touch "$PCAP_FILE"
    fi
}

stop_capture() {
    if [ -n "${CAPTURE_PID:-}" ]; then
        log_info "Oprire capture (PID: $CAPTURE_PID)..."
        kill "$CAPTURE_PID" 2>/dev/null || true
        sleep 1
    fi
}

#------------------------------------------------------------------------------
# Test DNS
#------------------------------------------------------------------------------
test_dns() {
    log_step "═══════════════════════════════════════"
    log_step "         TEST DNS SERVER"
    log_step "═══════════════════════════════════════"
    
    local result=""
    
    # Test 1: DNS implicit Docker
    log_info "Test 1: DNS implicit Docker (rezolvare 'web')"
    if docker compose -f "$DOCKER_DIR/docker-compose.yml" exec -T debug dig +short web 2>>"$LOG_FILE"; then
        result="dns_implicit:PASS"
        log_info "✓ DNS implicit functioneaza"
    else
        result="dns_implicit:FAIL"
        log_error "✗ DNS implicit esuat"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 2: DNS custom server
    log_info "Test 2: DNS custom server (port $DNS_PORT)"
    local dns_response
    if dns_response=$(docker compose -f "$DOCKER_DIR/docker-compose.yml" exec -T debug dig @dns-server -p $DNS_PORT myservice.lab.local +short 2>>"$LOG_FILE"); then
        if [ -n "$dns_response" ]; then
            result="dns_custom:PASS:$dns_response"
            log_info "✓ DNS custom raspunde: $dns_response"
        else
            result="dns_custom:PARTIAL"
            log_warn "⚠ DNS custom raspunde dar fara rezultat"
        fi
    else
        result="dns_custom:FAIL"
        log_error "✗ DNS custom esuat"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 3: dig de pe host (if disponibil)
    if command -v dig &>/dev/null; then
        log_info "Test 3: DNS de pe host"
        if dig @localhost -p $DNS_PORT myservice.lab.local +short +timeout=2 2>>"$LOG_FILE" | grep -q '.'; then
            result="dns_host:PASS"
            log_info "✓ DNS accesibil de pe host"
        else
            result="dns_host:FAIL"
            log_warn "✗ DNS inaccesibil de pe host"
        fi
        echo "$result" >> "$VALIDATION_FILE"
    fi
}

#------------------------------------------------------------------------------
# Test SSH
#------------------------------------------------------------------------------
test_ssh() {
    log_step "═══════════════════════════════════════"
    log_step "         TEST SSH SERVER"
    log_step "═══════════════════════════════════════"
    
    local result=""
    
    # Test 1: Conectivitate SSH port
    log_info "Test 1: Port SSH deschis ($SSH_PORT)"
    if timeout 5 bash -c "echo >/dev/tcp/localhost/$SSH_PORT" 2>/dev/null; then
        result="ssh_port:PASS"
        log_info "✓ Port SSH deschis"
    else
        result="ssh_port:FAIL"
        log_error "✗ Port SSH inchis"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 2: Banner SSH
    log_info "Test 2: Banner SSH"
    local banner
    if banner=$(timeout 3 nc -v localhost $SSH_PORT 2>&1 | head -1); then
        if echo "$banner" | grep -qi "ssh"; then
            result="ssh_banner:PASS"
            log_info "✓ Banner SSH valid"
        else
            result="ssh_banner:PARTIAL"
            log_warn "⚠ Raspuns dar fara banner SSH standard"
        fi
    else
        result="ssh_banner:FAIL"
        log_error "✗ Nu s-a putut obtine banner"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 3: SSH Paramiko (din container)
    log_info "Test 3: Conexiune SSH cu Paramiko"
    if docker compose -f "$DOCKER_DIR/docker-compose.yml" exec -T ssh-client \
        python3 -c "
import paramiko
import sys
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('ssh-server', port=22, username='labuser', password='labpass', timeout=10)
    stdin, stdout, stderr = client.exec_command('whoami')
    result = stdout.read().decode().strip()
    client.close()
    print(f'SUCCESS:{result}')
    sys.exit(0)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
" 2>>"$LOG_FILE" | tee -a "$LOG_FILE" | grep -q "SUCCESS"; then
        result="ssh_paramiko:PASS"
        log_info "✓ Conexiune Paramiko reusita"
    else
        result="ssh_paramiko:FAIL"
        log_error "✗ Conexiune Paramiko esuata"
    fi
    echo "$result" >> "$VALIDATION_FILE"
}

#------------------------------------------------------------------------------
# Test FTP
#------------------------------------------------------------------------------
test_ftp() {
    log_step "═══════════════════════════════════════"
    log_step "         TEST FTP SERVER"
    log_step "═══════════════════════════════════════"
    
    local result=""
    
    # Test 1: Port FTP deschis
    log_info "Test 1: Port FTP deschis ($FTP_PORT)"
    if timeout 5 bash -c "echo >/dev/tcp/localhost/$FTP_PORT" 2>/dev/null; then
        result="ftp_port:PASS"
        log_info "✓ Port FTP deschis"
    else
        result="ftp_port:FAIL"
        log_error "✗ Port FTP inchis"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 2: Banner FTP
    log_info "Test 2: Banner FTP"
    local banner
    if banner=$(timeout 3 nc -v localhost $FTP_PORT 2>&1 | head -1); then
        if echo "$banner" | grep -qi "220"; then
            result="ftp_banner:PASS"
            log_info "✓ Banner FTP valid (220)"
        else
            result="ftp_banner:PARTIAL"
            log_warn "⚠ Raspuns dar fara cod 220"
        fi
    else
        result="ftp_banner:FAIL"
        log_error "✗ Nu s-a putut obtine banner FTP"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 3: FTP curl (din container)
    log_info "Test 3: Listare FTP cu curl"
    if docker compose -f "$DOCKER_DIR/docker-compose.yml" exec -T debug \
        curl -s --connect-timeout 5 "ftp://labftp:labftp@ftp-server:2121/" 2>>"$LOG_FILE" | head -5 | tee -a "$LOG_FILE"; then
        result="ftp_list:PASS"
        log_info "✓ Listare FTP reusita"
    else
        result="ftp_list:FAIL"
        log_error "✗ Listare FTP esuata"
    fi
    echo "$result" >> "$VALIDATION_FILE"
}

#------------------------------------------------------------------------------
# Test HTTP/Web
#------------------------------------------------------------------------------
test_web() {
    log_step "═══════════════════════════════════════"
    log_step "         TEST WEB SERVER"
    log_step "═══════════════════════════════════════"
    
    local result=""
    
    # Test 1: HTTP de pe host
    log_info "Test 1: HTTP de pe host (port $HTTP_PORT)"
    if curl -s --connect-timeout 5 "http://localhost:$HTTP_PORT/" 2>>"$LOG_FILE" | head -5 | tee -a "$LOG_FILE" | grep -qi "html"; then
        result="http_host:PASS"
        log_info "✓ HTTP accesibil de pe host"
    else
        result="http_host:FAIL"
        log_error "✗ HTTP inaccesibil de pe host"
    fi
    echo "$result" >> "$VALIDATION_FILE"
    
    # Test 2: HTTP din container via DNS implicit
    log_info "Test 2: HTTP via DNS implicit Docker"
    if docker compose -f "$DOCKER_DIR/docker-compose.yml" exec -T debug \
        curl -s --connect-timeout 5 "http://web:8000/" 2>>"$LOG_FILE" | head -5 | tee -a "$LOG_FILE" | grep -qi "html"; then
        result="http_docker_dns:PASS"
        log_info "✓ HTTP via DNS implicit functioneaza"
    else
        result="http_docker_dns:FAIL"
        log_error "✗ HTTP via DNS implicit esuat"
    fi
    echo "$result" >> "$VALIDATION_FILE"
}

#------------------------------------------------------------------------------
# Generare sumar validation
#------------------------------------------------------------------------------
generate_validation_summary() {
    log_step "═══════════════════════════════════════"
    log_step "         SUMAR VALIDARE"
    log_step "═══════════════════════════════════════"
    
    echo "" >> "$VALIDATION_FILE"
    echo "# Sumar - $(date)" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
    
    local total=0
    local passed=0
    local failed=0
    
    while IFS= read -r line; do
        if [ -z "$line" ] || [[ "$line" == \#* ]]; then
            continue
        fi
        ((total++))
        if echo "$line" | grep -q ":PASS"; then
            ((passed++))
        elif echo "$line" | grep -q ":FAIL"; then
            ((failed++))
        fi
    done < "$VALIDATION_FILE"
    
    echo "TOTAL_TESTS=$total" >> "$VALIDATION_FILE"
    echo "PASSED=$passed" >> "$VALIDATION_FILE"
    echo "FAILED=$failed" >> "$VALIDATION_FILE"
    
    log_info "Rezultate: $passed/$total teste trecute"
    
    if [ $failed -gt 0 ]; then
        log_warn "Atentie: $failed teste esuate"
        return 1
    else
        log_info "Toate testele au trecut!"
        return 0
    fi
}

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------
cleanup_demo() {
    log_step "Cleanup demo..."
    
    stop_capture
    
    # Nu oprim containerele - le lasam for explorare
    log_info "Containerele raman active pentru explorare"
    log_info "Pentru oprire: cd docker && docker compose down"
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║  DEMO AUTOMAT - SAPTAMANA 10 - SERVICII DE RETEA IN CONTAINERE                ║"
    echo "║  DNS | SSH | FTP | Docker Compose                                             ║"
    echo "║  Retele de Calculatoare | ASE Bucharest | 2025-2026                           ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Setup
    setup_artifacts
    
    if ! check_prerequisites; then
        log_error "Prerequisite neindeplinite. Iesire."
        exit 1
    fi
    
    # Init validation file
    echo "# Validation Results - Week 10" > "$VALIDATION_FILE"
    echo "# Timestamp: $(date)" >> "$VALIDATION_FILE"
    echo "" >> "$VALIDATION_FILE"
    
    # Infrastructura
    if ! start_docker_services; then
        log_error "Nu s-a putut porni infrastructura Docker"
        exit 1
    fi
    
    # Captura trafic
    start_capture
    
    # Pauza for stabilizare
    sleep 3
    
    # Teste
    test_dns
    test_ssh
    test_ftp
    test_web
    
    # Sumar
    generate_validation_summary
    local test_result=$?
    
    # Cleanup
    cleanup_demo
    
    echo ""
    log_step "═══════════════════════════════════════"
    log_step "         ARTEFACTE GENERATE"
    log_step "═══════════════════════════════════════"
    log_info "Log complet:  $LOG_FILE"
    log_info "Captura PCAP: $PCAP_FILE"
    log_info "Validare:     $VALIDATION_FILE"
    echo ""
    
    # Afisare continut validation
    echo "--- Continut validation.txt ---"
    cat "$VALIDATION_FILE"
    echo "-------------------------------"
    
    exit $test_result
}

# Trap for cleanup la intrerupere
trap cleanup_demo EXIT

# Rulare
main "$@"
