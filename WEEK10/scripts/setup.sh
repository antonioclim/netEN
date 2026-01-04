#!/usr/bin/env bash
#==============================================================================
# setup.sh – Installation mediu for Week 10 (Network services)
# Computer Networks, ASE Bucharest 2025-2026
#==============================================================================
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

#------------------------------------------------------------------------------
# Detectare distributie
#------------------------------------------------------------------------------
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ "$(uname)" == "Darwin" ]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

#------------------------------------------------------------------------------
# Verifytion prerequisite
#------------------------------------------------------------------------------
check_prerequisites() {
    log_step "Verifyre prerequisite..."
    
    local missing=()
    
    # Python 3
    if ! command -v python3 &>/dev/null; then
        missing+=("python3")
    fi
    
    # Docker
    if ! command -v docker &>/dev/null; then
        missing+=("docker")
    fi
    
    # Docker Compose
    if ! docker compose version &>/dev/null 2>&1; then
        if ! command -v docker-compose &>/dev/null; then
            missing+=("docker-compose")
        fi
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Lipsesc urmatoarele: ${missing[*]}"
        log_info "Instalati-le inainte de a continua."
        exit 1
    fi
    
    log_info "Toate prerequisitele sunt instalate."
}

#------------------------------------------------------------------------------
# Installation packete Python
#------------------------------------------------------------------------------
setup_python() {
    log_step "Configurare mediu Python..."
    
    # Creation virtual environment if nu exista
    if [ ! -d "$ROOT_DIR/.venv" ]; then
        log_info "Creare mediu virtual Python..."
        python3 -m venv "$ROOT_DIR/.venv"
    fi
    
    # Activare and installation dependente
    # shellcheck disable=SC1091
    source "$ROOT_DIR/.venv/bin/activate"
    
    log_info "Install dependencies Python..."
    pip install --upgrade pip --quiet
    pip install -r "$ROOT_DIR/requirements.txt" --quiet
    
    log_info "Mediu Python configurat in $ROOT_DIR/.venv"
}

#------------------------------------------------------------------------------
# Generare certificate self-signed
#------------------------------------------------------------------------------
generate_certs() {
    log_step "Generare certificate SSL..."
    
    local cert_dir="$ROOT_DIR/certs"
    mkdir -p "$cert_dir"
    
    if [ -f "$cert_dir/server.crt" ] && [ -f "$cert_dir/server.key" ]; then
        log_info "Certificatele exista deja. Saltare..."
        return 0
    fi
    
    log_info "Generare certificat self-signed..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$cert_dir/server.key" \
        -out "$cert_dir/server.crt" \
        -subj "/C=RO/ST=Bucharest/L=Bucharest/O=ASE/OU=CSIE/CN=localhost" \
        2>/dev/null
    
    chmod 600 "$cert_dir/server.key"
    log_info "Certificate generate in $cert_dir/"
}

#------------------------------------------------------------------------------
# Build Docker images
#------------------------------------------------------------------------------
build_docker() {
    log_step "Build Docker images..."
    
    cd "$ROOT_DIR/docker"
    
    if docker compose build --quiet 2>/dev/null; then
        log_info "Docker images construite cu succes."
    else
        log_warn "docker compose build a intampinat probleme."
        log_info "Incercati manual: cd docker && docker compose build"
    fi
    
    cd "$ROOT_DIR"
}

#------------------------------------------------------------------------------
# Creation directoare necesare
#------------------------------------------------------------------------------
create_directoryies() {
    log_step "Creare directoare..."
    
    mkdir -p "$ROOT_DIR"/{pcap,logs,outputs}
    mkdir -p "$ROOT_DIR/docker/ftp-server/data/uploads"
    
    # Permisiuni for FTP
    chmod 777 "$ROOT_DIR/docker/ftp-server/data/uploads" 2>/dev/null || true
    
    log_info "Directoare create."
}

#------------------------------------------------------------------------------
# Verifytion functionalitate
#------------------------------------------------------------------------------
verify_setup() {
    log_step "Verifyre setup..."
    
    local errors=0
    
    # Verifytion Python packages
    if python3 -c "import flask, requests, paramiko" 2>/dev/null; then
        log_info "✓ Pachete Python OK"
    else
        log_warn "✗ Unele packete Python lipsesc"
        ((errors++))
    fi
    
    # Verifytion Docker
    if docker info &>/dev/null; then
        log_info "✓ Docker functional"
    else
        log_warn "✗ Docker nu ruleaza"
        ((errors++))
    fi
    
    # Verifytion certificate
    if [ -f "$ROOT_DIR/certs/server.crt" ]; then
        log_info "✓ Certificate SSL generate"
    else
        log_warn "✗ Certificate lipsa"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        log_info "Setup complet si functional!"
        return 0
    else
        log_warn "Setup incomplet - $errors erori"
        return 1
    fi
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo ""
    log_info "╔══════════════════════════════════════════════════════════════════╗"
    log_info "║  Setup Saptamana 10 – Network services (DNS, SSH, FTP)          ║"
    log_info "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    local distro
    distro=$(detect_distro)
    log_info "Sistem detectat: $distro"
    
    check_prerequisites
    create_directoryies
    setup_python
    generate_certs
    build_docker
    verify_setup
    
    echo ""
    log_info "════════════════════════════════════════════════════════════════════"
    log_info "  Setup complet! Pasi urmatori:"
    log_info "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "  1. Activati mediul Python:"
    echo "     source .venv/bin/activate"
    echo ""
    echo "  2. Porniti infrastructura Docker:"
    echo "     make docker-up"
    echo ""
    echo "  3. Verifyti ca totul functioneaza:"
    echo "     make verify"
    echo ""
    echo "  4. Rulati demonstratiile:"
    echo "     make demo"
    echo ""
}

main "$@"
