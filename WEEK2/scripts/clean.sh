#!/usr/bin/env bash
# =============================================================================
# clean.sh - Environment cleanup after laboratory for Week 2
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
NC='\033[0m'

# Script directory and project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# =============================================================================
# Utility functions
# =============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# =============================================================================
# Cleanup functions
# =============================================================================

cleanup_processes() {
    log_info "Stopping processes Python from demonstrations..."
    
    # stopping servers TCP/UDP on standard ports
    local DEMO_PORTS=(8080 8081 9999 5000)
    local killed=0
    
    for port in "${DEMO_PORTS[@]}"; do
        local pids
        pids=$(lsof -t -i :$port 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            for pid in $pids; do
                # Verify that e un process Python from project
                local cmdline
                cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' || echo "")
                if [[ "$cmdline" == *python* ]] || [[ "$cmdline" == *ex_2_* ]]; then
                    kill "$pid" 2>/dev/null && killed=$((killed + 1)) || true
                fi
            done
        fi
    done
    
    if [[ $killed -gt 0 ]]; then
        log_success "Stopped $killed processes"
    else
        log_info "Nu au fost found processes of demo active"
    fi
}

cleanup_mininet() {
    log_info "cleaning Mininet..."
    
    if command -v mn &> /dev/null; then
        if [[ $EUID -eq 0 ]]; then
            mn -c 2>/dev/null || true
            log_success "Mininet curatat"
        else
            log_warning "Mininet necesita sudo for cleaning"
            log_info "  Rulati: sudo mn -c"
        fi
    else
        log_info "Mininet is not installed, skip"
    fi
}

cleanup_captures() {
    log_info "cleaning files of capture temporare..."
    
    local captures_dir="$PROJECT_ROOT/seminar/captures"
    local pcap_dir="$PROJECT_ROOT/pcap"
    local logs_dir="$PROJECT_ROOT/logs"
    
    local deleted=0
    
    # deletes capturi temporare (mai old of 1 zi)
    if [[ -d "$captures_dir" ]]; then
        deleted=$(find "$captures_dir" -name "*.pcap" -mtime +1 -delete -print 2>/dev/null | wc -l || echo 0)
    fi
    
    # deletes log-uri old
    if [[ -d "$logs_dir" ]]; then
        find "$logs_dir" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    fi
    
    log_success "Deleted $deleted files temporare"
}

cleanup_pycache() {
    log_info "cleaning __pycache__ and .pyc..."
    
    local deleted=0
    
    # deletes directoriesle __pycache__
    while IFS= read -r -d '' dir; do
        rm -rf "$dir"
        deleted=$((deleted + 1))
    done < <(find "$PROJECT_ROOT" -type d -name "__pycache__" -print0 2>/dev/null)
    
    # deletes filesle .pyc
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Curatate $deleted directories __pycache__"
}

cleanup_temp() {
    log_info "Cleaning temporary files..."
    
    # files temporare comune
    find "$PROJECT_ROOT" \( \
        -name "*.tmp" -o \
        -name "*.swp" -o \
        -name "*~" -o \
        -name ".DS_Store" -o \
        -name "Thumbs.db" \
    \) -delete 2>/dev/null || true
    
    log_success "files temporare curatate"
}

reset_logs() {
    log_info "Resetare directories of log..."
    
    local logs_dir="$PROJECT_ROOT/logs"
    
    if [[ -d "$logs_dir" ]]; then
        rm -rf "${logs_dir:?}"/*
        touch "$logs_dir/.gitkeep"
        log_success "Directorul logs/ resetat"
    fi
}

show_status() {
    echo ""
    log_info "Status actual:"
    
    # processes on porturile demo
    echo "  processes on ports demo:"
    for port in 8080 8081 9999 5000; do
        local proc
        proc=$(lsof -i :$port 2>/dev/null | tail -1 | awk '{print $1, $2}' || echo "liber")
        echo "    port $port: $proc"
    done
    
    # Spatiu folosit
    echo ""
    echo "  Spatiu folosit:"
    echo "    captures/: $(du -sh "$PROJECT_ROOT/seminar/captures" 2>/dev/null | cut -f1 || echo '0')"
    echo "    logs/:     $(du -sh "$PROJECT_ROOT/logs" 2>/dev/null | cut -f1 || echo '0')"
    echo "    pcap/:     $(du -sh "$PROJECT_ROOT/pcap" 2>/dev/null | cut -f1 || echo '0')"
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           cleaning Mediu - Week 2: Sockets             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local mode="${1:-standard}"
    
    case "$mode" in
        --full|-f)
            log_info "Mod: cleaning COMPLETA"
            echo ""
            cleanup_processes
            cleanup_mininet
            cleanup_captures
            cleanup_pycache
            cleanup_temp
            reset_logs
            ;;
        --soft|-s)
            log_info "Mod: cleaning SOFT (pastreaza capturi)"
            echo ""
            cleanup_processes
            cleanup_pycache
            cleanup_temp
            ;;
        --status)
            show_status
            exit 0
            ;;
        --help|-h)
            cat << EOF
Utilizare: $0 [optiune]

Optiuni:
  (fara)     cleaning standard (processes, mininet, temp)
  --soft     cleaning soft (pastreaza capturi and logs)
  --full     cleaning completa (inclusiv capturi and logs)
  --status   Afiseaza status fara a curata
  --help     Afiseaza acest message

EOF
            exit 0
            ;;
        *)
            log_info "Mod: cleaning STANDARD"
            echo ""
            cleanup_processes
            cleanup_mininet
            cleanup_pycache
            cleanup_temp
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    cleaning completa!                         ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    
    show_status
}

main "$@"
