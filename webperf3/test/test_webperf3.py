# ****************************************************
# |docname| - Unit tests for `../webperf3/webperf3.py`
# ****************************************************
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
from pathlib import Path


# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from webperf3.webperf3 import extract_iperf3_performance, read_iperf3_json_log


# Globals
# =======
test_local = Path(__file__).resolve().parent


# Tests
# =====
def test_1():
    d = read_iperf3_json_log(test_local / "sample_iperf3_output.json")
    e = extract_iperf3_performance(d)
    print(e)
