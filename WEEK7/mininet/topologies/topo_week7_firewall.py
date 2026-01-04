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
    """A Node with IPv4 forwarding enabled."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class Week7FirewallTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        h1 = self.addHost("h1", ip="10.0.7.11/25", defaultRoute="via 10.0.7.1")
        h2 = self.addHost("h2", ip="10.0.7.200/25", defaultRoute="via 10.0.7.129")

        fw = self.addHost("fw", cls=LinuxRouter)

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s2)

        # Router links with explicit IPs on fw interfaces
        self.addLink(fw, s1, intfName1="fw-eth0", params1={"ip": "10.0.7.1/25"})
        self.addLink(fw, s2, intfName1="fw-eth1", params1={"ip": "10.0.7.129/25"})


topos = {"week7fw": Week7FirewallTopo}
