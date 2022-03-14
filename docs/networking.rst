********************************
Supported network configurations
********************************

Competition
===========
In this mode, the resulting network lacks a connection to the Internet.

-   The Pi connects to a monitoring station on the ground from its internal WiFi. It assigns IP addresses to devices connected via WiFi and Ethernet.
-   An WiFi access point / router connects via Ethernet to its WAN jack (not the LAN jacks).
-   The UEs connect to this access point.

The external access point / router must allow connections from UEs back to the Pi.


Development
===========
In this mode, the resulting network can connect to the Internet, allowing for easier development.

-   The Pi bridges its WiFi to its Ethernet port.
-   The Pi's Ethernet port connects to a LAN jack of an access point / router, which assigns it an IP address. If the Pi's Ethernet port isn't connected, then it self-assigns an address of 169.254.56.126.

UEs connected to either the Pi's WiFi or the access point / router's WiFi / LAN will share the same subnet and be routeable.