"""Week 7 base topology (one subnet, one switch).

This is useful for quick packet capture and socket debugging.
"""

from mininet.topo import Topo


class Week7BaseTopo(Topo):
    """h1 --- s1 --- h2"""

    def build(self) -> None:
        h1 = self.addHost("h1", ip="10.0.7.11/24")
        h2 = self.addHost("h2", ip="10.0.7.100/24")
        s1 = self.addSwitch("s1")
        self.addLink(h1, s1)
        self.addLink(h2, s1)


topos = {"week7base": Week7BaseTopo}
