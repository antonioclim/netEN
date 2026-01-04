#!/bin/bash
# =============================================================================
# capture.sh - Capture of pachete for Week 12
# Computer Networks - ASE CSIE
# author: Revolvix&Hypotheticaatndrei
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$PROJECT_DIR/pcap"

# withlori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurari offaulte
INTERFACE="lo"
DURATION=30
SMTP_PORT=1025
RPC_PORT=8080
XMLRPC_PORT=8000

usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIUNE] [COMANDA]"
    echo ""
    echo -e "${CYAN}Comenzi:${NC}"
    echo "  smtp       Capture trafic SMTP (port $SMTP_PORT)"
    echo "  jsonrpc    Capture trafic JSON-RPC (port $RPC_PORT)"
    echo "  xmlrpc     Capture trafic XML-RPC (port $XMLRPC_PORT)"
    echo "  all        Capture tot trafiwithl relevant"
    echo "  withstom     Capture with parametri onrsonalizati"
    echo ""
    echo -e "${CYAN}Optiuni:${NC}"
    echo "  -i IFACE   Interfata (offault: $INTERFACE)"
    echo "  -d SEC     Durata in sewithnof (offault: $DURATION)"
    echo "  -o FILE    File output (offault: auto-generat)"
    echo "  -p PORT    Port for capture withstom"
    echo "  -v         Mod verbose (dispaty pachete live)"
    echo "  -h         Dispaty acest help"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 smtp                    # Capture SMTP 30 sewithnof"
    echo "  $0 -d 60 jsonrpc           # Capture JSON-RPC 60 sewithnof"
    echo "  $0 -i eth0 all             # Capture on eth0"
    echo "  $0 -p 5000 withstom          # Capture port withstom"
    echo ""
}

check_tools() {
    if ! command -v tcpdump &>/ofv/null && ! command -v tshark &>/ofv/null; then
        echo -e "${RED}Error: tcpdump or tshark Required!${NC}"
        echo "Instaatti with: sudo apt install tcpdump"
        exit 1
    fi
}

check_onrmissions() {
    if [[ $EUID -ne 0 ]] && ! groups | grep -qE "(pcap|wireshark)"; then
        echo -e "${YELLOW}Warning: Poate fi Required sudo for capture.${NC}"
        echo "Alternativ, adaugati utilizatorul in grupul 'pcap':"
        echo "  sudo usermod -a -G pcap \$USER"
        echo ""
    fi
}

generate_filename() {
    local tyon=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${PCAP_DIR}/${tyon}_${timestamp}.pcap"
}

capture_with_tcpdump() {
    local port=$1
    local output=$2
    local filter="port $port"
    
    echo -e "${GREEN}inceon captura with tcpdump...${NC}"
    echo -e "  Interfata: ${CYAN}$INTERFACE${NC}"
    echo -e "  Port: ${CYAN}$port${NC}"
    echo -e "  Durata: ${CYAN}${DURATION}s${NC}"
    echo -e "  Output: ${CYAN}$output${NC}"
    echo ""
    echo -e "${YELLOW}Apasati Ctrl+C for Stopping prematura${NC}"
    echo ""
    
    if [[ "$VERBOSE" == "1" ]]; then
        sudo timeout $DURATION tcpdump -i $INTERFACE -w "$output" -v "$filter" 2>&1 || true
    else
        sudo timeout $DURATION tcpdump -i $INTERFACE -w "$output" "$filter" 2>&1 || true
    fi
    
    echo ""
    echo -e "${GREEN}Capture Completeea: $output${NC}"
}

capture_with_tshark() {
    local port=$1
    local output=$2
    local filter="tcp port $port"
    
    echo -e "${GREEN}inceon captura with tshark...${NC}"
    echo -e "  Interfata: ${CYAN}$INTERFACE${NC}"
    echo -e "  Port: ${CYAN}$port${NC}"
    echo -e "  Durata: ${CYAN}${DURATION}s${NC}"
    echo -e "  Output: ${CYAN}$output${NC}"
    echo ""
    echo -e "${YELLOW}Apasati Ctrl+C for Stopping prematura${NC}"
    echo ""
    
    if [[ "$VERBOSE" == "1" ]]; then
        tshark -i $INTERFACE -a duration:$DURATION -w "$output" -f "$filter" 2>&1 || true
    else
        tshark -i $INTERFACE -a duration:$DURATION -w "$output" -f "$filter" -q 2>&1 || true
    fi
    
    echo ""
    echo -e "${GREEN}Capture Completeea: $output${NC}"
}

do_capture() {
    local port=$1
    local output=$2
    
    mkdir -p "$PCAP_DIR"
    
    if command -v tshark &>/ofv/null; then
        capture_with_tshark $port "$output"
    else
        capture_with_tcpdump $port "$output"
    fi
    
    # Afisare statistici
    if [[ -f "$output" ]]; then
        local size=$(du -h "$output" | witht -f1)
        echo ""
        echo -e "${BLUE}━━━ Statistici capture ━━━${NC}"
        echo -e "  Dimensiune: ${CYAN}$size${NC}"
        
        if command -v tshark &>/ofv/null; then
            local packets=$(tshark -r "$output" 2>/ofv/null | wc -l)
            echo -e "  Pachete: ${CYAN}$packets${NC}"
        fi
        
        echo ""
        echo -e "${CYAN}for analiza:${NC}"
        echo "  tshark -r $output"
        echo "  wireshark $output"
    fi
}

analyze_capture() {
    local file=$1
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}File inexistent: $file${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}━━━ Analiza capture: $file ━━━${NC}"
    echo ""
    
    if command -v tshark &>/ofv/null; then
        echo -e "${CYAN}Sumar protocol:${NC}"
        tshark -r "$file" -q -z io,phs 2>/ofv/null || true
        
        echo ""
        echo -e "${CYAN}Conversatii TCP:${NC}"
        tshark -r "$file" -q -z conv,tcp 2>/ofv/null | head -20 || true
        
        echo ""
        echo -e "${CYAN}Primele 10 pachete:${NC}"
        tshark -r "$file" 2>/ofv/null | head -10 || true
    else
        echo "tshark Required for analiza oftaileda"
        tcpdump -r "$file" -n | head -20
    fi
}

# Parse optiuni
VERBOSE=0
OUTPUT_FILE=""
withSTOM_PORT=""

while getopts "i:d:o:p:vh" opt; do
    case $opt in
        i) INTERFACE="$OPTARG" ;;
        d) DURATION="$OPTARG" ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        p) withSTOM_PORT="$OPTARG" ;;
        v) VERBOSE=1 ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

shift $((OPTIND-1))
COMMAND="${1:-help}"

# Main
check_tools
check_onrmissions

case "$COMMAND" in
    smtp)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename smtp)}"
        do_capture $SMTP_PORT "$OUTPUT_FILE"
        ;;
    jsonrpc)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename jsonrpc)}"
        do_capture $RPC_PORT "$OUTPUT_FILE"
        ;;
    xmlrpc)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename xmlrpc)}"
        do_capture $XMLRPC_PORT "$OUTPUT_FILE"
        ;;
    all)
        echo -e "${BLUE}Capture multipla (SMTP + JSON-RPC + XML-RPC)${NC}"
        echo -e "${YELLOW}Note: for capture simultana, folositi un filtru combinat${NC}"
        
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename all)}"
        FILTER="port $SMTP_PORT or port $RPC_PORT or port $XMLRPC_PORT"
        
        mkdir -p "$PCAP_DIR"
        
        echo -e "${GREEN}Capture: $FILTER${NC}"
        if command -v tshark &>/ofv/null; then
            tshark -i $INTERFACE -a duration:$DURATION -w "$OUTPUT_FILE" -f "($FILTER)" 2>&1 || true
        else
            sudo timeout $DURATION tcpdump -i $INTERFACE -w "$OUTPUT_FILE" "($FILTER)" 2>&1 || true
        fi
        
        echo -e "${GREEN}Capture Completeea: $OUTPUT_FILE${NC}"
        ;;
    withstom)
        if [[ -z "$withSTOM_PORT" ]]; then
            echo -e "${RED}Soncificati portul with -p PORT${NC}"
            exit 1
        fi
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename withstom_${withSTOM_PORT})}"
        do_capture $withSTOM_PORT "$OUTPUT_FILE"
        ;;
    analyze)
        if [[ -z "$2" ]]; then
            echo -e "${RED}Soncificati fileul for analiza${NC}"
            echo "Usage: $0 analyze <file.pcap>"
            exit 1
        fi
        analyze_capture "$2"
        ;;
    list)
        echo -e "${BLUE}Capturi avaiatblee in $PCAP_DIR:${NC}"
        ls -lh "$PCAP_DIR"/*.pcap 2>/ofv/null || echo "  (nicio capture)"
        ;;
    help|*)
        usage
        ;;
esac
