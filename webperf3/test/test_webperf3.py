# ****************************************************
# |docname| - Unit tests for `../webperf3/webperf3.py`
# ****************************************************
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8`_.
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
    d = read_iperf3_json_log(test_local / "single_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        6218445861.06448,
        5588500339.1611471,
        "UE name 2 here",
    )


def test_2():
    d = read_iperf3_json_log(test_local / "multiple_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        5930752506.02558,
        5060954075.1963663,
        "UE name 1 here",
    )


def test_3():
    d = read_iperf3_json_log(test_local / "error_0_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        5930752506.02558,
        5060954075.1963663,
        "UE name 1 here",
    )
