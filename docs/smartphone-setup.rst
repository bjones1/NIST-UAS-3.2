****************
Smartphone setup
****************

Android
=======
#.  Download Termux for Android device to a PC from https://f-droid.org/en/packages/com.termux/. Download the latest version, currently 0.118.0 (118).
#.  Copy the downloaded APK to the Android device and install the APK.
#.  Ensure the device is connected to the internet.
#.  Open/Run Termux on the Android device, then run (choose default answers to questions when prompted)::

        pkg update
        pkg upgrade
        pkg install iperf3

#.  Connect the device the Pi via Ethernet or WiFi (SSID: ``PiNet``, password ``UAS3Chal``).
#.  Verify that an IP in the range 192.168.3.1xx was assigned.
#.  From the Termux terminal ping the Raspberry Pi server to ensure connectivity: ``ping 192.168.3.1``.
#.  Test data transfer between the UE and Pi from the Termux terminal: run ``iperf3 --client 192.168.3.1 --bidir --extra-data "<UE name here>" --port <port>`` where ``<port>`` is between 5201 and 5211 and ``<UE name here>`` is an arbitrary name for this device, used when displaying the device's name on the webserver.


iOS
===
#.  Ensure the device is connected to the internet.
#.  Install the iPerf3 Wifi Speed Test app from the Apple app store.
#.  Connect the device the Pi via WiFi (SSID: ``PiNet``, password ``UAS3Chal``).
#.  Verify that an IP in the range 192.168.3.1xx was assigned.
#.  Open the app. Select:

    #.  A server address of 192.168.3.1;
    #.  Set streams to 2.
    #.  A test duration of 10s.
    #.  The iOS client doesn't support bidirectional mode; test first with a transmit mode of download, then test again with a transmit mode of upload.

#.  Press start.


Windows/OS X
============
#.  Download a `Windows binary of iPerf3 <https://files.budman.pw/>`_ or `brew install iperf3 <https://formulae.brew.sh/formula/iperf3>`_.
#.  Connect the device the Pi via Ethernet or WiFi (SSID: ``PiNet``, password ``UAS3Chal``).

    #.  Ethernet devices will be assigned an address in the 192.168.2.1xx range.
    #.  Wi-Fi devices will be assigned an address in the 192.168.3.1xx range.

#.  From the terminal/command prompt, ping the Raspberry Pi server to ensure connectivity: ``ping 192.168.3.1``.
#.  Test data transfer between the UE and Pi from the terminal/command prompt: run ``iperf3 --client 192.168.3.1 --bidir --extra-data "<UE name here>" --port <port>`` where ``<port>`` is between 5201 and 5211 and ``<UE name here>`` is an arbitrary name for this device, used when displaying the device's name on the webserver.


Viewing results
===============
Connect any device to the Pi, then open a web browser to ``192.168.3.1`` to view performance results.