# **************************************************
# |docname| - A web server to display iPerf3 results
# **************************************************
# This program consists of:
#
# - `iPerf3 utilities`_, which run iPerf3 servers and interpret the results from JSON logs the servers create.
# - A webserver_, which reports iPerf3 results.
# - A `websocket and watcher`_, which looks for changes to the iPerf3 log files. A change causes the websocket to refresh the client, displaying any new results.
#
# Possible extensions:
#
# - Provide a way to clear the table of results. This requires server-side code -- simply write ``{}`` to the end of all log files, then refresh.
# - Kill all the iperf3 servers when this program exits.
#
# .. contents:: Table of Contents
#   :local:
#   :depth: 2
#
#
# Preamble
# ========
#
# Imports
# -------
# These are listed in the order prescribed by `PEP 8`_.
#
# Standard library
# ^^^^^^^^^^^^^^^^
import asyncio
import json
from pathlib import Path
import sys
from textwrap import dedent
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party imports
# ^^^^^^^^^^^^^^^^^^^
from bottle import route, request, response, run, static_file, template
from watchgod import awatch
import websockets
import websockets.server

# Local application imports
# ^^^^^^^^^^^^^^^^^^^^^^^^^
from .ci_utils import is_win, xqt

# Globals
# -------
# The number of iPerf3 servers in use by this program.
num_servers = None
# The first port (which iPerf3 defaults to) to use when starting servers.
starting_port = 5201


# iPerf3 utilities
# ================
# These functions interact with iPerf3.
#
# Read iPerf3 logs
# ----------------
# Read the last entry in a JSON-like log data from iPerf3, returning it as a Python data structure.
def read_iperf3_json_log(
    # _`log_path`: the Path (or its equivalent string) of the log file to read.
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


def read_all_iperf3_json_log(
    # See log_path_.
    log_path: Union[Path, str],
    # Returns an array of iPerf3 results.
) -> List[Dict[str, Any]]:
    # See comments in ``read_iperf3_json_log``.
    pseudo_json = Path(log_path).read_text()
    # Split the data based the beginning/end of JSON data.
    split_json = pseudo_json.split("\n}\n{")
    json_arr: List[Dict[str, Any]] = [{}] * len(split_json)
    for index, json_fragment in enumerate(split_json):
        # Patch up JSON by replacing the missing curly brackets then interpret.
        json_fragment += "}"
        if index:
            json_fragment = "{" + json_fragment
        try:
            json_arr[index] = json.loads(json_fragment)
        except json.decoder.JSONDecodeError:
            pass

    return json_arr


# Extract iPerf3 data rates (bps) from its log data
# -------------------------------------------------
def extract_iperf3_performance(
    # The iPerf3 log data returned by `read iPerf3 logs`_.
    iperf3_log_data: Dict[str, Any],
) -> Tuple[
    # The timestamp of this performance measurement, in seconds sine the epoch.
    Optional[int],
    # The average bits per second sent by the server.
    Optional[float],
    # The average bits per second received by the server.
    Optional[float],
    # The extra data provided by the client, if present; ``None`` otherwise.
    Optional[str],
]:
    # Extract the relevant data from the JSON file.
    timestamp = None
    send_bps = None
    receive_bps = None
    try:
        timestamp = iperf3_log_data["start"]["timestamp"]["timesecs"]
        se = iperf3_log_data["end"]["streams"]
        receive_bps = se[0]["receiver"]["bits_per_second"]
        send_bps = se[1]["sender"]["bits_per_second"]
    except (KeyError, IndexError):
        pass
    return timestamp, send_bps, receive_bps, iperf3_log_data.get("extra_data")


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

    for server_index in range(num_servers):
        cmd = (
            f"iperf3 --server --json --port {server_index + starting_port} "
            f"--logfile {iperf3_log_file_name(server_index)}"
        )
        xqt(f"start {cmd}" if is_win else f"{cmd} &")


# Webserver
# =========
#
# Main page
# ---------
# This is the main web page which displays iPerf3 stats.
@route("/")
def report_stats():
    # Previous iPerf3 data is stored in a cookie.
    try:
        prev_iperf3_data = json.loads(request.cookies.iperf3_data)
        assert (
            isinstance(prev_iperf3_data, list) and len(prev_iperf3_data) == num_servers
        )
    except (json.decoder.JSONDecodeError, AssertionError):
        prev_iperf3_data = [None] * num_servers

    # Look at logs to get current iPerf3 data.
    iperf3_data = []
    for index in range(num_servers):
        try:
            d = extract_iperf3_performance(
                read_iperf3_json_log(iperf3_log_file_name(index))
            )
        # If there's no log file yet, add a blank entry.
        except FileNotFoundError:
            d = [None, None, None, None]
        iperf3_data.append(d)

    # Save it for the next change detection.
    response.set_cookie("iperf3_data", json.dumps(iperf3_data))

    # Send the webpage.
    return template(
        dedent(
            """
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>iPerf3 performance measurements</title>

                    <!-- Use the ``ReconnectingWebsocket`` to automatically reconnect a websocket when the network connection drops. -->
                    <script src="/static/ReconnectingWebsocket.js?v=1"></script>
                    <script src="/static/webperf3.js?v=1"></script>

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
                            <th>Port</th>
                            <th style="width: 15rem">Name</th>
                            <th style="width: 10rem">Timestamp</th>
                            <th style="width: 10rem">Send rate (bps)</th>
                            <th style="width: 10rem">Receive rate (bps)</th>
                            <th>New</th>
                        </tr>

                        % for index in range(num_servers):
                            % # Use ``list()`` since prev_iperf3_data is a list, while iperf3_data is a tuple.
                            % d = list(iperf3_data[index])
                            <tr>
                                <td>{{index + starting_port}}</td>
                                <td>{{d[3] or ""}}</td>
                                <td><script>document.write(formatDate({{d[0] or ""}}));</script></td>
                                <td>{{"" if d[1] is None else "{0:,}".format(round(d[1]))}}</td>
                                <td>{{"" if d[2] is None else "{0:,}".format(round(d[2]))}}</td>
                                <td>{{"X" if d != prev_iperf3_data[index] else ""}}
                            </tr>
                        % end
                    </table>
                    <div>
                        Status: <span id="is_connected">waiting</span>.
                    </div>
                </body>
            </html>
            """
        ),
        iperf3_data=iperf3_data,
        num_servers=num_servers,
        prev_iperf3_data=prev_iperf3_data,
        starting_port=starting_port,
    )


# Static files
# ------------
# Serve static files (JS needed by the main page). Copied from the `bottle docs <http://bottlepy.org/docs/dev/tutorial.html#routing-static-files>`_.
@route("/static/<filename>")
def server_static(filename):
    return static_file(filename, root=str(Path(__file__).parent))


# Websocket and watcher
# =====================
# The watcher monitors the log directory, sending a message over a websocket to the client when the client needs to be updated.
class WebSocketWatcher:
    # Startup / shutdown
    # ------------------
    def __init__(
        self,
        # A Path to the directory containing logs.
        log_path: Path,
    ):
        self.log_path = log_path
        self.stop_event: Optional[asyncio.Event] = None
        self.update_event: Optional[asyncio.Event] = None
        self.thread = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self):
        self.thread = Thread(target=asyncio.run, args=(self.amain(),))
        self.thread.start()

    # Shut down the websocket / watcher from another thread.
    def stop(self):
        self.loop.call_soon_threadsafe(self.stop_event.set)
        self.thread.join()

    # Websocket and watcher core
    # --------------------------
    # This handles an open websocket connection.
    async def update(
        self,
        # The opened websocket that can now be read or written.
        websocket: websockets.server.WebSocketServerProtocol,
    ) -> None:
        try:
            # Wait until the watcher signals a change.
            await self.update_event.wait()
            # Tell this client to refresh. Exit after this, since the refresh causes it to close the connection. TODO: just send the updated table instead.
            await websocket.send("new data")
        except websockets.exceptions.WebSocketException:
            # Just allow the socket to close.
            pass
        print("Websocket connection closed.")

    async def watcher(self) -> None:
        # Very important: this hangs in shutdown unless we pass ``self.stop_event`` to the watcher.
        async for change in awatch(self.log_path, stop_event=self.stop_event):  # type: ignore
            print(change)
            # Signal any websockets to do an update.
            self.update_event.set()
            # Reset to prepare for the next signal.
            self.update_event.clear()

        # On shutdown, signal any waiting websockets so they can exit.
        self.update_event.set()

    # This is the websocket server main loop, which waits for connections.
    async def amain(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.stop_event = asyncio.Event()
        self.update_event = asyncio.Event()

        # Run the watcher.
        watcher_task = asyncio.create_task(self.watcher())

        # Start the server; per the `docs <https://websockets.readthedocs.io/en/stable/reference/server.html#websockets.server.serve>`__, exiting this context manager shuts it down.
        async with websockets.serve(self.update, "0.0.0.0", 8765):  # type:ignore
            # Run the server until a stop is requested.
            await self.stop_event.wait()
        await watcher_task
        print("Websocket server shutting down...")


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

    # Start the webserver and the watcher/websocket.
    start_iperf3_servers(num_servers)
    wsw = WebSocketWatcher(log_dir)
    wsw.start()
    # Ideally, run an asyncio server; however, I don't understand how this would integrate into the event loop. So, use a multi-threaded server instead.
    run(host="0.0.0.0", port=80, server="paste")

    # Shut down.
    print("Shutting down...")
    wsw.stop()
