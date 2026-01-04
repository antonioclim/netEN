# Expected Outputs - Week 10

## Artefacts Generate de `run_all.sh`

Dupa rularea success a `scripts/run_all.sh`, directoryyul `artifacts/` trebuie sa contina:

### 1. `demo.log`

**Dimensiune minimuma:** ~5-10 KB  
**Continut asteptat:**

```
# Demo Log - Week 10
# Timestamp: [data withrenta]
# Porturi: DNS=5353 SSH=2222 FTP=2121 HTTP=8000

[HH:MM:SS] [STEP] Verifytion prerequisite...
[HH:MM:SS] [INFO] Docker functional
[HH:MM:SS] [STEP] Pornire infrastructure Docker...
[HH:MM:SS] [INFO] Containere pornite
[HH:MM:SS] [STEP] ═══════════════════════════════════════
[HH:MM:SS] [STEP]          TEST DNS SERVER
[HH:MM:SS] [INFO] ✓ DNS implicit functioneaza
[HH:MM:SS] [INFO] ✓ DNS custom raspunde: 10.10.10.10
...
```

**Marcaje obligatorii:**
- `TEST DNS SERVER`
- `TEST SSH SERVER`
- `TEST FTP SERVER`
- `TEST WEB SERVER`

---

### 2. `demo.pcap`

**Dimensiune minimuma:** >24 bytes (header PCAP)  
**Dimensiune tipica:** 10-100 KB

**Continut asteptat (vizualizabil tshark/Wireshark):**
- Pachete DNS pe port UDP 5353
- Conexiuni TCP pe porturile 2222 (SSH), 2121 (FTP), 8000 (HTTP)
- Handshake-uri TCP (SYN, SYN-ACK, ACK)

**Verifytion rapida:**
```bash
tshark -r artifacts/demo.pcap -c 10
```

**Output example:**
```
    1   0.000000 172.20.0.200 → 172.20.0.53  DNS 75 Standard query 0x1234 A myservice.lab.local
    2   0.001234 172.20.0.53 → 172.20.0.200 DNS 91 Standard query response ...
    3   0.002000 172.20.0.200 → 172.20.0.22  TCP 74 [SYN] Seq=0 ...
```

**Note:** Daca `tshark`/`tcpdump` nu este instalat, fileul poate fi gol (doar header) or lipsa. Aceasta NU este o error critica.

---

### 3. `validation.txt`

**Format:** Perechi cheie:result, one per linie

**Continut asteptat (success complet):**
```
# Validation Results - Week 10
# Timestamp: [data withrenta]

dns_implicit:PASS
dns_custom:PASS:10.10.10.10
dns_host:PASS
ssh_port:PASS
ssh_banner:PASS
ssh_paramiko:PASS
ftp_port:PASS
ftp_banner:PASS
ftp_list:PASS
http_host:PASS
http_docker_dns:PASS

# Sumar - [data]
TOTAL_TESTS=11
PASSED=11
FAILED=0
```

**Resulte posibile:**
- `PASS` - Test trewitht
- `FAIL` - Test esuat
- `PARTIAL` - Test partial trewitht (functionalitate de baza OK, dar nu completa)

**Teste critice (trebuie sa fie PASS):**
- `dns_implicit` - DNS implicit Docker functioneaza
- `ssh_port` - Port SSH deschis
- `ftp_port` - Port FTP deschis
- `http_host` - HTTP accesibil de pe host

---

## Verifytion Smoke Test

```bash
./tests/smoke_test.sh
```

**Output asteptat (success):**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  SMOKE TEST - SAPTAMANA 10 - SERVICII DE RETEA                                ║
║  Verifytion artefacts and structura                                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════
  Verifytion: Structura directoare
═══════════════════════════════════════════
[PASS] Directory scripts/ exista
[PASS] Directory docker/ exista
[PASS] Directory python/ exista
[PASS] Directory artifacts/ exista
[PASS] Directory docs/ exista
[PASS] File scripts/setup.sh exista
[PASS] File scripts/run_all.sh exista
...

═══════════════════════════════════════════
  Verifytion: demo.log
═══════════════════════════════════════════
[PASS] demo.log exista (8234 bytes)
[PASS] demo.log are continut substantial (156 linii)
[PASS] demo.log contine teste DNS
[PASS] demo.log contine teste SSH
[PASS] demo.log contine teste FTP

═══════════════════════════════════════════
  Verifytion: demo.pcap
═══════════════════════════════════════════
[PASS] demo.pcap exista (45678 bytes)
[PASS] demo.pcap are date capturate (45678 bytes)

═══════════════════════════════════════════
  Verifytion: validation.txt
═══════════════════════════════════════════
[PASS] validation.txt exista (512 bytes)
[PASS] validation.txt contine 11 teste PASS
[PASS] validation.txt contine sumar

╔═══════════════════════════════════════════════════════════════════════════════╗
║                           SUMAR SMOKE TEST                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

  Total teste:  18
  Trewithte:      18
  Esuate:       0

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ✓ SMOKE TEST TRECUT - TOATE VERIFICARILE OK                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Comportament in Caz de Erori

### DNS custom nu raspunde

**Cauza probabila:** Container `dns-server` nu a pornit corect  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml logs dns-server
docker compose -f docker/docker-compose.yml exec debug dig @dns-server -p 5353 myservice.lab.local
```

**validation.txt va contine:**
```
dns_custom:FAIL
```

### SSH connection refused

**Cauza probabila:** `sshd` nu ruleaza in container  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml exec ssh-server pgrep sshd
docker compose -f docker/docker-compose.yml logs ssh-server
```

**validation.txt va contine:**
```
ssh_port:FAIL
ssh_banner:FAIL
ssh_paramiko:FAIL
```

### FTP banner lipseste

**Cauza probabila:** `pyftpdlib` a esuat la pornire  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml logs ftp-server
nc -v localhost 2121
```

### Captura PCAP goala

**Cauze posibile:**
1. `tshark`/`tcpdump` nu este instalat
2. Permisiuni insuficiente (necesita sudo for tcpdump)
3. Interfata de network nu a capturat trafic

**Aceasta NU este o error critica** - captura este optionala for verification.

---

## Criterii de Evaluare Automata

| Criteriu | Pondere | Verifytion |
|----------|---------|------------|
| Artefacts generate | 20% | Existenta demo.log, demo.pcap, validation.txt |
| DNS functional | 20% | dns_implicit:PASS, dns_custom:PASS |
| SSH functional | 20% | ssh_port:PASS, ssh_paramiko:PASS |
| FTP functional | 20% | ftp_port:PASS, ftp_list:PASS |
| HTTP functional | 20% | http_host:PASS, http_docker_dns:PASS |

**Note minimuma de trecere:** 50% (minimum 5 teste PASS din 10 critice)

---

## Note

Aceste output-uri sunt generate automat de `scripts/run_all.sh`. Pentru reproducerea exacta:

1. Asigurati-va ca Docker ruleaza
2. Nu exista alte services pe porturile 5353, 2222, 2121, 8000
3. Rulati din directoryyul radacina al kit-ului

```bash
cd /path/to/WEEK10
./scripts/run_all.sh
./tests/smoke_test.sh
```
