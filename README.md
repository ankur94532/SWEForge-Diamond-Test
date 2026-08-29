# SWEForge Diamond Workflow Test

This repository is a deliberately tiny live fixture for testing SWEForge's declarative serial workflow runtime.

The workflow dependency graph is:

```text
    A
   / \
  B   C
   \ /
    D
```

SWEForge must still execute it strictly serially in declaration order:

```text
A -> B -> C -> D
```

Each task changes exactly one file under `state/` from `PENDING` to `DONE`.

- A may change only `state/A.txt`.
- B may change only `state/B.txt` and must observe A as `DONE` first.
- C may change only `state/C.txt` and must observe A as `DONE` first.
- D may change only `state/D.txt` and must observe both B and C as `DONE` first.

`verify.py <TASK>` performs the deterministic dependency/state check for that task. The final expected repository state is that all four files contain exactly `DONE`.

This repository contains only the untrusted code fixture. The workflow specification and phase skills are trusted operator configuration and intentionally live outside this repository.
