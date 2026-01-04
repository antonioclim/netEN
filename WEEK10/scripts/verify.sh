#!/usr/bin/env bash
#==============================================================================
# verify.sh – Verifytion mediu for Week 10
# Computer Networks, ASE Bucharest 2025-2026
#==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS="${GREEN}✓${NC}"
FAIL="${RED}✗${NC}"
WARN="${YELLOW}!${NC}"

errors=0
warnings=0

check_pass() { echo -e "  $PASS $1"; }
check_fail() { echo -e "  $FAIL $1"; ((errors++)); }
check_warn() { echo -e "  $WARN $1"; ((warnings++)); }

#------------------------------------------------------------------------------
# Verifytion software de baza
#------------------------------------------------------------------------------
check_base_software() {
    echo ""
    echo "=== Verifyre Software de Baza ==="
    
    # Python
    if command -v python3 &>/dev/null; then
        version=$(python3 --version 2>&1)
        check_pass "Python: $version"
    else
        check_fail "Python3 nu este instalat"
    fi
    
    # Docker
    if command -v docker &>/dev/null; then
        if docker info &>/dev/null 2>&1; then
            version=$(docker --version)
            check_pass "Docker: $version"
        else
            check_fail "Docker nu ruleaza (porniti Docker Desktop)"
        fi
    else
        check_fail "Docker nu este instalat"
    fi
    
    # Docker Compose
    if docker compose version &>/dev/null 2>&1; then
        version=$(docker compose version --short)
        check_pass "Docker Compose: v$version"
    elif command -v docker-compose &>/dev/null; then
        version=$(docker-compose --version)
        check_pass "Docker Compose (legacy): $version"
    else
        check_fail "Docker Compose nu este instalat"
    fi
    
    # curl
    if command -v curl &>/dev/null; then
        check_pass "curl: instalat"
    else
        check_warn "curl nu este instalat (recomandat)"
    fi
}

#------------------------------------------------------------------------------
# Verifytion packete Python
#------------------------------------------------------------------------------
check_python_packages() {
    echo ""
    echo "=== Verifyre Pachete Python ==="
    
    local packages=("flask" "requests" "paramiko" "dnslib" "pyftpdlib" "pytest")
    
    for pkg in "${packages[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            check_pass "$pkg: instalat"
        else
            check_fail "$pkg: lipseste (pip install $pkg)"
        fi
    done
}

#------------------------------------------------------------------------------
# Verifytion structura filee
#------------------------------------------------------------------------------
check_file_structure() {
    echo ""
    echo "=== Verifyre Structura Fisiere ==="
    
    local required_files=(
        "Makefile"
        "README.md"
        "requirements.txt"
        "docker/docker-compose.yml"
        "python/exercises/ex_10_01_https.py"
        "python/exercises/ex_10_02_rest_levels.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$ROOT_DIR/$file" ]; then
            check_pass "$file"
        else
            check_fail "$file: lipseste"
        fi
    done
    
    # Verifytion directoare
    local required_dirs=("docker" "python" "scripts" "docs" "slides")
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$ROOT_DIR/$dir" ]; then
            check_pass "Directory: $dir/"
        else
            check_warn "Directory: $dir/ lipseste"
        fi
    done
}

#------------------------------------------------------------------------------
# Verifytion services Docker
#------------------------------------------------------------------------------
check_docker_services() {
    echo ""
    echo "=== Verifyre Services Docker ==="
    
    if ! docker info &>/dev/null 2>&1; then
        check_fail "Docker nu ruleaza - saltare verificare services"
        return
    fi
    
    cd "$ROOT_DIR/docker"
    
    # Verifytion if servicesle sunt pornite
    local services=("dns-server" "ssh-server" "ftp-server" "web" "debug")
    
    for service in "${services[@]}"; do
        if docker compose ps --format '{{.Name}}' 2>/dev/null | grep -q "$service"; then
            status=$(docker compose ps --format '{{.Status}}' "$service" 2>/dev/null | head -1)
            if echo "$status" | grep -qi "up"; then
                check_pass "$service: running"
            else
                check_warn "$service: $status"
            fi
        else
            check_warn "$service: not started (run: make docker-up)"
        fi
    done
    
    cd "$ROOT_DIR"
}

#------------------------------------------------------------------------------
# Verifytion conectivitate services
#------------------------------------------------------------------------------
check_connectivity() {
    echo ""
    echo "=== Verifyre Conectivitate ==="
    
    if ! docker info &>/dev/null 2>&1; then
        check_fail "Docker nu ruleaza - saltare verificare conectivitate"
        return
    fi
    
    # Verifytion DNS
    if nc -z localhost 5353 2>/dev/null; then
        check_pass "DNS (port 5353): accesibil"
        
        # Test query DNS
        if command -v dig &>/dev/null; then
            result=$(dig @localhost -p 5353 myservice.lab.local +short +timeout=2 2>/dev/null)
            if [ -n "$result" ]; then
                check_pass "DNS query: myservice.lab.local → $result"
            else
                check_warn "DNS query: niciun raspuns"
            fi
        fi
    else
        check_warn "DNS (port 5353): inaccesibil"
    fi
    
    # Verifytion SSH
    if nc -z localhost 2222 2>/dev/null; then
        check_pass "SSH (port 2222): accesibil"
    else
        check_warn "SSH (port 2222): inaccesibil"
    fi
    
    # Verifytion FTP
    if nc -z localhost 2121 2>/dev/null; then
        check_pass "FTP (port 2121): accesibil"
    else
        check_warn "FTP (port 2121): inaccesibil"
    fi
    
    # Verifytion HTTP
    if nc -z localhost 8000 2>/dev/null; then
        check_pass "HTTP (port 8000): accesibil"
        
        # Test endpoint
        if command -v curl &>/dev/null; then
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
            if [ "$response" = "200" ]; then
                check_pass "HTTP GET /: 200 OK"
            else
                check_warn "HTTP GET /: status $response"
            fi
        fi
    else
        check_warn "HTTP (port 8000): inaccesibil"
    fi
}

#------------------------------------------------------------------------------
# Verifytion certificate
#------------------------------------------------------------------------------
check_certificates() {
    echo ""
    echo "=== Verifyre Certificate SSL ==="
    
    if [ -f "$ROOT_DIR/certs/server.crt" ] && [ -f "$ROOT_DIR/certs/server.key" ]; then
        check_pass "Certificate SSL: prezente"
        
        # Verifytion validitate
        if command -v openssl &>/dev/null; then
            expiry=$(openssl x509 -enddate -noout -in "$ROOT_DIR/certs/server.crt" 2>/dev/null | cut -d= -f2)
            check_pass "Certificat expira: $expiry"
        fi
    else
        check_warn "Certificate SSL: lipsesc (run: make setup)"
    fi
}

#------------------------------------------------------------------------------
# Sumar
#------------------------------------------------------------------------------
print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  SUMAR VERIFICARE"
    echo "═══════════════════════════════════════════════════════════════════"
    
    if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
        echo -e "  ${GREEN}Toate verificarile au trecut!${NC}"
        echo ""
        echo "  Mediul este gata pentru laborator."
        return 0
    elif [ $errors -eq 0 ]; then
        echo -e "  ${YELLOW}Verifyre completa cu $warnings avertismente.${NC}"
        echo ""
        echo "  Mediul poate fi folosit, dar unele functionalitati"
        echo "  ar putea lipsi. Consultati avertismentele de mai sus."
        return 0
    else
        echo -e "  ${RED}Verifyre esuata: $errors erori, $warnings avertismente.${NC}"
        echo ""
        echo "  Rezolvati erorile inainte de a continua."
        return 1
    fi
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  Verifyre Mediu – Saptamana 10                                 ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    
    check_base_software
    check_python_packages
    check_file_structure
    check_certificates
    check_docker_services
    check_connectivity
    
    print_summary
}

main "$@"
