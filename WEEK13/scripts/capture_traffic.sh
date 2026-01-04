#!/bin/bash
set -euo pipefail
set -euo pipefail
# ============================================================================
# capture_traffic.sh - Wrapper for capturarea trafficului of network
# ============================================================================
# Faciliteaza capturarea and analiza trafficului for laboratorul S13:
# - tcpdump wrapper with filtre predefinite
# - Capture for protocols specifice (MQTT, FTP, HTTP)
# - Export in multiple formate (pcap, text)
# - Statistici in time real
#
# Author: Colectivul of Tehnologii Web, ASE-CSIE
# ============================================================================

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/captures"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Configuration default
INTERFACE="any"
DURATION=60
COUNT=0
FILTER=""
OUTPUT_FILE=""
VERBOSE=false
STATS_ONLY=false
PROTOCOL=""

# ============================================================================
# Filtre predefinite
# ============================================================================

declare -A FILTERS=(
    # MQTT
    ["mqtt"]="port 1883 or port 8883"
    ["mqtt-plain"]="port 1883"
    ["mqtt-tls"]="port 8883"
    
    # FTP
    ["ftp"]="port 21 or port 20"
    ["ftp-backdoor"]="port 21 or port 6200"
    
    # HTTP/HTTPS
    ["http"]="port 80 or port 8080"
    ["https"]="port 443"
    ["web"]="port 80 or port 443 or port 8080"
    
    # DNS
    ["dns"]="port 53"
    
    # SSH
    ["ssh"]="port 22"
    
    # Docker network
    ["docker"]="net 172.20.0.0/24"
    
    # Mininet IoT zone
    ["iot-zone"]="net 10.0.1.0/24"
    
    # Mininet MGMT zone
    ["mgmt-zone"]="net 10.0.2.0/24"
    
    # Combined pentest
    ["pentest"]="port 21 or port 22 or port 80 or port 1883 or port 6200"
    
    # Combined IoT
    ["iot"]="port 1883 or port 8883 or port 5683"
    
    # TCP SYN (for scan detection)
    ["syn-scan"]="tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) = 0"
    
    # ICMP
    ["icmp"]="icmp"
    
    # ARP
    ["arp"]="arp"
)

# ============================================================================
# Functions of utilitate
# ============================================================================

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           S13 Traffic Capture Tool                             ║"
    echo "║           Computer Networks - ASE-CSIE                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script requires root privileges for packet capture"
        log_info "Please run: sudo $0 $*"
        exit 1
    fi
}

check_dependencies() {
    local missing=0
    
    if ! command -v tcpdump &> /dev/null; then
        log_error "tcpdump not found"
        ((missing++))
    fi
    
    if [ "$missing" -gt 0 ]; then
        log_info "Install with: sudo apt-get install tcpdump"
        exit 1
    fi
}

list_interfaces() {
    echo -e "${CYAN}Available network interfaces:${NC}"
    echo ""
    
    # Lista interfaces with IP-uri
    ip -br addr show | while read -r line; do
        iface=$(echo "$line" | awk '{print $1}')
        state=$(echo "$line" | awk '{print $2}')
        addr=$(echo "$line" | awk '{print $3}')
        
        if [ "$state" = "UP" ]; then
            echo -e "  ${GREEN}$iface${NC} ($state) - $addr"
        else
            echo -e "  ${YELLOW}$iface${NC} ($state)"
        fi
    done
    
    echo ""
    echo "Common interfaces for this lab:"
    echo "  docker0     - Docker bridge network"
    echo "  eth0        - Primary network interface"
    echo "  any         - Capture on all interfaces"
}

list_filters() {
    echo -e "${CYAN}Predefined capture filters:${NC}"
    echo ""
    
    echo "MQTT:"
    echo "  mqtt           - All MQTT traffic (1883, 8883)"
    echo "  mqtt-plain     - Plaintext MQTT only (1883)"
    echo "  mqtt-tls       - TLS MQTT only (8883)"
    echo ""
    
    echo "FTP:"
    echo "  ftp            - Standard FTP (20, 21)"
    echo "  ftp-backdoor   - FTP + backdoor port (21, 6200)"
    echo ""
    
    echo "Web:"
    echo "  http           - HTTP (80, 8080)"
    echo "  https          - HTTPS (443)"
    echo "  web            - All web traffic"
    echo ""
    
    echo "Network:"
    echo "  docker         - Docker network (172.20.0.0/24)"
    echo "  iot-zone       - Mininet IoT zone (10.0.1.0/24)"
    echo "  mgmt-zone      - Mininet MGMT zone (10.0.2.0/24)"
    echo ""
    
    echo "Security:"
    echo "  pentest        - Common pentest ports"
    echo "  iot            - IoT protocols"
    echo "  syn-scan       - Detect SYN scans"
    echo ""
    
    echo "Other:"
    echo "  dns            - DNS traffic"
    echo "  ssh            - SSH traffic"
    echo "  icmp           - ICMP/ping"
    echo "  arp            - ARP traffic"
}

# ============================================================================
# Functions of capture
# ============================================================================

setup_output() {
    mkdir -p "$OUTPUT_DIR"
    
    if [ -z "$OUTPUT_FILE" ]; then
        local prefix="capture"
        if [ -n "$PROTOCOL" ]; then
            prefix="$PROTOCOL"
        fi
        OUTPUT_FILE="$OUTPUT_DIR/${prefix}_${TIMESTAMP}.pcap"
    fi
}

build_tcpdump_command() {
    local cmd="tcpdump"
    
    # Interface
    cmd="$cmd -i $INTERFACE"
    
    # Number of packets or duration
    if [ "$COUNT" -gt 0 ]; then
        cmd="$cmd -c $COUNT"
    fi
    
    # Output file
    cmd="$cmd -w $OUTPUT_FILE"
    
    # Verbose
    if [ "$VERBOSE" = true ]; then
        cmd="$cmd -v"
    fi
    
    # Snapshot length (capturem tot packetul)
    cmd="$cmd -s 0"
    
    # Timestamp precision
    cmd="$cmd --time-stamp-precision=micro"
    
    # Filtru BPF
    if [ -n "$FILTER" ]; then
        cmd="$cmd '$FILTER'"
    fi
    
    echo "$cmd"
}

run_capture() {
    setup_output
    
    local filter_display="$FILTER"
    if [ -z "$filter_display" ]; then
        filter_display="(no filter - all traffic)"
    fi
    
    echo ""
    log_info "Starting packet capture..."
    echo ""
    echo "Configuration:"
    echo "  Interface:  $INTERFACE"
    echo "  Filter:     $filter_display"
    echo "  Output:     $OUTPUT_FILE"
    if [ "$COUNT" -gt 0 ]; then
        echo "  Packets:    $COUNT"
    else
        echo "  Duration:   ${DURATION}s (or Ctrl+C to stop)"
    fi
    echo ""
    
    log_warn "Press Ctrl+C to stop capture"
    echo ""
    
    # Construire command
    local cmd
    cmd=$(build_tcpdump_command)
    
    if [ "$VERBOSE" = true ]; then
        log_info "Running: $cmd"
    fi
    
    # Capture with timeout if e specificata duration
    if [ "$DURATION" -gt 0 ] && [ "$COUNT" -eq 0 ]; then
        timeout "$DURATION" bash -c "$cmd" || true
    else
        eval "$cmd"
    fi
    
    echo ""
    log_info "Capture complete!"
    
    # Statistici
    if [ -f "$OUTPUT_FILE" ]; then
        local size=$(du -h "$OUTPUT_FILE" | cut -f1)
        local packets=$(tcpdump -r "$OUTPUT_FILE" 2>/dev/null | wc -l)
        echo ""
        echo "Statistics:"
        echo "  File size:  $size"
        echo "  Packets:    $packets"
        echo ""
        log_info "Output saved to: $OUTPUT_FILE"
    fi
}

run_live_stats() {
    log_info "Running live statistics mode..."
    echo ""
    
    local filter_display="$FILTER"
    if [ -z "$filter_display" ]; then
        filter_display="(no filter)"
    fi
    
    echo "Interface: $INTERFACE"
    echo "Filter:    $filter_display"
    echo ""
    log_warn "Press Ctrl+C to stop"
    echo ""
    
    # tcpdump in mod statistici
    if [ -n "$FILTER" ]; then
        tcpdump -i "$INTERFACE" -q -n "$FILTER" 2>/dev/null | while read -r line; do
            echo "$line"
        done
    else
        tcpdump -i "$INTERFACE" -q -n 2>/dev/null | while read -r line; do
            echo "$line"
        done
    fi
}

analyze_capture() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi
    
    echo ""
    log_info "Analyzing capture file: $file"
    echo ""
    
    # Statistici generale
    echo -e "${CYAN}=== General Statistics ===${NC}"
    tcpdump -r "$file" -q 2>/dev/null | wc -l | xargs -I {} echo "Total packets: {}"
    echo ""
    
    # Statistici per protocol
    echo -e "${CYAN}=== Protocol Distribution ===${NC}"
    tcpdump -r "$file" -n 2>/dev/null | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -10
    echo ""
    
    # Top source IPs
    echo -e "${CYAN}=== Top Source IPs ===${NC}"
    tcpdump -r "$file" -n 2>/dev/null | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -5
    echo ""
    
    # Top destination IPs
    echo -e "${CYAN}=== Top Destination IPs ===${NC}"
    tcpdump -r "$file" -n 2>/dev/null | awk '{print $5}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head -5
    echo ""
    
    # Ports
    echo -e "${CYAN}=== Top Destination Ports ===${NC}"
    tcpdump -r "$file" -n 2>/dev/null | grep -oP '\.\d+:' | tr -d '.:' | sort | uniq -c | sort -rn | head -10
    echo ""
    
    # MQTT specific (if e traffic MQTT)
    local mqtt_count=$(tcpdump -r "$file" -n 'port 1883 or port 8883' 2>/dev/null | wc -l)
    if [ "$mqtt_count" -gt 0 ]; then
        echo -e "${CYAN}=== MQTT Traffic ===${NC}"
        echo "MQTT packets: $mqtt_count"
        
        # Plaintext vs TLS
        local plain=$(tcpdump -r "$file" -n 'port 1883' 2>/dev/null | wc -l)
        local tls=$(tcpdump -r "$file" -n 'port 8883' 2>/dev/null | wc -l)
        echo "  Plaintext (1883): $plain"
        echo "  TLS (8883):       $tls"
        echo ""
    fi
    
    # FTP specific
    local ftp_count=$(tcpdump -r "$file" -n 'port 21 or port 20' 2>/dev/null | wc -l)
    if [ "$ftp_count" -gt 0 ]; then
        echo -e "${CYAN}=== FTP Traffic ===${NC}"
        echo "FTP packets: $ftp_count"
        
        # Check for backdoor port
        local backdoor=$(tcpdump -r "$file" -n 'port 6200' 2>/dev/null | wc -l)
        if [ "$backdoor" -gt 0 ]; then
            echo -e "${RED}  WARNING: Backdoor port 6200 detected: $backdoor packets${NC}"
        fi
        echo ""
    fi
}

convert_to_text() {
    local file="$1"
    local output="${file%.pcap}.txt"
    
    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        exit 1
    fi
    
    log_info "Converting to text format..."
    tcpdump -r "$file" -nn > "$output"
    log_info "Output: $output"
}

# ============================================================================
# Help and parsare arguments
# ============================================================================

show_help() {
    echo "Usage: sudo $0 [OPTIONS]"
    echo ""
    echo "Network traffic capture tool for Week 13 Lab"
    echo ""
    echo "Options:"
    echo "  -i, --interface IFACE    Network interface (default: any)"
    echo "  -f, --filter FILTER      BPF filter expression"
    echo "  -p, --protocol PROTO     Predefined filter (mqtt, ftp, http, etc.)"
    echo "  -o, --output FILE        Output file path"
    echo "  -c, --count N            Capture N packets then stop"
    echo "  -d, --duration SECS      Capture for N seconds (default: 60)"
    echo "  -v, --verbose            Verbose output"
    echo "  -s, --stats              Live statistics mode (no file)"
    echo "  -a, --analyze FILE       Analyze existing capture file"
    echo "  -t, --to-text FILE       Convert pcap to text"
    echo "  --list-interfaces        List available interfaces"
    echo "  --list-filters           List predefined filters"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo $0 -p mqtt                    # Capture MQTT traffic"
    echo "  sudo $0 -p ftp-backdoor -c 100     # Capture 100 FTP packets"
    echo "  sudo $0 -i docker0 -d 30           # Capture on docker0 for 30s"
    echo "  sudo $0 -f 'host 172.20.0.2'       # Custom filter"
    echo "  sudo $0 -a captures/mqtt.pcap      # Analyze existing file"
    echo "  sudo $0 -s -p mqtt                 # Live MQTT stats"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interface)
                INTERFACE="$2"
                shift 2
                ;;
            -f|--filter)
                FILTER="$2"
                shift 2
                ;;
            -p|--protocol)
                PROTOCOL="$2"
                if [ -n "${FILTERS[$PROTOCOL]}" ]; then
                    FILTER="${FILTERS[$PROTOCOL]}"
                else
                    log_error "Unknown protocol: $PROTOCOL"
                    log_info "Use --list-filters to see available options"
                    exit 1
                fi
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -c|--count)
                COUNT="$2"
                shift 2
                ;;
            -d|--duration)
                DURATION="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -s|--stats)
                STATS_ONLY=true
                shift
                ;;
            -a|--analyze)
                analyze_capture "$2"
                exit 0
                ;;
            -t|--to-text)
                convert_to_text "$2"
                exit 0
                ;;
            --list-interfaces)
                list_interfaces
                exit 0
                ;;
            --list-filters)
                list_filters
                exit 0
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ============================================================================
# Main
# ============================================================================

main() {
    parse_args "$@"
    
    print_banner
    check_root
    check_dependencies
    
    if [ "$STATS_ONLY" = true ]; then
        run_live_stats
    else
        run_capture
    fi
}

# Rulare
main "$@"
