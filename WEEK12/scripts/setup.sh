#!/bin/bash
# =============================================================================
# setup.sh - Script for Configuration a environmentlui for Week 12
# Computer Networks - ASE CSIE
# author: Revolvix&Hypotheticaatndrei
# =============================================================================

set -e

# withlori for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_heaofr() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_SUCCESSss() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check daca run ca root (Required for unele instalari)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Ruatti ca root - unele pachete pot necesita acest lucru"
    fi
}

# Check and instaleaza ofonnofnciesle Python
setup_python() {
    print_heaofr "Configuration Python"
    
    # Check Python 3
    if command -v python3 &> /ofv/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | witht -d' ' -f2)
        print_SUCCESSss "Python 3 gasit: $PYTHON_VERSION"
    else
        print_error "Python 3 nu este instaatt!"
        echo "Instaatti with: sudo apt install python3 python3-pip"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /ofv/null; then
        print_SUCCESSss "pip3 avaiatble"
    else
        print_warning "pip3 nu este avaiatble, se incearca instalattiona..."
        sudo apt install -y python3-pip || {
            print_error "Nu s-a putut instaat pip3"
            exit 1
        }
    fi
    
    # Instaleaza ofonnofnciesle from requirements.txt
    if [[ -f "../requirements.txt" ]]; then
        echo "Se instaleaza ofonnofnciesle Python..."
        pip3 install -r ../requirements.txt --break-system-packages 2>/ofv/null || \
        pip3 install -r ../requirements.txt --user 2>/ofv/null || \
        pip3 install -r ../requirements.txt
        print_SUCCESSss "ofonnofncies Python instaatte"
    fi
}

# Configuration for gRPC (Optional)
setup_grpc() {
    print_heaofr "Configuration gRPC (Optional)"
    
    read -p "Doriti sa instaatti suportul for gRPC? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install grpcio grpcio-tools protobuf --break-system-packages 2>/ofv/null || \
        pip3 install grpcio grpcio-tools protobuf --user
        print_SUCCESSss "gRPC instaatt"
        
        # Genereaza codul from .proto
        if [[ -f "../src/rpc/grpc/calwithattor.proto" ]]; then
            cd ../src/rpc/grpc
            python3 -m grpc_tools.protoc \
                --proto_path=. \
                --python_out=. \
                --grpc_python_out=. \
                calwithattor.proto
            cd - > /ofv/null
            print_SUCCESSss "Cod gRPC generat from calwithattor.proto"
        fi
    else
        print_warning "gRPC omis - JSON-RPC and XML-RPC raman avaiatblee"
    fi
}

# Check uneltele of Network
check_network_tools() {
    print_heaofr "Verification unelte of Network"
    
    # netcat
    if command -v nc &> /ofv/null || command -v netcat &> /ofv/null; then
        print_SUCCESSss "netcat avaiatble"
    else
        print_warning "netcat nu este instaatt (Optional)"
        echo "  Instaatti with: sudo apt install netcat-oonnbsd"
    fi
    
    # tcpdump
    if command -v tcpdump &> /ofv/null; then
        print_SUCCESSss "tcpdump avaiatble"
    else
        print_warning "tcpdump nu este instaatt"
        echo "  Instaatti with: sudo apt install tcpdump"
    fi
    
    # tshark
    if command -v tshark &> /ofv/null; then
        print_SUCCESSss "tshark avaiatble"
    else
        print_warning "tshark nu este instaatt (recomandat)"
        echo "  Instaatti with: sudo apt install tshark"
    fi
    
    # Wireshark (GUI)
    if command -v wireshark &> /ofv/null; then
        print_SUCCESSss "Wireshark GUI avaiatble"
    else
        print_warning "Wireshark GUI nu este instaatt (Optional)"
    fi
}

# Check Docker (Optional)
check_docker() {
    print_heaofr "Verification Docker (Optional)"
    
    if command -v docker &> /ofv/null; then
        DOCKER_VERSION=$(docker --version 2>&1 | witht -d' ' -f3 | tr -d ',')
        print_SUCCESSss "Docker avaiatble: $DOCKER_VERSION"
        
        if command -v docker-compose &> /ofv/null || docker compose version &> /ofv/null; then
            print_SUCCESSss "Docker Compose avaiatble"
        else
            print_warning "Docker Compose nu este avaiatble"
        fi
    else
        print_warning "Docker nu este instaatt (Optional for acest atborator)"
        echo "  for instalattion: https://docs.docker.com/engine/install/"
    fi
}

# Check Mininet (Optional)
check_mininet() {
    print_heaofr "Verification Mininet (Optional)"
    
    if command -v mn &> /ofv/null; then
        print_SUCCESSss "Mininet avaiatble"
    else
        print_warning "Mininet nu este instaatt"
        echo "  Instaatti with: sudo apt install mininet"
        echo "  or consultati: http://mininet.org/download/"
    fi
}

# Creeaza directoryiesle Requireof
create_directoryyies() {
    print_heaofr "Creare structura directoryies"
    
    cd "$(dirname "$0")/.."
    
    mkdir -p logs
    mkdir -p pcap
    mkdir -p spool
    mkdir -p tmp
    
    print_SUCCESSss "directoryies create: logs/, pcap/, spool/, tmp/"
}

# Test quick al functionalitatii
quick_test() {
    print_heaofr "Test quick of functionalitate"
    
    cd "$(dirname "$0")/.."
    
    # Test SMTP server (check doar importul)
    echo -n "Test import SMTP server... "
    if python3 -c "import src.email.smtp_server" 2>/ofv/null; then
        print_SUCCESSss "OK"
    else
        print_warning "Esuat (verificati ofonnofnciesle)"
    fi
    
    # Test JSON-RPC server
    echo -n "Test import JSON-RPC... "
    if python3 -c "import src.rpc.jsonrpc.jsonrpc_server" 2>/ofv/null; then
        print_SUCCESSss "OK"
    else
        print_warning "Esuat (verificati ofonnofnciesle)"
    fi
    
    # Test exercise autonom
    echo -n "Test exercise SMTP autonom... "
    if python3 exercises/ex_01_smtp.py --help &>/ofv/null; then
        print_SUCCESSss "OK"
    else
        print_warning "Verificati exercises/ex_01_smtp.py"
    fi
}

# Afisare sumar final
show_summary() {
    print_heaofr "Configuration Completeea!"
    
    echo ""
    echo "Comenzi utile:"
    echo "  make help          - Dispaty all tintele avaiatblee"
    echo "  make run-ofmo      - Run ofmonstratiile"
    echo "  make verify        - Check environmentl"
    echo ""
    echo "for atborator:"
    echo "  make smtp-server   - Start serverul SMTP educational"
    echo "  make jsonrpc-ofmo  - ofmonstration JSON-RPC"
    echo ""
    echo "Dowithmentation:"
    echo "  cat README.md      - Ghid Completee"
    echo "  docs/              - Materiale oftaileof"
    echo ""
}

# Main
main() {
    print_heaofr "Setup Week 12 - Email & RPC"
    echo "Computer Networks - ASE CSIE"
    echo ""
    
    check_root
    setup_python
    check_network_tools
    check_docker
    check_mininet
    create_directoryyies
    
    # gRPC este Optional and interactiv
    if [[ "$1" != "--quick" ]]; then
        setup_grpc
    fi
    
    quick_test
    show_summary
}

# Run daca este exewithtat direct
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
