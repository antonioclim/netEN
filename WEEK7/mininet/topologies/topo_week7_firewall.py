"""Week 7 firewall topology (two subnets with a Linux router).

Traffic flows through the router host `fw`, which is where filtering rules are applied.

Address plan (still within 10.0.7.0/24, split as two /25 subnets):
- left subnet:  10.0.7.0/25
  - h1: 10.0.7.11/25, default route via 10.0.7.1
  - fw-eth0: 10.0.7.1/25
- right subnet: 10.0.7.128/25
  - fw-eth1: 10.0.7.129/25
  - h2: 10.0.7.200/25, default route via 10.0.7.129
"""

from mininet.node import Node
from mininet.topo import Topo


class LinuxRouter(Node):
    """A Node with IPv4 forwarding enabled and manual interface configuration."""

    # Store interface IPs to configure after network start
    _intf_ips: dict = {}

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        # Configure interfaces that were specified via intfIPs
        for intf_name, ip_addr in self._intf_ips.items():
            self.cmd(f"ip addr flush dev {intf_name}")
            self.cmd(f"ip addr add {ip_addr} dev {intf_name}")
            self.cmd(f"ip link set {intf_name} up")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()

    def setIntfIP(self, intf_name: str, ip_addr: str):
        """Store interface IP for configuration during config()."""
        self._intf_ips[intf_name] = ip_addr


class Week7FirewallTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        h1 = self.addHost("h1", ip="10.0.7.11/25", defaultRoute="via 10.0.7.1")
        h2 = self.addHost("h2", ip="10.0.7.200/25", defaultRoute="via 10.0.7.129")

        # Create router - IPs will be configured in post_build or by demo script
        fw = self.addHost("fw", cls=LinuxRouter, ip=None)

        # Links - note: params1 IP won't be applied automatically for LinuxRouter
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(fw, s1, intfName1="fw-eth0")
        self.addLink(fw, s2, intfName1="fw-eth1")


def configure_router(net):
    """Configure router interfaces after network start. Call from demo script."""
    fw = net.get("fw")
    # Manually set IPs since params1 doesn't work with custom Node classes
    fw.cmd("ip addr flush dev fw-eth0")
    fw.cmd("ip addr add 10.0.7.1/25 dev fw-eth0")
    fw.cmd("ip link set fw-eth0 up")
    fw.cmd("ip addr flush dev fw-eth1")
    fw.cmd("ip addr add 10.0.7.129/25 dev fw-eth1")
    fw.cmd("ip link set fw-eth1 up")
    # Ensure forwarding is on
    fw.cmd("sysctl -w net.ipv4.ip_forward=1")


topos = {"week7fw": Week7FirewallTopo}
