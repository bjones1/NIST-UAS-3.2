#!/bin/sh -e
#
# ****************************************************************
# |docname| - Install files and set up the Pi for development mode
# ****************************************************************
# This was taken from |pi-bridge|. It must be run from the directory containing this file.
sudo apt update
sudo apt upgrade -y
sudo apt install -y hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo cp -r files/* /
sudo systemctl enable systemd-networkd
sudo rfkill unblock wlan
# Reboot for changes to take effect.
sudo systemctl reboot
