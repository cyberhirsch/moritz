# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Run every Moritz and Maximize test script in background mode, on any platform.

    python moritz/tools/run_headless_tests.py <moritz program> <Moritz repo> <Maximize repo>

Scripts that drive the window (simulated mouse events) do nothing in background mode and pass.
A script fails when it reports failures, prints a Python traceback or crashes. Exits with 1 if
any failed.
"""

import glob
import os
import re
import subprocess
import sys

FAILED = re.compile(r"FAILURES [1-9]|^FAIL |Traceback|EXCEPTION_ACCESS|Segmentation fault", re.MULTILINE)


def main():
    exe, moritz, maximize = (os.path.abspath(a) for a in sys.argv[1:4])
    scripts = (sorted(glob.glob(os.path.join(moritz, "moritz", "tests", "test_*.py"))) +
               sorted(glob.glob(os.path.join(maximize, "tests", "test_*.py"))))
    failed = []
    for script in scripts:
        name = os.path.relpath(script, os.path.dirname(moritz) if script.startswith(moritz) else maximize)
        try:
            run = subprocess.run([exe, "--factory-startup", "-b", "--python", script], capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                                 timeout=900)
            out = run.stdout + run.stderr
            bad = bool(FAILED.search(out)) or run.returncode not in (0,)
        except subprocess.TimeoutExpired:
            out, bad = "timed out", True
        print(("FAILED " if bad else "ok     ") + name, flush=True)
        if bad:
            failed.append(name)
            print("\n".join(out.splitlines()[-40:]), flush=True)
    print("{} scripts, {} failed".format(len(scripts), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
