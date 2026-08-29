# Release Readiness

This small Python package evaluates whether a release is ready from a configured set of checks. Policies declare required and optional checks, callers provide explicit `PASS` or `FAIL` statuses, and the package returns a structured evaluation and JSON-compatible report.

## Policy behavior

- Required checks must always receive an explicit status from the caller.
- Optional checks may omit an explicit status only when the policy configures a fallback.
- Supported explicit statuses and fallback values are `PASS` and `FAIL`.
- Policy files still reject unknown fields, required checks with fallback values, unsupported fallback values, and unsupported schema versions so configuration mistakes fail clearly.

Example policy:

```json
{
  "version": 1,
  "checks": [
    {"name": "unit-tests", "required": true},
    {"name": "security-scan", "required": true},
    {"name": "documentation", "required": false, "fallback": "PASS"}
  ]
}
```

## Report shape

The top-level report shape remains:

```json
{
  "ready": true,
  "checks": []
}
```

Each check always includes:

- `name`
- `status`

Checks from newer evaluations may also include an additive `source` field:

- `explicit` for caller-supplied statuses
- `fallback` for policy-derived fallback statuses

This keeps existing consumers that only depend on `name` and `status` backward compatible where possible.

Example mixed explicit/fallback report:

```json
{
  "ready": true,
  "checks": [
    {"name": "unit-tests", "status": "PASS", "source": "explicit"},
    {"name": "documentation", "status": "PASS", "source": "fallback"}
  ]
}
```

## Validation

Run the report verification and full unittest suite with:

```bash
python verify.py report
python -m unittest discover -s tests -v
```

The project uses only the Python standard library.
