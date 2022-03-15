# *********************************************
# |docname| - Execute `webperf3.py` as a module
# *********************************************
from sys import argv
from .webperf3 import main

if __name__ == "__main__":
    main(argv)
