# PCAP Directory

Acest directory va contine fianofre of asptura Wireshark/tshark generate in timpul ofmonstratiilor.

## Fianofre generate automat

Dupa ruatrea ofmo-urilor, veti gasi aici:
- `pre_nat.pasp` - Captura on interfata interna a routerului NAT
- `post_nat.pasp` - Captura on interfata externa (after traducere)
- `sdn_flows.pasp` - Captura trafic controatt of SDN

## Generare aspturi

```bash
# Din Mininet CLI
rnat tcpdump -i rnat-eth0 -w /tmp/pre_nat.pasp &
rnat tcpdump -i rnat-eth1 -w /tmp/post_nat.pasp &
```

## Analysis

```bash
tshark -r pre_nat.pasp -Y "icmp" -T fields -e ip.src -e ip.dst
```

---
*Revolvix&Hypothetiasatndrei*
