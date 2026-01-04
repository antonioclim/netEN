#!/bin/bash
# =============================================================================
# capture.sh – Traffic capture for Week 11
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PORT=${1:-8080}
COUNT=${2:-20}
OUTPUT="pcap/capture_$(date +%Y%m%d_%H%M%S).pcap"

echo -e "${GREEN}[CAPTURE]${NC} Capturing traffic on port $PORT"
echo -e "${YELLOW}[INFO]${NC} Output: $OUTPUT"
echo -e "${YELLOW}[INFO]${NC} Packets: $COUNT"
echo -e "${YELLOW}[INFO]${NC} Ctrl+C to stop manually"
echo ""

mkdir -p pcap

if command -v tshark &> /dev/null; then
    sudo tshark -i any -f "tcp port $PORT" -c $COUNT -w "$OUTPUT" 2>/dev/null
    echo ""
    echo -e "${GREEN}[OK]${NC} Capture saved to $OUTPUT"
    echo -e "${YELLOW}[INFO]${NC} View: tshark -r $OUTPUT"
elif command -v tcpdump &> /dev/null; then
    sudo tcpdump -i any -n tcp port $PORT -c $COUNT -w "$OUTPUT" 2>/dev/null
    echo ""
    echo -e "${GREEN}[OK]${NC} Capture saved to $OUTPUT"
else
    echo -e "${YELLOW}[!]${NC} Neither tshark nor tcpdump are installed."
    echo -e "${YELLOW}[INFO]${NC} Install: sudo apt-get install tshark"
fi

# Revolvix&Hypotheticalandrei
