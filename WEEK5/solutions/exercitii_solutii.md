# Exercises — Solutions (Week 5)

> **CONFIDENTIAL DOCUMENT**
> Doar pentru uz intern al cadrului didactic.
> Do not distribute to students before the deadline.

---

## Exercise S5.1 — Analiza CIDR (Nivel de baza)

**Enunt:** Data fiind address `10.45.128.200/18`, calculate manual and verify with Python.

### solution detaliata

**Pas 1: Conversia prefixului in mask**
```
/18 → 11111111.11111111.11000000.00000000 = 255.255.192.0
```

**Pas 2: Calculul address de network (AND)**
```
10.45.128.200 = 00001010.00101101.10000000.11001000
255.255.192.0 = 11111111.11111111.11000000.00000000
────────────────────────────────────────────────────
network         = 00001010.00101101.10000000.00000000 = 10.45.128.0
```

**Pas 3: Calculul broadcast**
```
Wildcard: 0.0.63.255
Broadcast = 10.45.128.0 OR 0.0.63.255 = 10.45.191.255
```

**Pas 4: Intervalul de hosts**
```
Prima host:  10.45.128.1
Ultima host: 10.45.191.254
Total hosts:  2^(32-18) - 2 = 16384 - 2 = 16382
```

**verification:**
```bash
python ex_5_01_cidr_flsm.py analyze 10.45.128.200/18
```

---

## Exercise S5.2 — FLSM (Nivel intermediar)

**Enunt:** Reteaua `172.30.0.0/20` impartita in 32 subnets egale.

### solution

**Calculul bitilor imprumutati:**
```
32 subnets → log₂(32) = 5 biti imprumutati
prefix nou: /20 + 5 = /25
```

**hosts per subnet:**
```
2^(32-25) - 2 = 128 - 2 = 126 hosts
```

**Primele 5 subnets:**

| # | network           | Prima host      | Ultima host      | Broadcast        |
|---|-----------------|------------------|-------------------|------------------|
| 0 | 172.30.0.0/25   | 172.30.0.1       | 172.30.0.126      | 172.30.0.127     |
| 1 | 172.30.0.128/25 | 172.30.0.129     | 172.30.0.254      | 172.30.0.255     |
| 2 | 172.30.1.0/25   | 172.30.1.1       | 172.30.1.126      | 172.30.1.127     |
| 3 | 172.30.1.128/25 | 172.30.1.129     | 172.30.1.254      | 172.30.1.255     |
| 4 | 172.30.2.0/25   | 172.30.2.1       | 172.30.2.126      | 172.30.2.127     |

**verification:**
```bash
python ex_5_01_cidr_flsm.py flsm 172.30.0.0/20 32
```

---

## Exercise S5.3 — VLSM (Nivel intermediar)

**Enunt:** Plan VLSM pentru `192.168.50.0/24` cu cerintele:
- Departament A: 60 hosts
- Departament B: 28 hosts
- Departament C: 14 hosts
- Departament D: 5 hosts
- 3 linkuri point-to-point

### solution

**Pas 1: Sortare descrescatoare**
```
60, 28, 14, 5, 2, 2, 2
```

**Pas 2: Alocare secventiala**

| Cerinta | prefix | hosts disp. | network alocata         | Eficienta |
|---------|--------|-------------|------------------------|-----------|
| 60      | /26    | 62          | 192.168.50.0/26        | 96.8%     |
| 28      | /27    | 30          | 192.168.50.64/27       | 93.3%     |
| 14      | /28    | 14          | 192.168.50.96/28       | 100%      |
| 5       | /29    | 6           | 192.168.50.112/29      | 83.3%     |
| 2       | /30    | 2           | 192.168.50.120/30      | 100%      |
| 2       | /30    | 2           | 192.168.50.124/30      | 100%      |
| 2       | /30    | 2           | 192.168.50.128/30      | 100%      |

**Pas 3: Calculul eficientei**
```
hosts necesare: 60 + 28 + 14 + 5 + 2 + 2 + 2 = 113
hosts alocate:  62 + 30 + 14 + 6 + 2 + 2 + 2 = 118
Eficienta: 113/118 = 95.8%
```

**Spatiu ramas:** 192.168.50.132/26 (122 addresses)

**verification:**
```bash
python ex_5_02_vlsm_ipv6.py vlsm 192.168.50.0/24 60 28 14 5 2 2 2
```

---

## Exercise S5.4 — IPv6 Comprimare (Nivel intermediar)

**Enunt:** Comprimati urmatoarele addresses IPv6.

### solutions

**1. `2001:0db8:85a3:0000:0000:8a2e:0370:7334`**
```
Pas 1: Eliminare zerouri de inceput
2001:db8:85a3:0:0:8a2e:370:7334

Pas 2: Nu exista secventa lunga de zerouri consecutive
Raspuns: 2001:db8:85a3:0:0:8a2e:370:7334
       sau: 2001:db8:85a3::8a2e:370:7334
```

**2. `fe80:0000:0000:0000:0000:0000:0000:0001`**
```
Pas 1: fe80:0:0:0:0:0:0:1
Pas 2: fe80::1
Raspuns: fe80::1
```

**3. `0000:0000:0000:0000:0000:0000:0000:0001`**
```
Pas 1: 0:0:0:0:0:0:0:1
Pas 2: ::1
Raspuns: ::1 (address loopback IPv6)
```

---

## Exercise S5.5 — IPv6 Expandare (Nivel intermediar)

**Enunt:** Expandati urmatoarele addresses IPv6 comprimate.

### solutions

**1. `2001:db8::1`**
```
:: inlocuieste 6 grupuri de zerouri
Raspuns: 2001:0db8:0000:0000:0000:0000:0000:0001
```

**2. `::ffff:192.168.1.1`**
```
Aceasta este o address IPv4-mapped
192.168.1.1 = c0.a8.01.01 in hex
Raspuns: 0000:0000:0000:0000:0000:ffff:c0a8:0101
```

**3. `ff02::2`**
```
:: inlocuieste 6 grupuri de zerouri
Raspuns: ff02:0000:0000:0000:0000:0000:0000:0002
(address multicast all-routers link-local)
```

---

## Exercise S5.6 — Challenge: Plan IPv6

**Enunt:** Proiectati plan pentru `2001:db8:abcd::/48` cu 4 subnets /64 + spatiu for 12 viitoare.

### solution

**Analiza:**
- prefix /48 permite 2^16 = 65536 subnets /64
- Necesare acum: 4
- Necesare viitor: 12
- Total rezervat: 16 (primele)

**Plan de numerotare:**

| Departament | subnet /64              | Stare      |
|-------------|---------------------------|------------|
| IT          | 2001:db8:abcd:0000::/64   | Activa     |
| HR          | 2001:db8:abcd:0001::/64   | Activa     |
| Finance     | 2001:db8:abcd:0002::/64   | Activa     |
| Operations  | 2001:db8:abcd:0003::/64   | Activa     |
| Rezervata 1 | 2001:db8:abcd:0004::/64   | Planificata|
| ...         | ...                       | ...        |
| Rezervata 12| 2001:db8:abcd:000f::/64   | Planificata|

**Schema:**
```
2001:db8:abcd:0000::/52  ← Bloc rezervat departamente (16 /64)
2001:db8:abcd:0010::/52  ← Disponibil pentru proiecte
2001:db8:abcd:0100::/56  ← Disponibil pentru servers
...
```

**verification:**
```bash
python ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:abcd::/48 16
```

---

## Criterii de evaluare

| exercise | Punctaj max | Criterii principale |
|-----------|-------------|---------------------|
| S5.1      | 10          | Toti parametrii corecti |
| S5.2      | 10          | prefix corect + primele 5 subnets |
| S5.3      | 15          | Plan complet + eficienta calculata |
| S5.4      | 10          | Toate 3 comprimate corect |
| S5.5      | 10          | Toate 3 expandate corect |
| S5.6      | 15          | Plan coerent + justificare |

**Total:** 70 puncte

---

*Document de uz intern — networks de calculatoare, ASE-CSIE*
