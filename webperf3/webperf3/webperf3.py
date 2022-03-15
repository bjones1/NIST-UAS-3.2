# **************************************************
# |docname| - A web server to display iPerf3 results
# **************************************************
# TODO: This isn't a web server quite yet... Overall plan:
#
# - Run iPerf3 servers; monitor for changes to log files, displaying each run to the console. Need to write unit tests.
# - Get Bottle running with a simple template to display results and scoring.
# - Get a websocket running to send the client updates.
# - Think about data to download as csv files, or .json logs. When to delete logs?
#
# .. contents:: Table of Contents
#   :local:
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8`_.
#
# Standard library
# ----------------
from json import loads
from pathlib import Path
import sys
from textwrap import dedent
from typing import Any, Dict, Optional, Tuple, Union

# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
from .ci_utils import xqt


# iPerf3 utilities
# ================
# These functions interact with iPerf3.
#
# Read iPerf3 logs
# ----------------
# Read the last entry in a JSON-like log data from iPerf3, returning it as a Python data structure.
def read_iperf3_json_log(
    # The Path (or its equivalent string) of the log file to read.
    log_path: Union[Path, str],
    # Returns the last iPerf3 result; this is a huge struct of iPerf3 data.
) -> Dict[str, Any]:

    pseudo_json = Path(log_path).read_text()
    # Each run of iPerf3 appends a valid JSON string to the log file; however, this makes the overall file invalid JSON after the first append. The structure looks like this:
    #
    # .. code-block:: text
    #   :linenos:
    #
    #   {
    #       ...JSON data for execution i of iPerf3...
    #   }
    #   {
    #       ...JSON data for execution i + 1 of iPerf3...
    #   }
    #
    # Since we only care about the last run, a simple backwards search for a single line containing an ``{`` with no leading spaces identifies the beginning of the last group of JSON data.
    try:
        index = pseudo_json.rindex("\n{") + 1
    except ValueError:
        # Special case: there's only one block of JSON data; therefore, include the entire file when loading JSON data.
        index = 0
    json_str = pseudo_json[index:]
    return loads(json_str)


# Extract iPerf3 data rates (bps) from its log data
# -------------------------------------------------
def extract_iperf3_performance(
    # The iPerf3 log data returned by `read iPerf3 logs`_.
    iperf3_log_data: Dict[str, Any],
) -> Tuple[
    # The average bits per second sent by the server.
    float,
    # The average bits per second received by the server.
    float,
    # The extra data provided by the client, if present; ``None`` otherwise.
    Optional[str],
]:
    # Extract the relevant data from the JSON file.
    se = iperf3_log_data["end"]["streams"]
    return (
        se[1]["sender"]["bits_per_second"],
        se[0]["receiver"]["bits_per_second"],
        iperf3_log_data.get("extra_data"),
    )


# Name iPerf3 log files
# ---------------------
def iperf3_log_file_name(
    # A value between 0 and the ``num_servers`` passed to `start iPerf3 servers`_.
    server_index: int,
    # A Path to an iPerf3 log file.
) -> str:
    return Path(f"/home/pi/iperf3-logs/port-{server_index}.json")


# Start iPerf3 servers
# --------------------
# TODO: will all these subprocesses automatically be killed when this program exits? That's what we want.
def start_iperf3_servers(
    # The number of servers to start; must be a non-negative number.
    num_servers: int,
) -> None:

    # The first port (which iPerf3 defaults to) to use when starting servers.
    starting_port = 5201
    for server_index in range(num_servers):
        xqt(
            f"iperf3 --server --json --port {server_index + starting_port} "
            f"--logfile {start_iperf3_servers(server_index)} &"
        )


# Main
# ====
if __name__ == "__main__":
    # Parse command line.
    if len(sys.argv < 1):
        print(
            dedent(
                f"""
                Usage: {sys.argv[0]} NUM_PORTS
                where NUM_PORTS gives the number of ports to monitor.

                Error: {'missing NUM_PORTS.' if sys.argv < 2 else 'too many arguments.'}
                """
            )
        )
    num_ports = int(sys.argv[1])
    start_iperf3_servers(num_ports)

    # TODO: monitor all log files.
    data = read_iperf3_json_log(iperf3_log_file_name(0))
