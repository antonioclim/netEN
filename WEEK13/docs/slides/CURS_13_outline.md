# CURS 13 — IoT and Security in Computer Networks

## Schita prezentarii for lecture (2 ore)

---

## SLIDE 1: Title page

**Titlu**: IoT and Security in Computer Networks  
**Lecture 13 — Computer Networks**  
**Academic Year 2025-2026, Semester 2**  
**Academia of Studii Economice from Bucharest**  
**Facultatea of Cibernetica, Statistica and Informatica Economica**

---

## SLIDE 2: Agenda cursului

1. Introduction in Internet of Things (IoT) — 20 min
2. Protocols of communication IoT — 25 min
3. Threats and vectori of attack — 25 min
4. Masuri defensive and best practices — 20 min
5. Studii of caz and demonstrations — 15 min
6. Recapitulare and preparation examen — 15 min

---

## SLIDE 3: Learning Objectives

By the end of this lecture, students will be able to:

- **Identifice** componentele arhitecturale ale sistemelor IoT
- **Explice** functionarea protocolslor MQTT, CoAP and HTTP in context IoT
- **Clasifice** amenintarile of security specifice deviceelor IoT
- **Evalueze** vulnerabilitiesle comune in infrastructuri of network
- **Propuna** masuri of protection adecvate for scenarii reale
- **Analizeze** trafficul of network for identificarea anomaliilor

---

## SLIDE 4: What is IoT?

### Definition
**Internet of Things** = Network of devices fizice echipate with sensors, software and conectivitate which le permit sa colecteze and sa schimbe date.

### Statistici (2025)
- ~15 miliarde devices IoT connectede global
- Crestere anuala of ~25%
- 70% from devices au vulnerabilities critice of security

### Domenii of aplicare
- Smart Home / Smart Building
- Industrial IoT (IIoT)
- Healthcare / Wearables
- Smart Cities / Transport
- Agriculture of precizie

---

## SLIDE 5: Arhitectura IoT on straturi

```
┌─────────────────────────────────────────────┐
│           STRATUL APLICATIE                 │
│  Dashboard-uri, Analysis, Automatizari       │
├─────────────────────────────────────────────┤
│           STRATUL PLATFORMA/CLOUD           │
│  Processing date, Storage, API-uri           │
├─────────────────────────────────────────────┤
│           STRATUL COMUNICARE                │
│  MQTT, CoAP, HTTP, WebSocket, LoRaWAN       │
├─────────────────────────────────────────────┤
│           STRATUL GATEWAY                   │
│  Agregare, Protocol translation, Edge       │
├─────────────────────────────────────────────┤
│           STRATUL DISPOZITIVE               │
│  Sensors, Actuatori, Microcontrollere       │
└─────────────────────────────────────────────┘
```

---

## SLIDE 6: The MQTT Protocol

### Message Queuing Telemetry Transport

**Caracteristici**:
- Protocol publish/subscribe
- Foarte usor (overhead minimal)
- Optimizat for connections nesigure
- Ports: 1883 (plaintext), 8883 (TLS)

**Concepte key**:
- **Broker**: Intermediar central
- **Topic**: Channel of communication (`home/kitchen/temperature`)
- **Publisher**: Send messages
- **Subscriber**: Receive messages
- **QoS**: 0 (fire-and-forget), 1 (at least once), 2 (exactly once)

---

## SLIDE 7: Diagrama MQTT

```
     Publisher                              Subscriber
    (Sensor)                               (Controller)
        │                                       │
        │ CONNECT                               │ CONNECT
        ├─────────────────►┌──────┐◄────────────┤
        │                  │      │             │
        │ PUBLISH          │Broker│  SUBSCRIBE  │
        │ topic: home/temp │      │  topic: #   │
        ├─────────────────►│      │◄────────────┤
        │                  │      │             │
        │                  │      │  PUBLISH    │
        │                  │      ├────────────►│
        │                  └──────┘             │
```

---

## SLIDE 8: QoS in MQTT

| QoS | Nume | Dewritere | Usage |
|-----|------|-----------|-----------|
| 0 | At most once | Fire-and-forget, without confirmare | Telemetry frecventa, non-critica |
| 1 | At least once | With ACK, posibile duplicate | Alerte, statusuri importante |
| 2 | Exactly once | 4-way handshake, without duplicate | Tranzactii, commands critice |

**Trade-off**: QoS more mare = overhead more mare, latenta crescuta

---

## SLIDE 9: Vectori of attack IoT

### Suprafata of attack extinsa

1. **Device**
   - Firmware vulnerabil
   - Credentials hardcodate
   - Interfaces of debug expuse

2. **Communication**
   - Lipsa criptarii
   - Interception traffic (MITM)
   - Replay attacks

3. **Cloud/Backend**
   - API-uri nesecurizate
   - Injection attacks
   - Authentication slaba

4. **Network**
   - Segmentare inadecvata
   - Services expuse nenecesar
   - Lipsa monitorizarii

---

## SLIDE 10: OWASP IoT Top 10 (2024)

1. **Weak, Guessable, or Hardcoded Passwords**
2. **Insecure Network Services**
3. **Insecure Ecosystem Interfaces**
4. **Lack of Secure Update Mechanism**
5. **Use of Insecure or Outdated Components**
6. **Insufficient Privacy Protection**
7. **Insecure Data Transfer and Storage**
8. **Lack of Device Management**
9. **Insecure Default Settings**
10. **Lack of Physical Hardening**

---

## SLIDE 11: Studiu of caz — Mirai Botnet (2016)

### Context
- Malware which a infectat devices IoT (camere IP, routere)
- A scanat internet for devices with credentiale default
- A format un botnet of ~600.000 devices

### Attack
- DDoS of 1.2 Tbps contra Dyn DNS
- Au cazut: Twitter, Netflix, Spotify, Reddit, GitHub

### Lessons learnt
- **Schimbati** passwordsle default
- **Dezactiveati** Telnet/SSH if not e necessary
- **Segmentati** networkua IoT
- **Monitorizati** trafficul outbound

---

## SLIDE 12: Procesul of Penetration Testing

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  1. RECON   │──►│ 2. SCANNING │──►│ 3. ENUMERA- │
│             │   │             │   │    TION     │
│ Information  │   │ Ports     │   │ Services    │
│ publice     │   │ opene    │   │ Versiuni    │
└─────────────┘   └─────────────┘   └─────────────┘
                                           │
                                           ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ 6. REPORT   │◄──│ 5. POST-    │◄──│ 4. EXPLOIT- │
│             │   │ EXPLOITA-   │   │    ATION    │
│ Documentare │   │ TION        │   │ Vulnerabi-  │
│ Remediation   │   │ Pivot       │   │ litati      │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## SLIDE 13: Scanninga portslor

### Of what scanam?
- Identifym servicesle expuse
- Detectam configurari gresite
- Evaluam suprafata of attack

### States ale portslor
- **OPEN**: Service activee, accept connections
- **CLOSED**: Port accesibil, but niciun service
- **FILTERED**: Firewall block probe

### Tehnici of scanning
- **TCP Connect**: Full 3-way handshake
- **SYN Scan**: Half-open (stealth)
- **UDP Scan**: Services UDP (DNS, DHCP)
- **Version Detection**: Fingerprinting services

---

## SLIDE 14: Vulnerabilitya vsftpd 2.3.4

### CVE-2011-2523 — Smiley Backdoor

**What s-a intamplat**:
- Attacker a compromis serverul of distributie vsftpd
- A injectat cod in sursa oficiala
- Backdoor-ul verifica username for `:)`
- If gasit, deschidea shell on portul 6200

**Lessons**:
- Verificati integritatea software-ului (checksums)
- Monitorizati portsle neasteptate
- Actualizati software-ul prompt

---

## SLIDE 15: Masuri defensive — Principii

### Defense in Depth
Multiple layers of protection:
```
┌─────────────────────────────────────┐
│         Politici and Proceduri       │
├─────────────────────────────────────┤
│           Firewall Perimetru        │
├─────────────────────────────────────┤
│         Segmentare Network            │
├─────────────────────────────────────┤
│         Encryption Transport          │
├─────────────────────────────────────┤
│         Authentication/Authorisation    │
├─────────────────────────────────────┤
│         Hardening Devices       │
└─────────────────────────────────────┘
```

---

## SLIDE 16: Encryptiona trafficului IoT

### TLS for MQTT

**Without TLS (port 1883)**:
- Traffic in clar
- Credentials vizibile
- Messages interceptabile

**With TLS (port 8883)**:
- Encryption end-to-end
- Authentication server (certificateses)
- Integritate messages (HMAC)

### Configuration recomandata:
- TLS 1.3 or 1.2 (minimum)
- Certificateses semnate of CA intern
- Mutual TLS for devices critice

---

## SLIDE 17: Authentication and Authorisation

### Authentication
- **What stii**: Username/password
- **What ai**: Token, certificateses
- **What esti**: Biometric (rar in IoT)

### Authorisation (ACL)
```
# Example Mosquitto ACL
user sensor1
topic write home/+/telemetry

user controller
topic read home/#/telemetry
```

### Best practices:
- Credentials unice per device
- Rotatie periodica
- Principiul privilegiului minimum

---

## SLIDE 18: Segmentarea networksi

### Of what segmentam?
- Izolam deviceele IoT of networkua principala
- Limitam miscarea laterala a attackatorilor
- Aplicam politici of firewall specifice

### Arhitectura recomandata:
```
[Internet] ─── [Firewall] ─── [Network Corporativa]
                   │
                   ├── [DMZ - Servere publice]
                   │
                   └── [VLAN IoT] ─── [Broker MQTT]
                                 └── [Sensors]
```

---

## SLIDE 19: Monitoring and Logging

### What monitorizam?
- **Traffic network**: Anomalii, volume neobisnuite
- **Loguri services**: Errors, tentative of acces
- **State devices**: Uptime, resurse

### Instrumente:
- **Wireshark/tcpdump**: Capture packets
- **ELK Stack**: Centralizare loguri
- **Prometheus/Grafana**: Metrici and alerte

### Indicatori of compromis:
- Connections to IP-uri suspecte
- Traffic in afara orelor normale
- Scanari of ports interne

---

## SLIDE 20: Recapitulare

### Puncte key:
1. IoT extinde dramatic suprafata of attack
2. MQTT is protocolul dominant, necesita TLS
3. Attackatorii exploateaza services neactualizate
4. Defense in depth: straturi multiple of protection
5. Segmentarea and monitoringa are esentiale

### For examen:
- Modelul OSI vs TCP/IP in context IoT
- Diferentele between QoS 0/1/2
- Tipuri of scanari and resultele lor
- Hardening Measures for devices IoT

---

## SLIDE 21: Resurse suplimentare

### Bibliografie recomandata:
- Kurose & Ross — Computer Networking, Cap. 8 (Security)
- OWASP IoT Security Verification Standard
- NIST SP 800-183 — Networks of 'Things'

### Online:
- https://mqtt.org/
- https://owasp.org/www-project-internet-of-things/
- https://www.shodan.io/ (motorul of cautare IoT)

### Laboratory:
- Starterkit S13 disponibil on platforma cursului
- Demo-uri: `make demo-offensive` and `make demo-defensive`

---

## SLIDE 22: Intrebari?

**Contact teaching staff**:  
retele-calc@ie.ase.ro

**Consultations**:  
Conform programarii on platforma online.ase.ro

**Evaluation**:
- Proiect echipa: 15%
- Tests seminar: 15%
- Written Examination: 70%

---

## Note for prezentator

### Timing recommended:
- Slides 1-5: 15 min (Introduction IoT)
- Slides 6-8: 15 min (MQTT detaliat)
- Slides 9-12: 25 min (Threats, studii of caz)
- Slides 13-14: 15 min (Pentest, vulnerabilities)
- Slides 15-19: 30 min (Masuri defensive)
- Slides 20-22: 10 min (Recapitulare)

### Demonstrations live (optional):
1. Capture traffic MQTT plaintext vs TLS (5 min)
2. Port Scanning with nmap/Python (5 min)
3. Exploatare vsftpd in container Docker (5 min)

### Intrebari of verification:
- "What QoS ati folosi for o alerta of incendiu?"
- "Of what e important sa segmentam networkua IoT?"
- "What indica un port in state filtered?"
