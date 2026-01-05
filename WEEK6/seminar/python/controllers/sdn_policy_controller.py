#!/usr/bin/env python3
"""
Seminar 6 – SDN Controller (OS-Ken + OpenFlow 1.3)

Educational controller for SDN topology with security policies.

SDN Architecture:
┌─────────────────────────────────────────┐
│            Control Plane                │
│  ┌─────────────────────────────────┐    │
│  │      Controller (this file)    │    │
│  │   - Receives packet_in         │    │
│  │   - Decides policy             │    │
│  │   - Installs flows             │    │
│  └──────────────┬──────────────────┘    │
└─────────────────┼───────────────────────┘
                  │ OpenFlow 1.3
┌─────────────────┼───────────────────────┐
│            Data Plane                   │
│  ┌──────────────▼──────────────────┐    │
│  │      OVS Switch (s1)           │    │
│  │   - Flow table (match→action)  │    │
│  │   - Hardware/software forwarding│    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

Implemented policy:
- h1 (10.0.6.11) ↔ h2 (10.0.6.12): PERMIT (all traffic)
- * → h3 (10.0.6.13): DROP (implicit)
- UDP → h3: CONFIGURABLE (see ALLOW_UDP_TO_H3)

Usage:
    osken-manager sdn_policy_controller.py
    
    # Optional, with verbose debugging:
    osken-manager --verbose sdn_policy_controller.py
"""

from __future__ import annotations

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    MAIN_DISPATCHER,
    CONFIG_DISPATCHER,
    set_ev_cls
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, ipv4, arp


# ═══════════════════════════════════════════════════════════════════════════
# EDUCATIONAL CONFIGURATION - students can modify these constants
# ═══════════════════════════════════════════════════════════════════════════

# Change to True to allow UDP to h3 (but TCP remains blocked)
ALLOW_UDP_TO_H3 = False

# Host IP addresses (correspond to topo_sdn.py topology)
# Week 6 standard: 10.0.6.0/24
H1_IP = "10.0.6.11"
H2_IP = "10.0.6.12"
H3_IP = "10.0.6.13"

# Fallback port for h3 (in our topology: port 3)
H3_PORT_FALLBACK = 3

# Timeout for installed flows (seconds)
FLOW_IDLE_TIMEOUT = 60
FLOW_HARD_TIMEOUT = 0  # 0 = no hard timeout


class SDNPolicyController(app_manager.OSKenApp):
    """
    SDN controller with per-host and per-protocol security policies.
    
    Operation:
    1. On switch connection: install table-miss rule
    2. On packet_in: learn MACs, then decide:
       - ARP: flood/forward for L2 operation
       - IPv4 h1↔h2: install allow flows
       - IPv4 *→h3: install drop flow (or allow UDP if configured)
       - Rest: basic L2 learning switch
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Learning table: dpid → {mac → port}
        self.mac_to_port: dict[int, dict[str, int]] = {}
    
    # ───────────────────────────────────────────────────────────────────────
    # Event handler: Switch connected
    # ───────────────────────────────────────────────────────────────────────
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def on_switch_features(self, ev):
        """
        Called when the switch connects to the controller.
        
        We install the table-miss rule with priority 0:
        - Match: any packet (empty match)
        - Action: send to controller (OFPP_CONTROLLER)
        
        This rule ensures that unknown packets reach the controller
        to be processed and generate specific flows.
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Empty match = matches anything
        match = parser.OFPMatch()
        
        # Action: send to controller
        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]
        
        # Install with minimum priority (0)
        self._add_flow(datapath, priority=0, match=match, actions=actions)
        
        self.logger.info(
            "Table-miss installed on dpid=%s (packets→controller)", 
            datapath.id
        )
    
    # ───────────────────────────────────────────────────────────────────────
    # Helper: Flow installation
    # ───────────────────────────────────────────────────────────────────────
    
    def _add_flow(
        self,
        datapath,
        priority: int,
        match,
        actions: list,
        buffer_id=None,
        idle_timeout: int = FLOW_IDLE_TIMEOUT,
        hard_timeout: int = FLOW_HARD_TIMEOUT
    ):
        """
        Install a flow in the switch.
        
        Args:
            datapath: Target switch
            priority: Rule priority (higher = checked first)
            match: Matching criteria
            actions: List of actions (empty = drop)
            buffer_id: Buffer ID if packet is in switch
            idle_timeout: Delete after X seconds of inactivity
            hard_timeout: Delete after X seconds (0 = never)
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Build instructions (wrapper around actions)
        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]
        
        # flow_mod parameters
        kwargs = dict(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
        )
        
        # If packet is in buffer, link it to flow
        if buffer_id is not None and buffer_id != ofproto.OFP_NO_BUFFER:
            kwargs["buffer_id"] = buffer_id
        
        # Send flow_mod message
        flow_mod = parser.OFPFlowMod(**kwargs)
        datapath.send_msg(flow_mod)
    
    # ───────────────────────────────────────────────────────────────────────
    # Helper: MAC learning
    # ───────────────────────────────────────────────────────────────────────
    
    def _learn_mac(self, dpid: int, mac: str, port: int) -> None:
        """Learn MAC → port association for a switch."""
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][mac] = port
    
    def _get_port(self, dpid: int, mac: str, fallback=None) -> int:
        """Get port for a MAC, or fallback if unknown."""
        return self.mac_to_port.get(dpid, {}).get(mac, fallback)
    
    # ───────────────────────────────────────────────────────────────────────
    # Event handler: Packet-in (unknown packet)
    # ───────────────────────────────────────────────────────────────────────
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def on_packet_in(self, ev):
        """
        Called when the switch sends an unknown packet.
        
        Processing flow:
        1. Extract information from packet (MACs, IPs)
        2. Learn source MAC
        3. Handle ARP (flood/forward for L2 operation)
        4. Handle IPv4 according to policy:
           - h1↔h2: permit
           - *→h3: drop (or permit UDP)
           - rest: L2 learning switch
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        in_port = msg.match["in_port"]
        
        # Parse packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        src_mac = eth.src
        dst_mac = eth.dst
        
        # Learn source MAC
        self._learn_mac(dpid, src_mac, in_port)
        
        # ─────────────────────────────────────────────────────────────────
        # ARP handling: learning + flood/forward
        # ─────────────────────────────────────────────────────────────────
        
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            # Log for debugging
            self.logger.debug(
                "ARP: %s → %s (op=%s)",
                arp_pkt.src_ip, arp_pkt.dst_ip, arp_pkt.opcode
            )
            
            # Determine output port
            out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
            
            # Send packet (we don't install flow for ARP)
            actions = [parser.OFPActionOutput(out_port)]
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return
        
        # ─────────────────────────────────────────────────────────────────
        # IPv4 handling: apply policy
        # ─────────────────────────────────────────────────────────────────
        
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if not ip_pkt:
            # Not IPv4, ignore
            return
        
        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst
        proto = ip_pkt.proto  # 1=ICMP, 6=TCP, 17=UDP
        
        self.logger.info(
            "IPv4: %s → %s (proto=%s) in_port=%s",
            src_ip, dst_ip, proto, in_port
        )
        
        # ─────────────────────────────────────────────────────────────────
        # Policy 1: Permit h1 ↔ h2
        # ─────────────────────────────────────────────────────────────────
        
        if self._is_h1_h2_traffic(src_ip, dst_ip):
            out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
            actions = [parser.OFPActionOutput(out_port)]
            
            # Install flow for this traffic
            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip
            )
            self._add_flow(
                datapath,
                priority=10,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
            
            # Send current packet
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                self._send_packet_out(datapath, in_port, actions, msg.data)
            
            self.logger.info(
                "ALLOW: %s → %s (proto=%s) out_port=%s",
                src_ip, dst_ip, proto, out_port
            )
            return
        
        # ─────────────────────────────────────────────────────────────────
        # Policy 2: Handle traffic to h3
        # ─────────────────────────────────────────────────────────────────
        
        if dst_ip == H3_IP:
            # Special case: UDP allowed (if configured)
            if proto == 17 and ALLOW_UDP_TO_H3:
                out_port = self._get_port(dpid, dst_mac, fallback=H3_PORT_FALLBACK)
                actions = [parser.OFPActionOutput(out_port)]
                
                # Flow for UDP to h3
                match = parser.OFPMatch(
                    eth_type=0x0800,
                    ip_proto=17,
                    ipv4_dst=H3_IP
                )
                self._add_flow(
                    datapath,
                    priority=20,
                    match=match,
                    actions=actions,
                    buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
                )
                
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    self._send_packet_out(datapath, in_port, actions, msg.data)
                
                self.logger.info("ALLOW UDP → %s out_port=%s", H3_IP, out_port)
                return
            
            # Implicit: DROP (flow without actions)
            match_kwargs = dict(eth_type=0x0800, ipv4_dst=H3_IP)
            
            # Optional: match also on protocol to see separate rules
            if proto in (1, 6, 17):  # ICMP, TCP, UDP
                match_kwargs["ip_proto"] = proto
            
            match = parser.OFPMatch(**match_kwargs)
            actions = []  # Empty list = DROP
            
            self._add_flow(
                datapath,
                priority=30,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
            
            self.logger.info(
                "DROP: → %s (proto=%s)",
                H3_IP, proto
            )
            return
        
        # ─────────────────────────────────────────────────────────────────
        # Implicit: L2 learning switch
        # ─────────────────────────────────────────────────────────────────
        
        out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]
        
        # Install flow only if we know the port
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self._add_flow(
                datapath,
                priority=1,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
        
        # Send packet
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            self._send_packet_out(datapath, in_port, actions, msg.data)
    
    # ───────────────────────────────────────────────────────────────────────
    # Private helpers
    # ───────────────────────────────────────────────────────────────────────
    
    def _is_h1_h2_traffic(self, src_ip: str, dst_ip: str) -> bool:
        """Check if traffic is between h1 and h2."""
        return (
            (src_ip == H1_IP and dst_ip == H2_IP) or
            (src_ip == H2_IP and dst_ip == H1_IP)
        )
    
    def _send_packet_out(self, datapath, in_port: int, actions: list, data: bytes):
        """Send an individual packet through the switch."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)
