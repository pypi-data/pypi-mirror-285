.. _overview:

.. |SecureKey (TM)| unicode:: SecureKey U+2122
   .. with trademark sign



Overview
========

The |SecureKey (TM)| VPN (SK-VPN) is a IPsec VPN gateway with a focus on security and performance.
Protecting customer's networks across the cloud and cross-premises to secure today's hybrid cloud networks.

.. _conops:

Concept of Operations
---------------------

The |SecureKey (TM)| VPN Gateway lies at the heart of a cloud-based and hybrid network. 
As a Network Gateway, it is used to protect networks that are connected across insecure links and the internet. 
It can be used to protect cross-premises networks and cloud-interconnect links between regions. 
The below image shows an example network protected by the SK-VPN Gateway. 
The VPN acts as an internet gateway device and traffic aggregator allowing network segments to connect securely. 
The VPN uses the strongest commercially available IPsec Encryption standards to encrypt traffic between networks.


.. image:: images/sk_vpn_protected_network.png
    :align: center


.. _azure_network_overview:

Azure Network Overview
----------------------

The |SecureKey (TM)| VPN is available in the Microsoft Azure Third Party Marketplace as a Virtual Machine. 
The SK-VPN integrates into a Microsoft Azure network as shown below. 
In this example, the SK-VPN is used to protect Virtual Networks (VNETs) in different geographic regions
and to connect resources hosted in a different Cloud Service Provider (CSP). 
Further, the SK-VPN connects networks that are protected using an On-Premises Firewalls. 
The SK-VPN(s) can be managed from anywhere with an internet connection, below shows management using On-Premises resources.

.. image:: images/sk_vpn_azure_vnet.png
    :align: center

.. _azure_vm_overview:


Azure Virtual Machine Overview
------------------------------

The |SecureKey (TM)| Virtual Machine (VM) uses Microsoft Azure secure provisioning and Azure network resources allowing for fast and secure deployment. 
As shown below the VM utilizes three Network Interfaces; 
a Local Area Network (LAN) used to connect to the Virtual Network Subnets,
a Wide Area Network (WAN) used to connect to remote peer networks, 
and a Management (MGMT) interface. 

The LAN and WAN interfaces utilize Accelerated Networking to achieve high-bandwidth network encryption. 
The MGMT and WAN interfaces are allocated a Public IP address as they are accessible on the internet. 
The MGMT interface is further protected using a Network Security Group (NSG) that allows only SSH and HTTPS traffic to the MGMT Interface. 
The LAN interface use Azure Network Route Table to direct traffic destined for remote private networks through the SK-VPN Gateway

.. image:: images/sk_vpn_azure_vm_setup.png
    :align: center


.. _security:


Security
--------

The |SecureKey (TM)| VPN was designed with security at the forefront. 
The SK-VPN uses the Patent Pending |SecureKey (TM)| Cryptographic Library to protect keys and secure networks beyond existing commercial standards.

More information about the |SecureKey (TM)| Cryptographic Library can be found at https://www.jettechlabs.com

The SK-VPN supports the following security standards:

Data Plane:

* CNSA v1.0 Algorithms for IKEv2 and IPsec see: `CNSA v1.0 <https://media.defense.gov/2021/Sep/27/2002862527/-1/-1/0/CNSS%20WORKSHEET.PDF>`_ 
* RSA (3072-bit+), ECC (P-384), AES-256-GCM, SHA-384
* Certificate Based Authentication IKEv2
* *Disallow*: Pre-Shared Keys (PSK), IKEv1, non-CNSA v1.0 algorithms
   
Management Interface:

* HTTPS using TLS 1.2+
* Password Based Authentication + Multi-Factor Authentication (MFA)
* Client Certificate Authentication (Mutual TLS)
* Role Based Access Control (RBAC)
* OpenAPI 3.0 compatible REST API
* Secure Shell (SSH) certificate-based authentication
* Command Line Interface (CLI) accessible over SSH and serial console
* Authenticated + Encrypted Syslog over TLS
* Encrypted + Authenticated Software Update using secure hosting servers



.. _performance_features:


Performance and Features
------------------------

The |SecureKey (TM)| VPN Gateway uses Open Source software to implement a high performance 
data plane capable of high-bandwidth IPsec above 10 Gbps+.

The SK-VPN supports the following features and standards:

* IPsec IKEv2 VPN
   * Certificate Based Authentication IKEv2
   * Route Based VPN
* Access Control List (ACL) Layer2-4 firewall 
* Dynamic Name Server (DNS) + DNS Security Extensions (DNSSEC)
* Network Time Protocol (NTP)
* Syslog + Authenticated/Encrypted Syslog over TLS
* Dynamic Host Configuration Portocol (DHCP)
* Certificate Signing Requests (CSR)
  
  





