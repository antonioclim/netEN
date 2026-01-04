#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topology Mininet - Network IoT of Baza
=====================================

Week 13 - IoT and Security in Computer Networks
Academia of Studii Economice - CSIE

Dewritere:
    Simulate o network IoT simpla with:
    - 2 sensors (publishers MQTT)
    - 1 broker MQTT (Mosquitto)
    - 1 controller (subscriber MQTT)
    - 1 attacker (for demonstrations pentest)

Topology:
                    ┌─────────────┐
                    │   Switch    │
                    │    (s1)     │
                    └──────┬──────┘
           ┌───────────┬───┴───┬───────────┐
           │           │       │           │
    ┌──────┴──────┐ ┌──┴──┐ ┌──┴──┐ ┌──────┴──────┐
    │  sensor1    │ │broker│ │ctrl │ │  attacker   │
    │ 10.0.0.11   │ │.100  │ │ .20 │ │  10.0.0.50  │
    └─────────────┘ └─────┘ └─────┘ └─────────────┘
    
    sensor2: 10.0.0.12

Usage:
    sudo python3 topo_base.py [--cli]
    
    In CLI Mininet:
        mininet> sensor1 ping broker
        mininet> attacker python3 scanner.py 10.0.0.100
        mininet> xterm broker  # deschide terminal for broker

Author: Teaching Staff ASE-CSIE
Data: 2025
"""

import sys 
import argparse 
import time 

# Verification disponibilitate Mininet
try :
    from mininet .net import Mininet 
    from mininet .node import Controller ,OVSSwitch ,Host 
    from mininet .cli import CLI 
    from mininet .log import setLogLevel ,info ,error 
    from mininet .link import TCLink 
    from mininet .topo import Topo 
    MININET_DISPONIBIL =True 
except ImportError :
    MININET_DISPONIBIL =False 
    print ("[!] Mininet is not installed.")
    print ("    Installation: sudo apt-get install mininet")
    print ("    Or: pip install mininet --break-system-packages")


    # ============================================================================
    # DEFINIRE TOPOLOGIE
    # ============================================================================

class IoTBaseTopo (Topo ):
    """
    Topology of baza for network IoT.
    
    Componente:
        - switch central (OpenFlow)
        - 2 sensors IoT
        - 1 broker MQTT
        - 1 controller
        - 1 attacker (optional)
    
    Parameters network:
        - Subnet: 10.0.0.0/24
        - Gateway default: 10.0.0.1
        - Bandwidth link-uri: 100 Mbps
        - Delay: 2ms (simulation latenta realista)
    """

    def build (self ,include_attacker :bool =True ,**kwargs ):
        """
        Construieste topologia.
        
        Args:
            include_attacker: Include host attacker for demonstrations
        """
        info ("*** Construire topology IoT Base\n")

        # ===================================================================
        # SWITCH CENTRAL
        # ===================================================================

        s1 =self .addSwitch ('s1',cls =OVSSwitch ,failMode ='standalone')
        info (f"    Switch adaugat: s1\n")

        # ===================================================================
        # SENZORI IoT
        # ===================================================================

        # Sensor 1 - Living Room
        sensor1 =self .addHost (
        'sensor1',
        ip ='10.0.0.11/24',
        defaultRoute ='via 10.0.0.1'
        )
        self .addLink (
        sensor1 ,s1 ,
        cls =TCLink ,
        bw =100 ,# 100 Mbps
        delay ='2ms'
        )
        info (f"    Sensor adaugat: sensor1 (10.0.0.11)\n")

        # Sensor 2 - Bedroom
        sensor2 =self .addHost (
        'sensor2',
        ip ='10.0.0.12/24',
        defaultRoute ='via 10.0.0.1'
        )
        self .addLink (
        sensor2 ,s1 ,
        cls =TCLink ,
        bw =100 ,
        delay ='2ms'
        )
        info (f"    Sensor adaugat: sensor2 (10.0.0.12)\n")

        # ===================================================================
        # BROKER MQTT
        # ===================================================================

        broker =self .addHost (
        'broker',
        ip ='10.0.0.100/24',
        defaultRoute ='via 10.0.0.1'
        )
        self .addLink (
        broker ,s1 ,
        cls =TCLink ,
        bw =1000 ,# 1 Gbps - server principal
        delay ='1ms'
        )
        info (f"    Broker adaugat: broker (10.0.0.100)\n")

        # ===================================================================
        # CONTROLLER
        # ===================================================================

        controller =self .addHost (
        'ctrl',
        ip ='10.0.0.20/24',
        defaultRoute ='via 10.0.0.1'
        )
        self .addLink (
        controller ,s1 ,
        cls =TCLink ,
        bw =100 ,
        delay ='2ms'
        )
        info (f"    Controller adaugat: ctrl (10.0.0.20)\n")

        # ===================================================================
        # ATACATOR (for demonstrations)
        # ===================================================================

        if include_attacker :
            attacker =self .addHost (
            'attacker',
            ip ='10.0.0.50/24',
            defaultRoute ='via 10.0.0.1'
            )
            self .addLink (
            attacker ,s1 ,
            cls =TCLink ,
            bw =100 ,
            delay ='2ms'
            )
            info (f"    Attacker adaugat: attacker (10.0.0.50)\n")


            # ============================================================================
            # HELPER FUNCTIONS
            # ============================================================================

def start_mosquitto (host ,config_path :str =None ):
    """
    Start Mosquitto broker on un host.
    
    Args:
        host: Obiect Mininet Host
        config_path: Calea catre fisierul of configuration (optional)
    """
    config_arg =f"-c {config_path}"if config_path else ""
    cmd =f"mosquitto {config_arg} -v &"
    info (f"*** Start Mosquitto on {host.name}: {cmd}\n")
    host .cmd (cmd )
    time .sleep (1 )# Wait pornirea


def start_sensor_simulation (host ,broker_ip :str ,topic :str ,interval :int =5 ):
    """
    Start simulation sensor which publica date periodic.
    
    Args:
        host: Obiect Mininet Host
        broker_ip: IP-ul broker-ului MQTT
        topic: Topic-ul on which publica
        interval: Interval between messages (secunde)
    """
    # Script Python inline for simulation sensor
    script =f'''
import time
import random
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("{broker_ip}", 1883)

while True:
    temp = round(20 + random.uniform(-5, 5), 1)
    humidity = round(50 + random.uniform(-10, 10), 1)
    client.publish("{topic}/temperature", temp)
    client.publish("{topic}/humidity", humidity)
    time.sleep({interval})
'''

    # Save script-ul and running-l
    script_path =f"/tmp/sensor_{host.name}.py"
    host .cmd (f"echo '{script}' > {script_path}")
    host .cmd (f"python3 {script_path} &")
    info (f"*** Sensor simulation started on {host.name}\n")


def run_test_connectivity (net ):
    """
    Test conectivitatea between all host-urile.
    
    Args:
        net: Obiect Mininet Network
    """
    info ("\n*** Test conectivitate (ping all)\n")
    net .pingAll ()


def capture_traffic (host ,interface :str =None ,output_file :str ="/tmp/capture.pcap"):
    """
    Start capture of traffic on un host.
    
    Args:
        host: Obiect Mininet Host
        interface: Interfata of capture (None = all)
        output_file: Fisierul of output
    """
    iface_arg =f"-i {interface}"if interface else "-i any"
    cmd =f"tcpdump {iface_arg} -w {output_file} &"
    info (f"*** Capture traffic on {host.name}: {cmd}\n")
    host .cmd (cmd )


    # ============================================================================
    # SCENARII PREDEFINITE
    # ============================================================================

def scenario_basic_mqtt (net ):
    """
    Scenariu: Communication MQTT of baza.
    
    1. Start broker
    2. Sensor1 publica date
    3. Controller subwrite and receive
    """
    info ("\n"+"="*60 +"\n")
    info ("  SCENARIU: Communication MQTT of Baza\n")
    info ("="*60 +"\n\n")

    broker =net .get ('broker')
    sensor1 =net .get ('sensor1')
    ctrl =net .get ('ctrl')

    # 1. Start broker
    info ("1. Start broker Mosquitto...\n")
    broker .cmd ("mosquitto -v &")
    time .sleep (2 )

    # 2. Subscriber on controller
    info ("2. Controller subwrite at home/#...\n")
    ctrl .cmd ("mosquitto_sub -h 10.0.0.100 -t 'home/#' -v > /tmp/mqtt_received.txt &")
    time .sleep (1 )

    # 3. Sensor publica
    info ("3. Sensor1 publica temperatura...\n")
    sensor1 .cmd ("mosquitto_pub -h 10.0.0.100 -t 'home/living/temp' -m '22.5'")
    sensor1 .cmd ("mosquitto_pub -h 10.0.0.100 -t 'home/living/humidity' -m '45'")
    time .sleep (1 )

    # 4. Verification
    info ("4. Messages primite of controller:\n")
    result =ctrl .cmd ("cat /tmp/mqtt_received.txt")
    print (result )

    info ("\n[✓] Scenariu complete!\n")


def scenario_sniff_attack (net ):
    """
    Scenariu: Attacker intercepteaza traffic MQTT.
    
    Demonstrate vulnerabilitya comunicatiei neencryptede.
    """
    info ("\n"+"="*60 +"\n")
    info ("  SCENARIU: Interception Traffic MQTT (Sniffing)\n")
    info ("="*60 +"\n\n")

    attacker =net .get ('attacker')
    broker =net .get ('broker')
    sensor1 =net .get ('sensor1')

    # 1. Attackatorul start tcpdump
    info ("1. Attacker start capture traffic port 1883...\n")
    attacker .cmd ("tcpdump -i attacker-eth0 port 1883 -A > /tmp/sniffed.txt &")
    time .sleep (1 )

    # 2. Broker pornit
    broker .cmd ("mosquitto -v &")
    time .sleep (2 )

    # 3. Sensor publica date "sensibile"
    info ("2. Sensor publica date (vizibile attackatorului!)...\n")
    sensor1 .cmd ("mosquitto_pub -h 10.0.0.100 -t 'home/alarm/code' -m 'PIN:1234'")
    sensor1 .cmd ("mosquitto_pub -h 10.0.0.100 -t 'home/alarm/status' -m 'DISARMED'")
    time .sleep (2 )

    # 4. Afisare date capturate
    attacker .cmd ("pkill tcpdump")
    info ("3. Date interceptate of attacker:\n")
    result =attacker .cmd ("grep -a 'PIN\\|DISARMED' /tmp/sniffed.txt")
    print (result if result else "    [folositi Wireshark on /tmp/capture.pcap for analysis completa]")

    info ("\n[!] LECTIE: Without TLS, trafficul MQTT can fi citit of oricine in network!\n")


    # ============================================================================
    # MAIN
    # ============================================================================

def main ():
    """Punct of intrare principal."""

    if not MININET_DISPONIBIL :
        print ("[!] Mininet not is disponibil. Instalati with:")
        print ("    sudo apt-get install mininet")
        sys .exit (1 )

    parser =argparse .ArgumentParser (
    description ="Topology Mininet - Network IoT of Baza",
    formatter_class =argparse .RawDescriptionHelpFormatter ,
    epilog ="""
Examples:
    sudo python3 topo_base.py              # Start and deschide CLI
    sudo python3 topo_base.py --no-cli     # Only start networkua
    sudo python3 topo_base.py --scenario basic  # Running scenariu MQTT
    sudo python3 topo_base.py --scenario sniff  # Demonstration sniffing
        """
    )

    parser .add_argument (
    '--no-cli',
    action ='store_true',
    help ='Not deschide CLI Mininet'
    )

    parser .add_argument (
    '--no-attacker',
    action ='store_true',
    help ='Not include host-ul attacker'
    )

    parser .add_argument (
    '--scenario',
    choices =['basic','sniff'],
    help ='Running un scenariu predefinit'
    )

    parser .add_argument (
    '--test',
    action ='store_true',
    help ='Running test of conectivitate'
    )

    args =parser .parse_args ()

    # Setting nivel logging
    setLogLevel ('info')

    info ("\n"+"="*60 +"\n")
    info ("  Mininet IoT Base Topology - Week 13\n")
    info ("="*60 +"\n\n")

    # Create topology
    topo =IoTBaseTopo (include_attacker =not args .no_attacker )

    # Create network
    net =Mininet (
    topo =topo ,
    controller =Controller ,
    switch =OVSSwitch ,
    link =TCLink ,
    autoSetMacs =True 
    )

    try :
    # Start network
        info ("*** Start network...\n")
        net .start ()

        # Test conectivitate
        if args .test :
            run_test_connectivity (net )

            # Running scenariu
        if args .scenario =='basic':
            scenario_basic_mqtt (net )
        elif args .scenario =='sniff':
            scenario_sniff_attack (net )

            # CLI interactive
        if not args .no_cli and not args .scenario :
            info ("\n*** Commands utile in CLI:\n")
            info ("    sensor1 ping broker\n")
            info ("    xterm broker  # terminal for broker\n")
            info ("    broker mosquitto -v &  # start broker\n")
            info ("    attacker tcpdump -i attacker-eth0 port 1883\n")
            info ("    exit  # stop Mininet\n\n")
            CLI (net )

    finally :
    # Cleanup
        info ("\n*** Stop network...\n")
        net .stop ()


        # ============================================================================
        # ALTERNATIVA: Usage ca modules
        # ============================================================================

def create_network (include_attacker :bool =True )->'Mininet':
    """
    Create and return networkua Mininet (for import from alt script).
    
    Args:
        include_attacker: Include host attacker
        
    Returns:
        Obiect Mininet Network (nepornit)
    """
    if not MININET_DISPONIBIL :
        raise ImportError ("Mininet is not installed")

    topo =IoTBaseTopo (include_attacker =include_attacker )
    net =Mininet (
    topo =topo ,
    controller =Controller ,
    switch =OVSSwitch ,
    link =TCLink 
    )
    return net 


if __name__ =="__main__":
    main ()
