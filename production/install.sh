#!/bin/sh -e
#
# ***************************************************************
# |docname| - Install files and set up the Pi for production mode
# ***************************************************************
# This must be run from the directory containing this file. It assumes that `../install-prep.sh` has already been executed.
#
# Set up networking.
sudo apt install -y dnsmasq hostapd
sudo cp -r production/files/* /
sudo rfkill unblock wlan

# Reboot for changes to take effect.
sudo systemctl reboot
