***************************************************
3.2-Lifelink: UAS Data Relay | UAS Triple Challenge
***************************************************
This site provides software and instructions for configuring the Raspberry Pi used in the `Challenge 3.2: Lifelink – UAS Data Relay <https://www.uastriplechallenge.com/copy-of-3-2-lifelink-uas-data-relay>`_ of the `First Responder UAS Triple Challenge <https://www.uastriplechallenge.com/>`_. See `github <https://github.com/bjones1/NIST-UAS-3.2>`_ for the source files discussed in this site.


TODO
====
#.  Provide a nice way to rebuild the Pi setup needed to produce an image:

    #.  Create a script to take a Pi from its raw install of the Raspberry PI OS to the proper config for this challenge.

#.  Run multiple iPerf3 instances at boot-up, capturing output from each instance in a uniquely-named log file.

#.  Create a simple webserver to present iPerf3 results as a web page.

#.  Include iOS support. It looks like there are two iPerf3 iOS ports available in the Apple App Store.


Smartphone setup
================
.. toctree::
    :maxdepth: 2

    docs/smartphone-setup


Pi setup
========
To use a provided image:

.. toctree::
    :maxdepth: 2

    docs/pi-setup


To build a Pi image from scratch, refer to the following subsections.

Manual configuration: these steps apply to both the production and development configurations below.

#.  Download `Raspian 64-bit Lite (no desktop) <https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip>`_.
#.  Unzip and use Rufus to burn to 32GB+ card. Boot on Pi.
#.  Run ``sudo raspi-config``

    #.  Localisation->WLAN country-> US
    #.  Localisation->Timezone->Chicago
    #.  Keyboard 104, US, default
    #.  Enable SSH


Pi production configuration
---------------------------
This statically assigns addresses to both the Ethernet and Wifi sides of the Pi; the Pi is configured as a wireless access point.

#.  Run::

        sudo apt update
        sudo apt upgrade
        sudo apt install dnsmasq hostapd
        cp -r production/files /

.. toctree::
    :maxdepth: 2

    production/files/etc/dhcpcd.conf
    production/files/etc/dnsmasq.conf
    production/files/etc/hostapd/hostapd.conf


Pi development configuration
----------------------------
For development, the Pi is configured as a bridged wireless access point. This allows devices plugged in via either Ethernet or connected via WiFi to live on the same subnet, so that iPerf3 client / servers can connect across the Pi. It also allows developers to plug the Pi in to Ethernet and still connect to it via WiFi for testing. When no Ethernet cable is present (meaning the Ethernet interfaced doesn't assign the Pi an IP address), the Pi uses a default address of 169.254.56.126.

This configuration was produced by following the |pi-bridge| instructions. To set this up (warning: this is untested!):

.. code-block:: bash

    sudo apt install -y hostapd
    sudo systemctl unmask hostapd
    sudo systemctl enable hostapd
    cp -r development/files /
    sudo systemctl enable systemd-networkd
    sudo rfkill unblock wlan
    # Reboot for changes to take effect.
    sudo systemctl reboot

.. toctree::
    :maxdepth: 2

    development/files/etc/systemd/network/bridge-br0.netdev
    development/files/etc/systemd/network/br0-member-eth0.network
    development/files/etc/dhcpcd.conf
    development/files/etc/hostapd/hostapd.conf


Generating an image file
========================
#.  Mount a flash drive:

    #.  Do this one time::

            sudo apt-get install exfat-fuse exfat-utils
            sudo mkdir /media/usb

    #.  Connect flash drive
    #.  Run::

            sudo fdisk -l # (shows /dev/sda)
            sudo mount /dev/sda1 /media/usb

#.  Create the image: ``sudo dd if=/dev/mmcblk0 of=/media/usb/pi.img bs=1k conv=noerror``. This took about 20 minutes
#.  Unmount flash drive: ``sudo umount /media/usb``


Documentation generation/misc files
===================================
.. toctree::
    :maxdepth: 2

    .gitignore
    conf.py
    codechat_config.yaml
    readthedocs.yml


Search
======
`Search <search>` this site.
