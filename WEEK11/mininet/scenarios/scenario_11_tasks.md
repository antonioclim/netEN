# Mininet Tasks – Week 11

## Scenario: Load Balancer Topology

### Objective
Building and testing a network topology with load balancer and multiple backends.

### Topology
```
       [h1: client]
            |
          [s1: switch]
            |
    +-------+-------+-------+
    |       |       |       |
  [h2]    [h3]    [h4]    [h5: LB]
 (backend)(backend)(backend)
```

### Tasks

#### Task 1: Starting the topology
```bash
sudo python3 mininet/topologies/topo_11_base.py --cli
```

#### Task 2: Testing connectivity
```bash
mininet> pingall
```

**Expected result:** All nodes communicate with each other (0% losses).

#### Task 3: Starting HTTP servers on backends
```bash
mininet> h2 python3 -m http.server 8000 &
mininet> h3 python3 -m http.server 8000 &
mininet> h4 python3 -m http.server 8000 &
```

#### Task 4: Testing direct access to backends
```bash
mininet> h1 curl http://10.0.0.2:8000/
mininet> h1 curl http://10.0.0.3:8000/
mininet> h1 curl http://10.0.0.4:8000/
```

#### Task 5: Traffic capture on switch
```bash
mininet> s1 tcpdump -i s1-eth1 -c 10 &
mininet> h1 curl http://10.0.0.2:8000/
```

#### Task 6: Latency analysis
```bash
mininet> h1 ping -c 5 10.0.0.2
mininet> h1 ping -c 5 10.0.0.3
mininet> h1 ping -c 5 10.0.0.4
```

### Verification questions

1. What do you observe about the RTT between h1 and backends?
2. How does the number of hops influence latency?
3. What happens if you stop a backend?

### Extensions (optional)

1. Add rate limiting on s1
2. Implement QoS with tc
3. Add a second switch for redundancy

---
*Revolvix&Hypotheticalandrei*
