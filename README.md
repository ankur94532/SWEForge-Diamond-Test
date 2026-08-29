# Release Readiness

This small Python package evaluates whether a release is ready from a configured set of checks. Policies declare required and optional checks, callers provide explicit `PASS` or `FAIL` statuses, and the package returns a structured evaluation and JSON-compatible report.

The current behavior intentionally requires an explicit status for every configured check. Policy files reject unknown fields and unsupported schema versions so configuration mistakes fail clearly.

Run the baseline checks with:

```bash
python -m unittest discover -s tests -v
python verify.py baseline
```

The project uses only the Python standard library.
