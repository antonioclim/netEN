#!/usr/bin/env bash
#==============================================================================
# capture.sh – Captura packete for Week 10
# Computer Networks, ASE Bucharest 2025-2026
#==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$ROOT_DIR/pcap"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

#------------------------------------------------------------------------------
# Verifytion privilegii
#------------------------------------------------------------------------------
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Acest script necesita privilegii root pentru capture."
        log_info "Rulati cu: sudo $0 $*"
        exit 1
    fi
}

#------------------------------------------------------------------------------
# Captura DNS
#------------------------------------------------------------------------------
capture_dns() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/dns_${TIMESTAMP}.pcap"
    
    log_info "Captura trafic DNS pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 53 or port 5353' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captura completa. Pachete:"
        tcpdump -r "$output" -nn | head -20
    fi
}

#------------------------------------------------------------------------------
# Captura SSH
#------------------------------------------------------------------------------
capture_ssh() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/ssh_${TIMESTAMP}.pcap"
    
    log_info "Captura trafic SSH pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 22 or port 2222' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captura completa. Pachete:"
        tcpdump -r "$output" -nn | head -20
    fi
}

#------------------------------------------------------------------------------
# Captura FTP
#------------------------------------------------------------------------------
capture_ftp() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/ftp_${TIMESTAMP}.pcap"
    
    log_info "Captura trafic FTP pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 21 or port 2121 or portrange 30000-30009' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captura completa. Pachete:"
        tcpdump -r "$output" -nn -A | head -40
    fi
}

#------------------------------------------------------------------------------
# Captura HTTP
#------------------------------------------------------------------------------
capture_http() {
    local duration="${1:-10}"
    local output="$PCAP_DIR/http_${TIMESTAMP}.pcap"
    
    log_info "Captura trafic HTTP pentru $duration secunde..."
    log_info "Output: $output"
    
    timeout "$duration" tcpdump -i any -w "$output" 'port 80 or port 8000 or port 8080' 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captura completa. Pachete:"
        tcpdump -r "$output" -nn -A | head -40
    fi
}

#------------------------------------------------------------------------------
# Captura all (all protocoalele de interes)
#------------------------------------------------------------------------------
capture_all() {
    local duration="${1:-30}"
    local output="$PCAP_DIR/all_${TIMESTAMP}.pcap"
    
    log_info "Captura tot traficul relevant pentru $duration secunde..."
    log_info "Output: $output"
    
    local filter="port 53 or port 5353 or port 22 or port 2222 or port 21 or port 2121 or port 80 or port 8000 or portrange 30000-30009"
    
    timeout "$duration" tcpdump -i any -w "$output" "$filter" 2>/dev/null || true
    
    if [ -f "$output" ]; then
        log_info "Captura completa."
        echo ""
        log_info "Rezumat:"
        tcpdump -r "$output" -nn | wc -l | xargs -I{} echo "  Total packete: {}"
        tcpdump -r "$output" -nn 'port 53 or port 5353' | wc -l | xargs -I{} echo "  DNS: {}"
        tcpdump -r "$output" -nn 'port 22 or port 2222' | wc -l | xargs -I{} echo "  SSH: {}"
        tcpdump -r "$output" -nn 'port 21 or port 2121' | wc -l | xargs -I{} echo "  FTP: {}"
        tcpdump -r "$output" -nn 'port 80 or port 8000' | wc -l | xargs -I{} echo "  HTTP: {}"
    fi
}

#------------------------------------------------------------------------------
# Analiza PCAP
#------------------------------------------------------------------------------
analyse() {
    local pcap_file="$1"
    
    if [ ! -f "$pcap_file" ]; then
        log_error "Fisierul nu exista: $pcap_file"
        exit 1
    fi
    
    log_info "Analiza: $pcap_file"
    echo ""
    
    log_info "Statistici generale:"
    capinfos "$pcap_file" 2>/dev/null || tcpdump -r "$pcap_file" -nn | wc -l | xargs -I{} echo "Total packete: {}"
    
    echo ""
    log_info "Protocol breakdown:"
    tcpdump -r "$pcap_file" -nn 2>/dev/null | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -10
    
    echo ""
    log_info "Primele 20 packete:"
    tcpdump -r "$pcap_file" -nn | head -20
}

#------------------------------------------------------------------------------
# Usage
#------------------------------------------------------------------------------
usage() {
    cat << EOF
Utilizare: $0 <comanda> [optiuni]

Comenzi:
  dns [durata]      Captura trafic DNS (default: 10s)
  ssh [durata]      Captura trafic SSH (default: 10s)
  ftp [durata]      Captura trafic FTP (default: 10s)
  http [durata]     Captura trafic HTTP (default: 10s)
  all [durata]      Captura tot traficul (default: 30s)
  analyse <file>    Analizeaza file PCAP

Exemple:
  sudo $0 dns 15      # Captura DNS 15 secunde
  sudo $0 all 60      # Captura tot 60 secunde
  $0 analyse pcap/dns_20241220_143000.pcap

Fisierele sunt salvate in: $PCAP_DIR/
EOF
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    mkdir -p "$PCAP_DIR"
    
    if [ $# -eq 0 ]; then
        usage
        exit 0
    fi
    
    local cmd="$1"
    shift
    
    case "$cmd" in
        dns)
            check_root
            capture_dns "${1:-10}"
            ;;
        ssh)
            check_root
            capture_ssh "${1:-10}"
            ;;
        ftp)
            check_root
            capture_ftp "${1:-10}"
            ;;
        http)
            check_root
            capture_http "${1:-10}"
            ;;
        all)
            check_root
            capture_all "${1:-30}"
            ;;
        analyse)
            if [ $# -eq 0 ]; then
                log_error "Specificati fileul PCAP"
                exit 1
            fi
            analyse "$1"
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            log_error "Comanda necunoscuta: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"
