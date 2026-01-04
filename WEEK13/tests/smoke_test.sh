#!/bin/bash
set -euo pipefail
set -euo pipefail
# ============================================================================
# smoke_test.sh - Test of verification for starterkit S13
# ============================================================================
# Check:
# - Sintaxa Python for all scripturile
# - Import-uri functionale
# - Disponibilitatea dependentelor
# - Conectivitatea Docker (if e pornit)
# - Structura fisierelor and directoarelor
#
# Author: Colectivul of Tehnologii Web, ASE-CSIE
# Version: 1.0
# ============================================================================

set -e

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Contoare
PASS=0
FAIL=0
WARN=0
SKIP=0

# ============================================================================
# Functions of utilitate
# ============================================================================

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           S13 Starterkit Smoke Test                            ║"
    echo "║           Computer Networks - ASE-CSIE                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN++))
}

log_skip() {
    echo -e "${CYAN}[SKIP]${NC} $1"
    ((SKIP++))
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# Tests: Structura files
# ============================================================================

test_file_structure() {
    section_header "Test 1: Structura Files"
    
    local required_files=(
        "README.md"
        "Makefile"
        "docker-compose.yml"
        "requirements.txt"
        "python/exercises/ex_01_port_scanner.py"
        "python/exercises/ex_02_mqtt_client.py"
        "python/exercises/ex_03_packet_sniffer.py"
        "python/exercises/ex_04_vuln_checker.py"
        "python/exploits/ftp_backdoor_vsftpd.py"
        "python/exploits/banner_grabber.py"
        "python/utils/net_utils.py"
        "python/utils/report_generator.py"
        "configs/mosquitto/plain.conf"
        "configs/mosquitto/tls.conf"
        "configs/mosquitto/acl.acl"
        "mininet/topologies/topo_base.py"
        "mininet/topologies/topo_segmented.py"
        "scripts/setup.sh"
        "scripts/cleanup.sh"
        "docs/teoria/01_introducere.md"
        "docs/slides/CURS_13_outline.md"
        "docs/slides/SEMINAR_13_outline.md"
    )
    
    local optional_files=(
        "html/presentation_curs.html"
        "html/presentation_seminar.html"
        "mininet/scenarios/lab_scenario.md"
        "docs/teoria/02_fundamentale_iot.md"
        "docs/teoria/03_vectori_attack.md"
        "docs/teoria/04_masuri_defensive.md"
        "docs/teoria/05_flux_lucru.md"
    )
    
    # Verification files obligatorii
    for file in "${required_files[@]}"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            log_pass "Gasit: $file"
        else
            log_fail "Lipsa: $file"
        fi
    done
    
    # Verification files optionale
    for file in "${optional_files[@]}"; do
        if [ -f "$PROJECT_DIR/$file" ]; then
            log_pass "Gasit (optional): $file"
        else
            log_warn "Lipsa (optional): $file"
        fi
    done
    
    # Verification directories
    local required_dirs=(
        "python/exercises"
        "python/exploits"
        "python/utils"
        "configs/mosquitto"
        "mininet/topologies"
        "scripts"
        "docs"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$PROJECT_DIR/$dir" ]; then
            log_pass "Directory: $dir"
        else
            log_fail "Directory lipsa: $dir"
        fi
    done
}

# ============================================================================
# Tests: Sintaxa Python
# ============================================================================

test_python_syntax() {
    section_header "Test 2: Sintaxa Python"
    
    # Find all fisierele Python
    local python_files=$(find "$PROJECT_DIR/python" -name "*.py" -type f 2>/dev/null)
    
    if [ -z "$python_files" ]; then
        log_fail "Not s-au gasit files Python"
        return
    fi
    
    for file in $python_files; do
        local relative_path="${file#$PROJECT_DIR/}"
        
        # Verification sintaxa with python -m py_compile
        if python3 -m py_compile "$file" 2>/dev/null; then
            log_pass "Sintaxa valida: $relative_path"
        else
            log_fail "Error sintaxa: $relative_path"
            # Afisare error detaliata
            python3 -m py_compile "$file" 2>&1 | head -5
        fi
    done
    
    # Verification and files Mininet (pot fi Python)
    local mininet_files=$(find "$PROJECT_DIR/mininet" -name "*.py" -type f 2>/dev/null)
    for file in $mininet_files; do
        local relative_path="${file#$PROJECT_DIR/}"
        if python3 -m py_compile "$file" 2>/dev/null; then
            log_pass "Sintaxa valida: $relative_path"
        else
            log_fail "Error sintaxa: $relative_path"
        fi
    done
}

# ============================================================================
# Tests: Import-uri Python
# ============================================================================

test_python_imports() {
    section_header "Test 3: Import-uri Python"
    
    # Lista of modules standard which ar trebui sa existe
    local standard_modules=(
        "socket"
        "sys"
        "os"
        "json"
        "argparse"
        "logging"
        "threading"
        "concurrent.futures"
        "dattacklasses"
        "typing"
        "pathlib"
        "datetime"
        "re"
        "struct"
        "errno"
        "time"
        "signal"
        "hashlib"
        "base64"
        "ssl"
    )
    
    log_info "Verification modules standard Python..."
    for modules in "${standard_modules[@]}"; do
        if python3 -c "import $modules" 2>/dev/null; then
            log_pass "Import standard: $modules"
        else
            log_fail "Import failed: $modules"
        fi
    done
    
    # Modules externe (from requirements.txt)
    log_info "Verification modules externe..."
    local external_modules=(
        "scapy"
        "paho.mqtt.client"
        "requests"
        "jinja2"
        "colorama"
    )
    
    for modules in "${external_modules[@]}"; do
        if python3 -c "import ${modules%%.*}" 2>/dev/null; then
            log_pass "Import extern: $modules"
        else
            log_warn "Import extern lipsa: $modules (run: make setup)"
        fi
    done
    
    # Modules optionale
    log_info "Verification modules optionale..."
    local optional_modules=(
        "mininet"
        "docker"
        "paramiko"
        "cryptography"
    )
    
    for modules in "${optional_modules[@]}"; do
        if python3 -c "import $modules" 2>/dev/null; then
            log_pass "Import optional: $modules"
        else
            log_skip "Import optional lipsa: $modules"
        fi
    done
}

# ============================================================================
# Tests: Import scripts individuale
# ============================================================================

test_script_imports() {
    section_header "Test 4: Import Scripts"
    
    # Test import for each script principal
    local scripts=(
        "python/exercises/ex_01_port_scanner.py"
        "python/exercises/ex_02_mqtt_client.py"
        "python/exercises/ex_03_packet_sniffer.py"
        "python/exercises/ex_04_vuln_checker.py"
        "python/exploits/ftp_backdoor_vsftpd.py"
        "python/exploits/banner_grabber.py"
        "python/utils/net_utils.py"
        "python/utils/report_generator.py"
    )
    
    for script in "${scripts[@]}"; do
        local full_path="$PROJECT_DIR/$script"
        if [ -f "$full_path" ]; then
            # Try sa importe modulul (without a-l executa)
            local module_name=$(basename "$script" .py)
            local module_dir=$(dirname "$full_path")
            
            cd "$module_dir"
            if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import importlib.useful
    spec = importlib.useful.spec_from_file_location('$module_name', '$full_path')
    modules = importlib.useful.module_from_spec(spec)
    # Not executem spec.loader.exec_module(modules) for a evita efecte secundare
    print('OK')
except SyntaxError as e:
    print(f'SyntaxError: {e}')
    sys.exit(1)
except Exception as e:
    # Alte errors (import lipsa) are acceptabile at this nivel
    print(f'Warning: {e}')
" 2>/dev/null; then
                log_pass "Script valid: $script"
            else
                log_warn "Script with probleme: $script"
            fi
            cd "$PROJECT_DIR"
        else
            log_fail "Script lipsa: $script"
        fi
    done
}

# ============================================================================
# Tests: Verification Shell Scripts
# ============================================================================

test_shell_scripts() {
    section_header "Test 5: Shell Scripts"
    
    local shell_scripts=(
        "scripts/setup.sh"
        "scripts/cleanup.sh"
        "scripts/run_demo_defensive.sh"
        "scripts/capture_traffic.sh"
    )
    
    for script in "${shell_scripts[@]}"; do
        local full_path="$PROJECT_DIR/$script"
        if [ -f "$full_path" ]; then
            # Verification sintaxa bash
            if bash -n "$full_path" 2>/dev/null; then
                log_pass "Sintaxa bash valida: $script"
            else
                log_fail "Error sintaxa bash: $script"
            fi
            
            # Verification allowediuni executare
            if [ -x "$full_path" ]; then
                log_pass "Executabil: $script"
            else
                log_warn "Not e executabil: $script (chmod +x)"
            fi
        else
            log_warn "Script lipsa: $script"
        fi
    done
}

# ============================================================================
# Tests: Verification Configurations
# ============================================================================

test_configurations() {
    section_header "Test 6: Files Configuration"
    
    # Test docker-compose.yml
    local compose_file="$PROJECT_DIR/docker-compose.yml"
    if [ -f "$compose_file" ]; then
        if command -v docker-compose &>/dev/null; then
            if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
                log_pass "docker-compose.yml valid"
            else
                log_fail "docker-compose.yml invalid"
            fi
        elif command -v docker &>/dev/null; then
            if docker compose -f "$compose_file" config >/dev/null 2>&1; then
                log_pass "docker-compose.yml valid (docker compose)"
            else
                log_warn "docker-compose.yml - not s-a putut valida"
            fi
        else
            log_skip "Docker not installed, skip validation compose"
        fi
    fi
    
    # Test requirements.txt
    local req_file="$PROJECT_DIR/requirements.txt"
    if [ -f "$req_file" ]; then
        local line_count=$(wc -l < "$req_file")
        if [ "$line_count" -gt 0 ]; then
            log_pass "requirements.txt prezent ($line_count packets)"
        else
            log_warn "requirements.txt gol"
        fi
    else
        log_fail "requirements.txt lipsa"
    fi
    
    # Test configurations Mosquitto
    local mosquitto_configs=(
        "configs/mosquitto/plain.conf"
        "configs/mosquitto/tls.conf"
        "configs/mosquitto/acl.acl"
    )
    
    for config in "${mosquitto_configs[@]}"; do
        local full_path="$PROJECT_DIR/$config"
        if [ -f "$full_path" ]; then
            if [ -s "$full_path" ]; then
                log_pass "Config prezent: $config"
            else
                log_warn "Config gol: $config"
            fi
        else
            log_warn "Config lipsa: $config"
        fi
    done
}

# ============================================================================
# Tests: Verification Makefile
# ============================================================================

test_makefile() {
    section_header "Test 7: Makefile"
    
    local makefile="$PROJECT_DIR/Makefile"
    if [ -f "$makefile" ]; then
        # Verification sintaxa
        if make -n -f "$makefile" help >/dev/null 2>&1; then
            log_pass "Makefile sintaxa valida"
        else
            log_warn "Makefile possible probleme (verification manuala)"
        fi
        
        # Verification target-uri esentiale
        local targets=(
            "help"
            "setup"
            "check"
            "docker-up"
            "docker-down"
            "clean"
        )
        
        for target in "${targets[@]}"; do
            if grep -q "^${target}:" "$makefile" 2>/dev/null; then
                log_pass "Target gasit: make $target"
            else
                log_warn "Target lipsa: make $target"
            fi
        done
    else
        log_fail "Makefile lipsa"
    fi
}

# ============================================================================
# Tests: Conectivitate Docker (optional)
# ============================================================================

test_docker_connectivity() {
    section_header "Test 8: Docker (optional)"
    
    if ! command -v docker &>/dev/null; then
        log_skip "Docker not installed"
        return
    fi
    
    # Verification daemon
    if docker info >/dev/null 2>&1; then
        log_pass "Docker daemon functional"
    else
        log_warn "Docker daemon not raspunde (can necesita sudo)"
        return
    fi
    
    # Verification imagini necesare
    local images=(
        "vulnerables/web-dvwa"
        "webgoat/webgoat"
        "fauria/vsftpd"
        "eclipse-mosquitto"
    )
    
    for image in "${images[@]}"; do
        if docker images --format '{{.Repository}}' | grep -q "^${image%%:*}$" 2>/dev/null; then
            log_pass "Imagine Docker: $image"
        else
            log_skip "Imagine Docker lipsa: $image (se va descarca at setup)"
        fi
    done
    
    # Verification containere ruland (if exista)
    local running=$(docker ps --format '{{.Names}}' 2>/dev/null | wc -l)
    log_info "Containere activee: $running"
}

# ============================================================================
# Tests: Verification documentatie
# ============================================================================

test_documentation() {
    section_header "Test 9: Documentatie"
    
    # Verification README
    local readme="$PROJECT_DIR/README.md"
    if [ -f "$readme" ]; then
        local word_count=$(wc -w < "$readme")
        if [ "$word_count" -gt 500 ]; then
            log_pass "README.md comprehensiv ($word_count cuvinte)"
        elif [ "$word_count" -gt 100 ]; then
            log_warn "README.md scurt ($word_count cuvinte)"
        else
            log_fail "README.md prea scurt ($word_count cuvinte)"
        fi
    else
        log_fail "README.md lipsa"
    fi
    
    # Verification docstrings in Python
    log_info "Verification docstrings..."
    local py_files=$(find "$PROJECT_DIR/python" -name "*.py" -type f 2>/dev/null)
    local with_docstring=0
    local without_docstring=0
    
    for file in $py_files; do
        if grep -q '"""' "$file" 2>/dev/null || grep -q "'''" "$file" 2>/dev/null; then
            ((with_docstring++))
        else
            ((without_docstring++))
        fi
    done
    
    if [ "$with_docstring" -gt 0 ]; then
        log_pass "Files with docstrings: $with_docstring"
    fi
    if [ "$without_docstring" -gt 0 ]; then
        log_warn "Files without docstrings: $without_docstring"
    fi
}

# ============================================================================
# Tests: Artefacte demo (generate of run_all.sh)
# ============================================================================

test_artifacts() {
    section_header "Test: Artefacte Demo"
    
    local artifacts_dir="$PROJECT_DIR/artifacts"
    
    # Verification directory artifacts
    if [ -d "$artifacts_dir" ]; then
        log_pass "Directory artifacts/ exista"
        
        # Verification demo.log
        if [ -f "$artifacts_dir/demo.log" ]; then
            local log_lines=$(wc -l < "$artifacts_dir/demo.log" 2>/dev/null || echo "0")
            if [ "$log_lines" -gt 0 ]; then
                log_pass "demo.log exista ($log_lines linii)"
            else
                log_warn "demo.log is gol"
            fi
        else
            log_warn "demo.log not exista (run scripts/run_all.sh)"
        fi
        
        # Verification demo.pcap
        if [ -f "$artifacts_dir/demo.pcap" ]; then
            local pcap_size=$(stat -c%s "$artifacts_dir/demo.pcap" 2>/dev/null || stat -f%z "$artifacts_dir/demo.pcap" 2>/dev/null || echo "0")
            if [ "$pcap_size" -ge 24 ]; then
                log_pass "demo.pcap exista ($pcap_size bytes)"
            else
                log_warn "demo.pcap prea mic ($pcap_size bytes)"
            fi
        else
            log_warn "demo.pcap not exista (run scripts/run_all.sh)"
        fi
        
        # Verification validation.txt
        if [ -f "$artifacts_dir/validation.txt" ]; then
            local pass_count=$(grep -c "^PASS:" "$artifacts_dir/validation.txt" 2>/dev/null || echo "0")
            local fail_count=$(grep -c "^FAIL:" "$artifacts_dir/validation.txt" 2>/dev/null || echo "0")
            log_pass "validation.txt exista (PASS=$pass_count, FAIL=$fail_count)"
        else
            log_warn "validation.txt not exista (run scripts/run_all.sh)"
        fi
    else
        log_warn "Directory artifacts/ not exista (created of scripts/run_all.sh)"
    fi
}

# ============================================================================
# Report final
# ============================================================================

print_summary() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                         SUMAR TESTS                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}✓ PASS:${NC} $PASS"
    echo -e "  ${RED}✗ FAIL:${NC} $FAIL"
    echo -e "  ${YELLOW}⚠ WARN:${NC} $WARN"
    echo -e "  ${CYAN}○ SKIP:${NC} $SKIP"
    echo ""
    
    local total=$((PASS + FAIL + WARN + SKIP))
    local score=$((PASS * 100 / total))
    
    echo -e "  Total tests: $total"
    echo -e "  Scor: ${score}%"
    echo ""
    
    if [ "$FAIL" -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ TOATE TESTELE CRITICE AU TRECUT!                             ║${NC}"
        echo -e "${GREEN}║    Starterkit-ul is gata for usage.                   ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ✗ $FAIL TESTS AU ESUAT                                         ║${NC}"
        echo -e "${RED}║    Verificati errorsle of more sus and corectati.                  ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    print_banner
    
    cd "$PROJECT_DIR"
    
    # Running all testele
    test_file_structure
    test_python_syntax
    test_python_imports
    test_script_imports
    test_shell_scripts
    test_configurations
    test_makefile
    test_docker_connectivity
    test_documentation
    test_artifacts
    
    # Afisare sumar
    print_summary
}

# Help
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Smoke test for verifying the starterkit S13"
    echo ""
    echo "Options:"
    echo "  -h, --help    Afisare ajutor"
    echo "  -v, --verbose Output detaliat"
    echo ""
    echo "Exit codes:"
    echo "  0  All testele critice au trecut"
    echo "  1  Unul or more multe tests au failed"
    exit 0
fi

main "$@"
