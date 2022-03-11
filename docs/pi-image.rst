*******************
Building a Pi image
*******************
**These instructions aren't necessary to use this system.** They're intended for developers who need to build a Pi image from scratch.

Pi setup
========
Manual configuration: these steps apply to both the production and development configurations below.

#.  Download `Raspian 64-bit Lite (no desktop) <https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip>`_.
#.  Unzip and use Rufus to burn to 32GB+ card. Boot on Pi.
#.  Run ``sudo raspi-config``

    #.  Localisation->WLAN country-> US
    #.  Localisation->Timezone->Chicago
    #.  Keyboard 104, US, default
    #.  Enable SSH

After this, follow the steps in the production or development configuration.


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

    ../production/files/etc/dhcpcd.conf
    ../production/files/etc/dnsmasq.conf
    ../production/files/etc/hostapd/hostapd.conf


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

    ../development/files/etc/systemd/network/bridge-br0.netdev
    ../development/files/etc/systemd/network/br0-member-eth0.network
    ../development/files/etc/dhcpcd.conf
    ../development/files/etc/hostapd/hostapd.conf


Generating an image file
========================
Finally, create an image from the working Pi setup produced by following the previous two steps.

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
