# DNS Scenario – TTL and caching

## Objective
Observing the DNS caching mechanism and the effect of TTL.

## What happens
- a recursive resolver queries an authoritative server
- responses are cached
- the DNS zone is modified

## What to observe
- when the new IP appears
- how TTL influences propagation

## Running
docker compose up --build

## Questions
- why DNS is not "instant"
- what compromise TTL makes
