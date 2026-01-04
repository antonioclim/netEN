"""
================================================================================
Utilitare Network - Functions comune for laboratory S13
================================================================================
This modules ofera functions of baza for:
- Operatii TCP/UDP
- Rate limiting
- Export date
- Parsing configurations
================================================================================
"""

from __future__ import annotations 

import base64 
import json 
import socket 
import time 
from dataclasses import dataclass ,field 
from typing import Any ,Dict ,Optional ,Tuple 


# ==============================================================================
# CONSTANTE
# ==============================================================================

DEFAULT_TIMEOUT =2.0 
MAX_RECV_SIZE =65536 


# ==============================================================================
# FUNCTII SOCKET
# ==============================================================================

def tcp_connect (
host :str ,
port :int ,
timeout_s :float =DEFAULT_TIMEOUT 
)->Tuple [bool ,str ]:
    """
    Try o connection TCP and return resultul.
    
    Returns:
        Tuple (success, reason)
        - success: True if portul e open
        - reason: "open", "closed", "filtered/timeout", or message error
    """
    sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
    sock .settimeout (timeout_s )

    try :
        sock .connect ((host ,port ))
        return True ,"open"
    except ConnectionRefusedError :
        return False ,"closed"
    except socket .timeout :
        return False ,"filtered/timeout"
    except OSError as e :
        return False ,f"error:{e.__class__.__name__}"
    finally :
        try :
            sock .close ()
        except Exception :
            pass 


def recv_until (
sock :socket .socket ,
marker :bytes ,
max_bytes :int =MAX_RECV_SIZE 
)->bytes :
    """
    Read of on socket until at marker or max_bytes.
    
    Useful for citirea headerelor HTTP or responseurilor FTP.
    """
    data =bytearray ()

    while len (data )<max_bytes :
        try :
            chunk =sock .recv (4096 )
            if not chunk :
                break 
            data .extend (chunk )
            if marker in data :
                break 
        except socket .timeout :
            break 
        except Exception :
            break 

    return bytes (data )


def recv_some (
sock :socket .socket ,
max_bytes :int =4096 
)->bytes :
    """
    Read any date disponibile on socket.
    
    Not block more mult decat timeout-ul setat on socket.
    """
    try :
        return sock .recv (max_bytes )
    except socket .timeout :
        return b""
    except ConnectionError :
        return b""


def send_and_recv (
host :str ,
port :int ,
data :bytes ,
timeout_s :float =DEFAULT_TIMEOUT ,
recv_size :int =4096 
)->Optional [bytes ]:
    """
    Send date and receive response (one-shot TCP).
    
    Returns:
        Responseul received or None if error
    """
    try :
        sock =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )
        sock .settimeout (timeout_s )
        sock .connect ((host ,port ))
        sock .sendall (data )
        response =sock .recv (recv_size )
        sock .close ()
        return response 
    except Exception :
        return None 


        # ==============================================================================
        # RATE LIMITING
        # ==============================================================================

@dataclass 
class RateLimiter :
    """
    Rate limiter simple for scanari defensive.
    
    Asigura un interval minimum between operatii for a evita
    saturarea networksi or detectarea ca attack.
    """
    min_interval_s :float 
    _last_call :float =field (default =0.0 ,repr =False )

    def wait (self )->None :
        """Wait until when can fi efectuata urmatoarea operatie."""
        if self .min_interval_s <=0 :
            return 

        now =time .time ()
        elapsed =now -self ._last_call 

        if elapsed <self .min_interval_s :
            time .sleep (self .min_interval_s -elapsed )

        self ._last_call =time .time ()

    def reset (self )->None :
        """Reset timer-ul."""
        self ._last_call =0.0 


        # ==============================================================================
        # AUTENTIFICARE
        # ==============================================================================

def b64_basic_auth (username :str ,password :str )->str :
    """
    Generate header Authorization for HTTP Basic Auth.
    
    Returns:
        String of forma "Basic dXNlcjpwYXNz"
    """
    credentials =f"{username}:{password}"
    encoded =base64 .b64encode (credentials .encode ("utf-8")).decode ("ascii")
    return f"Basic {encoded}"


def parse_basic_auth (header :str )->Tuple [str ,str ]:
    """
    Parseaza un header Authorization Basic.
    
    Returns:
        Tuple (username, password) or ("", "") if invalid
    """
    if not header or not header .startswith ("Basic "):
        return "",""

    try :
        encoded =header .split (" ",1 )[1 ].strip ()
        decoded =base64 .b64decode (encoded ).decode ("utf-8",errors ="replace")

        if ":"not in decoded :
            return "",""

        username ,password =decoded .split (":",1 )
        return username ,password 

    except Exception :
        return "",""


        # ==============================================================================
        # EXPORT SI SERIALIZARE
        # ==============================================================================

def safe_json_dump (obj :Any ,path :str ,indent :int =2 )->bool :
    """
    Save obiect in file JSON with handling of errors.
    
    Returns:
        True if salvarea a successful
    """
    try :
        with open (path ,"w",encoding ="utf-8")as f :
            json .dump (obj ,f ,indent =indent ,sort_keys =True ,ensure_ascii =False )
        return True 
    except Exception as e :
        print (f"[!] Error salvare JSON: {e}")
        return False 


def safe_json_load (path :str )->Optional [Any ]:
    """
    Load obiect from file JSON with handling of errors.
    
    Returns:
        Obiectul deserializat or None if error
    """
    try :
        with open (path ,"r",encoding ="utf-8")as f :
            return json .load (f )
    except Exception :
        return None 


        # ==============================================================================
        # TIMESTAMP SI FORMATARE
        # ==============================================================================

def now_ts ()->float :
    """Return timestamp-ul curent (Unix time)."""
    return time .time ()


def format_duration (seconds :float )->str :
    """
    Formateaza o duration in format citibil.
    
    Examples:
        format_duration(0.5) -> "500ms"
        format_duration(65) -> "1m 5s"
        format_duration(3700) -> "1h 1m 40s"
    """
    if seconds <1 :
        return f"{int(seconds * 1000)}ms"

    if seconds <60 :
        return f"{seconds:.1f}s"

    minutes ,secs =divmod (int (seconds ),60 )
    if minutes <60 :
        return f"{minutes}m {secs}s"

    hours ,minutes =divmod (minutes ,60 )
    return f"{hours}h {minutes}m {secs}s"


def format_bytes (size :int )->str :
    """
    Formateaza o size in bytes in format citibil.
    
    Examples:
        format_bytes(500) -> "500 B"
        format_bytes(2048) -> "2.0 KB"
        format_bytes(1500000) -> "1.4 MB"
    """
    for unit in ["B","KB","MB","GB"]:
        if size <1024 :
            return f"{size:.1f} {unit}"if size !=int (size )else f"{int(size)} {unit}"
        size /=1024 
    return f"{size:.1f} TB"


    # ==============================================================================
    # VALIDARE
    # ==============================================================================

def is_valid_ip (ip :str )->bool :
    """Check if string-ul is o address IP valida (IPv4)."""
    parts =ip .split (".")
    if len (parts )!=4 :
        return False 

    try :
        return all (0 <=int (part )<=255 for part in parts )
    except ValueError :
        return False 


def is_valid_port (port :int )->bool :
    """Check if portul is in intervalul valid."""
    return 1 <=port <=65535 


def normalize_host (host :str )->str :
    """
    Normalizeaza un hostname (lowercase, strip whitespace).
    """
    return host .strip ().lower ()


    # ==============================================================================
    # MODULE TEST
    # ==============================================================================

if __name__ =="__main__":
# Test simple
    print ("Testing net_utils modules...")

    # Test tcp_connect
    success ,reason =tcp_connect ("127.0.0.1",22 ,timeout_s =1.0 )
    print (f"SSH local: {reason}")

    # Test rate limiter
    limiter =RateLimiter (min_interval_s =0.1 )
    start =time .time ()
    for _ in range (5 ):
        limiter .wait ()
    elapsed =time .time ()-start 
    print (f"Rate limiter 5x0.1s: {elapsed:.2f}s")

    # Test formatare
    print (f"Duration: {format_duration(125.5)}")
    print (f"Bytes: {format_bytes(1_500_000)}")

    print ("OK!")
