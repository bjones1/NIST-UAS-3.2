******************
Raspberry Pi setup
******************
#.  Download uas-v01.img file from UAS 3.2 Challenge Website.
#.  Create microSD card using a program like Windows Disk Imager or `Rufus <https://rufus.ie/en/>`_.

    #.  This image was tested on a 32GB and 128GB microSD card.
    #.  This process will completely erase and create new partitions on the microSD card.

    .. image:: Rufus.png

#.  Insert card in Raspberry Pi 4 and power on.
a.  Login with default Raspian credentials (login: pi, pw: raspberry)
#.  Start server instances

    a.  Run: ``iperf3 -s -p 5201 &> logfile-5201 &``
    b.  Run: ``iperf3 -s -p 5202 &> logfile-5202 &``
    c.  Additional servers can be started as needed.

#.  Connect devices via ethernet or wifi (SSID: PiNet, password UAS3Chal)

    #.  Ethernet devices will be assigned an address in the 192.168.2.1xx range
    #.  Wi-Fi devices will be assigned an address in the 192.168.3.1xx range

#.  Configure UEs and run data tests.
