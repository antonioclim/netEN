#!/usr/bin/env bash
#==============================================================================
# cleanup.sh – Cleanup mediu for Week 10
# Computer Networks, ASE Bucharest 2025-2026
#==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#------------------------------------------------------------------------------
# Oprire containere Docker
#------------------------------------------------------------------------------
stop_docker() {
    log_info "Oprire containere Docker..."
    
    if ! command -v docker &>/dev/null; then
        log_warn "Docker nu este instalat"
        return
    fi
    
    cd "$ROOT_DIR/docker"
    
    if docker compose ps -q 2>/dev/null | grep -q .; then
        docker compose down --remove-orphans 2>/dev/null || true
        log_info "Containere oprite"
    else
        log_info "Nu exista containere active"
    fi
    
    cd "$ROOT_DIR"
}

#------------------------------------------------------------------------------
# Cleanup volume Docker
#------------------------------------------------------------------------------
clean_volumes() {
    log_info "Curatare volume Docker..."
    
    cd "$ROOT_DIR/docker"
    
    docker compose down -v 2>/dev/null || true
    
    cd "$ROOT_DIR"
    log_info "Volume curatate"
}

#------------------------------------------------------------------------------
# Cleanup images Docker
#------------------------------------------------------------------------------
clean_images() {
    log_info "Curatare images Docker (doar pentru acest proiect)..."
    
    # Deletere images prefix din acest proiect
    docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | \
        grep -E '^docker[-_]' | \
        xargs -r docker rmi 2>/dev/null || true
    
    # Cleanup images dangling
    docker image prune -f 2>/dev/null || true
    
    log_info "Images curatate"
}

#------------------------------------------------------------------------------
# Cleanup filee temporare
#------------------------------------------------------------------------------
clean_temp_files() {
    log_info "Curatare filee temporare..."
    
    # Python cache
    find "$ROOT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$ROOT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    find "$ROOT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
    
    # Pytest cache
    rm -rf "$ROOT_DIR/.pytest_cache" 2>/dev/null || true
    
    # Logs
    rm -rf "$ROOT_DIR/logs/"* 2>/dev/null || true
    
    log_info "Fisiere temporare curatate"
}

#------------------------------------------------------------------------------
# Cleanup PCAP
#------------------------------------------------------------------------------
clean_pcap() {
    log_info "Curatare filee PCAP..."
    
    if [ -d "$ROOT_DIR/pcap" ]; then
        rm -f "$ROOT_DIR/pcap/"*.pcap 2>/dev/null || true
        log_info "Fisiere PCAP sterse"
    fi
}

#------------------------------------------------------------------------------
# Cleanup certificate
#------------------------------------------------------------------------------
clean_certs() {
    log_info "Curatare certificate..."
    
    if [ -d "$ROOT_DIR/certs" ]; then
        rm -f "$ROOT_DIR/certs/"*.crt 2>/dev/null || true
        rm -f "$ROOT_DIR/certs/"*.key 2>/dev/null || true
        rm -f "$ROOT_DIR/certs/"*.pem 2>/dev/null || true
        log_info "Certificate sterse"
    fi
}

#------------------------------------------------------------------------------
# Cleanup venv
#------------------------------------------------------------------------------
clean_venv() {
    log_info "Curatare mediu virtual Python..."
    
    if [ -d "$ROOT_DIR/.venv" ]; then
        rm -rf "$ROOT_DIR/.venv"
        log_info "Mediu virtual sters"
    else
        log_info "Mediul virtual nu exista"
    fi
}

#------------------------------------------------------------------------------
# Reset complet
#------------------------------------------------------------------------------
full_reset() {
    log_warn "Resetare completa - toate datele vor fi sterse!"
    
    read -p "Sigur? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Anulat."
        return
    fi
    
    stop_docker
    clean_volumes
    clean_images
    clean_temp_files
    clean_pcap
    clean_certs
    clean_venv
    
    log_info "Reset complet finalizat"
}

#------------------------------------------------------------------------------
# Usage
#------------------------------------------------------------------------------
usage() {
    cat << EOF
Utilizare: $0 [optiune]

Optiuni:
  docker      Opreste containerele Docker
  volumes     Curata volume Docker
  images      Curata images Docker
  temp        Curata filee temporare
  pcap        Curata filee PCAP
  certs       Curata certificate
  venv        Curata mediul virtual Python
  all         Complete cleanup (fara venv)
  reset       Reset complet (inclusiv venv)
  -h, --help  Afiseaza acest mesaj

Fara optiuni: opreste Docker si curata temp files

Exemple:
  $0              # Cleanup de baza
  $0 all          # Complete cleanup
  $0 reset        # Reset total
EOF
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  Cleanup Saptamana 10                                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ $# -eq 0 ]; then
        # Default: cleanup de baza
        stop_docker
        clean_temp_files
        log_info "Cleanup de baza completat."
        exit 0
    fi
    
    case "$1" in
        docker)
            stop_docker
            ;;
        volumes)
            clean_volumes
            ;;
        images)
            clean_images
            ;;
        temp)
            clean_temp_files
            ;;
        pcap)
            clean_pcap
            ;;
        certs)
            clean_certs
            ;;
        venv)
            clean_venv
            ;;
        all)
            stop_docker
            clean_volumes
            clean_temp_files
            clean_pcap
            log_info "Complete cleanup finalizata."
            ;;
        reset)
            full_reset
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            log_error "Optiune necunoscuta: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"
