# /check

## Purpose

Run full code and documentation verification for the current change.

## Read First

1. `AGENTS.md`
2. `docs/project-state.md`
3. Changed files from `git status --short`

## Steps

1. Inspect current changes.
2. Run focused tests for the changed area when possible.
3. Run project checks from `web-admin/`:

```powershell
python scripts/run_ci.py --quick
npm --prefix frontend run build
```

4. Run backend tests from `web-admin/backend/`:

```powershell
python -m pytest tests -v
```

5. If broad checks fail, report the first actionable failure and likely owner.
6. Do not hide warnings that affect release confidence.

## Output

Return:

- Commands run.
- Pass/fail result for each command.
- Important warnings.
- Required fixes or confidence statement.
