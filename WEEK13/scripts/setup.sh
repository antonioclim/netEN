#!/usr/bin/env bash
set -euo pipefail
set -euo pipefail
# =============================================================================
# Setup Script - Week 13 IoT & Security
# =============================================================================
# Prepares the working environment for laboratory exercises.
#
# Actions:
#   1. Install system packages (apt-get)
#   2. Install Python libraries (pip)
#   3. Generate TLS certificates for MQTT
#   4. Create password file Mosquitto
#   5. Configuration verification
#
# Usage:
#   ./setup.sh              # Complete setup
#   ./setup.sh --certs      # Only certificatese generation
#   ./setup.sh --pip        # Only Python dependencies
#   ./setup.sh --check      # Only verification
#
# Author: Teaching Staff ASE-CSIE
# =============================================================================

set -e  # Exit on error

# -----------------------------------------------------------------------------
# CONSTANTS AND COLOURS
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$PROJECT_DIR/configs/certs"
MOSQUITTO_DIR="$PROJECT_DIR/configs/mosquitto"

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour
BOLD='\033[1m'

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BOLD}${BLUE}=== $1 ===${NC}"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_warning "Some operations require root privileges."
        log_info "Run with: sudo ./setup.sh"
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# INSTALL SYSTEM PACKAGES
# -----------------------------------------------------------------------------

install_system_packages() {
    log_section "Installation Packets System"
    
    if ! check_root; then
        log_warning "Skip installation packets system (requires sudo)"
        return
    fi
    
    log_info "Updating package lists..."
    apt-get update -qq
    
    log_info "Installing packages..."
    apt-get install -y -qq \
        mosquitto \
        mosquitto-clients \
        tcpdump \
        nmap \
        netcat-openbsd \
        python3-pip \
        python3-venv \
        docker.io \
        docker-compose \
        wireshark-common \
        tshark \
        2>/dev/null
    
    # Mininet (optional, can be installed separately)
    if ! command -v mn &> /dev/null; then
        log_info "Installation Mininet..."
        apt-get install -y -qq mininet 2>/dev/null || \
            log_warning "Mininet not s-a putut instala. Instalati manual."
    fi
    
    log_success "System packages installed"
}

# -----------------------------------------------------------------------------
# INSTALL PYTHON DEPENDENCIES
# -----------------------------------------------------------------------------

install_python_deps() {
    log_section "Installation Python dependencies"
    
    local req_file="$PROJECT_DIR/requirements.txt"
    
    if [[ ! -f "$req_file" ]]; then
        log_warning "requirements.txt does not exist, creating default..."
        cat > "$req_file" << 'EOF'
# Python dependencies - Week 13 IoT & Security

# MQTT Client
paho-mqtt>=1.6.0

# Packet sniffing
scapy>=2.5.0

# Utilities
requests>=2.28.0
colorama>=0.4.6
EOF
    fi
    
    log_info "Installation from requirements.txt..."
    
    # Incercam without --break-system-packages prima date
    if pip3 install -r "$req_file" -q 2>/dev/null; then
        log_success "Python dependencies installed"
    elif pip3 install -r "$req_file" --break-system-packages -q 2>/dev/null; then
        log_success "Python dependencies installed (--break-system-packages)"
    else
        log_warning "pip installation failed. Try manually:"
        log_info "  pip3 install -r requirements.txt --break-system-packages"
    fi
}

# -----------------------------------------------------------------------------
# GENERATE TLS CERTIFICATES
# -----------------------------------------------------------------------------

generate_certificates() {
    log_section "Generation Certificateses TLS"
    
    # Create directory
    mkdir -p "$CERTS_DIR"
    cd "$CERTS_DIR"
    
    # Verification if exista deja
    if [[ -f "server.crt" && -f "server.key" && -f "ca.crt" ]]; then
        log_warning "Existing certificates found. Regenerare? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Keeping existing certificates"
            return
        fi
    fi
    
    log_info "Generation Certificateses Authority (CA)..."
    
    # 1. Generation CA private key
    openssl genrsa -out ca.key 2048 2>/dev/null
    
    # 2. Generation CA certificates (self-signed)
    openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=Laboratory/CN=MQTT-CA" \
        2>/dev/null
    
    log_success "CA generated: ca.crt, ca.key"
    
    log_info "Generation certificates server MQTT..."
    
    # 3. Generation server private key
    openssl genrsa -out server.key 2048 2>/dev/null
    
    # 4. Generation Certificateses Signing Request (CSR)
    openssl req -new -key server.key -out server.csr \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=MQTT/CN=mqtt-broker" \
        2>/dev/null
    
    # 5. Semnare CSR with CA -> server certificates
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out server.crt -days 365 \
        2>/dev/null
    
    # 6. Cleanup CSR
    rm -f server.csr
    
    log_success "Server certificates generated: server.crt, server.key"
    
    # Optional: certificatese generation client
    log_info "Generation certificates client (optional)..."
    
    openssl genrsa -out client.key 2048 2>/dev/null
    openssl req -new -key client.key -out client.csr \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=Client/CN=mqtt-client" \
        2>/dev/null
    openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out client.crt -days 365 \
        2>/dev/null
    rm -f client.csr
    
    log_success "Client certificates generated: client.crt, client.key"
    
    # Set allowedsions
    chmod 600 *.key
    chmod 644 *.crt
    
    # Afisare rezumat
    log_info "Certificateses generated in: $CERTS_DIR"
    ls -at "$CERTS_DIR"
    
    cd - > /dev/null
}

# -----------------------------------------------------------------------------
# CREATE MOSQUITTO PASSWORD FILE
# -----------------------------------------------------------------------------

create_mosquitto_passwords() {
    log_section "Configuration Passwords Mosquitto"
    
    local passwd_file="$MOSQUITTO_DIR/passwd"
    
    mkdir -p "$MOSQUITTO_DIR"
    
    if [[ -f "$passwd_file" ]]; then
        log_warning "Existing password file. Regenerare? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Keeping existing file"
            return
        fi
    fi
    
    # Create password file
    log_info "Create users MQTT..."
    
    # Verification if mosquitto_passwd e disponibil
    if ! command -v mosquitto_passwd &> /dev/null; then
        log_warning "mosquitto_passwd is not installed. Creez file manual..."
        
        # Format: user:password_hash (plain text for demo - NOT in productie!)
        cat > "$passwd_file" << 'EOF'
# WARNING: In productie, folositi mosquitto_passwd for hash-uri!
# This file e only for demonstration
admin:admin123
sensor1:sensor123
sensor2:sensor123
controller:ctrl123
dashboard:dash123
student:student123
guest:guest123
EOF
        log_warning "Passwords in plain text! For production: mosquitto_passwd -c passwd user"
    else
        # Usage mosquitto_passwd
        rm -f "$passwd_file"
        
        # Addition users
        echo "admin123" | mosquitto_passwd -b -c "$passwd_file" admin admin123 2>/dev/null || true
        echo "sensor123" | mosquitto_passwd -b "$passwd_file" sensor1 sensor123 2>/dev/null || true
        echo "sensor123" | mosquitto_passwd -b "$passwd_file" sensor2 sensor123 2>/dev/null || true
        echo "ctrl123" | mosquitto_passwd -b "$passwd_file" controller ctrl123 2>/dev/null || true
        echo "dash123" | mosquitto_passwd -b "$passwd_file" dashboard dash123 2>/dev/null || true
        echo "student123" | mosquitto_passwd -b "$passwd_file" student student123 2>/dev/null || true
        echo "guest123" | mosquitto_passwd -b "$passwd_file" guest guest123 2>/dev/null || true
        
        log_success "Hashed passwords created"
    fi
    
    # Afisare users
    log_info "Users created:"
    echo "  admin      : admin123     (full access)"
    echo "  sensor1    : sensor123    (publish telemetry)"
    echo "  sensor2    : sensor123    (publish telemetry)"
    echo "  controller : ctrl123      (read all, write commands)"
    echo "  dashboard  : dash123      (read only)"
    echo "  student    : student123   (test/sandbox)"
    echo "  guest      : guest123     (read public only)"
}

# -----------------------------------------------------------------------------
# CONFIGURATION VERIFICATION
# -----------------------------------------------------------------------------

verify_setup() {
    log_section "Verification Configuration"
    
    local errors=0
    
    # Python verification
    log_info "Python verification..."
    if command -v python3 &> /dev/null; then
        log_success "Python3: $(python3 --version)"
    else
        log_error "Python3 is not installed"
        ((errors++))
    fi
    
    # Python modules verification
    log_info "Python modules verification..."
    
    for modules in "paho.mqtt.client" "scapy.all" "requests"; do
        if python3 -c "import $modules" 2>/dev/null; then
            log_success "  $modules: OK"
        else
            log_warning "  $modules: Not is instalat"
        fi
    done
    
    # Docker verification
    log_info "Docker verification..."
    if command -v docker &> /dev/null; then
        if docker ps &> /dev/null; then
            log_success "Docker: OK (service running)"
        else
            log_warning "Docker installed but service not running"
        fi
    else
        log_warning "Docker is not installed"
    fi
    
    # Verification certificates
    log_info "TLS certificates verification..."
    if [[ -f "$CERTS_DIR/ca.crt" && -f "$CERTS_DIR/server.crt" ]]; then
        log_success "Certificateses TLS: OK"
        openssl x509 -in "$CERTS_DIR/server.crt" -noout -subject -dates 2>/dev/null | \
            sed 's/^/  /'
    else
        log_warning "Certificateses TLS: Does not exist (run --certs)"
    fi
    
    # Mosquitto verification
    log_info "Mosquitto verification..."
    if command -v mosquitto &> /dev/null; then
        log_success "Mosquitto: OK"
    else
        log_warning "Mosquitto is not installed"
    fi
    
    # tcpdump verification
    log_info "tcpdump verification..."
    if command -v tcpdump &> /dev/null; then
        log_success "tcpdump: OK"
    else
        log_warning "tcpdump is not installed"
    fi
    
    # Mininet verification
    log_info "Mininet verification..."
    if command -v mn &> /dev/null; then
        log_success "Mininet: OK"
    else
        log_warning "Mininet is not installed (optional for Docker workflow)"
    fi
    
    echo ""
    if [[ $errors -eq 0 ]]; then
        log_success "Verification complete - environment is ready!"
    else
        log_error "Verification complete with $errors errors"
    fi
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

main() {
    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║   Setup Script - Week 13 IoT & Security                 ║${NC}"
    echo -e "${BOLD}║   Academia of Studii Economice - CSIE                        ║${NC}"
    echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    case "${1:-}" in
        --apt|--system)
            install_system_packages
            ;;
        --pip|--python)
            install_python_deps
            ;;
        --certs|--certificates)
            generate_certificates
            ;;
        --passwd|--passwords)
            create_mosquitto_passwords
            ;;
        --check|--verify)
            verify_setup
            ;;
        --help|-h)
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  (without)      Complete setup"
            echo "  --apt       Only packets system (requires sudo)"
            echo "  --pip       Only Python dependencies"
            echo "  --certs     Only certificatese generation TLS"
            echo "  --passwd    Only creare passwords Mosquitto"
            echo "  --check     Configuration verification"
            echo "  --help      Afisare this message"
            ;;
        *)
            # Complete setup
            install_system_packages
            install_python_deps
            generate_certificates
            create_mosquitto_passwords
            verify_setup
            ;;
    esac
    
    echo ""
    log_success "Complete setup!"
    echo ""
}

main "$@"
