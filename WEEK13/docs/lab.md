# Laboratory 13 — Ghid Pas with Pas

## Step 0: Verification Prerechizite

```bash
python3 --version  # >= 3.8
docker --version   # >= 20.10
which tshark       # must instalat
```

## Step 1: Setup

```bash
make setup
make docker-up
make test
```

## Step 2: Scanning Ports

```bash
python python/exercises/ex_01_port_scanner.py localhost -p 1-1000
```

**Expected Output:**
```
[+] localhost:1883   OPEN     mqtt
[+] localhost:8888   OPEN     http-alt
```

## Step 3: MQTT Communication

Terminal 1:
```bash
python python/exercises/ex_02_mqtt_client.py --mode controller --topic "iot/#"
```

Terminal 2:
```bash
python python/exercises/ex_02_mqtt_client.py --mode sensor --topic "iot/temp" --count 5
```

## Step 4: Traffic Capture

```bash
make capture
# or
sudo tshark -i any -f "port 1883" -w capture.pcap -a duration:60
```

## Step 5: TLS Verification

```bash
openssl s_client -connect localhost:8883 -showcerts
```

## Step 6: Mininet Topology

```bash
sudo python mininet/topologies/topo_base.py
mininet> pingall
```

## Step 7: Cleanup

```bash
make clean
```

---
*Revolvix&Hypotheticalandrei*
