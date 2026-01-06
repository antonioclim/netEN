# Mininet scenarios – Week 10

This document describes small Mininet experiments that complement the Docker-based seminar by running similar checks inside an emulated network.

Estimated duration: 45–60 minutes.

## Scenario 1: Client–server HTTP

### Objective

Demonstrate HTTP communication between a client and a server in Mininet.

### Steps

1. Start the base topology:

```bash
sudo python3 mininet/topologies/topo_10_base.py
```

2. From the Mininet CLI, confirm connectivity:

```bash
pingall
```

3. Start a simple HTTP server on the chosen server host, then query it from a client host using `curl` or `nc`.

### What to record

- the IP addresses used
- the HTTP request and response headers
- any relevant packet capture output

## Scenario 2: DNS resolution

### Objective

Demonstrate a DNS query and response, then relate it to application behaviour.

### Steps

1. Ensure the DNS service is running (Docker or host-based, depending on your setup).
2. Run `dig` from a Mininet host towards the DNS endpoint.
3. Compare the response to the expected mapping in the DNS server configuration.

## Scenario 3: SSH and FTP reachability

### Objective

Validate reachability and authentication flows for SSH and FTP.

### Steps

1. Confirm TCP reachability with `nc`.
2. Establish an SSH session to the demo service.
3. Perform an FTP login, then upload or download a small file.

## Notes

- Keep commands non-interactive where possible so results can be validated.
- If you change IP addresses or ports, update all references coherently and re-run the smoke test.
