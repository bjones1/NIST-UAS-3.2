#!/bin/sh -e
#
# ***************************************************************
# |docname| - Install files and set up the Pi for production mode
# ***************************************************************
# This must be run from the directory containing this file. It assumes that `../install-prep.sh` has already been executed. It somewhat follows the `official Pi docs <https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point>`_.
#
# Set up networking.
sudo apt install -y dnsmasq hostapd
sudo cp -r files/* /
sudo rfkill unblock wlan
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

# Reboot for changes to take effect.
sudo systemctl reboot
