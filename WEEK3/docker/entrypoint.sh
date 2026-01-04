#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# entrypoint.sh — Script de starting for containerul S3
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     STARTERKIT S3 — Socket Programming                          ║"
echo "║     Computer Networks, ASE-CSIE                            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Porneste Open vSwitch if e disponibil (for Mininet)
if command -v ovs-vsctl &> /dev/null; then
    service openvswitch-switch start 2>/dev/null || true
fi

# Afiseaza informatii despre retea
echo "Informatii retea:"
echo "  IP:       $(hostname -I 2>/dev/null | awk '{print $1}' || echo 'N/A')"
echo "  Hostname: $(hostname)"
echo ""

# Afiseaza comenzi utile
echo "Useful commands:"
echo "  python3 python/examples/ex01_udp_broadcast.py --help"
echo "  python3 python/examples/ex02_udp_multicast.py --help"
echo "  python3 python/examples/ex03_tcp_tunnel.py --help"
echo "  bash scripts/run_all_demos.sh"
echo ""

# Executa comanda transmisa sau bash interactiv
exec "$@"
