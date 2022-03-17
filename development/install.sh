#!/bin/sh -e
#
# ****************************************************************
# |docname| - Install files and set up the Pi for development mode
# ****************************************************************
# This must be run from the directory containing this file.
#
# Upgrade Linux.
sudo apt update
sudo apt upgrade -y

# Install the iPerf3 webserver.
sudo apt install -y git python3-venv iperf3
curl -sSL https://install.python-poetry.org | python3 -
git clone https://github.com/bjones1/NIST-UAS-3.2.git
cd NIST-UAS-3.2/webperf3
sudo /home/pi/.local/bin/poetry update --no-dev

# Set up networking. This was taken from |pi-bridge|.
sudo apt install -y hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo cp -r files/* /
sudo systemctl enable systemd-networkd
sudo rfkill unblock wlan

# Reboot for changes to take effect.
sudo systemctl reboot
