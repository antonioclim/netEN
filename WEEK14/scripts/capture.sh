#!/bin/bash
# capture.sh — Starts standalone tcpdump capture
# Run: sudo bash scripts/capture.sh [output.pcap] [interface]

OUTPUT="${1:-capture.pcap}"
INTERFACE="${2:-any}"

echo "=============================================="
echo "  tcpdump Capture"
echo "=============================================="
echo ""
echo "Output: $OUTPUT"
echo "Interface: $INTERFACE"
echo ""
echo "Stop: Ctrl+C"
echo ""

sudo tcpdump -i "$INTERFACE" -w "$OUTPUT" -v

echo ""
echo "Capture saved to: $OUTPUT"
echo ""
echo "Analysis:"
echo "  tshark -r $OUTPUT -q -z conv,ip"
echo "  tshark -r $OUTPUT -Y 'http.request'"
echo ""
