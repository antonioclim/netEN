#!/usr/bin/env python3
"""
================================================================================
Exercise 2: MQTT Client (Publisher/Subscriber)
================================================================================
S13 - IoT and Security in Computer Networks

PEDAGOGICAL OBJECTIVES:
1. Understanding the model publish-subscribe
2. Implementing communication MQTT plaintext and TLS
3. Configuring authentication and QoS
4. Analysing security differences between modes

KEY CONCEPTS:
- Topic: communication channel (ex: home/kitchen/temperature)
- Publisher: sends messages to a topic
- Subscriber: receives messages from topics
- QoS: Quality of Service (0 = fire-and-forget, 1 = at least once, 2 = exactly once)
- TLS: Transport Layer Security (end-to-end encryption)

USAGE:
    # Controller (subscriber) - plaintext
    python3 ex_02_mqtt_client.py --role controller --host 10.0.0.100 --port 1883 \\
        --topic home/kitchen/telemetry

    # Sensor (publisher) - plaintext
    python3 ex_02_mqtt_client.py --role sensor --host 10.0.0.100 --port 1883 \\
        --topic home/kitchen/telemetry --payload '{"temp":22.5}' --count 5

    # With TLS and Authentication
    python3 ex_02_mqtt_client.py --role sensor --host 10.0.0.100 --port 8883 \\
        --tls on --cafile configs/certs/ca.crt \\
        --username sensor1 --password sensor1pass \\
        --topic home/kitchen/telemetry
================================================================================
"""

from __future__ import annotations 

import argparse 
import json 
import os 
import random 
import sys 
import time 
from datetime import datetime 
from typing import Optional 

# ==============================================================================
# VERIFICATION DEPENDENTE
# ==============================================================================

try :
    import paho .mqtt .client as mqtt 
except ImportError :
    print ("[FATAL] Biblioteca paho-mqtt is not installeda!")
    print ("        Running: pip install paho-mqtt")
    sys .exit (1 )

    # ==============================================================================
    # CONSTANTS AND CONFIGURATION
    # ==============================================================================

class Colors :
    RED ="\033[91m"
    GREEN ="\033[92m"
    YELLOW ="\033[93m"
    BLUE ="\033[94m"
    CYAN ="\033[96m"
    RESET ="\033[0m"
    BOLD ="\033[1m"


    # Coduri of returnare MQTT
MQTT_RC_CODES ={
0 :"Connection successful",
1 :"Connection refused - incorrect protocol version",
2 :"Connection refused - invalid client identifier",
3 :"Connection refused - server unavailable",
4 :"Connection refused - bad username or password",
5 :"Connection refused - not authorised"
}


# ==============================================================================
# FUNCTII AUXILIARE
# ==============================================================================

def generate_sensor_data ()->dict :
    """
    Generate date simulate of sensor IoT.
    
    Simulate un sensor of environment with:
    - Temperatura (°C)
    - Umiditate (%)
    - Presiune (hPa)
    - Luminozitate (lux)
    """
    return {
    "device_id":f"sensor_{os.getpid()}",
    "timestamp":datetime .now ().isoformat (),
    "readings":{
    "temperature_c":round (20 +random .gauss (0 ,2 ),2 ),
    "humidity_pct":round (50 +random .gauss (0 ,10 ),1 ),
    "pressure_hpa":round (1013 +random .gauss (0 ,5 ),1 ),
    "light_lux":round (max (0 ,500 +random .gauss (0 ,100 )),0 )
    },
    "status":"ok"
    }


def format_message (topic :str ,payload :str ,qos :int )->str :
    """Formateaza messageul for afisare."""
    try :
        obj =json .loads (payload )
        formatted =json .dumps (obj ,indent =2 ,ensure_ascii =False )
    except json .JSONDecodeError :
        formatted =payload 
    return formatted 


    # ==============================================================================
    # CLIENT MQTT
    # ==============================================================================

class MQTTClient :
    """
    MQTT Client with suport for plaintext and TLS.
    
    This class incapsuleaza functionalitatea paho-mqtt and ofera
    o interface simplificata for scenariile of laboratory.
    """

    def __init__ (
    self ,
    role :str ,# "sensor" or "controller"
    host :str ,
    port :int ,
    topic :str ,
    qos :int =0 ,
    tls :bool =False ,
    cafile :Optional [str ]=None ,
    username :Optional [str ]=None ,
    password :Optional [str ]=None ,
    client_id :Optional [str ]=None 
    ):
        self .role =role 
        self .host =host 
        self .port =port 
        self .topic =topic 
        self .qos =qos 
        self .tls =tls 
        self .connected =False 
        self .message_count =0 

        # Generam un client ID unic if not e furnizat
        self .client_id =client_id or f"{role}_{os.getpid()}"

        # ========================================
        # STUDENT SECTION - Create MQTT client
        # ========================================
        # Cream clientul paho-mqtt
        self .client =mqtt .Client (
        client_id =self .client_id ,
        clean_session =True ,
        protocol =mqtt .MQTTv311 
        )

        # Configuram authenticationa if e necesara
        if username :
            self .client .username_pw_set (username ,password )

            # Configuram TLS if e activeat
        if tls :
            if not cafile :
                raise ValueError ("TLS activeat but cafile not e specificat!")
            self .client .tls_set (ca_certs =cafile )
            self .client .tls_insecure_set (False )

            # Inregistram callback-urile
        self .client .on_connect =self ._on_connect 
        self .client .on_message =self ._on_message 
        self .client .on_disconnect =self ._on_disconnect 
        self .client .on_publish =self ._on_publish 

    def _on_connect (self ,client ,userdata ,flags ,rc ):
        """Callback apelat at conectare."""
        if rc ==0 :
            self .connected =True 
            print (f"{Colors.GREEN}[✓] Connected at broker{Colors.RESET}")
            print (f"    Host: {self.host}:{self.port}")
            print (f"    TLS: {'DA' if self.tls else 'NOT'}")
            print (f"    Client ID: {self.client_id}")

            # If suntem controller (subscriber), ne abonam
            if self .role =="controller":
                self .client .subscribe (self .topic ,qos =self .qos )
                print (f"    {Colors.BLUE}Subscriber at: {self.topic} (QoS={self.qos}){Colors.RESET}")
        else :
            print (f"{Colors.RED}[✗] Connection esuata: {MQTT_RC_CODES.get(rc, f'Unknown error ({rc})')}{Colors.RESET}")

    def _on_message (self ,client ,userdata ,msg ):
        """Callback apelat at primirea unui message."""
        self .message_count +=1 

        try :
            payload =msg .payload .decode ("utf-8",errors ="replace")
        except Exception :
            payload =str (msg .payload )

        print (f"\n{Colors.CYAN}[MSG #{self.message_count}]{Colors.RESET}")
        print (f"  Topic: {msg.topic}")
        print (f"  QoS: {msg.qos}")
        print (f"  Payload: {format_message(msg.topic, payload, msg.qos)}")

    def _on_disconnect (self ,client ,userdata ,rc ):
        """Callback apelat at disconnection."""
        self .connected =False 
        if rc ==0 :
            print (f"{Colors.YELLOW}[i] Deconnected of at broker{Colors.RESET}")
        else :
            print (f"{Colors.RED}[!] Connection pierduta (rc={rc}){Colors.RESET}")

    def _on_publish (self ,client ,userdata ,mid ):
        """Callback apelat at publisha with success a unui message."""
        pass # Log minimal for a not polua output-ul

    def connect (self ,timeout :float =10.0 )->bool :
        """Connect at broker."""
        print (f"\n{Colors.BOLD}[*] Connection at broker MQTT...{Colors.RESET}")

        try :
            self .client .connect (self .host ,self .port ,keepalive =60 )
            self .client .loop_start ()

            # Asteptam connection
            start =time .time ()
            while not self .connected and (time .time ()-start )<timeout :
                time .sleep (0.1 )

            return self .connected 

        except Exception as e :
            print (f"{Colors.RED}[✗] Error conectare: {e}{Colors.RESET}")
            return False 

    def disconnect (self ):
        """Deconnect of at broker."""
        self .client .loop_stop ()
        self .client .disconnect ()

    def publish (self ,payload :str ,retain :bool =False )->bool :
        """
        Publica un message on topic.
        
        Args:
            payload: Contentul messageului (string, of obicei JSON)
            retain: If messageul sa fie retinut for subscriberi noi
        
        Returns:
            True if publisha a successful
        """
        if not self .connected :
            print (f"{Colors.RED}[!] Not are connected at broker{Colors.RESET}")
            return False 

            # ========================================
            # STUDENT SECTION - Publish message
            # ========================================
        info =self .client .publish (
        topic =self .topic ,
        payload =payload ,
        qos =self .qos ,
        retain =retain 
        )

        # Asteptam confirmarea for QoS > 0
        if self .qos >0 :
            info .wait_for_publish (timeout =5.0 )

        return info .is_published ()if self .qos >0 else True 

    def run_publisher (self ,count :int =1 ,interval :float =1.0 ,custom_payload :Optional [str ]=None ):
        """
        Running in modules publisher (sensor).
        
        Publica messages periodice with date simulate or payload custom.
        """
        print (f"\n{Colors.BOLD}[*] Mod Publisher - {count} messages{Colors.RESET}")
        print (f"    Topic: {self.topic}")
        print (f"    Interval: {interval}s")
        print (f"    QoS: {self.qos}")
        print ()

        for i in range (count ):
        # Generam payload-ul
            if custom_payload :
                try :
                    data =json .loads (custom_payload )
                except json .JSONDecodeError :
                    data ={"raw":custom_payload }
            else :
                data =generate_sensor_data ()

                # Adaugam metadate
            data ["sequence"]=i +1 
            data ["total"]=count 

            payload =json .dumps (data ,ensure_ascii =False )

            # Publicam
            if self .publish (payload ):
                print (f"{Colors.GREEN}[PUB #{i+1}]{Colors.RESET} {self.topic}")
                print (f"  {payload[:100]}{'...' if len(payload) > 100 else ''}")
            else :
                print (f"{Colors.RED}[!] Publish esuata for message #{i+1}{Colors.RESET}")

                # Pauza between messages
            if i <count -1 :
                time .sleep (interval )

        print (f"\n{Colors.GREEN}[✓] Publish completa ({count} messages){Colors.RESET}")

    def run_subscriber (self ):
        """
        Running in modules subscriber (controller).
        
        Listen messages until at Ctrl+C.
        """
        print (f"\n{Colors.BOLD}[*] Mod Subscriber - wait messages...{Colors.RESET}")
        print (f"    Topic: {self.topic}")
        print (f"    QoS: {self.qos}")
        print (f"    (Ctrl+C for stop)")
        print ()

        try :
            while True :
                time .sleep (0.1 )
        except KeyboardInterrupt :
            print (f"\n\n{Colors.YELLOW}[i] Stop at requesta userului{Colors.RESET}")
            print (f"    Messages primite: {self.message_count}")


            # ==============================================================================
            # MAIN
            # ==============================================================================

def main ():
    parser =argparse .ArgumentParser (
    description ="MQTT Client for laboratory S13",
    formatter_class =argparse .RawDescriptionHelpFormatter ,
    epilog ="""
Examples:
  # Subscriber (controller)
  %(prog)s --role controller --host 10.0.0.100 --port 1883 --topic home/temp

  # Publisher (sensor)  
  %(prog)s --role sensor --host 10.0.0.100 --port 1883 --topic home/temp --count 5

  # With TLS
  %(prog)s --role sensor --host 10.0.0.100 --port 8883 --tls on \\
      --cafile configs/certs/ca.crt --username sensor1 --password pass123
        """
    )

    # Arguments obligatorii
    parser .add_argument ("--role",required =True ,choices =["sensor","controller"],
    help ="Rol: sensor (publisher) or controller (subscriber)")
    parser .add_argument ("--host",required =True ,
    help ="Adresa broker MQTT")
    parser .add_argument ("--topic",required =True ,
    help ="Topic MQTT (ex: home/kitchen/telemetry)")

    # Arguments optionale
    parser .add_argument ("--port",type =int ,default =1883 ,
    help ="Port broker (default: 1883, TLS: 8883)")
    parser .add_argument ("--qos",type =int ,choices =[0 ,1 ,2 ],default =0 ,
    help ="Quality of Service (default: 0)")

    # TLS and Authentication
    parser .add_argument ("--tls",choices =["on","off"],default ="off",
    help ="Activeare TLS (default: off)")
    parser .add_argument ("--cafile",
    help ="Certificateses CA for TLS")
    parser .add_argument ("--username",
    help ="Username for authentication")
    parser .add_argument ("--password",
    help ="Password for authentication")

    # Options publisher
    parser .add_argument ("--count",type =int ,default =1 ,
    help ="Number messages of publicat (default: 1)")
    parser .add_argument ("--interval",type =float ,default =1.0 ,
    help ="Interval between messages in secunde (default: 1.0)")
    parser .add_argument ("--payload",
    help ="Payload custom (JSON string)")

    # Alte options
    parser .add_argument ("--client-id",
    help ="Client ID custom")

    args =parser .parse_args ()

    # Banner
    print (f"\n{Colors.CYAN}{'='*60}")
    print ("  S13 - MQTT Client for laboratory IoT")
    print (f"{'='*60}{Colors.RESET}")

    # Cream clientul
    client =MQTTClient (
    role =args .role ,
    host =args .host ,
    port =args .port ,
    topic =args .topic ,
    qos =args .qos ,
    tls =(args .tls =="on"),
    cafile =args .cafile ,
    username =args .username ,
    password =args .password ,
    client_id =args .client_id 
    )

    # Conectam
    if not client .connect ():
        print (f"\n{Colors.RED}[✗] Not s-a putut conecta at broker{Colors.RESET}")
        sys .exit (1 )

    try :
        if args .role =="sensor":
            client .run_publisher (
            count =args .count ,
            interval =args .interval ,
            custom_payload =args .payload 
            )
        else :
            client .run_subscriber ()

    finally :
        client .disconnect ()

    print ()


if __name__ =="__main__":
    main ()
