# **************************************************
# |docname| - Read JSON-like data produced by iPerf3
# **************************************************
# The JSON data output by iPerf3 --json is valid only when the program runs a single test; after that, the JSON from each run is concatenated, producing an invalid result. This splits each run's data back apart.

# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
from json import loads
from pathlib import Path
from typing import Any, List

# Third-party imports
# -------------------
# None.
#
# Local application imports
# -------------------------
# None.
#
#
# Code
# ====


# Read iPerf3 logs
# ----------------
# Read JSON-like log data from iPerf3, returning it as a Python data structure.
def read_iperf3_json_log(
    # The Path of the log file to read.
    log_path: Path,

    # Returns a list iPerf3 results; each list item is a huge struct of iPerf3 data.
) -> List[Any]:

    pseudo_json = log_path.read_text()
    # This turns a bunch of concatenated JSON strings into a valid array of JSON data. Each string ends with:
    #
    #   .. code-block:: JSON
    #       :linenos:
    #
    #       {
    #       }
    #
    # Simply adding a comma between these curly brackets, plus sandwiching the entire file with ``[`` and ``]`` produces valid JSON.
    json_str = "[" + pseudo_json.replace("\n}\n{", "\n},\n{") + "]"
    return loads(json_str)


# Main
# ----
if __name__ == "__main__":
    data = read_iperf3_json_log(Path('port-5201-log.json'))

    # Extract the relevant data from the JSON file.
    for session in data:
        se = session["end"]["streams"]
        print(
            f'Send: {se[1]["sender"]["bits_per_second"]/1e6}Mbps  '
            f'Receive: {se[0]["receiver"]["bits_per_second"]/1e6}Mbps'
        )
