******************************************************************************
User Instructions to Install Termux app to run ``iPerf3`` on an Android device
******************************************************************************
#.  Download Termux for Android device to a PC from https://f-droid.org/en/packages/com.termux/. Download the latest version, currently 0.118.0 (118).
#.  Copy the downloaded APK to the Android device and install the APK.
#.  Ensure the Android device is connected to the internet.
#.  Open/Run Termux on the Android device, then run (choose default answers to questions when prompted)::

        pkg update
        pkg upgrade
        pkg install iperf3

#.  Verify that an IP in the range 192.168.3.1xx was assigned.
#.  From the Termux terminal ping the Raspberry Pi server to ensure connectivity: ``ping 192.168.3.1``.
#.  Test data transfer between the UE and Pi from the Termux terminal:
#.  ``iPerf3 -c 192.168.3.1``
