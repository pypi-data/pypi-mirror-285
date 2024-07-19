.. _release_notes:

Release Notes
=============

Release v1.1
--------------
Web User Interface has been added to allow management and configuration of the SK-VPN using a web browser.

Bug Fixes and improvements.

* Fix MAC/LAN address Role assignment - was failing if the initial LAN/WAN ip address was 10.X.0.X where X >= 10
* REST API now allows LAN/WAN MAC assignemnt even if initial IPs are not valid or unassigned
* ACL IP Rules now use an Integer for Protocol instead of string

 
New Features and REST API updates:

* Expand Version reporting in sys/version 
* Expand system report in sys/system-report to report "build-type"
* Web User Interface 
* Various API updates and bug fixes in support of the Web User Interface



Release v1.0
--------------
v1.0.1717174796

Initial Release of the SK-VPN.
