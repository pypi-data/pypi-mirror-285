************************
Test scenario definition
************************

In the current release, it is possible to supply a configuration file
in ``JSON`` format for running your tests.

.. _config_file_example:

Configuration file example
==========================

- Using `ByteBlower Endpoint <../json/airtime-fairness/endpoint/tr_398.json>`_

  .. literalinclude:: ../extra/test-cases/tr-398/json/airtime-fairness/endpoint/tr_398.json
     :language: json

In the following sections, we will provide a detailed explanation of the
structure and all parameters in the JSON configuration file.

Structure
=========

A quick short reference for the structure:

.. code-block:: json

   {
       "server": "<bb_server_name_or_ip:str>",
       "meeting_point": "<bb_meeting_point_name_or_ip:str>",
       "dut": {
           "name": "<traffic_endpoint_name:str>",
           "interface": "<bb_interface_name:str>",
           "ipv4": "<ipv4_address:str>|dhcp",
           "netmask": "<ipv4_address:str>",
           "gateway": "<ipv4_address:str>",
           "nat": "<nat_resolution:bool>",
           "ipv6": "dhcp|slaac"
       },
       "wlan_stations": [
           {
               "name": "<traffic_endpoint_name:str>",
               "uuid":"<endpoint_uuid:str>",
               "ipv4": true,
               "ipv6": true
           },
           {
               "name": "<traffic_endpoint_name:str>",
               "uuid":"<endpoint_uuid:str>",
               "ipv4": true,
               "ipv6": true
           },
           {
               "name": "<traffic_endpoint_name:str>",
               "uuid":"<endpoint_uuid:str>",
               "ipv4": true,
               "ipv6": true
           }
       ]
   }

JSON schema
===========

The complete structure and documentation of the file is available in
`Configuration file JSON schema <../json/airtime-fairness/config-schema.json>`_
, and documented below.

Server
------

.. jsonschema:: ../extra/test-cases/tr-398/json/airtime-fairness/config-schema.json#/$defs/server_address
   :auto_reference:
   :auto_target:
   :lift_title: False

Meeting point
-------------

.. jsonschema:: ../extra/test-cases/tr-398/json/airtime-fairness/config-schema.json#/$defs/meeting_point_address
   :auto_reference:
   :auto_target:
   :lift_title: False

Traffic endpoints
-----------------

The ``"dut"`` and ``"wlan_stations"`` blocks define the traffic endpoints.

The ``"dut"`` is a ByteBlower port connected to the LAN of the ``DUT``.
A ByteBlower port is a simulated host at a given ByteBlower interface.
Where a ByteBlower interface is the physical connection on either the
*non-trunking interface* (direct connection at a ByteBlower server) or a
*trunking interface* (connection at a physical port on the ByteBlower switch).

Each port supports IPv4 address assignment using static IPv4 configuration
or DHCP. IPv6 address configuration is possible through DHCPv6 or
Stateless autoconfiguration (SLAAC).

When an (IPv4) port is located behind a NAT gateway, then the test framework
will perform additional flow setup steps to resolve the NAT gateway's public
IPv4 address and UDP port (*when required*).

The ``"wlan_stations"`` define the connections to ByteBlower Endpoints. The
ByteBlower Endpoints run on hosts connected to the WLAN stations involved in
the test. The configuration is in the order of appearance in the test scenario
definition: ``STA1``, ``STA2`` and ``STA3``.

They can be configured by:

#. Providing the `meeting point address <Meeting point_>`_ and the *UUID*
   of the endpoint.
#. Setting the IPv4 or IPv6 parameter to ``true``.

.. jsonschema:: ../extra/test-cases/tr-398/json/airtime-fairness/config-schema.json#/$defs/wlan_stations
   :auto_reference:
   :auto_target:
   :lift_title: True

.. jsonschema:: ../extra/test-cases/tr-398/json/airtime-fairness/config-schema.json#/$defs/port
   :auto_reference:
   :auto_target:
   :lift_title: True

.. jsonschema:: ../extra/test-cases/tr-398/json/airtime-fairness/config-schema.json#/$defs/vlan
   :auto_reference:
   :auto_target:


