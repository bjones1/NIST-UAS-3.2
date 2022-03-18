#!/bin/sh -e
#
# **********************************************
# |docname| - Prepare for futher Pi installation
# **********************************************
# Run this script first; next, run either `production/install.sh` or `development/install.sh` to complete Pi setup.
#
# Upgrade Linux.
sudo apt update
sudo apt upgrade -y

# Install the iPerf3 webserver.
sudo apt install -y git python3-venv iperf3
curl -sSL https://install.python-poetry.org | python3 -
git clone https://github.com/bjones1/NIST-UAS-3.2.git
cd NIST-UAS-3.2/webperf3
# Note: for development, consider omitting ``--no-dev``. However, this would also require installing a C compiler, since development dependencies include LXML, which lacks pre-compiled binaries for the Pi. Another alternative is to develop on a PC, where pre-compiled binaries are available.
sudo /home/pi/.local/bin/poetry update --no-dev
