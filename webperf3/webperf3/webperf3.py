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
import json
from pathlib import Path
import sys
from textwrap import dedent
from typing import Any, Dict, Optional, Tuple, Union

# Third-party imports
# -------------------
from bottle import route, request, response, run, template

# Local application imports
# -------------------------
from .ci_utils import is_win, xqt


# Globals
# =======
num_servers = None


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

    # Errors produce confused JSON intermixed with error messages.
    try:

        json_str = pseudo_json[index:]
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        return {}


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
    try:
        se = iperf3_log_data["end"]["streams"]
        send_bps = se[1]["sender"]["bits_per_second"]
        receive_bps = se[0]["receiver"]["bits_per_second"]
    except KeyError:
        send_bps = None
        receive_bps = None
    return send_bps, receive_bps, iperf3_log_data.get("extra_data")


# Name iPerf3 log files
# ---------------------
def iperf3_log_file_name(
    # A value between 0 and the ``num_servers`` passed to `start iPerf3 servers`_.
    server_index: int,
    # A Path to an iPerf3 log file.
) -> Path:
    return (
        Path.home() / f"/iperf3-logs/port-{server_index}.json"
        if is_win
        else Path(f"/home/pi/iperf3-logs/port-{server_index}.json")
    )


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
        cmd = (
            f"iperf3 --server --json --port {server_index + starting_port} "
            f"--logfile {iperf3_log_file_name(server_index)}"
        )
        xqt(f"start {cmd}" if is_win else f"{cmd} &")


# Webserver
# =========
@route("/")
def report_stats():
    # Previous iPerf3 data is stored in a cookie.
    try:
        prev_iperf3_data = json.loads(request.cookies.iperf3_data)
        assert isinstance(prev_iperf3_data, list) and len(prev_iperf3_data) == num_servers
    except (json.decoder.JSONDecodeError, AssertionError):
        prev_iperf3_data = [None] * num_servers
    iperf3_data = []
    for index in range(num_servers):
        try:
            d = extract_iperf3_performance(read_iperf3_json_log(iperf3_log_file_name(index)))
        # If there's no log file yet, add a blank entry.
        except FileNotFoundError:
            d = [0, 0, ""]
        iperf3_data.append(d)
    response.set_cookie("iperf3_data", json.dumps(iperf3_data))
    print(iperf3_data, prev_iperf3_data)
    return template(
        dedent(
            """
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>iPerf3 performance measurements</title>
                    <style>
                        table, th, td {
                            border: 1px solid white;
                            border-collapse: collapse;
                        }
                        th, td {
                            background-color: #96D4D4;
                        }
                    </style>
                </head>
                <body>
                    <h1>iPerf3 performance measurements</h1>
                    <table>
                        <tr>
                            <th>Index</th>
                            <th style="width: 20rem">Name</th>
                            <th style="width: 10rem">Send rate (bps)</th>
                            <th style="width: 10rem">Receive rate (bps)</th>
                            <th>New</th>
                        </tr>

                        % for index in range(num_servers):
                            % # Use ``list()`` since prev_iperf3_data is a list, while iperf3_data is a tuple.
                            % d = list(iperf3_data[index])
                            <tr>
                                <td>{{index + 1}}</td>
                                <td>{{d[2]}}</td>
                                <td>{{d[0]}}</td>
                                <td>{{d[1]}}</td>
                                <td>{{"new" if d != prev_iperf3_data[index] else ""}}
                            </tr>
                        % end
                    </table>
                </body>
            </html>
            """
        ),
        num_servers=num_servers,
        iperf3_data=iperf3_data,
        prev_iperf3_data=prev_iperf3_data,
    )


# Main
# ====
def main(argv):
    # Parse command line.
    if len(argv) != 2:
        print(
            dedent(
                f"""
                Usage: {argv[0]} NUM_PORTS
                where NUM_PORTS gives the number of ports to monitor.

                Error: {'missing NUM_PORTS.' if len(argv) < 2 else 'too many arguments.'}
                """
            ),
            file=sys.stderr,
        )
        return
    global num_servers
    num_servers = int(argv[1])

    # Set up logging subdirectory.
    log_dir = iperf3_log_file_name(0).parent
    print(f"Logging iPerf3 data to {log_dir}.")
    log_dir.mkdir(exist_ok=True)

    # Start iPerf3 and the webserver.
    start_iperf3_servers(num_servers)
    run(host="0.0.0.0", port=80)
