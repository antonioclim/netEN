#!/bin/bash
set -euo pipefail
# Capture traffic for Starterkit S9

PORT=${1:-3333}
OUTPUT=${2:-"pcap/capture_$(date +%Y%m%d_%H%M%S).pcap"}

echo "Capture traffic on port $PORT"
echo "Output: $OUTPUT"
echo "Ctrl+C for stopping"

sudo tcpdump -i any "tcp port $PORT" -w "$OUTPUT"
echo "✓ Capture saved in $OUTPUT"
