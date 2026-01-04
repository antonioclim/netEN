# Week 7 troubleshooting (expanded)

1) **`sudo python3 <script>` cannot import modules**  
   Use absolute paths or run from the kit root directory. The demo does this automatically.

2) **`iptables` not found**  
   Install it (`sudo apt-get install -y iptables`) or use the distribution equivalent.

3) **`tshark` prompts during installation**  
   Re-run `./scripts/setup.sh`. If asked about capture permissions, pick a consistent option and document it for students.

4) **Docker Compose not available**  
   The Docker demo is optional. If you want it, install Docker Engine and the Compose plugin.

5) **Ports already in use**  
   Check with `ss -lntup`. Adjust the app ports in `configs/ports.env` and update the demo, tests and README consistently.

6) **You see traffic but the client fails**  
   Inspect TCP flags. A `RST` often means a local rejection. A lack of replies often means a drop or routing issue.

7) **Mininet topology starts but hosts cannot reach each other**  
   Verify routes on the hosts and that IP forwarding is enabled on the router node.

8) **Captures are empty**  
   Check the capture interface and whether traffic is actually flowing through that namespace. In Mininet, capturing on the router (`fw`) with `-i any` is usually sufficient.
