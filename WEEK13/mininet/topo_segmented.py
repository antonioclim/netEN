#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topology Mininet - Network IoT Segmentata with Firewall
====================================================

Week 13 - IoT and Security in Computer Networks
Academia of Studii Economice - CSIE

Dewritere:
    Implement "Defense in Depth" through segmentare of network:
    - Zona IoT (10.0.1.0/24) - Sensors with acces limitat
    - Zona Management (10.0.2.0/24) - Broker MQTT and Controller
    - Zona DMZ (10.0.3.0/24) - Gateway extern (optional)
    - Router central with reguli iptables ca firewall

Topology:
    
    ┌─────────────────┐
    │   ZONA IoT      │
    │  10.0.1.0/24    │
    │ ┌─────┐ ┌─────┐ │
    │ │ s1  │ │ s2  │ │
    │ │.11  │ │.12  │ │
    │ └──┬──┘ └──┬──┘ │
    │    └───┬───┘    │
    └────────┼────────┘
             │ eth0 (.1)
    ┌────────┴────────┐
    │     ROUTER      │
    │  r1 (Firewall)  │
    │   + iptables    │
    └────────┬────────┘
             │ eth1 (.1)
    ┌────────┼────────┐
    │   ZONA MGMT     │
    │  10.0.2.0/24    │
    │ ┌─────┐ ┌─────┐ │
    │ │broker │ctrl │ │
    │ │.100 │ │.20  │ │
    │ └─────┘ └─────┘ │
    └─────────────────┘

Reguli Firewall (iptables):
    - IoT → MGMT: ONLY ports 1883, 8883 (MQTT)
    - MGMT → IoT: PERMITE (management complete)
    - Inter-IoT: BLOCAT (izolare sensors)
    - Logging for traffic suspect

Usage:
    sudo python3 topo_segmented.py
    sudo python3 topo_segmented.py --scenario isolation
    sudo python3 topo_segmented.py --show-rules

Author: Teaching Staff ASE-CSIE
Data: 2025
"""

import sys 
import argparse 
import time 

# Mininet verification
try :
    from mininet .net import Mininet 
    from mininet .node import Controller ,OVSSwitch ,Host ,Node 
    from mininet .cli import CLI 
    from mininet .log import setLogLevel ,info ,error 
    from mininet .link import TCLink 
    from mininet .topo import Topo 
    MININET_DISPONIBIL =True 
except ImportError :
    MININET_DISPONIBIL =False 
    print ("[!] Mininet is not installed.")


    # ============================================================================
    # ROUTER LINUX CU IP FORWARDING
    # ============================================================================

class LinuxRouter (Node ):
    """
    Router Linux with IP forwarding activeat.
    
    Used ca punct of segmentare and firewall between zone.
    Implement iptables for control traffic.
    """

    def config (self ,**params ):
        super ().config (**params )
        # Activeare IP forwarding
        self .cmd ('sysctl -w net.ipv4.ip_forward=1')

    def terminate (self ):
    # Dezactiveare IP forwarding at cleanup
        self .cmd ('sysctl -w net.ipv4.ip_forward=0')
        super ().terminate ()


        # ============================================================================
        # TOPOLOGIE SEGMENTATA
        # ============================================================================

class IoTSegmentedTopo (Topo ):
    """
    Segmented topology with zone separate and router/firewall.
    
    Zone:
        - IoT Zone (10.0.1.0/24): Sensors with privilegii minimum
        - Management Zone (10.0.2.0/24): Broker and Controller
        - DMZ (optional, 10.0.3.0/24): Expunere externa controlata
    
    Principiul "Least Privilege":
        - Sensorii pot only comunica with broker-ul on ports specifice
        - Not pot comunica between ei (prevent lateral movement)
        - Management zone are control complete
    """

    def build (self ,**kwargs ):
        """Construieste topologia segmentata."""
        info ("*** Construire topology IoT Segmentata\n")

        # ===================================================================
        # ROUTER CENTRAL (Firewall)
        # ===================================================================

        router =self .addNode (
        'r1',
        cls =LinuxRouter ,
        ip ='10.0.1.1/24'# IP on interfata catre IoT
        )
        info (f"    Router adaugat: r1 (gateway/firewall)\n")

        # ===================================================================
        # SWITCH-URI PER ZONA
        # ===================================================================

        # Switch for zona IoT
        s_iot =self .addSwitch ('s_iot',cls =OVSSwitch ,failMode ='standalone')
        info (f"    Switch IoT adaugat: s_iot\n")

        # Switch for zona Management
        s_mgmt =self .addSwitch ('s_mgmt',cls =OVSSwitch ,failMode ='standalone')
        info (f"    Switch Management adaugat: s_mgmt\n")

        # ===================================================================
        # CONECTARE ROUTER LA SWITCH-URI
        # ===================================================================

        # Router eth0 -> Switch IoT (10.0.1.1)
        self .addLink (
        router ,s_iot ,
        intfName1 ='r1-eth0',
        params1 ={'ip':'10.0.1.1/24'}
        )

        # Router eth1 -> Switch Management (10.0.2.1)
        self .addLink (
        router ,s_mgmt ,
        intfName1 ='r1-eth1',
        params1 ={'ip':'10.0.2.1/24'}
        )

        # ===================================================================
        # ZONA IoT - SENZORI
        # ===================================================================

        # Sensor 1
        sensor1 =self .addHost (
        'sensor1',
        ip ='10.0.1.11/24',
        defaultRoute ='via 10.0.1.1'# Gateway = router
        )
        self .addLink (sensor1 ,s_iot ,cls =TCLink ,bw =100 ,delay ='5ms')
        info (f"    [IoT] sensor1: 10.0.1.11\n")

        # Sensor 2
        sensor2 =self .addHost (
        'sensor2',
        ip ='10.0.1.12/24',
        defaultRoute ='via 10.0.1.1'
        )
        self .addLink (sensor2 ,s_iot ,cls =TCLink ,bw =100 ,delay ='5ms')
        info (f"    [IoT] sensor2: 10.0.1.12\n")

        # Sensor 3 (optional - device compromis for demo)
        sensor3 =self .addHost (
        'sensor3',
        ip ='10.0.1.13/24',
        defaultRoute ='via 10.0.1.1'
        )
        self .addLink (sensor3 ,s_iot ,cls =TCLink ,bw =100 ,delay ='5ms')
        info (f"    [IoT] sensor3: 10.0.1.13 (for demo attacks)\n")

        # ===================================================================
        # ZONA MANAGEMENT
        # ===================================================================

        # MQTT Broker
        broker =self .addHost (
        'broker',
        ip ='10.0.2.100/24',
        defaultRoute ='via 10.0.2.1'
        )
        self .addLink (broker ,s_mgmt ,cls =TCLink ,bw =1000 ,delay ='1ms')
        info (f"    [MGMT] broker: 10.0.2.100\n")

        # Controller / Dashboard
        controller =self .addHost (
        'ctrl',
        ip ='10.0.2.20/24',
        defaultRoute ='via 10.0.2.1'
        )
        self .addLink (controller ,s_mgmt ,cls =TCLink ,bw =100 ,delay ='2ms')
        info (f"    [MGMT] ctrl: 10.0.2.20\n")

        # Admin workstation
        admin =self .addHost (
        'admin',
        ip ='10.0.2.10/24',
        defaultRoute ='via 10.0.2.1'
        )
        self .addLink (admin ,s_mgmt ,cls =TCLink ,bw =100 ,delay ='2ms')
        info (f"    [MGMT] admin: 10.0.2.10\n")


        # ============================================================================
        # CONFIGURATION FIREWALL (IPTABLES)
        # ============================================================================

def configure_firewall (router ,strict :bool =True ):
    """
    Configure reguli iptables on router.
    
    Args:
        router: Obiect Mininet Node (router)
        strict: True = reguli stricte, False = allowediv for debug
    
    Reguli implementate:
        1. Default policy: DROP (deny all)
        2. Allow established/related (stateful)
        3. IoT → MGMT: only MQTT (1883, 8883)
        4. MGMT → IoT: permit all (management)
        5. IoT ↔ IoT: DROP (izolare laterala)
        6. Log traffic blocked
    """
    info ("\n*** Configuration Firewall (iptables)\n")

    # Reset reguli existente
    router .cmd ('iptables -F')
    router .cmd ('iptables -X')
    router .cmd ('iptables -t nat -F')

    if not strict :
    # Mod allowediv for debugging
        info ("    [!] Mod PERMISIV activeat (only logging)\n")
        router .cmd ('iptables -P FORWARD ACCEPT')
        router .cmd ('iptables -A FORWARD -j LOG --log-prefix "[FW-DEBUG] "')
        return 

        # =========================================================================
        # POLITICI DEFAULT - DROP
        # =========================================================================

    router .cmd ('iptables -P INPUT DROP')
    router .cmd ('iptables -P FORWARD DROP')
    router .cmd ('iptables -P OUTPUT ACCEPT')
    info ("    Politici default: INPUT=DROP, FORWARD=DROP, OUTPUT=ACCEPT\n")

    # =========================================================================
    # LOOPBACK
    # =========================================================================

    router .cmd ('iptables -A INPUT -i lo -j ACCEPT')
    router .cmd ('iptables -A OUTPUT -o lo -j ACCEPT')

    # =========================================================================
    # STATEFUL - ESTABLISHED/RELATED
    # =========================================================================

    router .cmd ('iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT')
    router .cmd ('iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
    info ("    Stateful: ESTABLISHED/RELATED allowed\n")

    # =========================================================================
    # REGULI ICMP (ping for diagnostic)
    # =========================================================================

    router .cmd ('iptables -A FORWARD -p icmp --icmp-type echo-request -j ACCEPT')
    router .cmd ('iptables -A FORWARD -p icmp --icmp-type echo-reply -j ACCEPT')
    router .cmd ('iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT')
    info ("    ICMP: ping allowed (diagnostic)\n")

    # =========================================================================
    # IoT → MANAGEMENT: ONLY MQTT
    # =========================================================================

    # Subnet IoT: 10.0.1.0/24
    # Subnet MGMT: 10.0.2.0/24

    # MQTT plain (port 1883)
    router .cmd ('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 1883 -j ACCEPT')

    # MQTT TLS (port 8883)
    router .cmd ('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 8883 -j ACCEPT')

    # DNS (for rezolvare nume, optional)
    router .cmd ('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p udp --dport 53 -j ACCEPT')

    info ("    IoT → MGMT: PERMIT tcp/1883,8883 (MQTT), udp/53 (DNS)\n")

    # =========================================================================
    # MANAGEMENT → IoT: PERMIT ALL (for management)
    # =========================================================================

    router .cmd ('iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -j ACCEPT')
    info ("    MGMT → IoT: PERMIT ALL (management)\n")

    # =========================================================================
    # IoT ↔ IoT: DROP (izolare laterala)
    # =========================================================================

    # This regula not e necesara explicit deoarece trafficul intra-subnet
    # not trece through router. But o adaugam for claritate and logging.
    router .cmd ('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.1.0/24 -j DROP')
    info ("    IoT ↔ IoT: DROP (izolare - but trafficul not trece through router)\n")

    # =========================================================================
    # LOGGING TRAFIC BLOCAT
    # =========================================================================

    router .cmd ('iptables -A FORWARD -j LOG --log-prefix "[FW-BLOCKED] " --log-level 4')
    info ("    Logging: Traffic blocked inregistrat with prefix [FW-BLOCKED]\n")

    # =========================================================================
    # AFISARE REGULI
    # =========================================================================

    info ("\n*** Reguli iptables activee:\n")
    result =router .cmd ('iptables -L -v -n --line-numbers')
    for line in result .split ('\n')[:20 ]:# Primele 20 linii
        info (f"    {line}\n")


def show_firewall_rules (router ):
    """Display regulile iptables curente."""
    info ("\n*** Reguli iptables on router:\n")
    info ("\n--- FILTER table ---\n")
    print (router .cmd ('iptables -L -v -n --line-numbers'))
    info ("\n--- NAT table ---\n")
    print (router .cmd ('iptables -t nat -L -v -n'))


    # ============================================================================
    # SCENARII
    # ============================================================================

def scenario_isolation_test (net ):
    """
    Test izolarea between zone.
    
    Check:
        1. Sensor can comunica with broker (MQTT)
        2. Sensor NOT can comunica with alte ports
        3. Admin can accesa tot
    """
    info ("\n"+"="*60 +"\n")
    info ("  SCENARIU: Test Izolare Zone\n")
    info ("="*60 +"\n\n")

    sensor1 =net .get ('sensor1')
    sensor2 =net .get ('sensor2')
    broker =net .get ('broker')
    admin =net .get ('admin')

    # Test 1: Ping cross-zone
    info ("1. Test ping sensor1 → broker:\n")
    result =sensor1 .cmd ('ping -c 2 10.0.2.100')
    print (f"   {result}")

    # Test 2: Connection MQTT (ar trebui sa functioneze)
    info ("2. Test connection MQTT (port 1883):\n")
    result =sensor1 .cmd ('nc -zv 10.0.2.100 1883 2>&1')
    print (f"   {result}")

    # Test 3: Connection SSH (ar trebui blockeda)
    info ("3. Test connection SSH (port 22) - ar trebui BLOCATA:\n")
    result =sensor1 .cmd ('nc -zv -w 2 10.0.2.100 22 2>&1')
    print (f"   {result}")

    # Test 4: Admin can accesa sensor (management)
    info ("4. Test admin → sensor1 (ar trebui sa functioneze):\n")
    result =admin .cmd ('ping -c 2 10.0.1.11')
    print (f"   {result}")

    # Test 5: Verification log firewall
    info ("5. Log-uri firewall (ultimele intrari blockede):\n")
    router =net .get ('r1')
    result =router .cmd ('dmesg | grep FW-BLOCKED | tail -5')
    print (f"   {result if result else '   (niciun traffic blocked inca)'}")

    info ("\n[✓] Test izolare complete!\n")


def scenario_lateral_movement (net ):
    """
    Demonstrate prevenirea lateral movement.
    
    Simulate un sensor compromis which try sa attacke alt sensor.
    """
    info ("\n"+"="*60 +"\n")
    info ("  SCENARIU: Prevenire Lateral Movement\n")
    info ("="*60 +"\n\n")

    sensor3 =net .get ('sensor3')# "Compromis"
    sensor1 =net .get ('sensor1')# Target

    info ("Premisa: sensor3 a fost compromis and try sa attacke sensor1\n\n")

    # Port Scanning
    info ("1. Attacker (sensor3) try scanning ports on sensor1:\n")
    result =sensor3 .cmd ('nc -zv -w 1 10.0.1.11 22 80 443 2>&1')
    print (f"   {result}")

    # Ping
    info ("2. Attacker try ping:\n")
    result =sensor3 .cmd ('ping -c 1 -W 1 10.0.1.11')
    print (f"   {result}")

    info ("""
NOTA: Trafficul between sensors (10.0.1.x ↔ 10.0.1.y) NOT trece through router!
      Ei are on acelasi switch (s_iot), deci communicationa directa e posibila.
      
For izolare completa intra-zona, aveti options:
  a) Switch-uri separate per sensor
  b) VLANs with ACLs on switch
  c) Microsegmentare with SDN controller
  d) Host-based firewall on each sensor

In productie, izolarea Layer 2 necesita configuration suplimentara!
""")


def scenario_attack_blocked (net ):
    """
    Demonstrate blocarea unui attack from zona IoT.
    """
    info ("\n"+"="*60 +"\n")
    info ("  SCENARIU: Attack Blocked of Firewall\n")
    info ("="*60 +"\n\n")

    sensor3 =net .get ('sensor3')
    ctrl =net .get ('ctrl')
    router =net .get ('r1')

    info ("Sensor compromis try sa acceseze services from zona MGMT\n\n")

    # Incercare SSH
    info ("1. Incercare SSH catre controller (10.0.2.20):\n")
    result =sensor3 .cmd ('timeout 2 nc -zv 10.0.2.20 22 2>&1')
    print (f"   Result: {result if result else 'Timeout/Blocked'}")

    # Incercare HTTP
    info ("2. Incercare HTTP catre controller:\n")
    result =sensor3 .cmd ('timeout 2 nc -zv 10.0.2.20 80 2>&1')
    print (f"   Result: {result if result else 'Timeout/Blocked'}")

    # Verification log
    info ("3. Verification log firewall:\n")
    time .sleep (1 )
    result =router .cmd ('dmesg | grep FW-BLOCKED | tail -5')
    print (f"   {result if result else '   (verificati with: dmesg | grep FW)'}")

    # MQTT ar trebui sa functioneze
    info ("4. DAR MQTT functioneaza (port 1883):\n")
    result =sensor3 .cmd ('nc -zv 10.0.2.100 1883 2>&1')
    print (f"   {result}")

    info ("""
[✓] Firewall-ul a blocked accesul at services neauthorisede!
    Sensorul compromis can only sa comunice through MQTT.
    
    Chiar if attackatorul are acces at un sensor, daunele are limitate.
    This is esenta "Defense in Depth"!
""")


    # ============================================================================
    # MAIN
    # ============================================================================

def main ():
    """Punct of intrare principal."""

    if not MININET_DISPONIBIL :
        print ("[!] Mininet not is disponibil.")
        sys .exit (1 )

    parser =argparse .ArgumentParser (
    description ="Topology Mininet - Network IoT Segmentata with Firewall"
    )

    parser .add_argument (
    '--no-cli',
    action ='store_true',
    help ='Not deschide CLI Mininet'
    )

    parser .add_argument (
    '--permissive',
    action ='store_true',
    help ='Firewall in mod allowediv (only logging)'
    )

    parser .add_argument (
    '--scenario',
    choices =['isolation','lateral','attack'],
    help ='Running un scenariu predefinit'
    )

    parser .add_argument (
    '--show-rules',
    action ='store_true',
    help ='Display regulile firewall and iesi'
    )

    args =parser .parse_args ()

    setLogLevel ('info')

    info ("\n"+"="*60 +"\n")
    info ("  Mininet IoT Segmented Topology - Week 13\n")
    info ("  Defense in Depth with Firewall\n")
    info ("="*60 +"\n\n")

    # Create topology
    topo =IoTSegmentedTopo ()

    # Create network
    net =Mininet (
    topo =topo ,
    controller =Controller ,
    switch =OVSSwitch ,
    link =TCLink 
    )

    try :
        info ("*** Start network...\n")
        net .start ()

        # Obtine router
        router =net .get ('r1')

        # Configuration firewall
        configure_firewall (router ,strict =not args .permissive )

        # Afisare reguli and iesire
        if args .show_rules :
            show_firewall_rules (router )
            return 

            # Test conectivitate of baza
        info ("\n*** Test conectivitate of baza:\n")
        sensor1 =net .get ('sensor1')
        broker =net .get ('broker')
        info (f"    sensor1 ping broker: ")
        result =sensor1 .cmd ('ping -c 1 10.0.2.100')
        info ("OK\n"if "1 received"in result else "FAIL\n")

        # Running scenariu
        if args .scenario =='isolation':
            scenario_isolation_test (net )
        elif args .scenario =='lateral':
            scenario_lateral_movement (net )
        elif args .scenario =='attack':
            scenario_attack_blocked (net )

            # CLI interactive
        if not args .no_cli and not args .scenario :
            info ("\n*** Commands utile:\n")
            info ("    sensor1 ping broker  # test cross-zone\n")
            info ("    sensor1 nc -zv 10.0.2.100 1883  # test MQTT\n")
            info ("    r1 iptables -L -v -n  # vezi reguli firewall\n")
            info ("    r1 dmesg | grep FW  # vezi log blocare\n")
            info ("    xterm sensor3  # terminal for test attacks\n")
            CLI (net )

    finally :
        info ("\n*** Stop network...\n")
        net .stop ()


if __name__ =="__main__":
    main ()
