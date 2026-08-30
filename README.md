# Release Readiness

This small Python package evaluates whether a release is ready from a configured set of checks. Policies declare required and optional checks, callers provide explicit `PASS` or `FAIL` statuses, and the package returns a structured evaluation and JSON-compatible report.

Optional checks may define a policy fallback/default status when a caller does not supply one explicitly. Required checks still require explicit statuses, and missing required statuses fail clearly instead of silently using a default. Policy files continue to reject unknown fields, unsupported schema versions, fallback values other than `PASS` or `FAIL`, and fallbacks configured on required checks so configuration mistakes fail clearly.

Reports preserve the top-level `ready` and `checks` shape and each check entry still includes `name` and `status`. Reports now also include `source`, which is `explicit` when the caller supplied the status and `fallback` when the status came from policy configuration.

Run the baseline checks with:

```bash
python -m unittest discover -s tests -v
python verify.py baseline
```

For the report stage specifically, run:

```bash
python -m unittest tests.test_report -v
python verify.py report
```

The project uses only the Python standard library.
