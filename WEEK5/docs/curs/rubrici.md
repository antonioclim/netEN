# Assessment Rubric — Week 5 (IP Addressing)

This rubric is intended for consistent marking across groups.

## Criteria

### 1) Correctness of subnet calculations (40%)
- Correct network address, broadcast address and host range
- Correct usable host count and mask for each subnet
- No overlapping subnets, no gaps unless justified

### 2) Reproducibility and evidence (25%)
- Commands are recorded and can be rerun on a clean VM
- Outputs are saved under `artifacts/`
- The work matches `tests/expected_outputs.md` where applicable

### 3) Clarity of explanation (20%)
- The rationale for prefix lengths is explicit
- The addressing plan is readable and consistent
- Terminology is accurate (CIDR, prefix, mask, gateway)

### 4) Hygiene and conventions (15%)
- No bytecode artefacts or OS junk in submissions
- File names and paths are not changed
- Scripts are executable and non-interactive

## Common penalties
- Hard-coded paths that break on another VM
- Mixed language in documentation or help text
- Unexplained changes to ports or IPs
