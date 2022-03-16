*************************************************
webperf3 - A web server to display iPerf3 results
*************************************************
Basic setup for development:

#.  Install `Poetry <https://python-poetry.org/docs/master/#installing-with-the-official-installer>`_.
#.  Install this project: ``poetry install``.
#.  Run the tests: ``poetry run test/pre_commit_check.py``.


Modules
=======
.. toctree::
    :maxdepth: 2

    webperf3/webperf3.py
    webperf3/ci_utils.py
    webperf3/ReconnectingWebsocket.js
    webperf3/__init__.py
    webperf3/__main__.py


Development support
===================
A standard dev setup: use Poetry, Black, flake8, mypy, pytest, and coverage.

.. toctree::
    :maxdepth: 2

    pyproject.toml
    pre_commit_check.py
    test/test_webperf3.py
    mypy.ini
    .flake8