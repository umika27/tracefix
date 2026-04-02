# TraceFix 🔍

**Hybrid ML + rule-based Python error analyzer — right in your terminal.**

TraceFix catches Python errors, identifies their root cause using a rule engine
and a trained ML model, and gives you clear, step-by-step fixes.

---

## Install

```bash
pip install -e .
```

---

## Commands

### `analyze` — diagnose any error string

```bash
tracefix analyze "No module named numpy"
tracefix analyze "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
tracefix analyze "KeyError: 'user_id'" --beginner
```

`--beginner` / `-b` → shows numbered step-by-step fix instructions.

---

### `run` — run a Python file and catch errors automatically

```bash
tracefix run my_script.py
tracefix run my_script.py --beginner
```

TraceFix runs the file, captures any exception, prints the raw traceback,
then gives you a full analysis + fix.

---

### `watch` — monitor a folder for new error/log files

```bash
tracefix watch ./logs
tracefix watch /var/log/myapp --interval 5
```

Any new `.log`, `.txt`, or `.err` file dropped into the folder is
automatically analyzed. Great for long-running services.

---

### `stats` — view your error history

```bash
tracefix stats
```

Shows total errors logged, breakdown by type, average confidence,
and the path to your log file (`~/.tracefix/error_log.json`).

---

### `similar` — find past errors like this one

```bash
tracefix similar "No module named pandas"
```

Uses token-overlap similarity to find the closest matches in your
error memory — shows the type, fix, and timestamp for each.

---

### `export` — export log to CSV for retraining

```bash
tracefix export
tracefix export --output my_errors.csv
```

Exports `~/.tracefix/error_log.json` as a CSV you can use to retrain
the ML model with your own real-world errors.

---

## Embed in your own code

Use the `@run_safely` decorator to auto-analyze errors in any function:

```python
from runner import run_safely

@run_safely
def my_function():
    x = 10 + "hello"   # TraceFix catches and explains this

my_function()
```

---

## How it works

```
Error input (CLI / run / watch / decorator)
        │
        ▼
    parser.py     → cleans text, extracts type, module, key, mismatch
        │
        ├──► engine.py    → rule-based candidates (regex + parsed fields)
        │
        └──► ml_model.py  → TF-IDF + Naive Bayes prediction
                │
                ▼
          Candidate pool
                │
                ▼
           Best by confidence score
                │
                ▼
          display.py   → styled ANSI terminal output
                │
                ▼
          memory.py    → logged to ~/.tracefix/error_log.json
```

- **Rules** handle known errors with very high confidence (88–95%)
- **ML** catches unknown patterns the rules miss
- **Memory** grows over time and powers the `similar` command

---

## Files

| File | Role |
|---|---|
| `cli.py` | Entry point — all CLI commands |
| `engine.py` | Rule engine + candidate ranking |
| `ml_model.py` | TF-IDF + Naive Bayes classifier |
| `parser.py` | Error text cleaner + field extractor |
| `display.py` | ANSI terminal output |
| `memory.py` | JSON log, similarity search, CSV export |
| `watcher.py` | Folder watcher |
| `runner.py` | `@run_safely` decorator |
| `setup.py` | pip install config |

---

## Retraining the ML model

After collecting real errors via `tracefix export`:

```bash
tracefix export --output my_errors.csv
```

Edit `ml_model.py` and add rows from `my_errors.csv` to the `data` list,
then re-run any tracefix command — the model retrains on startup.
