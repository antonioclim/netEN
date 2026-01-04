#!/usr/bin/env bash
# =============================================================================
# capture.sh - Captura and analiza packets for Week 2
# Computer Networks - ASE Bucharest, CSIE
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Script directory and project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CAPTURES_DIR="$PROJECT_ROOT/seminar/captures"
PCAP_DIR="$PROJECT_ROOT/pcap"

# Configurari implicite
DEFAULT_INTERFACE="lo"
DEFAULT_PORT="8080"
DEFAULT_DURATION="30"
DEFAULT_COUNT="100"

# =============================================================================
# Utility functions
# =============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

usage() {
    cat << EOF
${CYAN}═══════════════════════════════════════════════════════════════${NC}
${CYAN}         capture.sh - Captura packets for S2               ${NC}
${CYAN}═══════════════════════════════════════════════════════════════${NC}

Utilizare: $0 <command> [optiuni]

${BLUE}commands availablee:${NC}
  tcp           Captura trafic TCP on interfata/port
  udp           Captura trafic UDP on interfata/port
  handshake     Captura handshake TCP (SYN, SYN-ACK, ACK)
  analyze       Analizeaza un file .pcap existent
  stats         Afiseaza statistici from capture
  live          Captura live with afisare in terminal
  clean         deletes capturile old

${BLUE}Optiuni:${NC}
  -i, --interface   Interfata of network (implicit: $DEFAULT_INTERFACE)
  -p, --port        port of capturet (implicit: $DEFAULT_PORT)
  -d, --duration    Durata capture in secunde (implicit: $DEFAULT_DURATION)
  -c, --count       Numar maxim of packets (implicit: $DEFAULT_COUNT)
  -o, --output      file output .pcap
  -f, --file        file input for analiza
  -h, --help        Afiseaza acest message

${BLUE}Exemple:${NC}
  $0 tcp -p 8080 -d 60          # Captura TCP 60s on port 8080
  $0 udp -p 9999 -c 50          # Captura 50 packets UDP on 9999
  $0 handshake -p 8080          # Captura doar handshake TCP
  $0 analyze -f capture.pcap    # Analiza pcap existent
  $0 stats -f capture.pcap      # Statistici from capture
  $0 live -p 8080               # Vizualizare live

EOF
    exit 0
}

check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Capturile necesita privilegii root"
        log_info "Rulati: sudo $0 $*"
        exit 1
    fi
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        log_error "$tool is not installed"
        case "$tool" in
            tshark) log_info "Instalare: sudo apt-get install tshark" ;;
            tcpdump) log_info "Instalare: sudo apt-get install tcpdump" ;;
        esac
        exit 1
    fi
}

ensure_dirs() {
    mkdir -p "$CAPTURES_DIR" "$PCAP_DIR"
}

generate_filename() {
    local prefix=$1
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${CAPTURES_DIR}/${prefix}_${timestamp}.pcap"
}

# =============================================================================
# Functii of capture
# =============================================================================

capture_tcp() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${port:-$DEFAULT_PORT}"
    local duration="${DURATION:-$DEFAULT_DURATION}"
    local count="${COUNT:-$DEFAULT_COUNT}"
    local output="${OUTPUT:-$(generate_filename tcp_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captura TCP on $interface:$port"
    log_info "Durata: ${duration}s, Max packets: $count"
    log_info "Output: $output"
    echo ""
    
    # Folosim tshark for capture
    timeout "$duration" tshark \
        -i "$interface" \
        -f "tcp port $port" \
        -c "$count" \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        local pkt_count
        pkt_count=$(tshark -r "$output" 2>/dev/null | wc -l)
        log_success "Captura completa: $pkt_count packets"
        log_info "file salvat: $output"
        
        # Rezumat rapid
        echo ""
        log_info "Rezumat rapid:"
        tshark -r "$output" -q -z io,phs 2>/dev/null | head -20 || true
    else
        log_warning "Nu s-au capturet packets (trafic inexistent on $interface:$port)"
    fi
}

capture_udp() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${port:-$DEFAULT_PORT}"
    local duration="${DURATION:-$DEFAULT_DURATION}"
    local count="${COUNT:-$DEFAULT_COUNT}"
    local output="${OUTPUT:-$(generate_filename udp_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captura UDP on $interface:$port"
    log_info "Durata: ${duration}s, Max packets: $count"
    log_info "Output: $output"
    echo ""
    
    timeout "$duration" tshark \
        -i "$interface" \
        -f "udp port $port" \
        -c "$count" \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        local pkt_count
        pkt_count=$(tshark -r "$output" 2>/dev/null | wc -l)
        log_success "Captura completa: $pkt_count packets"
        log_info "file salvat: $output"
    else
        log_warning "Nu s-au capturet packets UDP"
    fi
}

capture_handshake() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${port:-$DEFAULT_PORT}"
    local output="${OUTPUT:-$(generate_filename handshake_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captura TCP Handshake on $interface:$port"
    log_info "Astept SYN, SYN-ACK, ACK..."
    log_info "Output: $output"
    echo ""
    
    # Filtram doar pachetele of handshake (SYN, SYN-ACK, ACK fara date)
    timeout 30 tshark \
        -i "$interface" \
        -f "tcp port $port" \
        -Y "tcp.flags.syn==1 || (tcp.flags.ack==1 && tcp.len==0)" \
        -c 10 \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        log_success "Handshake capturet"
        echo ""
        log_info "packets capturete:"
        tshark -r "$output" -T fields \
            -e frame.number \
            -e ip.src \
            -e ip.dst \
            -e tcp.srcport \
            -e tcp.dstport \
            -e tcp.flags.syn \
            -e tcp.flags.ack \
            -E header=y \
            -E separator='|' \
            2>/dev/null || true
    else
        log_warning "Nu s-a capturet handshake"
    fi
}

analyze_pcap() {
    local input="${FILE:-}"
    
    if [[ -z "$input" ]]; then
        log_error "Specificati fisierul with -f"
        exit 1
    fi
    
    if [[ ! -f "$input" ]]; then
        log_error "Fisierul nu exista: $input"
        exit 1
    fi
    
    check_tool tshark
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         Analiza: $(basename "$input")                         ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    log_info "information generale:"
    capinfos "$input" 2>/dev/null || tshark -r "$input" -q -z io,stat,0 2>/dev/null
    echo ""
    
    log_info "Primele 20 of packets:"
    tshark -r "$input" -c 20 2>/dev/null
    echo ""
    
    log_info "Protocoale detectate:"
    tshark -r "$input" -q -z io,phs 2>/dev/null
}

show_stats() {
    local input="${FILE:-}"
    
    if [[ -z "$input" ]]; then
        log_error "Specificati fisierul with -f"
        exit 1
    fi
    
    if [[ ! -f "$input" ]]; then
        log_error "Fisierul nu exista: $input"
        exit 1
    fi
    
    check_tool tshark
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         Statistici: $(basename "$input")                      ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    log_info "Conversatii TCP:"
    tshark -r "$input" -q -z conv,tcp 2>/dev/null || echo "  No conversatii TCP"
    echo ""
    
    log_info "Conversatii UDP:"
    tshark -r "$input" -q -z conv,udp 2>/dev/null || echo "  No conversatii UDP"
    echo ""
    
    log_info "Distributie on protocoale:"
    tshark -r "$input" -q -z io,phs 2>/dev/null
    echo ""
    
    log_info "Statistici I/O (intervale 1s):"
    tshark -r "$input" -q -z io,stat,1 2>/dev/null | head -30
}

capture_live() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${port:-$DEFAULT_PORT}"
    
    check_privileges
    check_tool tshark
    
    log_info "Captura LIVE on $interface:$port"
    log_info "Apasati Ctrl+C for stopping"
    echo ""
    
    tshark -i "$interface" \
        -f "port $port" \
        -T fields \
        -e frame.time_relative \
        -e ip.src \
        -e ip.dst \
        -e tcp.srcport \
        -e tcp.dstport \
        -e udp.srcport \
        -e udp.dstport \
        -e frame.len \
        -e _ws.col.Protocol \
        -e _ws.col.Info \
        -E header=y \
        2>/dev/null
}

clean_captures() {
    log_info "cleaning capturi old..."
    
    local count=0
    
    if [[ -d "$CAPTURES_DIR" ]]; then
        count=$(find "$CAPTURES_DIR" -name "*.pcap" -mtime +7 | wc -l)
        find "$CAPTURES_DIR" -name "*.pcap" -mtime +7 -delete 2>/dev/null || true
    fi
    
    log_success "Deleted $count files .pcap mai old of 7 zile"
}

# =============================================================================
# Parser argumente
# =============================================================================

COMMAND=""
INTERFACE=""
port=""
DURATION=""
COUNT=""
OUTPUT=""
FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        tcp|udp|handshake|analyze|stats|live|clean)
            COMMAND=$1
            shift
            ;;
        -i|--interface)
            INTERFACE=$2
            shift 2
            ;;
        -p|--port)
            port=$2
            shift 2
            ;;
        -d|--duration)
            DURATION=$2
            shift 2
            ;;
        -c|--count)
            COUNT=$2
            shift 2
            ;;
        -o|--output)
            OUTPUT=$2
            shift 2
            ;;
        -f|--file)
            FILE=$2
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Argument necunoscut: $1"
            echo "Rulati: $0 --help"
            exit 1
            ;;
    esac
done

# =============================================================================
# Executie command
# =============================================================================

case "$COMMAND" in
    tcp)        capture_tcp ;;
    udp)        capture_udp ;;
    handshake)  capture_handshake ;;
    analyze)    analyze_pcap ;;
    stats)      show_stats ;;
    live)       capture_live ;;
    clean)      clean_captures ;;
    "")
        log_error "Nicio command specificata"
        echo "Rulati: $0 --help"
        exit 1
        ;;
    *)
        log_error "command necunoscuta: $COMMAND"
        exit 1
        ;;
esac
