# Comparative Analysis of W11 Archives

## Inventory of Analysed Archives

| Archive | Size | Main Focus | Strengths |
|---------|------|------------|-----------|
| S11v1andrei | 156KB | FTP/DNS/SSH Theory | PlantUML diagrams, 4 complete Docker scenarios |
| S11v2starterkit | 29KB | Standard structure | Clean organisation, basic Mininet |
| S11v3DEMOGPTstarterkit | 40KB | Demos | python/apps, multiple nginx configs |
| S11v3starterkit_ideal | 100KB | Complete structure | Elaborate Makefile, HTML presentations |

## Integration Decisions

### 1. Project Structure
- **Adopted base**: v3_ideal (most complete and organised)
- **Rationale**: Clear structure, complete Makefile, lecture/seminar separation

### 2. Theoretical Content
- **Integrated sources**: v1_andrei/c11.md + v3_ideal/teoria/
- **Result**: Complete FTP, DNS, SSH documentation with diagrams
- **Modernisation**: Added DNSSEC, DoH/DoT, SFTP vs FTPS

### 3. Docker Scenarios
- **FTP Demo**: v1_andrei/scenario-ftp-baseline (complete pyftpdlib)
- **DNS Demo**: v1_andrei/scenario-dns-ttl-caching (BIND + Unbound)
- **SSH Demo**: v1_andrei/scenario-ssh-provision (Paramiko)
- **Nginx/LB**: v2_starterkit + v3_ideal (combined)

### 4. Python Exercises
- **HTTP Backend**: v2_starterkit (ex_11_01.py) + improvements
- **Load Balancer**: v3_ideal (ex_11_02_loadbalancer.py) - 3 algorithms
- **DNS Client**: v3_ideal (ex_11_03_dns_client.py) - RFC 1035

### 5. Mininet Topologies
- **Base**: v2_starterkit/topo_11_base.py
- **Extended**: v3_ideal/topo_11_extended.py (failover)

### 6. HTML Presentations
- **Style**: Newly created, inspired by v3_ideal
- **Palette**: Dark theme (#0f172a), blue accent (#1e40af)
- **Features**: Keyboard navigation, progress bar, quizzes

## Decision Log

1. **Adopted Python 3.10+** for compatibility with type hints and match statements
2. **Removed `version:` from docker-compose.yml** (deprecated in Compose V2)
3. **Added --break-system-packages** to pip for Ubuntu 24.04
4. **Unified ports**: LB=8080, backends=8001-8003, FTP=2121
5. **Standardised README.md** with consistent structure
6. **Added health checks** to all Python exercises
7. **Created unified Makefile** with 30+ targets
8. **Integrated environment verification** (make verify)
9. **Added logging** in all scripts for debugging
10. **Created slide outlines** for PowerPoint/reveal.js
11. **Documented troubleshooting** for common errors
12. **Added benchmark** with Apache Bench and Python fallback
13. **Standardised naming** (ex_11_XX_name.py)
14. **Created comprehensive DOCX** with two perspectives (instructor/student)
15. **Added assessment rubrics** with detailed scores

## Assumptions

1. Runtime environment is Ubuntu 22.04+ LTS (CLI-only VM recommended)
2. Students have access to Docker and sudo rights for Mininet
3. Internet connection available for Docker image pulls
4. Python 3.10+ installed (standard in Ubuntu 22.04+)
5. Prior knowledge: TCP/IP, socket programming, HTTP basics
6. Allocated time: 90 min lecture + 90 min seminar + 100 min laboratory
7. Team project is ongoing and requires incremental artefact
8. Assessment includes both individual and team components

---
*Revolvix&Hypotheticalandrei*
