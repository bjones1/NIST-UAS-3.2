#!/bin/sh -e
#
# ****************************************************************
# |docname| - Install files and set up the Pi for development mode
# ****************************************************************
# This must be run from the directory containing this file. It assumes that `../install-prep.sh` has already been executed.
#
# Set up networking. This was taken from |pi-bridge|.
sudo apt install -y hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo cp -r files/* /
sudo systemctl enable systemd-networkd
sudo rfkill unblock wlan

# Reboot for changes to take effect.
sudo systemctl reboot
