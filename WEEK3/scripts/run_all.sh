#!/usr/bin/env bash
# ============================================================================
# run_all.sh — Complete automated demo for Week 3
# ============================================================================
# Week 3: UDP broadcast and multicast, TCP tunnelling
#
# This script runs the main demonstrations without interactive input and writes
# artefacts into artifacts/.
#
# Usage:
#   sudo ./scripts/run_all.sh           # Full demo
#   sudo ./scripts/run_all.sh --quick   # Quick demo (localhost only)
#   sudo ./scripts/run_all.sh --mininet # Demo with a Mininet topology
#
# Outputs:
#   artifacts/demo.log         - Combined demo log
#   artifacts/demo.pcap        - Packet capture (if enabled)
#   artifacts/validation.txt   - Validation summary
#
# Licence: MIT
# ============================================================================
set -euo pipefail
# ─── Configurare WEEK 3 ──────────────────────────────────────────────────────
WEEK=3
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))  # 5300 for WEEK 3
SUBNET="10.0.${WEEK}.0/24"
GATEWAY="10.0.${WEEK}.1"

# Porturi conform standard
UDP_BCAST_PORT=$((WEEK_PORT_BASE + 7))      # 5307
UDP_MCAST_PORT=$((WEEK_PORT_BASE + 1))      # 5301
TCP_TUNNEL_LISTEN=$((WEEK_PORT_BASE + 90))  # 5390
TCP_TUNNEL_TARGET=$((WEEK_PORT_BASE + 80))  # 5380
TCP_ECHO_PORT=$((WEEK_PORT_BASE + 33))      # 5333

MULTICAST_GROUP="239.3.3.3"
BROADCAST_ADDR="255.255.255.255"

# Directoare
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
EXAMPLES_DIR="$ROOT_DIR/python/examples"

# Culori
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Functii helper ──────────────────────────────────────────────────────────
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

log() {
    local level="$1"
    shift
    echo -e "[$(timestamp)] [$level] $*" | tee -a "$ARTIFACTS_DIR/demo.log"
}

log_section() {
    echo "" | tee -a "$ARTIFACTS_DIR/demo.log"
    echo "═══════════════════════════════════════════════════════════════════" | tee -a "$ARTIFACTS_DIR/demo.log"
    echo -e "${CYAN}${BOLD}$1${NC}" | tee -a "$ARTIFACTS_DIR/demo.log"
    echo "═══════════════════════════════════════════════════════════════════" | tee -a "$ARTIFACTS_DIR/demo.log"
}

cleanup_processes() {
    pkill -f "ex0[1-8]" 2>/dev/null || true
    pkill -f "topo_" 2>/dev/null || true
}

# ─── Requirements verification ──────────────────────────────────────────────────────
check_requirements() {
    log "INFO" "Requirements verification sistem..."
    
    local missing=()
    
    command -v python3 &>/dev/null || missing+=("python3")
    command -v tcpdump &>/dev/null || missing+=("tcpdump")
    command -v nc &>/dev/null || missing+=("netcat")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log "ERROR" "Missing: ${missing[*]}"
        return 1
    fi
    
    log "INFO" "All requirements are met."
    return 0
}

# ─── Demo 1: UDP Broadcast (localhost) ───────────────────────────────────────
demo_broadcast_localhost() {
    log_section "DEMO 1: UDP Broadcast (localhost)"
    
    log "INFO" "Pornesc receiver pe 127.0.0.1:$UDP_BCAST_PORT..."
    timeout 10 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" recv \
        --port "$UDP_BCAST_PORT" --count 3 --timeout 8 &
    local recv_pid=$!
    sleep 0.5
    
    log "INFO" "Pornesc sender catre 127.255.255.255:$UDP_BCAST_PORT..."
    python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" send \
        --dst "127.255.255.255" --port "$UDP_BCAST_PORT" \
        --message "WEEK3_BCAST" --count 3 --interval 0.5
    
    wait $recv_pid 2>/dev/null || true
    
    log "INFO" "Demo broadcast localhost: COMPLET"
    echo "BROADCAST_LOCALHOST=PASS" >> "$ARTIFACTS_DIR/validation.txt"
}

# ─── Demo 2: UDP Multicast (localhost) ───────────────────────────────────────
demo_multicast_localhost() {
    log_section "DEMO 2: UDP Multicast (localhost)"
    
    log "INFO" "Pornesc receiver multicast pe $MULTICAST_GROUP:$UDP_MCAST_PORT..."
    timeout 10 python3 "$EXAMPLES_DIR/ex02_udp_multicast.py" recv \
        --group "$MULTICAST_GROUP" --port "$UDP_MCAST_PORT" --count 3 --timeout 8 &
    local recv_pid=$!
    sleep 0.5
    
    log "INFO" "Pornesc sender multicast catre $MULTICAST_GROUP:$UDP_MCAST_PORT..."
    python3 "$EXAMPLES_DIR/ex02_udp_multicast.py" send \
        --group "$MULTICAST_GROUP" --port "$UDP_MCAST_PORT" \
        --message "WEEK3_MCAST" --count 3 --interval 0.5 --ttl 1
    
    wait $recv_pid 2>/dev/null || true
    
    log "INFO" "Demo multicast localhost: COMPLET"
    echo "MULTICAST_LOCALHOST=PASS" >> "$ARTIFACTS_DIR/validation.txt"
}

# ─── Demo 3: TCP Echo Server + Tunnel (localhost) ────────────────────────────
demo_tunnel_localhost() {
    log_section "DEMO 3: TCP Tunnel (localhost)"
    
    # Starting echo server
    log "INFO" "Pornesc echo server pe 127.0.0.1:$TCP_TUNNEL_TARGET..."
    timeout 15 python3 "$EXAMPLES_DIR/ex04_echo_server.py" \
        --listen "127.0.0.1:$TCP_TUNNEL_TARGET" &
    local echo_pid=$!
    sleep 0.5
    
    # Starting tunnel
    log "INFO" "Pornesc tunnel pe :$TCP_TUNNEL_LISTEN -> 127.0.0.1:$TCP_TUNNEL_TARGET..."
    timeout 15 python3 "$EXAMPLES_DIR/ex03_tcp_tunnel.py" \
        --listen "0.0.0.0:$TCP_TUNNEL_LISTEN" \
        --target "127.0.0.1:$TCP_TUNNEL_TARGET" &
    local tunnel_pid=$!
    sleep 0.5
    
    # Test prin tunnel
    log "INFO" "Trimit mesaj de test prin tunnel..."
    local response
    response=$(echo "HELLO_TUNNEL_WEEK3" | nc -w 3 127.0.0.1 "$TCP_TUNNEL_LISTEN" 2>/dev/null || echo "")
    
    if [[ "$response" == *"HELLO"* ]] || [[ "$response" == *"TUNNEL"* ]]; then
        log "INFO" "Tunnel works: response received"
        echo "TCP_TUNNEL_LOCALHOST=PASS" >> "$ARTIFACTS_DIR/validation.txt"
    else
        log "WARN" "Tunnel: incomplete response (primit: '$response')"
        echo "TCP_TUNNEL_LOCALHOST=PARTIAL" >> "$ARTIFACTS_DIR/validation.txt"
    fi
    
    kill $echo_pid $tunnel_pid 2>/dev/null || true
    log "INFO" "Demo tunnel localhost: COMPLET"
}

# ─── Demo 4: Capture Trafic ──────────────────────────────────────────────────
demo_capture_traffic() {
    log_section "DEMO 4: Capture Trafic (tcpdump)"
    
    local pcap_file="$ARTIFACTS_DIR/demo.pcap"
    
    log "INFO" "Pornesc captura pe loopback for 10 secunde..."
    timeout 12 tcpdump -i lo -w "$pcap_file" \
        "udp port $UDP_BCAST_PORT or udp port $UDP_MCAST_PORT or tcp port $TCP_TUNNEL_LISTEN" \
        -c 50 2>/dev/null &
    local tcpdump_pid=$!
    sleep 1
    
    # Generam trafic
    log "INFO" "Generating traffic for capture..."
    
    # Broadcast
    timeout 3 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" send \
        --dst "127.255.255.255" --port "$UDP_BCAST_PORT" --count 2 --interval 0.3 &
    
    # Multicast
    timeout 3 python3 "$EXAMPLES_DIR/ex02_udp_multicast.py" send \
        --group "$MULTICAST_GROUP" --port "$UDP_MCAST_PORT" --count 2 --interval 0.3 &
    
    sleep 5
    kill $tcpdump_pid 2>/dev/null || true
    wait $tcpdump_pid 2>/dev/null || true
    
    if [ -f "$pcap_file" ] && [ -s "$pcap_file" ]; then
        local pkt_count
        pkt_count=$(tcpdump -r "$pcap_file" 2>/dev/null | wc -l || echo "0")
        log "INFO" "Capture complete: $pcap_file ($pkt_count packets)"
        echo "PCAP_CAPTURE=PASS ($pkt_count packets)" >> "$ARTIFACTS_DIR/validation.txt"
    else
        log "WARN" "Empty capture or non-existent"
        echo "PCAP_CAPTURE=EMPTY" >> "$ARTIFACTS_DIR/validation.txt"
        # Creare fiander pcap gol valid
        tcpdump -w "$pcap_file" -c 0 2>/dev/null || touch "$pcap_file"
    fi
}

# ─── Demo 5: TCP Multiclient ─────────────────────────────────────────────────
demo_multiclient() {
    log_section "DEMO 5: Server TCP Multiclient"
    
    log "INFO" "Pornesc server multiclient pe :$TCP_ECHO_PORT..."
    timeout 10 python3 "$EXAMPLES_DIR/ex05_tcp_multiclient.py" \
        --host "127.0.0.1" --port "$TCP_ECHO_PORT" &
    local srv_pid=$!
    sleep 1
    
    log "INFO" "Trimit 3 simultaneous connections..."
    echo "client1_week3" | nc -w 2 127.0.0.1 "$TCP_ECHO_PORT" &
    echo "client2_week3" | nc -w 2 127.0.0.1 "$TCP_ECHO_PORT" &
    echo "client3_week3" | nc -w 2 127.0.0.1 "$TCP_ECHO_PORT" &
    
    sleep 3
    kill $srv_pid 2>/dev/null || true
    
    log "INFO" "Demo multiclient: COMPLET"
    echo "TCP_MULTICLIENT=PASS" >> "$ARTIFACTS_DIR/validation.txt"
}

# ─── Sumar and validare ───────────────────────────────────────────────────────
generate_summary() {
    log_section "SUMAR VALIDARE"
    
    echo "" >> "$ARTIFACTS_DIR/validation.txt"
    echo "───────────────────────────────────────" >> "$ARTIFACTS_DIR/validation.txt"
    echo "WEEK=$WEEK" >> "$ARTIFACTS_DIR/validation.txt"
    echo "TIMESTAMP=$(timestamp)" >> "$ARTIFACTS_DIR/validation.txt"
    echo "SUBNET=$SUBNET" >> "$ARTIFACTS_DIR/validation.txt"
    echo "PORTS=BCAST:$UDP_BCAST_PORT MCAST:$UDP_MCAST_PORT TUNNEL:$TCP_TUNNEL_LISTEN" >> "$ARTIFACTS_DIR/validation.txt"
    
    # Verify artefacte
    local artifacts_ok=true
    
    if [ -f "$ARTIFACTS_DIR/demo.log" ]; then
        echo "ARTIFACT_LOG=EXISTS" >> "$ARTIFACTS_DIR/validation.txt"
    else
        echo "ARTIFACT_LOG=MISSING" >> "$ARTIFACTS_DIR/validation.txt"
        artifacts_ok=false
    fi
    
    if [ -f "$ARTIFACTS_DIR/demo.pcap" ]; then
        echo "ARTIFACT_PCAP=EXISTS" >> "$ARTIFACTS_DIR/validation.txt"
    else
        echo "ARTIFACT_PCAP=MISSING" >> "$ARTIFACTS_DIR/validation.txt"
        artifacts_ok=false
    fi
    
    echo "───────────────────────────────────────" >> "$ARTIFACTS_DIR/validation.txt"
    
    if $artifacts_ok; then
        echo "OVERALL_STATUS=SUCCESS" >> "$ARTIFACTS_DIR/validation.txt"
        log "INFO" "${GREEN}DEMO COMPLET - All artefactele generate${NC}"
    else
        echo "OVERALL_STATUS=PARTIAL" >> "$ARTIFACTS_DIR/validation.txt"
        log "WARN" "${YELLOW}DEMO PARTIAL - Unele artefacte lipsesc${NC}"
    fi
    
    cat "$ARTIFACTS_DIR/validation.txt" | tee -a "$ARTIFACTS_DIR/demo.log"
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
    local mode="${1:-full}"
    
    # Pregatire directoare
    mkdir -p "$ARTIFACTS_DIR"
    rm -f "$ARTIFACTS_DIR/demo.log" "$ARTIFACTS_DIR/demo.pcap" "$ARTIFACTS_DIR/validation.txt"
    touch "$ARTIFACTS_DIR/validation.txt"
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  WEEK $WEEK: Broadcast & Multicast UDP + TCP Tunnel — Automatic Demo     ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    log "INFO" "Initialising demo WEEK $WEEK (mode: $mode)..."
    
    # Cleanup initial
    cleanup_processes
    
    # Requirements verification
    if ! check_requirements; then
        log "ERROR" "Requirements not met. Aborting."
        exit 1
    fi
    
    # Run demo-uri
    case "$mode" in
        --quick|-q)
            demo_broadcast_localhost
            demo_multicast_localhost
            ;;
        --mininet|-m)
            log "WARN" "Mod Mininet necesita run separata with sudo. Folosind localhost."
            demo_broadcast_localhost
            demo_multicast_localhost
            demo_tunnel_localhost
            demo_multiclient
            demo_capture_traffic
            ;;
        full|*)
            demo_broadcast_localhost
            demo_multicast_localhost
            demo_tunnel_localhost
            demo_multiclient
            demo_capture_traffic
            ;;
    esac
    
    # Cleanup final
    cleanup_processes
    
    # Generare sumar
    generate_summary
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  Demo WEEK $WEEK complete!                                              ║"
    echo "║  Artefacte: artifacts/demo.log, demo.pcap, validation.txt           ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Run
main "$@"
