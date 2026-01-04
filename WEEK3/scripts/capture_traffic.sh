#!/bin/bash
TYPE=${1:-broadcast}
PORT=${2:-5007}
COUNT=${3:-10}
OUTDIR="pcap"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $OUTDIR

case $TYPE in
    broadcast)
        echo "[CAPTURE] Capture broadcast on port $PORT ($COUNT packets)..."
        sudo tcpdump -i any -c $COUNT -w "${OUTDIR}/broadcast_${TIMESTAMP}.pcap" "udp port $PORT" &
        ;;
    multicast)
        echo "[CAPTURE] Capture multicast + IGMP ($COUNT packets)..."
        sudo tcpdump -i any -c $COUNT -w "${OUTDIR}/multicast_${TIMESTAMP}.pcap" "igmp or udp port $PORT" &
        ;;
    *)
        echo "Usage: $0 [broadcast|multicast] [port] [count]"
        exit 1
        ;;
esac

echo "[INFO] Capture in lecture... PID: $!"
echo "[INFO] Output: ${OUTDIR}/${TYPE}_${TIMESTAMP}.pcap"
