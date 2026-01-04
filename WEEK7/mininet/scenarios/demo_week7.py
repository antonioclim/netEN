"""Automated Week 7 demo.

Runs a Mininet topology with a router firewall and demonstrates:
- baseline TCP and UDP connectivity
- blocking TCP port 9090 on the forwarding path
- blocking UDP port 9091 on the forwarding path

Artefacts are produced for reproducibility.
"""

from __future__ import annotations

import argparse
import os
import signal
import time
from pathlib import Path
from typing import Optional

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

# Import the local topology class (avoid namespace collision with system mininet package)
import sys
_local_topo_dir = str(Path(__file__).resolve().parent.parent / "topologies")
if _local_topo_dir not in sys.path:
    sys.path.insert(0, _local_topo_dir)
from topo_week7_firewall import Week7FirewallTopo, configure_router  # type: ignore


TCP_PORT = 9090
UDP_PORT = 9091
H2_IP = "10.0.7.200"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the Week 7 Mininet demo.")
    p.add_argument("--artifacts", required=True, help="Artefacts directory")
    p.add_argument("--pcap", required=True, help="Where to write demo.pcap")
    p.add_argument("--log", required=True, help="Where to write demo.log")
    p.add_argument("--validation", required=True, help="Where to write validation.txt")
    return p


def log_line(log_path: Path, line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def run_cmd(node, argv: list[str], log_path: Path, expect_ok: Optional[bool] = None) -> int:
    """Run a command on a Mininet node and return its exit code."""
    proc = node.popen(argv)
    out, _ = proc.communicate(timeout=20)
    rc = proc.returncode
    # Some Mininet versions return bytes on stdout for popen, be robust
    if isinstance(out, bytes):
        out_text = out.decode("utf-8", errors="replace")
    else:
        out_text = str(out)
    log_line(log_path, f"{node.name}$ {' '.join(argv)} -> rc={rc}")
    if out_text.strip():
        for ln in out_text.strip().splitlines()[:20]:
            log_line(log_path, f"  {ln}")
    if expect_ok is True and rc != 0:
        log_line(log_path, "  unexpected failure")
    if expect_ok is False and rc == 0:
        log_line(log_path, "  unexpected success")
    return rc


def main() -> int:
    args = build_parser().parse_args()
    art_dir = Path(args.artifacts)
    art_dir.mkdir(parents=True, exist_ok=True)

    log_path = Path(args.log)
    validation_path = Path(args.validation)
    pcap_path = Path(args.pcap)

    # Reset log files
    log_path.write_text("", encoding="utf-8")
    validation_path.write_text("", encoding="utf-8")

    setLogLevel("warning")

    log_line(log_path, "starting Mininet")
    topo = Week7FirewallTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=None, autoSetMacs=True, autoStaticArp=True)
    net.start()
    
    # Configure router interfaces (params1 IP doesn't work with custom Node classes)
    log_line(log_path, "configuring router interfaces")
    configure_router(net)

    h1 = net.get("h1")
    h2 = net.get("h2")
    fw = net.get("fw")

    # Prepare firewall baseline rules
    firewallctl = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "firewallctl.py").resolve())
    log_line(log_path, "applying baseline firewall profile on fw")
    fw_result = fw.cmd(f"python3 {firewallctl} --profile baseline 2>&1")
    log_line(log_path, f"firewallctl output: {fw_result.strip()[:200]}")
    
    # Verify basic connectivity with ping before TCP tests
    log_line(log_path, "verifying connectivity: h1 ping fw-eth0")
    ping_fw = h1.cmd("ping -c 1 -W 2 10.0.7.1")
    log_line(log_path, f"ping fw: {'OK' if '1 received' in ping_fw else 'FAIL'}")
    
    log_line(log_path, "verifying connectivity: h1 ping h2")
    ping_h2 = h1.cmd("ping -c 1 -W 2 10.0.7.200")
    log_line(log_path, f"ping h2: {'OK' if '1 received' in ping_h2 else 'FAIL'}")
    
    if '1 received' not in ping_h2:
        log_line(log_path, "WARNING: h1 cannot reach h2, checking routes...")
        log_line(log_path, f"h1 routes: {h1.cmd('ip route')}")
        log_line(log_path, f"h2 routes: {h2.cmd('ip route')}")
        log_line(log_path, f"fw routes: {fw.cmd('ip route')}")
        log_line(log_path, f"fw ip_forward: {fw.cmd('cat /proc/sys/net/ipv4/ip_forward')}")

    # Start tcpdump on fw for evidence (if available)
    tcpdump_proc = None
    if fw.cmd("command -v tcpdump >/dev/null 2>&1 && echo yes || echo no").strip() == "yes":
        log_line(log_path, f"starting tcpdump capture on fw: {pcap_path}")
        tcpdump_proc = fw.popen(["tcpdump", "-i", "any", "-nn", "-U", "-w", str(pcap_path), "tcp", "or", "udp"])
        time.sleep(0.4)
    else:
        log_line(log_path, "tcpdump not available in PATH, pcap will be missing")

    # Start servers on h2
    tcp_server = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "tcp_server.py").resolve())
    udp_receiver = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "udp_receiver.py").resolve())

    log_line(log_path, "starting TCP server on h2")
    tcp_srv_proc = h2.popen(["python3", tcp_server, "--host", "0.0.0.0", "--port", str(TCP_PORT), "--log", str(art_dir / "tcp_server.log")])
    time.sleep(1.0)  # Wait for server to bind and listen

    log_line(log_path, "baseline: TCP client from h1")
    tcp_client = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "tcp_client.py").resolve())
    rc_tcp_baseline = run_cmd(h1, ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "baseline"], log_path, expect_ok=True)

    log_line(log_path, "baseline: UDP send and receive")
    # Start receiver expecting 1 message
    udp_rcv_proc = h2.popen(["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--count", "1", "--timeout", "5", "--log", str(art_dir / "udp_receiver.log")])
    time.sleep(0.2)
    udp_sender = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "udp_sender.py").resolve())
    rc_udp_send = run_cmd(h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "baseline"], log_path, expect_ok=True)
    udp_rcv_proc.wait(timeout=10)
    rc_udp_baseline = udp_rcv_proc.returncode if udp_rcv_proc.returncode is not None else 9

    baseline_ok = (rc_tcp_baseline == 0) and (rc_udp_send == 0) and (rc_udp_baseline == 0)
    validation_lines = []
    validation_lines.append(f"BASELINE_OK: tcp_echo={'ok' if rc_tcp_baseline == 0 else 'fail'} udp_echo={'ok' if rc_udp_baseline == 0 else 'fail'}")

    # Block TCP 9090
    log_line(log_path, "applying block_tcp_9090 profile on fw")
    fw.cmd(f"python3 {firewallctl} --profile block_tcp_9090")
    log_line(log_path, "test: TCP should fail, UDP should still work")
    rc_tcp_block = run_cmd(h1, ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "blocked", "--timeout", "1"], log_path, expect_ok=False)

    udp_rcv_proc2 = h2.popen(["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--count", "1", "--timeout", "5"])
    time.sleep(0.2)
    run_cmd(h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "still_ok"], log_path, expect_ok=True)
    udp_rcv_proc2.wait(timeout=10)
    rc_udp_still = udp_rcv_proc2.returncode if udp_rcv_proc2.returncode is not None else 9

    block_tcp_ok = (rc_tcp_block != 0) and (rc_udp_still == 0)
    validation_lines.append(f"BLOCK_TCP_OK: tcp_echo={'blocked' if rc_tcp_block != 0 else 'unexpected_ok'} udp_echo={'ok' if rc_udp_still == 0 else 'fail'}")

    # Block UDP 9091 (restore baseline first to avoid stacking confusion)
    log_line(log_path, "restoring baseline profile on fw")
    fw.cmd(f"python3 {firewallctl} --profile baseline")
    log_line(log_path, "applying block_udp_9091 profile on fw")
    fw.cmd(f"python3 {firewallctl} --profile block_udp_9091")

    log_line(log_path, "test: UDP should fail, TCP should work")
    rc_tcp_after = run_cmd(h1, ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "tcp_ok_again"], log_path, expect_ok=True)

    udp_rcv_proc3 = h2.popen(["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--count", "1", "--timeout", "2"])
    time.sleep(0.2)
    run_cmd(h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "udp_blocked"], log_path, expect_ok=True)
    udp_rcv_proc3.wait(timeout=5)
    rc_udp_blocked = udp_rcv_proc3.returncode if udp_rcv_proc3.returncode is not None else 9

    block_udp_ok = (rc_tcp_after == 0) and (rc_udp_blocked != 0)
    validation_lines.append(f"BLOCK_UDP_OK: tcp_echo={'ok' if rc_tcp_after == 0 else 'fail'} udp_echo={'blocked' if rc_udp_blocked != 0 else 'unexpected_ok'}")

    # Stop servers and capture
    log_line(log_path, "stopping servers and capture")
    try:
        tcp_srv_proc.send_signal(signal.SIGTERM)
        tcp_srv_proc.wait(timeout=3)
    except Exception:
        try:
            tcp_srv_proc.kill()
        except Exception:
            pass

    if tcpdump_proc is not None:
        try:
            tcpdump_proc.send_signal(signal.SIGINT)
            tcpdump_proc.wait(timeout=3)
        except Exception:
            try:
                tcpdump_proc.kill()
            except Exception:
                pass

    # Stop Mininet
    net.stop()

    validation_path.write_text("\n".join(validation_lines) + "\n", encoding="utf-8")

    # Return code reflects overall success
    if baseline_ok and block_tcp_ok and block_udp_ok:
        log_line(log_path, "demo completed successfully")
        return 0

    log_line(log_path, "demo completed with failures")
    return 10


if __name__ == "__main__":
    raise SystemExit(main())
