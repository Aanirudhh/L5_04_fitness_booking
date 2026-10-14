# Static Analysis Issues — `gym_system.py`

| Issue | Type | Line(s)* | Description | Fix Approach |
|---|---|---|---|---|
| Command injection via `os.system` | Security (High) | 36 (orig) | `clear_old_exports` builds a shell command by string-concatenating the `prefix` argument into `os.system("rm -f " + prefix + "*.json")`. Any caller that controls `prefix` can inject shell metacharacters (`;`, `` ` ``, `$()`) and run arbitrary commands. Bandit flags this as B605/B607/B602 (subprocess/os.system with a partial or untrusted path). | Replaced the shell call with `glob.glob(f"{prefix}*.json")` + `os.remove(path)` for each match — no shell is ever invoked. |
| Off-by-one booking capacity check | Logic bug (High) | 11 (orig) | `len(rosters[class_name]) > class_capacity.get(class_name, 0)` only blocks a booking once the roster is *already over* capacity, so a class with capacity 3 actually accepts a 4th member before rejecting the 5th. | Changed the comparison to `>=` so the class is closed once it reaches its capacity, not after it's exceeded. |
| Mutable default argument | Bug / code smell (Medium) | 8 (orig) | `def book_class(member_id, class_name, attendance_log=[])` uses a mutable list literal as a default value. Python evaluates defaults once at function definition time, so every call that doesn't pass its own list shares and silently accumulates into the *same* list across calls — a classic source of hard-to-trace bugs. Pylint flags this as `dangerous-default-value` (W0102). | Changed the default to `None` and initialize `attendance_log = []` inside the function body when it isn't supplied. |
| Bare `except:` swallows all errors | Code quality / Bug (Medium) | 21 (orig) | `except:` in `cancel_booking` catches *everything*, including `KeyboardInterrupt` and `SystemExit`, and hides real bugs (e.g. a typo in a class name raising `KeyError`) behind a generic "Nothing to cancel" message. Flagged by Pylint (`bare-except` W0702) and Flake8 (E722). | Narrowed it to `except (KeyError, ValueError):`, the two exceptions that can actually occur here (unknown class, member not in the list). |
| Unvalidated / negative capacity | Logic bug (Medium) | 24-25 (orig) | `set_capacity` accepts any value, including negatives (the demo calls `set_capacity("Spin", -2)`), which then feeds into the capacity check and produces nonsensical behavior. | Added a guard that rejects `seats <= 0` and prints a warning instead of silently corrupting `class_capacity`. |
| Booking into a non-existent class | Logic bug (Medium) | 9-13 (orig) | Booking a class name that was never in `class_capacity` (e.g. `"Pilates"`) falls back to a default capacity of `0` via `.get(class_name, 0)`, but because the check only fires on the *second* booking attempt (see off-by-one issue above), the first walk-in into an unregistered class is silently accepted anyway. | `book_class` now checks `class_name not in CLASS_CAPACITY` up front and rejects the booking with a clear "Unknown class" message, instead of registering it with an implicit capacity. |
| File handle never closed | Code quality (Low) | 32-33 (orig) | `export_roster` calls `open(file, "w")` but never calls `f.close()`, leaking the file descriptor and risking incomplete writes if the process exits early. Pylint flags this as `consider-using-with` (R1732). | Used a `with open(file, "w", encoding="utf-8") as f:` context manager so the file is always closed, and pinned the encoding explicitly. |
| Unvalidated user input can crash the program | Bug (Low) | 52-53 (orig) | `int(n)` on the walk-in guest count has no error handling; typing anything non-numeric at the prompt raises an uncaught `ValueError` and crashes the script. | Wrapped the conversion in a `try/except ValueError` that falls back to 1 guest and prints a warning. |
| `camelCase` function name | Style | 27 (orig) | `addMembers` breaks PEP 8 / the project's snake_case convention used everywhere else. Pylint flags this as `invalid-name` (C0103). | Renamed to `add_members` (all call sites updated). |
| Missing docstrings and `__main__` guard | Style | whole file | No module or function docstrings (Pylint C0114/C0116), and `main()` was called unconditionally at import time instead of behind `if __name__ == "__main__":`, which would re-run the whole demo if the module were ever imported elsewhere. | Added a module docstring and a one-line docstring per function, and moved the `main()` call behind the standard guard. |

\* Line numbers refer to the **original** `gym_system.py` before fixes; after the fixes, the file has been reorganized slightly (module docstring, `CLASS_CAPACITY` constant, `glob` import) so line numbers have shifted.

## Tool output summary

This sandbox could not reach PyPI to install `pylint`, `bandit`, and `flake8` (no network access in this session), so the exact `pylint_report.txt` / `bandit_report.txt` / `flake8_report.txt` files could not be generated here. The issues above are exactly the classes of problem those three tools are built to catch (confirmed against each tool's known check IDs, noted in the table), but **you still need to run the three commands yourself** per the README to produce the actual report files and the final Pylint score for your submission:

```bash
pip install pylint bandit flake8
pylint gym_system.py > pylint_report.txt
bandit -r gym_system.py > bandit_report.txt
flake8 gym_system.py > flake8_report.txt
```

Run them once on the **original** file (keep a copy) to get your "before" reports, and once on the fixed file for your "after" reports, so you can show the warnings disappearing.
