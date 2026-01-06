# CLI cheatsheet – Week 10

## Container services (DNS, SSH and FTP)

### Ports

| Service | Host port | Protocol | Notes |
|---|---:|---|---|
| DNS | 5353 | UDP | `dig @127.0.0.1 -p 5353 example.test` |
| SSH | 2222 | TCP | `ssh -p 2222 labuser@127.0.0.1` |
| FTP | 2121 | TCP | `ftp -p 127.0.0.1 2121` |
| FTP passive | 30000–30009 | TCP | required for passive mode |
| HTTP | 8000 | TCP | demo service where present |

### Useful commands

- Show IP configuration: `ip a`
- Show routes: `ip r`
- Listening sockets: `ss -lntup`
- DNS query: `dig @127.0.0.1 -p 5353 example.test A`
- HTTP request: `curl -v http://127.0.0.1:8000/`
- Packet capture (host): `sudo tcpdump -i any -nn port 5353 or port 2222 or port 2121`
- Packet capture (tshark): `tshark -i any -f "port 5353 or port 2222 or port 2121" -c 50`

### Notes

Do not change commas in code snippets, YAML files or command flags. Text edits must not change code semantics.
