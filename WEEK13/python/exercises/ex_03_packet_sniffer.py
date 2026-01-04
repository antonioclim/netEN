#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise 03 - Packet Sniffer and Analizor of Traffic
====================================================

Week 13 - IoT and Security in Computer Networks
Academia of Studii Economice - CSIE

Scopul exercitiului:
    Implementing unui sniffer of packets for interceptarea and analiza
    trafficului of network in time real, with focus on protocolsle relevante
    for IoT (MQTT, HTTP, FTP, DNS).

Competente dezvoltate:
    - Understanding structurii packetelor TCP/IP at nivel of octeti
    - Utilizarea bibliotecii Scapy for analysis of traffic
    - Identificationa patterns of communication in network
    - Detectiona potentialelor threats of security

Dependencies:
    pip install scapy --break-system-packages

WARNING:
    This instrument is destinat EXCLUSIV for medii of testing controlate!
    Interceptiona trafficului of network without authorisation is ILEGALA.

Author: Teaching Staff ASE-CSIE
Data: 2025
"""

import argparse 
import json 
import sys 
import signal 
import os 
from datetime import datetime 
from collections import defaultdict 
from typing import Optional ,Dict ,List ,Any ,Callable 

# ============================================================================
# VERIFICATION DEPENDENTE
# ============================================================================

try :
    from scapy .all import (
    sniff ,IP ,TCP ,UDP ,ICMP ,DNS ,DNSQR ,DNSRR ,
    Raw ,Ether ,ARP ,conf ,get_if_list ,hexdump 
    )
    SCAPY_DISPONIBIL =True 
except ImportError :
    SCAPY_DISPONIBIL =False 
    print ("[!] AVERTISMENT: Scapy is not installed.")
    print ("    Installation: pip install scapy --break-system-packages")
    print ("    Or folositi modules simple with socket raw.")

    # ============================================================================
    # CONSTANTE SI CONFIGURATII
    # ============================================================================

    # Ports cunoscute for analysis
PORTURI_CUNOSCUTE ={
20 :("FTP-DATA","Transfer date FTP"),
21 :("FTP","Control FTP"),
22 :("SSH","Secure Shell"),
23 :("TELNET","Telnet (nesigur!)"),
25 :("SMTP","Email outgoing"),
53 :("DNS","Domain Name System"),
80 :("HTTP","Web traffic neencrypted"),
110 :("POP3","Email retrieval"),
143 :("IMAP","Email access"),
443 :("HTTPS","Web traffic encrypted"),
445 :("SMB","Windows file sharing"),
1883 :("MQTT","IoT messaging (plain)"),
8883 :("MQTT-TLS","IoT messaging (encrypted)"),
3306 :("MySQL","Baza of date"),
5432 :("PostgreSQL","Baza of date"),
6379 :("Redis","Cache/NoSQL"),
27017 :("MongoDB","NoSQL database"),
}

# Coduri of colour ANSI
class Colours :
    """Coduri ANSI for output colorat in terminal."""
    RESET ="\033[0m"
    BOLD ="\033[1m"
    RED ="\033[91m"
    GREEN ="\033[92m"
    YELLOW ="\033[93m"
    BLUE ="\033[94m"
    MAGENTA ="\033[95m"
    CYAN ="\033[96m"
    WHITE ="\033[97m"

    @classmethod 
    def disable (cls ):
        """Dezactiveeaza culorile for pipe/file."""
        cls .RESET =cls .BOLD =cls .RED =cls .GREEN =""
        cls .YELLOW =cls .BLUE =cls .MAGENTA =cls .CYAN =cls .WHITE =""

        # Dezactiveare colours if output not e terminal
if not sys .stdout .isatty ():
    Colours .disable ()

    # ============================================================================
    # CLASA PRINCIPALA - PACKET SNIFFER
    # ============================================================================

class PacketSniffer :
    """
    Sniffer of packets with suport for multiple protocols.
    
    Arhitectura:
        - Capture: Scapy sniff() with BPF filter
        - Processing: Callback chain for each packet
        - Statistici: Agregare in time real
        - Export: JSON for analysis ulterioara
    
    Attributes:
        interface: Interfata of network for capture
        packet_count: Number maximum of packets of capturat (0=infinit)
        bpf_filter: Berkeley Packet Filter for pre-filtrare
        verbose: Nivel of detaliere output
    """

    def __init__ (
    self ,
    interface :str ="any",
    packet_count :int =0 ,
    bpf_filter :str ="",
    verbose :int =1 ,
    output_file :Optional [str ]=None 
    ):
        """
        Initialise sniffer-ul.
        
        Args:
            interface: Interfata of capture ("any", "eth0", "docker0", etc.)
            packet_count: Number packets of capturat (0 = infinit)
            bpf_filter: Filtru BPF (ex: "tcp port 1883")
            verbose: 0=silent, 1=normal, 2=detaliat, 3=debug
            output_file: File JSON for export statistici
        """
        self .interface =interface 
        self .packet_count =packet_count 
        self .bpf_filter =bpf_filter 
        self .verbose =verbose 
        self .output_file =output_file 

        # Statistici agregate
        self .statistici :Dict [str ,Any ]={
        "start_time":None ,
        "end_time":None ,
        "total_packete":0 ,
        "total_bytes":0 ,
        "protocols":defaultdict (int ),
        "ip_sursa":defaultdict (int ),
        "ip_dest":defaultdict (int ),
        "ports_sursa":defaultdict (int ),
        "ports_dest":defaultdict (int ),
        "dns_queries":[],
        "http_requests":[],
        "mqtt_messagee":[],
        "alerte_security":[],
        "connections":defaultdict (lambda :{"packets":0 ,"bytes":0 }),
        }

        # Flag for stop gracioasa
        self ._running =False 
        self ._packete_capturate :List [Dict ]=[]

        # Configuration handler for SIGINT
        signal .signal (signal .SIGINT ,self ._signal_handler )

    def _signal_handler (self ,sig ,frame ):
        """Handler for Ctrl+C - stop gracioasa."""
        print (f"\n{Colours.YELLOW}[*] Se stop captura...{Colours.RESET}")
        self ._running =False 

        # ========================================================================
        # PARSARE PACHETE
        # ========================================================================

    def _parseaza_packet (self ,packet )->Optional [Dict ]:
        """
        Parseaza un packet and extrage information relevante.
        
        Strategie of parsare:
            1. Layer 2 (Ethernet/ARP)
            2. Layer 3 (IP)
            3. Layer 4 (TCP/UDP/ICMP)
            4. Layer 7 (HTTP/MQTT/DNS/FTP)
        
        Args:
            packet: Packet Scapy raw
            
        Returns:
            Dict with information parsate or None if not e relevant
        """
        info ={
        "timestamp":datetime .now ().isoformat (),
        "length":len (packet ),
        "layers":[],
        "sursa":{},
        "destinatie":{},
        "protocol":"UNKNOWN",
        "detalii":{},
        }

        # -------------------------------------------------------------------
        # Layer 2 - Data Link
        # -------------------------------------------------------------------
        if packet .haslayer (Ether ):
            info ["layers"].append ("Ethernet")
            info ["sursa"]["mac"]=packet [Ether ].src 
            info ["destinatie"]["mac"]=packet [Ether ].dst 

        if packet .haslayer (ARP ):
            info ["layers"].append ("ARP")
            info ["protocol"]="ARP"
            info ["detalii"]["arp_op"]="request"if packet [ARP ].op ==1 else "reply"
            info ["detalii"]["arp_src_ip"]=packet [ARP ].psrc 
            info ["detalii"]["arp_dst_ip"]=packet [ARP ].pdst 
            return info 

            # -------------------------------------------------------------------
            # Layer 3 - Network
            # -------------------------------------------------------------------
        if not packet .haslayer (IP ):
            return None # Ignoram packets non-IP

        info ["layers"].append ("IP")
        info ["sursa"]["ip"]=packet [IP ].src 
        info ["destinatie"]["ip"]=packet [IP ].dst 
        info ["detalii"]["ttl"]=packet [IP ].ttl 
        info ["detalii"]["ip_id"]=packet [IP ].id 

        # -------------------------------------------------------------------
        # Layer 4 - Transport
        # -------------------------------------------------------------------
        if packet .haslayer (TCP ):
            info ["layers"].append ("TCP")
            info ["protocol"]="TCP"
            info ["sursa"]["port"]=packet [TCP ].sport 
            info ["destinatie"]["port"]=packet [TCP ].dport 
            info ["detalii"]["tcp_flags"]=self ._parseaza_tcp_flags (packet [TCP ].flags )
            info ["detalii"]["seq"]=packet [TCP ].seq 
            info ["detalii"]["ack"]=packet [TCP ].ack 
            info ["detalii"]["window"]=packet [TCP ].window 

            # Detection protocol Layer 7 on baza portului
            port_dst =packet [TCP ].dport 
            port_src =packet [TCP ].sport 

            if port_dst in PORTURI_CUNOSCUTE or port_src in PORTURI_CUNOSCUTE :
                port_info =PORTURI_CUNOSCUTE .get (port_dst )or PORTURI_CUNOSCUTE .get (port_src )
                info ["detalii"]["service"]=port_info [0 ]if port_info else "Unknown"

                # Parsare payload for protocols text
            if packet .haslayer (Raw ):
                self ._parseaza_payload_tcp (packet ,info )

        elif packet .haslayer (UDP ):
            info ["layers"].append ("UDP")
            info ["protocol"]="UDP"
            info ["sursa"]["port"]=packet [UDP ].sport 
            info ["destinatie"]["port"]=packet [UDP ].dport 

            # DNS
            if packet .haslayer (DNS ):
                self ._parseaza_dns (packet ,info )

        elif packet .haslayer (ICMP ):
            info ["layers"].append ("ICMP")
            info ["protocol"]="ICMP"
            info ["detalii"]["icmp_type"]=packet [ICMP ].type 
            info ["detalii"]["icmp_code"]=packet [ICMP ].code 

        return info 

    def _parseaza_tcp_flags (self ,flags )->str :
        """
        Converteste flags TCP in string lizibil.
        
        Flags TCP:
            S = SYN (synchronize)
            A = ACK (acknowledge)
            F = FIN (finish)
            R = RST (reset)
            P = PSH (push)
            U = URG (urgent)
        """
        flag_map ={
        'F':'FIN',
        'S':'SYN',
        'R':'RST',
        'P':'PSH',
        'A':'ACK',
        'U':'URG',
        'E':'ECE',
        'C':'CWR',
        }
        result =[]
        flags_str =str (flags )
        for char ,name in flag_map .items ():
            if char in flags_str :
                result .append (name )
        return ",".join (result )if result else str (flags )

    def _parseaza_payload_tcp (self ,packet ,info :Dict ):
        """
        Parseaza payload TCP for protocols Layer 7.
        
        Protocols detectate:
            - HTTP (GET, POST, HEAD, etc.)
            - FTP (commands and responses)
            - MQTT (CONNECT, PUBLISH, SUBSCRIBE)
        """
        try :
            payload =bytes (packet [Raw ].load )

            # Incercam decodare UTF-8
            try :
                payload_text =payload .decode ('utf-8',errors ='ignore')
            except :
                payload_text =""

            port_dst =packet [TCP ].dport 
            port_src =packet [TCP ].sport 

            # ---------------------------------------------------------------
            # STUDENT SECTION - Analiza HTTP
            # Completati: Identificationa metodei HTTP and path-ului
            # Hint: HTTP incepe with "GET ", "POST ", "HEAD ", etc.
            # ---------------------------------------------------------------
            if port_dst ==80 or port_src ==80 :
                info ["detalii"]["service"]="HTTP"
                if payload_text .startswith (("GET ","POST ","HEAD ","PUT ","DELETE ")):
                    lines =payload_text .split ('\r\n')
                    if lines :
                        info ["detalii"]["http_request"]=lines [0 ]
                        # Extrage headers
                        headers ={}
                        for line in lines [1 :]:
                            if ': 'in line :
                                key ,val =line .split (': ',1 )
                                headers [key .lower ()]=val 
                        info ["detalii"]["http_headers"]=headers 
                elif payload_text .startswith ("HTTP/"):
                    lines =payload_text .split ('\r\n')
                    if lines :
                        info ["detalii"]["http_response"]=lines [0 ]

                        # ---------------------------------------------------------------
                        # Analiza FTP
                        # ---------------------------------------------------------------
            if port_dst ==21 or port_src ==21 :
                info ["detalii"]["service"]="FTP"
                # Commands FTP cunoscute
                ftp_commands =["USER","PASS","LIST","RETR","STOR","QUIT","PWD","CWD"]
                for cmd in ftp_commands :
                    if payload_text .upper ().startswith (cmd ):
                        info ["detalii"]["ftp_command"]=payload_text .strip ()
                        # Alerta for credentiale in clar
                        if cmd in ["USER","PASS"]:
                            self ._adauga_alerta (
                            "MEDIUM",
                            "FTP_CREDENTIALS_CLEARTEXT",
                            f"Credentiale FTP transmise in clar: {cmd}",
                            info 
                            )
                        break 
                        # Response FTP
                if payload_text [:3 ].isdigit ():
                    info ["detalii"]["ftp_response"]=payload_text .strip ()[:100 ]

                    # ---------------------------------------------------------------
                    # Analiza MQTT
                    # ---------------------------------------------------------------
            if port_dst ==1883 or port_src ==1883 :
                info ["detalii"]["service"]="MQTT"
                self ._parseaza_mqtt (payload ,info )
                # Alerta: MQTT without TLS
                self ._adauga_alerta (
                "HIGH",
                "MQTT_NO_TLS",
                "Traffic MQTT neencrypted detectat",
                info 
                )

        except Exception as e :
            if self .verbose >=3 :
                print (f"{Colours.RED}[!] Error parsare payload: {e}{Colours.RESET}")

    def _parseaza_mqtt (self ,payload :bytes ,info :Dict ):
        """
        Parseaza messages MQTT at nivel of octeti.
        
        Structura header MQTT:
            Byte 0: Control packet type (bits 7-4) + Flags (bits 3-0)
            Bytes 1-4: Remaining length (variable length encoding)
        
        Tipuri of packets:
            1 = CONNECT
            2 = CONNACK
            3 = PUBLISH
            4 = PUBACK
            8 = SUBSCRIBE
            9 = SUBACK
            12 = PINGREQ
            13 = PINGRESP
            14 = DISCONNECT
        """
        if len (payload )<2 :
            return 

            # Primul byte: type packet (4 biti superiori)
        packet_type =(payload [0 ]&0xF0 )>>4 

        mqtt_types ={
        1 :"CONNECT",
        2 :"CONNACK",
        3 :"PUBLISH",
        4 :"PUBACK",
        5 :"PUBREC",
        6 :"PUBREL",
        7 :"PUBCOMP",
        8 :"SUBSCRIBE",
        9 :"SUBACK",
        10 :"UNSUBSCRIBE",
        11 :"UNSUBACK",
        12 :"PINGREQ",
        13 :"PINGRESP",
        14 :"DISCONNECT",
        }

        mqtt_type_name =mqtt_types .get (packet_type ,f"UNKNOWN({packet_type})")
        info ["detalii"]["mqtt_type"]=mqtt_type_name 

        # ---------------------------------------------------------------
        # STUDENT SECTION - Parsare MQTT PUBLISH
        # Completati: Extrageti topic and payload from message PUBLISH
        # Hint: After header, urmeaza length topic (2 bytes) + topic + payload
        # ---------------------------------------------------------------
        if packet_type ==3 :# PUBLISH
            try :
            # QoS from flags (bits 1-2)
                qos =(payload [0 ]&0x06 )>>1 
                info ["detalii"]["mqtt_qos"]=qos 

                # Skip remaining length (can fi 1-4 bytes)
                pos =1 
                remaining_length =0 
                multiplier =1 
                while pos <min (len (payload ),5 ):
                    byte =payload [pos ]
                    remaining_length +=(byte &0x7F )*multiplier 
                    pos +=1 
                    if (byte &0x80 )==0 :
                        break 
                    multiplier *=128 

                    # Topic length (2 bytes big-endian)
                if pos +2 <=len (payload ):
                    topic_len =(payload [pos ]<<8 )|payload [pos +1 ]
                    pos +=2 

                    # Topic name
                    if pos +topic_len <=len (payload ):
                        topic =payload [pos :pos +topic_len ].decode ('utf-8',errors ='ignore')
                        info ["detalii"]["mqtt_topic"]=topic 
                        pos +=topic_len 

                        # Skip packet identifier for QoS > 0
                        if qos >0 and pos +2 <=len (payload ):
                            pos +=2 

                            # Payload
                        if pos <len (payload ):
                            mqtt_payload =payload [pos :].decode ('utf-8',errors ='ignore')
                            info ["detalii"]["mqtt_payload"]=mqtt_payload [:200 ]# Limita
            except Exception as e :
                if self .verbose >=3 :
                    print (f"[!] Error parsare MQTT PUBLISH: {e}")

    def _parseaza_dns (self ,packet ,info :Dict ):
        """
        Parseaza interogari and responses DNS.
        
        DNS can expune:
            - Domenii accesate (privacy concern)
            - Potentiale tuneluri DNS (exfiltrare date)
            - DNS spoofing attacks
        """
        info ["detalii"]["service"]="DNS"
        info ["protocol"]="DNS"

        dns =packet [DNS ]

        # Query (QR=0) or Response (QR=1)
        is_response =dns .qr ==1 
        info ["detalii"]["dns_type"]="response"if is_response else "query"

        # Extrage query name
        if dns .qdcount >0 and packet .haslayer (DNSQR ):
            qname =packet [DNSQR ].qname .decode ('utf-8',errors ='ignore').rstrip ('.')
            info ["detalii"]["dns_query"]=qname 

            # Stocare for statistici
            if not is_response :
                self .statistici ["dns_queries"].append ({
                "timestamp":info ["timestamp"],
                "query":qname ,
                "src_ip":info ["sursa"]["ip"]
                })

                # Responses
        if is_response and dns .ancount >0 and packet .haslayer (DNSRR ):
            answers =[]
            for i in range (dns .ancount ):
                try :
                    rr =dns .year [i ]
                    if hasattr (rr ,'rdata'):
                        answers .append (str (rr .rdata ))
                except :
                    pass 
            info ["detalii"]["dns_answers"]=answers 

    def _adauga_alerta (
    self ,
    severitate :str ,
    type :str ,
    message :str ,
    packet_info :Dict 
    ):
        """
        Add o alerta of security.
        
        Severitati:
            - LOW: Informational
            - MEDIUM: Potential risc
            - HIGH: Risc semnificativ
            - CRITICAL: Necesita actiune imediata
        """
        alerta ={
        "timestamp":datetime .now ().isoformat (),
        "severitate":severitate ,
        "type":type ,
        "message":message ,
        "sursa_ip":packet_info .get ("sursa",{}).get ("ip","N/A"),
        "dest_ip":packet_info .get ("destinatie",{}).get ("ip","N/A"),
        }
        self .statistici ["alerte_security"].append (alerta )

        if self .verbose >=1 :
            colour ={
            "LOW":Colours .BLUE ,
            "MEDIUM":Colours .YELLOW ,
            "HIGH":Colours .RED ,
            "CRITICAL":Colours .RED +Colours .BOLD ,
            }.get (severitate ,Colours .WHITE )

            print (f"{colour}[ALERTA {severitate}] {type}: {message}{Colours.RESET}")

            # ========================================================================
            # PROCESARE PACHETE
            # ========================================================================

    def _proceseaza_packet (self ,packet ):
        """
        Callback for each packet capturat.
        
        Flow:
            1. Parsare packet
            2. Update statistici
            3. Afisare (if verbose)
            4. Stocare for export
        """
        info =self ._parseaza_packet (packet )
        if info is None :
            return 

            # Update statistici
        self .statistici ["total_packete"]+=1 
        self .statistici ["total_bytes"]+=info ["length"]
        self .statistici ["protocols"][info ["protocol"]]+=1 

        if "ip"in info ["sursa"]:
            self .statistici ["ip_sursa"][info ["sursa"]["ip"]]+=1 
        if "ip"in info ["destinatie"]:
            self .statistici ["ip_dest"][info ["destinatie"]["ip"]]+=1 
        if "port"in info ["sursa"]:
            self .statistici ["ports_sursa"][info ["sursa"]["port"]]+=1 
        if "port"in info ["destinatie"]:
            self .statistici ["ports_dest"][info ["destinatie"]["port"]]+=1 

            # Tracking connections (5-tuple)
        if "ip"in info ["sursa"]and "port"in info ["sursa"]:
            conn_key =(
            info ["sursa"]["ip"],
            info ["sursa"].get ("port",0 ),
            info ["destinatie"]["ip"],
            info ["destinatie"].get ("port",0 ),
            info ["protocol"]
            )
            self .statistici ["connections"][conn_key ]["packets"]+=1 
            self .statistici ["connections"][conn_key ]["bytes"]+=info ["length"]

            # Afisare
        if self .verbose >=1 :
            self ._afiseaza_packet (info )

            # Stocare for export
        self ._packete_capturate .append (info )

    def _afiseaza_packet (self ,info :Dict ):
        """
        Display information about packet in format lizibil.
        """
        ts =info ["timestamp"].split ("T")[1 ][:12 ]# HH:MM:SS.mmm

        # Colour on baza protocolului
        colour ={
        "TCP":Colours .GREEN ,
        "UDP":Colours .BLUE ,
        "ICMP":Colours .YELLOW ,
        "DNS":Colours .CYAN ,
        "ARP":Colours .MAGENTA ,
        }.get (info ["protocol"],Colours .WHITE )

        # Format of baza
        src =info ["sursa"].get ("ip",info ["sursa"].get ("mac","?"))
        dst =info ["destinatie"].get ("ip",info ["destinatie"].get ("mac","?"))

        if "port"in info ["sursa"]:
            src +=f":{info['sursa']['port']}"
        if "port"in info ["destinatie"]:
            dst +=f":{info['destinatie']['port']}"

        output =f"{colour}[{ts}] {info['protocol']:5} {src:22} → {dst:22}"

        # Addition detalii
        detalii =info .get ("detalii",{})
        extracted =[]

        if "tcp_flags"in detalii :
            extracted .append (f"Flags={detalii['tcp_flags']}")
        if "service"in detalii :
            extracted .append (f"[{detalii['service']}]")
        if "http_request"in detalii :
            extracted .append (detalii ["http_request"][:50 ])
        if "mqtt_type"in detalii :
            extracted .append (f"MQTT:{detalii['mqtt_type']}")
            if "mqtt_topic"in detalii :
                extracted .append (f"Topic={detalii['mqtt_topic']}")
        if "dns_query"in detalii :
            extracted .append (f"DNS:{detalii['dns_query']}")
        if "ftp_command"in detalii :
            extracted .append (detalii ["ftp_command"][:30 ])

        if extracted :
            output +=f" | {' '.join(extracted)}"

        output +=f" ({info['length']}B){Colours.RESET}"
        print (output )

        # ========================================================================
        # EXECUTIE CAPTURA
        # ========================================================================

    def start (self ):
        """
        Start captura of packets.
        
        Metoda:
            - Scapy sniff() with callback
            - Filter BPF for eficienta
            - Stop condition: count or Ctrl+C
        """
        if not SCAPY_DISPONIBIL :
            print (f"{Colours.RED}[!] Scapy not is disponibil. Instalati with:")
            print (f"    pip install scapy --break-system-packages{Colours.RESET}")
            return False 

            # Verification allowediuni
        if os .geteuid ()!=0 :
            print (f"{Colours.YELLOW}[!] AVERTISMENT: Running without root can limita functionalitatea")
            print (f"    Recomandare: sudo python3 {sys.argv[0]}{Colours.RESET}")

            # Header
        print (f"\n{Colours.CYAN}{'='*70}")
        print (f"  PACKET SNIFFER - IoT & Network Security")
        print (f"  Interface: {self.interface}")
        if self .bpf_filter :
            print (f"  Filtru BPF: {self.bpf_filter}")
        if self .packet_count >0 :
            print (f"  Limita packets: {self.packet_count}")
        print (f"  Apasati Ctrl+C for stop")
        print (f"{'='*70}{Colours.RESET}\n")

        self .statistici ["start_time"]=datetime .now ().isoformat ()
        self ._running =True 

        try :
        # Configuration Scapy
            conf .verb =0 # Dezactiveare output Scapy

            # Start sniffing
            sniff (
            iface =self .interface if self .interface !="any"else None ,
            filter =self .bpf_filter if self .bpf_filter else None ,
            prn =self ._proceseaza_packet ,
            count =self .packet_count if self .packet_count >0 else 0 ,
            store =False ,# Not stocam in memorie Scapy
            stop_filter =lambda x :not self ._running 
            )

        except AllowedsionError :
            print (f"{Colours.RED}[!] Error allowediuni. Run with sudo.{Colours.RESET}")
            return False 
        except Exception as e :
            print (f"{Colours.RED}[!] Error capture: {e}{Colours.RESET}")
            return False 
        finally :
            self .statistici ["end_time"]=datetime .now ().isoformat ()
            self ._afiseaza_statistici ()

            if self .output_file :
                self ._exporta_json ()

        return True 

    def _afiseaza_statistici (self ):
        """
        Display statistici agregate at finalul capturesi.
        """
        stats =self .statistici 

        print (f"\n{Colours.CYAN}{'='*70}")
        print (f"  STATISTICI CAPTURA")
        print (f"{'='*70}{Colours.RESET}")

        # Sumar
        print (f"\n{Colours.BOLD}Sumar:{Colours.RESET}")
        print (f"  Total packets:  {stats['total_packete']}")
        print (f"  Total bytes:    {stats['total_bytes']:,}")
        print (f"  Duration:         {stats['start_time']} - {stats['end_time']}")

        # Protocols
        if stats ["protocols"]:
            print (f"\n{Colours.BOLD}Protocols:{Colours.RESET}")
            for proto ,count in sorted (stats ["protocols"].items (),key =lambda x :-x [1 ]):
                pct =(count /stats ["total_packete"])*100 if stats ["total_packete"]>0 else 0 
                print (f"  {proto:10} {count:6} ({pct:5.1f}%)")

                # Top IP-uri
        if stats ["ip_sursa"]:
            print (f"\n{Colours.BOLD}Top 5 IP-uri sursa:{Colours.RESET}")
            for ip ,count in sorted (stats ["ip_sursa"].items (),key =lambda x :-x [1 ])[:5 ]:
                print (f"  {ip:20} {count:6} packets")

                # Top ports destinatie
        if stats ["ports_dest"]:
            print (f"\n{Colours.BOLD}Top 5 ports destinatie:{Colours.RESET}")
            for port ,count in sorted (stats ["ports_dest"].items (),key =lambda x :-x [1 ])[:5 ]:
                port_name =PORTURI_CUNOSCUTE .get (port ,("Unknown",))[0 ]
                print (f"  {port:5} ({port_name:10}) {count:6} packets")

                # DNS Queries
        if stats ["dns_queries"]:
            print (f"\n{Colours.BOLD}DNS Queries ({len(stats['dns_queries'])}):{Colours.RESET}")
            # Unique queries
            unique =list (set (q ["query"]for q in stats ["dns_queries"]))[:10 ]
            for query in unique :
                print (f"  {query}")

                # Alerte security
        if stats ["alerte_security"]:
            print (f"\n{Colours.RED}{Colours.BOLD}Alerte Security ({len(stats['alerte_security'])}):{Colours.RESET}")
            for alerta in stats ["alerte_security"][-10 :]:# Ultimele 10
                print (f"  [{alerta['severitate']}] {alerta['type']}: {alerta['message']}")

        print (f"\n{Colours.CYAN}{'='*70}{Colours.RESET}")

    def _exporta_json (self ):
        """
        Exporta statisticile in format JSON.
        """
        try :
        # Convertim defaultdict in dict standard
            export_data ={
            "metadata":{
            "start_time":self .statistici ["start_time"],
            "end_time":self .statistici ["end_time"],
            "interface":self .interface ,
            "filter":self .bpf_filter ,
            },
            "summary":{
            "total_packets":self .statistici ["total_packete"],
            "total_bytes":self .statistici ["total_bytes"],
            },
            "protocols":dict (self .statistici ["protocols"]),
            "top_src_ips":dict (sorted (
            self .statistici ["ip_sursa"].items (),
            key =lambda x :-x [1 ]
            )[:20 ]),
            "top_dst_ips":dict (sorted (
            self .statistici ["ip_dest"].items (),
            key =lambda x :-x [1 ]
            )[:20 ]),
            "top_dst_ports":dict (sorted (
            self .statistici ["ports_dest"].items (),
            key =lambda x :-x [1 ]
            )[:20 ]),
            "dns_queries":self .statistici ["dns_queries"][-100 :],
            "security_alerts":self .statistici ["alerte_security"],
            }

            with open (self .output_file ,'w',encoding ='utf-8')as f :
                json .dump (export_data ,f ,indent =2 ,ensure_ascii =False )

            print (f"\n{Colours.GREEN}[✓] Statistici exportate in: {self.output_file}{Colours.RESET}")

        except Exception as e :
            print (f"{Colours.RED}[!] Error export JSON: {e}{Colours.RESET}")


            # ============================================================================
            # HELPER FUNCTIONS - FILTRE PREDEFINITE
            # ============================================================================

def get_predefined_filters ()->Dict [str ,str ]:
    """
    Return filtre BPF predefinite for scenarii comune.
    
    BPF (Berkeley Packet Filter) allow filtrarea eficienta
    at nivel kernel, inainte ca packetele sa ajunga in userspace.
    """
    return {
    "mqtt":"tcp port 1883 or tcp port 8883",
    "http":"tcp port 80 or tcp port 443 or tcp port 8080",
    "ftp":"tcp port 20 or tcp port 21",
    "dns":"udp port 53 or tcp port 53",
    "ssh":"tcp port 22",
    "pentest":"tcp port 21 or tcp port 22 or tcp port 80 or tcp port 443 or tcp port 1883",
    "iot":"tcp port 1883 or tcp port 8883 or tcp port 5683 or tcp port 5684",# MQTT + CoAP
    "docker":"net 172.17.0.0/16 or net 172.18.0.0/16 or net 172.20.0.0/16",
    }


    # ============================================================================
    # CLI - INTERFATA LINIE DE COMANDA
    # ============================================================================

def lista_interfete ():
    """Listeaza interfacesle of network disponibile."""
    if not SCAPY_DISPONIBIL :
        print ("[!] Scapy is not installed")
        return 

    print (f"\n{Colours.CYAN}Interfaces of network disponibile:{Colours.RESET}")
    for iface in get_if_list ():
        print (f"  - {iface}")
    print ()


def main ():
    """
    Punct of intrare principal.
    
    Examples usage:
        # Capture on all interfacesle
        sudo python3 ex_03_packet_sniffer.py
        
        # Only MQTT
        sudo python3 ex_03_packet_sniffer.py --filter mqtt
        
        # Interface specify, 100 packets
        sudo python3 ex_03_packet_sniffer.py -i eth0 -c 100
        
        # Export JSON
        sudo python3 ex_03_packet_sniffer.py --output captura.json
        
        # Filtru BPF custom
        sudo python3 ex_03_packet_sniffer.py --bpf "tcp port 1883 and host 10.0.13.110"
    """
    parser =argparse .ArgumentParser (
    description ="Packet Sniffer for IoT and Security in Networks",
    formatter_class =argparse .RawDescriptionHelpFormatter ,
    epilog ="""
Examples:
  %(prog)s                           # Capture on all interfacesle
  %(prog)s -i docker0 --filter mqtt  # MQTT on docker0
  %(prog)s -c 50 --output cap.json   # 50 packets, export JSON
  %(prog)s --bpf "tcp port 80"       # Filtru BPF custom
  %(prog)s --list-interfaces         # Listeaza interfaces disponibile
  %(prog)s --list-filters            # Listeaza filtre predefinite
        """
    )

    parser .add_argument (
    '-i','--interface',
    default ='any',
    help ='Interfata of capture (default: any)'
    )

    parser .add_argument (
    '-c','--count',
    type =int ,
    default =0 ,
    help ='Number maximum of packets (default: infinit)'
    )

    parser .add_argument (
    '--bpf',
    default ='',
    help ='Filtru BPF custom (ex: "tcp port 1883")'
    )

    parser .add_argument (
    '--filter',
    choices =list (get_predefined_filters ().keys ()),
    help ='Filtru predefinit: mqtt, http, ftp, dns, pentest, iot'
    )

    parser .add_argument (
    '-o','--output',
    help ='File JSON for export statistici'
    )

    parser .add_argument (
    '-v','--verbose',
    action ='count',
    default =1 ,
    help ='Nivel verbozitate (-v, -vv, -vvv)'
    )

    parser .add_argument (
    '-q','--quiet',
    action ='store_true',
    help ='Mod silentios (only statistici at final)'
    )

    parser .add_argument (
    '--list-interfaces',
    action ='store_true',
    help ='Listeaza interfacesle of network disponibile'
    )

    parser .add_argument (
    '--list-filters',
    action ='store_true',
    help ='Listeaza filtrele predefinite'
    )

    parser .add_argument (
    '--no-color',
    action ='store_true',
    help ='Dezactiveeaza output colorat'
    )

    args =parser .parse_args ()

    # Dezactiveare colours
    if args .no_color :
        Colours .disable ()

        # Listare interfaces
    if args .list_interfaces :
        lista_interfete ()
        return 

        # Listare filtre
    if args .list_filters :
        print (f"\n{Colours.CYAN}Filtre BPF predefinite:{Colours.RESET}")
        for name ,bpf in get_predefined_filters ().items ():
            print (f"  {Colours.GREEN}{name:10}{Colours.RESET} → {bpf}")
        print ()
        return 

        # Determinare filtru BPF
    bpf_filter =args .bpf 
    if args .filter :
        bpf_filter =get_predefined_filters ()[args .filter ]

        # Verbose level
    verbose =0 if args .quiet else args .verbose 

    # Create and start sniffer
    sniffer =PacketSniffer (
    interface =args .interface ,
    packet_count =args .count ,
    bpf_filter =bpf_filter ,
    verbose =verbose ,
    output_file =args .output 
    )

    # Disclaimer
    print (f"""
{Colours.YELLOW}{'='*70}
  DISCLAIMER: This instrument is destinat EXCLUSIV for
  medii of testing controlate (laboratoare, containere Docker).
  
  Interceptiona trafficului of network without authorisation is ILEGALA!
{'='*70}{Colours.RESET}
    """)

    sniffer .start ()


if __name__ =="__main__":
    main ()
