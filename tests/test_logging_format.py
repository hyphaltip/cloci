import subprocess
import sys


def test_cloci_log_lines_carry_a_timestamp():
    """Run in a fresh interpreter: pytest installs its own logging handlers."""
    code = (
        "import cloci.main, logging;"
        "logging.getLogger('cloci.main').info('stage marker')"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    line = [l for l in res.stderr.splitlines() if "stage marker" in l][0]
    # e.g. "12:34:56 INFO:cloci.main:stage marker"
    assert line[2] == ":" and line[5] == ":" and line[8] == " "
