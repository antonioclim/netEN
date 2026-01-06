# Expected outputs for Week 13

## After running the demo

The demo must create `artifacts/demo.log` and `artifacts/validation.txt`. If traffic capture is enabled it may also create `artifacts/demo.pcap`.

## Minimum validation strings

`artifacts/validation.txt` should include lines confirming that Python scripts ran, that expected ports were used and that any optional capture step completed or was skipped with a clear message.

## Report artefacts

If `python/utils/report_generator.py` is used, the generated report should be placed under `artifacts/` and referenced in `artifacts/demo.log`.
