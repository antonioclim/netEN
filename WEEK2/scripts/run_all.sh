#!/usr/bin/env bash
# =============================================================================
# run_all.sh - Automated Demo Week 2: Socket Programming TCP/UDP
# =============================================================================
# runs the full demonstration with no interactive input.
# Produces artefacts in artifacts/:
#   - demo.log      (complete demo log)
#   - demo.pcap     (combined capture TCP+UDP)
#   - validation.txt (validation results)
# =============================================================================
# Computer Networks - ASE Bucharest, CSIE
# Hypotheticalandrei & Rezolvix | MIT License
# =============================================================================

set -euo pipefail

# =============================================================================
# VARIABILE and CONSTANTE (WEEK 2)
# =============================================================================
WEEK=2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Plan IP for WEEK 2: 10.0.2.0/24
NETWORK="10.0.${WEEK}"
SERVER_IP="${NETWORK}.100"
HOST_IP="127.0.0.1"  # Fallback for localhost demo

# Plan ports WEEK 2
# WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5200
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))
TCP_APP_PORT=9090
UDP_APP_PORT=9091

# directories
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"
LOGS_DIR="$PROJECT_ROOT/logs"
PYTHON_APPS="$PROJECT_ROOT/seminar/python/exercises"

# files exercises
EX_TCP="$PYTHON_APPS/ex_2_01_tcp.py"
EX_UDP="$PYTHON_APPS/ex_2_02_udp.py"

# files output
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# FUNCTII UTILITARE
# =============================================================================
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

log() {
    local level="$1"
    shift
    local msg="$*"
    echo -e "[$(timestamp)][$level] $msg" | tee -a "$DEMO_LOG"
}

log_info() { log "INFO" "$@"; }
log_ok() { log " OK " "$@"; }
log_err() { log "ERR " "$@"; }
log_warn() { log "WARN" "$@"; }

cleanup_processes() {
    pkill -f "ex_2_01_tcp.py" 2>/dev/null || true
    pkill -f "ex_2_02_udp.py" 2>/dev/null || true
    pkill -f "tcpdump.*port.*909" 2>/dev/null || true
}

check_port_free() {
    local port="$1"
    if ss -tuln 2>/dev/null | grep -q ":${port} "; then
        return 1
    fi
    return 0
}

wait_for_port() {
    local port="$1"
    local max_wait="${2:-10}"
    local waited=0
    while ! ss -tuln 2>/dev/null | grep -q ":${port} "; do
        sleep 0.2
        waited=$((waited + 1))
        if [ $waited -ge $((max_wait * 5)) ]; then
            return 1
        fi
    done
    return 0
}

# =============================================================================
# INITIALIZARE
# =============================================================================
init() {
    log_info "════════════════════════════════════════════════════════════════"
    log_info " WEEK $WEEK - Demo Automat: Socket Programming TCP/UDP"
    log_info "════════════════════════════════════════════════════════════════"
    
    # creation directories
    mkdir -p "$ARTIFACTS_DIR" "$LOGS_DIR"
    
    # cleaning files anterioare
    : > "$DEMO_LOG"
    rm -f "$DEMO_PCAP" "$VALIDATION_FILE" 2>/dev/null || true
    
    # cleaning processes anterioare
    cleanup_processes
    
    log_info "Artefacte vor fi salvate in: $ARTIFACTS_DIR"
    log_info "Network plan: ${NETWORK}.0/24 | Ports: TCP=$TCP_APP_PORT, UDP=$UDP_APP_PORT"
}

# =============================================================================
# VERIFICARI PRE-EXECUTIE
# =============================================================================
preflight_checks() {
    log_info "─── Verificari pre-executie ───"
    
    local errors=0
    
    # Python
    if command -v python3 &>/dev/null; then
        log_ok "Python3: $(python3 --version 2>&1)"
    else
        log_err "Python3 is not installed"
        errors=$((errors + 1))
    fi
    
    # exercises
    if [[ -f "$EX_TCP" ]]; then
        log_ok "exercise TCP: $EX_TCP"
    else
        log_err "exercise TCP lipsa: $EX_TCP"
        errors=$((errors + 1))
    fi
    
    if [[ -f "$EX_UDP" ]]; then
        log_ok "exercise UDP: $EX_UDP"
    else
        log_err "exercise UDP lipsa: $EX_UDP"
        errors=$((errors + 1))
    fi
    
    # tcpdump (optional dar recomandat)
    if command -v tcpdump &>/dev/null; then
        log_ok "tcpdump available"
    else
        log_warn "tcpdump inavailable - capturile vor fi sarite"
    fi
    
    # ports
    if check_port_free $TCP_APP_PORT; then
        log_ok "port TCP $TCP_APP_PORT available"
    else
        log_warn "port TCP $TCP_APP_PORT ocupat - se va incerca eliberarea"
    fi
    
    if check_port_free $UDP_APP_PORT; then
        log_ok "port UDP $UDP_APP_PORT available"
    else
        log_warn "port UDP $UDP_APP_PORT ocupat - se va incerca eliberarea"
    fi
    
    if [[ $errors -gt 0 ]]; then
        log_err "Verificari esuate: $errors errors critice"
        return 1
    fi
    
    log_ok "Toate verificarile au trecut"
    return 0
}

# =============================================================================
# DEMO TCP
# =============================================================================
demo_tcp() {
    log_info "─── Demo TCP (server Concurent) ───"
    
    local tcp_log="$LOGS_DIR/tcp_demo.log"
    local tcp_pcap="$ARTIFACTS_DIR/tcp_demo.pcap"
    
    # starting capture (if tcpdump available)
    local tcpdump_pid=""
    if command -v tcpdump &>/dev/null; then
        log_info "starting capture TCP on lo:$TCP_APP_PORT"
        tcpdump -i lo -w "$tcp_pcap" "tcp port $TCP_APP_PORT" 2>/dev/null &
        tcpdump_pid=$!
        sleep 0.5
    fi
    
    # starting server TCP
    log_info "starting server TCP on 0.0.0.0:$TCP_APP_PORT (threaded)"
    python3 -u "$EX_TCP" server --bind 0.0.0.0 --port $TCP_APP_PORT --mode threaded \
        >> "$tcp_log" 2>&1 &
    local server_pid=$!
    
    # waiting server sa fie gata
    if wait_for_port $TCP_APP_PORT 5; then
        log_ok "server TCP active (PID: $server_pid)"
    else
        log_err "server TCP nu a pornit in timp util"
        kill $server_pid 2>/dev/null || true
        return 1
    fi
    
    # Trimitere messages of test
    log_info "Trimitere messages of test (3 clients secventiali)"
    
    for i in 1 2 3; do
        local msg="WEEK${WEEK}_TEST_MSG_${i}"
        log_info "  client $i: $msg"
        python3 "$EX_TCP" client --host $HOST_IP --port $TCP_APP_PORT --message "$msg" \
            >> "$tcp_log" 2>&1 || log_warn "client $i nu a primit raspuns"
        sleep 0.2
    done
    
    # Test load (5 clients concurenti)
    log_info "Test incarcare: 5 clients concurenti"
    python3 "$EX_TCP" load --host $HOST_IP --port $TCP_APP_PORT --clients 5 \
        --message "CONCURRENT_TEST" >> "$tcp_log" 2>&1 || log_warn "Load test partial esuat"
    
    # stopping server
    sleep 0.5
    kill $server_pid 2>/dev/null || true
    wait $server_pid 2>/dev/null || true
    log_ok "server TCP oprit"
    
    # stopping capture
    if [[ -n "$tcpdump_pid" ]]; then
        sleep 0.3
        kill $tcpdump_pid 2>/dev/null || true
        wait $tcpdump_pid 2>/dev/null || true
        log_ok "Captura TCP salvata: $tcp_pcap"
    fi
    
    return 0
}

# =============================================================================
# DEMO UDP
# =============================================================================
demo_udp() {
    log_info "─── Demo UDP (Protocol Aplicatie Custom) ───"
    
    local udp_log="$LOGS_DIR/udp_demo.log"
    local udp_pcap="$ARTIFACTS_DIR/udp_demo.pcap"
    
    # starting capture (if tcpdump available)
    local tcpdump_pid=""
    if command -v tcpdump &>/dev/null; then
        log_info "starting capture UDP on lo:$UDP_APP_PORT"
        tcpdump -i lo -w "$udp_pcap" "udp port $UDP_APP_PORT" 2>/dev/null &
        tcpdump_pid=$!
        sleep 0.5
    fi
    
    # starting server UDP
    log_info "starting server UDP on 0.0.0.0:$UDP_APP_PORT"
    python3 -u "$EX_UDP" server --bind 0.0.0.0 --port $UDP_APP_PORT \
        >> "$udp_log" 2>&1 &
    local server_pid=$!
    
    sleep 0.5
    log_ok "server UDP active (PID: $server_pid)"
    
    # Testare commands protocol
    log_info "Testare commands protocol UDP"
    
    local cmds=("ping" "time" "upper:hello_week${WEEK}" "reverse:network" "help")
    for cmd in "${cmds[@]}"; do
        log_info "  command: $cmd"
        python3 "$EX_UDP" client --host $HOST_IP --port $UDP_APP_PORT --once "$cmd" \
            >> "$udp_log" 2>&1 || log_warn "command '$cmd' fara raspuns"
        sleep 0.1
    done
    
    # stopping server
    sleep 0.3
    kill $server_pid 2>/dev/null || true
    wait $server_pid 2>/dev/null || true
    log_ok "server UDP oprit"
    
    # stopping capture
    if [[ -n "$tcpdump_pid" ]]; then
        sleep 0.3
        kill $tcpdump_pid 2>/dev/null || true
        wait $tcpdump_pid 2>/dev/null || true
        log_ok "Captura UDP salvata: $udp_pcap"
    fi
    
    return 0
}

# =============================================================================
# COMBINARE CAPTURI
# =============================================================================
merge_captures() {
    log_info "─── Combinare capturi ───"
    
    local tcp_pcap="$ARTIFACTS_DIR/tcp_demo.pcap"
    local udp_pcap="$ARTIFACTS_DIR/udp_demo.pcap"
    
    if command -v mergecap &>/dev/null; then
        if [[ -f "$tcp_pcap" && -f "$udp_pcap" ]]; then
            mergecap -w "$DEMO_PCAP" "$tcp_pcap" "$udp_pcap" 2>/dev/null
            log_ok "Capturi combinate in: $DEMO_PCAP"
        elif [[ -f "$tcp_pcap" ]]; then
            cp "$tcp_pcap" "$DEMO_PCAP"
            log_ok "Doar capture TCP availablea: $DEMO_PCAP"
        elif [[ -f "$udp_pcap" ]]; then
            cp "$udp_pcap" "$DEMO_PCAP"
            log_ok "Doar capture UDP availablea: $DEMO_PCAP"
        else
            log_warn "Nicio capture availablea"
        fi
    else
        # Fallback: copiaza TCP if exista
        if [[ -f "$tcp_pcap" ]]; then
            cp "$tcp_pcap" "$DEMO_PCAP"
            log_ok "mergecap inavailable, copiat TCP: $DEMO_PCAP"
        elif [[ -f "$udp_pcap" ]]; then
            cp "$udp_pcap" "$DEMO_PCAP"
            log_ok "mergecap inavailable, copiat UDP: $DEMO_PCAP"
        else
            # creation pcap gol for validare
            touch "$DEMO_PCAP"
            log_warn "Nicio capture - file gol creat"
        fi
    fi
}

# =============================================================================
# VALIDARE
# =============================================================================
validate() {
    log_info "─── Validare artefacts ───"
    
    {
        echo "═══════════════════════════════════════════════════════════════"
        echo " WEEK $WEEK - Socket Programming: Validare Demo"
        echo " Generat: $(timestamp)"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        
        # verification files
        echo "─── verification files artefacts ───"
        local all_ok=true
        
        if [[ -f "$DEMO_LOG" && -s "$DEMO_LOG" ]]; then
            local lines=$(wc -l < "$DEMO_LOG")
            echo "[OK] demo.log prezent ($lines linii)"
        else
            echo "[FAIL] demo.log lipsa or gol"
            all_ok=false
        fi
        
        if [[ -f "$DEMO_PCAP" ]]; then
            local size=$(stat -f%z "$DEMO_PCAP" 2>/dev/null || stat -c%s "$DEMO_PCAP" 2>/dev/null || echo "0")
            if [[ "$size" -gt 0 ]]; then
                echo "[OK] demo.pcap prezent ($size bytes)"
            else
                echo "[WARN] demo.pcap gol (tcpdump inavailable?)"
            fi
        else
            echo "[FAIL] demo.pcap lipsa"
            all_ok=false
        fi
        
        echo ""
        
        # verification log-uri TCP/UDP
        echo "─── verification executie demo ───"
        
        local tcp_log="$LOGS_DIR/tcp_demo.log"
        local udp_log="$LOGS_DIR/udp_demo.log"
        
        if [[ -f "$tcp_log" ]]; then
            if grep -q "OK:" "$tcp_log" 2>/dev/null; then
                local ok_count=$(grep -c "OK:" "$tcp_log" 2>/dev/null || echo "0")
                echo "[OK] server TCP: $ok_count raspunsuri OK"
            else
                echo "[WARN] server TCP: niciun raspuns OK gasit"
            fi
        else
            echo "[FAIL] Log TCP lipsa"
            all_ok=false
        fi
        
        if [[ -f "$udp_log" ]]; then
            if grep -qi "PONG\|time\|upper" "$udp_log" 2>/dev/null; then
                echo "[OK] server UDP: raspunsuri protocol validate"
            else
                echo "[WARN] server UDP: raspunsuri incomplete"
            fi
        else
            echo "[FAIL] Log UDP lipsa"
            all_ok=false
        fi
        
        echo ""
        
        # Analiza pcap (if tshark available)
        echo "─── Analiza trafic (if tshark available) ───"
        if command -v tshark &>/dev/null && [[ -f "$DEMO_PCAP" && -s "$DEMO_PCAP" ]]; then
            local tcp_pkts=$(tshark -r "$DEMO_PCAP" -Y "tcp" 2>/dev/null | wc -l || echo "0")
            local udp_pkts=$(tshark -r "$DEMO_PCAP" -Y "udp" 2>/dev/null | wc -l || echo "0")
            echo "[INFO] packets TCP: $tcp_pkts"
            echo "[INFO] packets UDP: $udp_pkts"
            
            # verification handshake TCP (SYN packets)
            local syn_pkts=$(tshark -r "$DEMO_PCAP" -Y "tcp.flags.syn==1" 2>/dev/null | wc -l || echo "0")
            if [[ "$syn_pkts" -gt 0 ]]; then
                echo "[OK] Handshake TCP detectat ($syn_pkts SYN flags)"
            fi
        else
            echo "[SKIP] tshark inavailable or pcap gol"
        fi
        
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        if $all_ok; then
            echo " result: VALIDARE REUSITA"
        else
            echo " result: VALIDARE PARTIALA (verificati warnings)"
        fi
        echo "═══════════════════════════════════════════════════════════════"
        
    } > "$VALIDATION_FILE"
    
    log_ok "Validare completa: $VALIDATION_FILE"
    cat "$VALIDATION_FILE"
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    init
    
    if ! preflight_checks; then
        log_err "Verificari pre-executie esuate. Abandonare."
        exit 1
    fi
    
    # Executie demo-uri
    demo_tcp || log_warn "Demo TCP with warnings"
    demo_udp || log_warn "Demo UDP with warnings"
    
    # Combinare capturi
    merge_captures
    
    # Validare
    validate
    
    # cleaning finala
    cleanup_processes
    
    log_info "════════════════════════════════════════════════════════════════"
    log_info " Demo WEEK $WEEK complet"
    log_info " Artefacte: $ARTIFACTS_DIR"
    log_info "════════════════════════════════════════════════════════════════"
}

# Trap for cleaning at exit
trap cleanup_processes EXIT

main "$@"
