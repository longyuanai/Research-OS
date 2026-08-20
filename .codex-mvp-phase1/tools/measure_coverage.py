"""Stdlib-only line coverage for research_os_mvp. No install, no network."""
import io
import os
import sys
import trace
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve()
MVP = Path(os.environ["MVP_DIR"]).resolve()
os.chdir(MVP)
sys.path.insert(0, str(MVP))

PKG = (MVP / "research_os_mvp").resolve()

tracer = trace.Trace(
    count=1,
    trace=0,
    ignoredirs=[sys.prefix, sys.exec_prefix],
)

_result_holder = {}


def _run():
    loader = unittest.TestLoader()
    suite = loader.discover(str(MVP / "tests"), top_level_dir=str(MVP))
    buf = io.StringIO()
    runner = unittest.TextTestRunner(stream=buf, verbosity=0)
    res = runner.run(suite)
    _result_holder["res"] = res
    _result_holder["out"] = buf.getvalue()


tracer.runfunc(_run)

res = _result_holder["res"]
counts = tracer.results().counts  # {(filename, lineno): hits}

hit_by_file = {}
for (fname, lineno), n in counts.items():
    if n <= 0:
        continue
    try:
        rp = Path(fname).resolve()
    except OSError:
        continue
    if PKG in rp.parents or rp == PKG:
        hit_by_file.setdefault(rp, set()).add(lineno)

rows = []
tot_exec = tot_hit = 0


def _executable_lines(path: Path) -> set[int] | None:
    try:
        return set(trace._find_executable_linenos(str(path)))
    except (OSError, SyntaxError, UnicodeError):
        return None


for src in sorted(PKG.glob("*.py")):
    executable = _executable_lines(src)
    if executable is None:
        continue
    hit = hit_by_file.get(src.resolve(), set()) & executable
    n_exec, n_hit = len(executable), len(hit)
    tot_exec += n_exec
    tot_hit += n_hit
    pct = (100.0 * n_hit / n_exec) if n_exec else 100.0
    missing = sorted(executable - hit)
    rows.append((src.name, n_exec, n_hit, pct, missing))

rows.sort(key=lambda r: r[3])

print("=" * 78)
print("TESTS")
print("=" * 78)
print(f"  run     : {res.testsRun}")
print(f"  failures: {len(res.failures)}")
print(f"  errors  : {len(res.errors)}")
print(f"  skipped : {len(res.skipped)}")
print(f"  success : {res.wasSuccessful()}")
print()
print("=" * 78)
print("LINE COVERAGE  (research_os_mvp/)")
print("=" * 78)
print(f"{'module':<28}{'stmts':>7}{'hit':>7}{'miss':>7}{'cover':>9}")
print("-" * 78)
for name, n_exec, n_hit, pct, missing in rows:
    print(f"{name:<28}{n_exec:>7}{n_hit:>7}{n_exec - n_hit:>7}{pct:>8.1f}%")
print("-" * 78)
overall = (100.0 * tot_hit / tot_exec) if tot_exec else 100.0
print(f"{'TOTAL':<28}{tot_exec:>7}{tot_hit:>7}{tot_exec - tot_hit:>7}{overall:>8.1f}%")
print()
print("=" * 78)
print("LARGEST UNCOVERED RANGES (top 3 modules by miss count)")
print("=" * 78)
for name, n_exec, n_hit, pct, missing in sorted(rows, key=lambda r: -(r[1] - r[2]))[:3]:
    if not missing:
        continue
    ranges, start, prev = [], missing[0], missing[0]
    for ln in missing[1:]:
        if ln == prev + 1:
            prev = ln
            continue
        ranges.append((start, prev))
        start = prev = ln
    ranges.append((start, prev))
    ranges.sort(key=lambda r: -(r[1] - r[0]))
    top = ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in ranges[:8])
    print(f"{name} ({n_exec - n_hit} missed): {top}")
