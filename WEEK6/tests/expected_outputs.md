# Expected outputs checked by smoke_test.sh

The smoke test validates:

- `artifacts/demo.log` exists and is non-empty
- `artifacts/validation.txt` exists and includes the word `OK`
- The demo log mentions the Week number and at least one of: NAT, ARP, DHCP, ICMP, SDN

If you change the demo wording, update this file and the grep patterns in `tests/smoke_test.sh`.
