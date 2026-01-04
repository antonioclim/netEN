#!/usr/bin/env python3
"""
================================================================================
Exercise 4: Verificator of Vulnerabilities
================================================================================
S13 - IoT and Security in Computer Networks

PEDAGOGICAL OBJECTIVES:
1. Understanding conceptului of CVE (Common Vulnerabilities and Exposures)
2. Corelarea versiunilor software with vulnerabilities cunoscute
3. Automatizarea procesului of verification
4. Generationa security reports

VULNERABILITATI ACOPERITE:
- CVE-2011-2523: vsftpd 2.3.4 backdoor
- CVE-2017-5638: Apache Struts2 RCE
- CVE-2014-0160: OpenSSL Heartbleed
- Diverse configurari nesigure

USAGE:
    python3 ex_04_vuln_checker.py --target 10.0.13.12 --port 2121 --service ftp
    python3 ex_04_vuln_checker.py --target 10.0.13.11 --port 80 --service http --all
================================================================================
"""

from __future__ import annotations 

import argparse 
import json 
import re 
import socket 
import sys 
from dataclasses import dataclass 
from datetime import datetime 
from typing import Dict ,List ,Optional ,Tuple 

# ==============================================================================
# CONSTANTE SI BAZA DE DATE VULNERABILITATI
# ==============================================================================

class Colors :
    RED ="\033[91m"
    GREEN ="\033[92m"
    YELLOW ="\033[93m"
    BLUE ="\033[94m"
    CYAN ="\033[96m"
    RESET ="\033[0m"
    BOLD ="\033[1m"


    # Baza of date locala with vulnerabilities cunoscute
VULNERABILITY_DB :Dict [str ,List [dict ]]={
"ftp":[
{
"id":"CVE-2011-2523",
"name":"vsftpd 2.3.4 Backdoor",
"severity":"CRITICAL",
"cvss":10.0 ,
"affected_versions":["2.3.4"],
"banner_pattern":r"vsftpd 2\.3\.4",
"description":"Versiunea 2.3.4 contains un backdoor which deschide portul 6200 when username-ul contains ':)'",
"remediation":"Update at versiunea 2.3.5 or more noua",
"references":[
"https://nvd.nist.gov/vuln/detail/CVE-2011-2523",
"https://www.rapid7.com/db/modules/exploit/unix/ftp/vsftpd_234_backdoor/"
]
},
{
"id":"FTP-ANON",
"name":"Anonymous FTP Access",
"severity":"MEDIUM",
"cvss":5.3 ,
"affected_versions":["*"],
"banner_pattern":None ,# Verification speciala
"description":"Serverul FTP allow acces anonim, expunand potential files sensibile",
"remediation":"Dezactiveeaza accesul anonim or restrictioneaza directoarele expuse",
"references":[]
}
],
"http":[
{
"id":"HTTP-METHODS",
"name":"Dangerous HTTP Methods Enabled",
"severity":"MEDIUM",
"cvss":5.3 ,
"affected_versions":["*"],
"banner_pattern":None ,
"description":"Metodele HTTP periculoase (PUT, DELETE, TRACE) are activeate",
"remediation":"Dezactiveeaza metodele HTTP nefolosite in configuratia serverului",
"references":[]
},
{
"id":"HTTP-HEADERS",
"name":"Missing Security Headers",
"severity":"LOW",
"cvss":3.7 ,
"affected_versions":["*"],
"banner_pattern":None ,
"description":"Lipsesc headerele of security (X-Frame-Options, CSP, etc.)",
"remediation":"Add headerele of security in configuratia serverului",
"references":[]
},
{
"id":"PHP-VERSION",
"name":"Outdated PHP Version",
"severity":"HIGH",
"cvss":7.5 ,
"affected_versions":["5.*","7.0.*","7.1.*","7.2.*"],
"banner_pattern":r"PHP/([0-9]+\.[0-9]+)",
"description":"Versiunea PHP is depasita and can contains vulnerabilities cunoscute",
"remediation":"Update at PHP 8.1+ or cea more recenta version suportata",
"references":[]
}
],
"ssh":[
{
"id":"SSH-WEAK-ALGO",
"name":"Weak SSH Algorithms",
"severity":"MEDIUM",
"cvss":5.9 ,
"affected_versions":["*"],
"banner_pattern":None ,
"description":"Serverul SSH accept algoritmi of encryption slabi",
"remediation":"Configure only algoritmi moderni (ChaCha20, AES-GCM)",
"references":[]
}
],
"mqtt":[
{
"id":"MQTT-NOAUTH",
"name":"MQTT Anonymous Access",
"severity":"HIGH",
"cvss":7.5 ,
"affected_versions":["*"],
"banner_pattern":None ,
"description":"Broker-ul MQTT allow connections anonime",
"remediation":"Activeeaza authenticationa and ACL-uri",
"references":[]
},
{
"id":"MQTT-NOTLS",
"name":"MQTT Without TLS",
"severity":"HIGH",
"cvss":7.5 ,
"affected_versions":["*"],
"banner_pattern":None ,
"description":"Trafficul MQTT not is encrypted",
"remediation":"Configure TLS on portul 8883",
"references":[]
}
]
}


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass 
class VulnerabilityResult :
    """Resultul checkrii unei vulnerabilities."""
    vuln_id :str 
    name :str 
    severity :str 
    cvss :float 
    vulnerable :bool 
    evidence :Optional [str ]=None 
    description :Optional [str ]=None 
    remediation :Optional [str ]=None 


@dataclass 
class ScanReport :
    """Report complete of scanning."""
    target :str 
    port :int 
    service :str 
    scan_time :str 
    banner :Optional [str ]
    vulnerabilities :List [VulnerabilityResult ]
    risk_score :float 


    # ==============================================================================
    # FUNCTII DE VERIFICATION
    # ==============================================================================

def grab_banner (host :str ,port :int ,timeout :float =2.0 )->Optional [str ]:
    """Obtine banner-ul servicelui."""
    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout )
        sock .connect ((host ,port ))

        # Sendm un stimul for a obtine response
        sock .sendall (b"\r\n")
        banner =sock .recv (1024 ).decode ("utf-8",errors ="replace").strip ()
        sock .close ()
        return banner 
    except Exception :
        return None 


def check_http_headers (host :str ,port :int ,timeout :float =2.0 )->Tuple [dict ,str ]:
    """Check headerele HTTP ale serverului."""
    headers ={}
    raw_response =""

    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout )
        sock .connect ((host ,port ))

        request =f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock .sendall (request .encode ())

        response =b""
        while True :
            chunk =sock .recv (4096 )
            if not chunk :
                break 
            response +=chunk 

        sock .close ()
        raw_response =response .decode ("utf-8",errors ="replace")

        # Parsam headerele
        for line in raw_response .split ("\r\n"):
            if ": "in line :
                key ,value =line .split (": ",1 )
                headers [key .lower ()]=value 

    except Exception as e :
        pass 

    return headers ,raw_response 


def check_http_methods (host :str ,port :int ,timeout :float =2.0 )->List [str ]:
    """Check metodele HTTP disponibile."""
    methods =[]

    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout )
        sock .connect ((host ,port ))

        request =f"OPTIONS / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock .sendall (request .encode ())

        response =sock .recv (4096 ).decode ("utf-8",errors ="replace")
        sock .close ()

        # Cautam headerul Allow
        for line in response .split ("\r\n"):
            if line .lower ().startswith ("allow:"):
                methods =[m .strip ()for m in line .split (":",1 )[1 ].split (",")]
                break 

    except Exception :
        pass 

    return methods 


def check_ftp_anonymous (host :str ,port :int ,timeout :float =5.0 )->bool :
    """Check if serverul FTP allow acces anonim."""
    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout )
        sock .connect ((host ,port ))

        # Citim bannerul
        sock .recv (1024 )

        # Incercam login anonim
        sock .sendall (b"USER anonymous\r\n")
        response =sock .recv (1024 ).decode ("utf-8",errors ="replace")

        if "331"in response :# 331 = password required
            sock .sendall (b"PASS anonymous@\r\n")
            response =sock .recv (1024 ).decode ("utf-8",errors ="replace")
            sock .close ()
            return "230"in response # 230 = login successful

        sock .close ()
        return False 

    except Exception :
        return False 


def check_mqtt_anonymous (host :str ,port :int =1883 ,timeout :float =3.0 )->bool :
    """Check if broker-ul MQTT allow connections anonime."""
    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout )
        sock .connect ((host ,port ))

        # MQTT CONNECT packet (protocol level)
        # Simplificat - only checkm if accept connection
        connect_packet =bytes ([
        0x10 ,# CONNECT packet type
        0x10 ,# Remaining length
        0x00 ,0x04 ,# Protocol name length
        0x4D ,0x51 ,0x54 ,0x54 ,# "MQTT"
        0x04 ,# Protocol level (4 = 3.1.1)
        0x02 ,# Connect flags (clean session)
        0x00 ,0x3C ,# Keep alive (60 seconds)
        0x00 ,0x04 ,# Client ID length
        0x74 ,0x65 ,0x73 ,0x74 # "test"
        ])

        sock .sendall (connect_packet )
        response =sock .recv (4 )
        sock .close ()

        # CONNACK with return code 0 = acceptat
        if len (response )>=4 and response [0 ]==0x20 and response [3 ]==0x00 :
            return True 

        return False 

    except Exception :
        return False 


        # ==============================================================================
        # ENGINE DE VERIFICATION
        # ==============================================================================

def check_vulnerabilities (
host :str ,
port :int ,
service :str ,
check_all :bool =False 
)->ScanReport :
    """
    Check vulnerabilities for un service specific.
    
    Args:
        host: IP address or hostname
        port: Portul servicelui
        service: Tipul servicelui (ftp, http, ssh, mqtt)
        check_all: Check all vulnerabilitiesle, not only cele critice
    
    Returns:
        ScanReport with all vulnerabilitiesle gasite
    """
    scan_time =datetime .now ().isoformat ()
    vulnerabilities :List [VulnerabilityResult ]=[]
    banner =None 

    print (f"\n{Colors.BOLD}[*] Verification vulnerabilities: {host}:{port} ({service}){Colors.RESET}")
    print (f"    Timestamp: {scan_time}")

    # Obtinem banner-ul
    if service in ["ftp","ssh"]:
        banner =grab_banner (host ,port )
        if banner :
            print (f"    Banner: {banner[:60]}...")
    elif service =="http":
        headers ,raw =check_http_headers (host ,port )
        banner =headers .get ("server","")
        if banner :
            print (f"    Server: {banner}")

            # Checkm vulnerabilitiesle from baza of date
    if service not in VULNERABILITY_DB :
        print (f"    {Colors.YELLOW}[!] Service unknown: {service}{Colors.RESET}")
        return ScanReport (
        target =host ,port =port ,service =service ,
        scan_time =scan_time ,banner =banner ,
        vulnerabilities =[],risk_score =0.0 
        )

    print (f"\n{Colors.BLUE}[*] Verification vulnerabilities cunoscute...{Colors.RESET}")

    for vuln in VULNERABILITY_DB [service ]:
    # Checkm if must sa checkm this vulnerability
        if not check_all and vuln ["severity"]not in ["CRITICAL","HIGH"]:
            continue 

        result =VulnerabilityResult (
        vuln_id =vuln ["id"],
        name =vuln ["name"],
        severity =vuln ["severity"],
        cvss =vuln ["cvss"],
        vulnerable =False ,
        description =vuln ["description"],
        remediation =vuln ["remediation"]
        )

        # Verification bazata on banner pattern
        if vuln .get ("banner_pattern")and banner :
            if re .search (vuln ["banner_pattern"],banner ,re .IGNORECASE ):
                result .vulnerable =True 
                result .evidence =f"Banner match: {banner}"

                # Checkri specifice
        if vuln ["id"]=="FTP-ANON"and service =="ftp":
            if check_ftp_anonymous (host ,port ):
                result .vulnerable =True 
                result .evidence ="Anonymous FTP login successful"

        elif vuln ["id"]=="HTTP-METHODS"and service =="http":
            methods =check_http_methods (host ,port )
            dangerous =set (methods )&{"PUT","DELETE","TRACE"}
            if dangerous :
                result .vulnerable =True 
                result .evidence =f"Dangerous methods: {', '.join(dangerous)}"

        elif vuln ["id"]=="HTTP-HEADERS"and service =="http":
            headers ,_ =check_http_headers (host ,port )
            missing =[]
            for h in ["x-frame-options","x-content-type-options","content-security-policy"]:
                if h not in headers :
                    missing .append (h )
            if missing :
                result .vulnerable =True 
                result .evidence =f"Missing headers: {', '.join(missing)}"

        elif vuln ["id"]=="MQTT-NOAUTH"and service =="mqtt":
            if check_mqtt_anonymous (host ,port ):
                result .vulnerable =True 
                result .evidence ="Anonymous MQTT connection accepted"

        elif vuln ["id"]=="MQTT-NOTLS"and service =="mqtt":
            if port ==1883 :# Port plaintext standard
                result .vulnerable =True 
                result .evidence =f"MQTT on plaintext port {port}"

                # Afisam resultul
        if result .vulnerable :
            severity_color ={
            "CRITICAL":Colors .RED ,
            "HIGH":Colors .RED ,
            "MEDIUM":Colors .YELLOW ,
            "LOW":Colors .BLUE 
            }.get (result .severity ,Colors .RESET )

            print (f"    {severity_color}[VULN] {result.vuln_id}: {result.name}{Colors.RESET}")
            print (f"           Severitate: {result.severity} (CVSS: {result.cvss})")
            if result .evidence :
                print (f"           Evidenta: {result.evidence}")

        vulnerabilities .append (result )

        # Calculam scorul of risc
    vuln_found =[v for v in vulnerabilities if v .vulnerable ]
    if vuln_found :
        risk_score =max (v .cvss for v in vuln_found )
    else :
        risk_score =0.0 

        # Sumar
    print (f"\n{Colors.BOLD}[+] Sumar verification:{Colors.RESET}")
    print (f"    Vulnerabilities gasite: {len(vuln_found)}")
    print (f"    Scor risc: {risk_score:.1f}/10.0")

    return ScanReport (
    target =host ,
    port =port ,
    service =service ,
    scan_time =scan_time ,
    banner =banner ,
    vulnerabilities =vulnerabilities ,
    risk_score =risk_score 
    )


def export_report (report :ScanReport ,output_path :str )->None :
    """Exporta raportul in format JSON."""
    data ={
    "vulnerability_report":{
    "target":report .target ,
    "port":report .port ,
    "service":report .service ,
    "scan_time":report .scan_time ,
    "banner":report .banner ,
    "risk_score":report .risk_score ,
    "vulnerabilities":[
    {
    "id":v .vuln_id ,
    "name":v .name ,
    "severity":v .severity ,
    "cvss":v .cvss ,
    "vulnerable":v .vulnerable ,
    "evidence":v .evidence ,
    "description":v .description ,
    "remediation":v .remediation 
    }
    for v in report .vulnerabilities if v .vulnerable 
    ]
    }
    }

    with open (output_path ,"w",encoding ="utf-8")as f :
        json .dump (data ,f ,indent =2 ,ensure_ascii =False )

    print (f"\n{Colors.GREEN}[✓] Report exportat: {output_path}{Colors.RESET}")


    # ==============================================================================
    # MAIN
    # ==============================================================================

def main ():
    parser =argparse .ArgumentParser (
    description ="Vulnerability checker for laboratory S13"
    )

    parser .add_argument ("--target",required =True ,help ="Adresa IP target")
    parser .add_argument ("--port",type =int ,required =True ,help ="Port service")
    parser .add_argument ("--service",required =True ,
    choices =["ftp","http","ssh","mqtt"],
    help ="Type service")
    parser .add_argument ("--all",action ="store_true",
    help ="Check all vulnerabilitiesle, not only critice")
    parser .add_argument ("--json-out",metavar ="FILE",
    help ="Export report JSON")

    args =parser .parse_args ()

    # Banner
    print (f"\n{Colors.CYAN}{'='*60}")
    print ("  S13 - Verificator Vulnerabilities")
    print ("  WARNING: For controlled environment only!")
    print (f"{'='*60}{Colors.RESET}")

    # Rulam verification
    report =check_vulnerabilities (
    host =args .target ,
    port =args .port ,
    service =args .service ,
    check_all =args .all 
    )

    # Export if cerut
    if args .json_out :
        export_report (report ,args .json_out )

    print ()


if __name__ =="__main__":
    main ()
