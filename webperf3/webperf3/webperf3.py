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
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
from json import loads
from pathlib import Path
import subprocess
import sys
from textwrap import dedent
from typing import Any, Dict, Tuple, Union

# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
# None.
#
#
# OS detection
# ============
# This follows the `Python recommendations <https://docs.python.org/3/library/sys.html#sys.platform>`_.
is_win = sys.platform == "win32"
is_linux = sys.platform.startswith("linux")
is_darwin = sys.platform == "darwin"

# Copied from https://docs.python.org/3.5/library/platform.html#cross-platform.
is_64bits = sys.maxsize > 2**32


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
) -> Dict[Any]:

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
    json_str = pseudo_json[pseudo_json.rindex("\n{") + 1:]
    return loads(json_str)


# Extract iPerf3 data rates (bps) from its log data
# -------------------------------------------------
def extract_iperf3_performance(
    # The iPerf3 log data returned by `read iPerf3 logs`_.
    iperf3_log_data: Dict[Any],
) -> Tuple[
    # The average bits per second sent by the server.
    float,
    # The average bits per second received by the server.
    float
]:
    # Extract the relevant data from the JSON file.
    se = data["end"]["streams"]
    return se[1]["sender"]["bits_per_second"], se[0]["receiver"]["bits_per_second"]


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


# Python command-line utilities
# =============================
# These tools make it easier to do shell-like scripting in Python.
#
# xqt
# ---
# Pronounced "execute": provides a simple way to execute a system command.
def xqt(
    # Commands to run. For example, ``'foo -param firstArg secondArg', 'bar |
    # grep alpha'``.
    *cmds,
    # Optional keyword arguments to pass on to `subprocess.run <https://docs.python.org/3/library/subprocess.html#subprocess.run>`_.
    **kwargs
):

    ret = []
    # Although https://docs.python.org/3/library/subprocess.html#subprocess.Popen
    # states, "The only time you need to specify ``shell=True`` on Windows is
    # when the command you wish to execute is built into the shell (e.g.
    # **dir** or **copy**). You do not need ``shell=True`` to run a batch file
    # or console-based executable.", use ``shell=True`` to both allow shell
    # commands and to support simple redirection (such as ``blah > nul``,
    # instead of passing ``stdout=subprocess.DEVNULL`` to ``check_call``).
    for _ in cmds:
        # Per http://stackoverflow.com/questions/15931526/why-subprocess-stdout-to-a-file-is-written-out-of-order,
        # the ``check_call`` below will flush stdout and stderr, causing all
        # the subprocess output to appear first, followed by all the Python
        # output (such as the print statement above). So, flush the buffers to
        # avoid this.
        flush_print(_)
        # Use bash instead of sh, so that ``source`` and other bash syntax
        # works. See https://docs.python.org/3/library/subprocess.html#subprocess.Popen.
        executable = "/bin/bash" if is_linux or is_darwin else None
        try:
            cp = subprocess.run(
                _, shell=True, executable=executable, check=True, **kwargs
            )
        except subprocess.CalledProcessError as e:
            flush_print(
                "Subprocess output:\n{}\n{}".format(e.stderr or "", e.stdout or "")
            )
            raise
        ret.append(cp)

    # Return a list only if there were multiple commands to execute.
    return ret[0] if len(ret) == 1 else ret


# flush_print
# -----------
# Anything sent to ``print`` won't be printed until Python flushes its buffers,
# which means what CI logs report may be reflect what's actually being executed
# -- until the buffers are flushed.
def flush_print(*args, **kwargs):
    print(*args, **kwargs)
    # Flush both buffers, just in case there's something in ``stdout``.
    sys.stdout.flush()
    sys.stderr.flush()


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
