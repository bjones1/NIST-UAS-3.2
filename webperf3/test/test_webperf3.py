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
from webperf3.webperf3 import (
    extract_iperf3_performance,
    read_iperf3_json_log,
    read_all_iperf3_json_log,
)


# Globals
# =======
test_local = Path(__file__).resolve().parent


# Tests
# =====
def test_1():
    d = read_iperf3_json_log(test_local / "single_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        1647312652,
        6218445861.06448,
        5588500339.1611471,
        "UE name 2 here",
    )


def test_2():
    d = read_iperf3_json_log(test_local / "multiple_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        1647312637,
        5930752506.02558,
        5060954075.1963663,
        "UE name 1 here",
    )


def test_3():
    d = read_iperf3_json_log(test_local / "error_0_iperf3_output.json")
    assert extract_iperf3_performance(d) == (None, None, None, None)
    d = read_iperf3_json_log(test_local / "error_1_iperf3_output.json")
    assert extract_iperf3_performance(d) == (None, None, None, None)


def test_4():
    d = read_iperf3_json_log(test_local / "no_bidir_iperf3_output.json")
    assert extract_iperf3_performance(d) == (
        1647873959,
        None,
        39130143.4457638,
        None,
    )


def test_5():
    arr = read_all_iperf3_json_log(test_local / "multiple_iperf3_output.json")
    d = [extract_iperf3_performance(el) for el in arr]
    assert d == [
        (1647307558, 5644924535.6456957, 4900633492.4580631, "UE name here"),
        (1647312637, 5930752506.02558, 5060954075.1963663, "UE name 1 here"),
    ]


# For simple interactive testing.
if False:
    from webperf3.webperf3 import export_csv

    def test_6():
        print(export_csv(1))
        assert False
