*******************
Building a Pi image
*******************
**These instructions aren't necessary to use this system.** They're intended for developers who need to build a Pi image from scratch.

Pi setup
========
Manual configuration: these steps apply to both the production and development configurations below.

#.  Download `Raspian 64-bit Lite (no desktop) <https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64-lite.zip>`_.
#.  Unzip and use Rufus to burn to 32GB+ card. Boot on Pi.
#.  Run ``sudo raspi-config``. Set the following:

    #.  Localisation->WLAN country-> US
    #.  Localisation->Timezone->Chicago
    #.  Localisation->Keyboard (auto-sets to 104 keys, US)
    #.  Enable SSH

Next, run:

.. toctree::
    :maxdepth: 2

    ../install-prep.sh

Finally, follow the steps for the production or development configuration below.


Pi production configuration
---------------------------
This statically assigns addresses to both the Ethernet and Wifi sides of the Pi; the Pi is configured as a wireless access point.

#.  Run::

        cd NIST-UAS-3.2/production
        ./install.sh

Configuration files
^^^^^^^^^^^^^^^^^^^
These files configure the Pi for production mode.

.. toctree::
    :maxdepth: 2

    ../production/install.sh
    ../production/files/etc/rc.local
    ../production/files/etc/dhcpcd.conf
    ../production/files/etc/dnsmasq.conf
    ../production/files/etc/hostapd/hostapd.conf


Pi development configuration
----------------------------
For development, the Pi is configured as a bridged wireless access point. This allows devices plugged in via either Ethernet or connected via WiFi to live on the same subnet, so that iPerf3 client / servers can connect across the Pi. It also allows developers to plug the Pi in to Ethernet and still connect to it via WiFi for testing. When no Ethernet cable is present (meaning the Ethernet interfaced doesn't assign the Pi an IP address), the Pi uses a default address of 169.254.56.126.

This configuration was produced by following the |pi-bridge| instructions. To set this up, run::

    cd NIST-UAS-3.2/development
    ./install.sh

Configuration files
^^^^^^^^^^^^^^^^^^^
These files configure the Pi for development mode.

.. toctree::
    :maxdepth: 2

    ../development/install.sh
    ../development/files/etc/rc.local
    ../development/files/etc/systemd/network/bridge-br0.netdev
    ../development/files/etc/systemd/network/br0-member-eth0.network
    ../development/files/etc/dhcpcd.conf
    ../development/files/etc/hostapd/hostapd.conf


Generating an image file
========================
Finally, create an image from the working Pi setup produced by following the previous two steps.

#.  (Optional) Boot Linux on a PC; use partition management tools to shrink the partition on the Pi's flash drive to make the image faster to generate.

#.  Mount a flash drive:

    #.  Do this one time::

            sudo apt-get install exfat-fuse exfat-utils
            sudo mkdir /media/usb

    #.  Connect flash drive
    #.  Run::

            # (shows /dev/sda)
            sudo fdisk -l
            sudo mount /dev/sda1 /media/usb

#.  Create the image: ``sudo dd if=/dev/mmcblk0 of=/media/usb/pi.img bs=1k conv=noerror``. This took about 20 minutes.
#.  TODO -- need details: run ``pishrink.sh``.
#.  Unmount flash drive: ``sudo umount /media/usb``
