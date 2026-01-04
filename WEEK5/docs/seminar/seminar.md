# Seminar 5 — Reasoning About IP Addressing

## Objectives
- Move from memorising formulas to reasoning with constraints
- Practise CIDR mental maths for common prefixes
- Connect addressing decisions to routing and troubleshooting

## Suggested flow
1. Warm-up: identify network and host portions for `/24`, `/26`, `/30`
2. Short exercise: compute network address and broadcast for a given IP
3. Group activity: design a VLSM plan for a small organisation
4. Validation: use the CLI calculator to verify the plan

## Mini-exercises
- What is the usable host range for `10.0.5.64/26`?
- Which prefixes provide at least 30 usable hosts?
- Why does IPv6 not use broadcast?

## Practical verification
Run:
```bash
make demo
```
Then compare `artifacts/` against `tests/expected_outputs.md`.

## Troubleshooting cues
- Wrong broadcast means the prefix or mask is wrong
- Overlapping subnets usually come from allocating in the wrong order
- Hard-coded IPs in scripts should be centralised in `configs/`
