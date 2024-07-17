========================
Test scenario definition
========================

In the current release, it is possible to supply a configuration file
in ``JSON`` format for running your tests.

In the following sections, we will provide a detailed explanation of the
structure and all parameters in the JSON configuration file.

Structure
=========

The JSON configuration file consists of:

* ByteBlower server address (and optionally a ByteBlower meeting point)
* List of port definitions: Where you want to send traffic from/to
* List of flow definitions: We currently support UDP frame blasting
  and stateful TCP (HTTP) flows.
* (*optional*) Reporting parameters
* Test-specific parameters

A quick short reference for the structure:

.. code-block:: json

   {
       "server": "<bb_server_name_or_ip:str>",
       "meeting_point": "<bb_meeting_point_name_or_ip:str>",
       "ports": [
           {
               "name": "<port_name:str>",
               "interface": "<bb_interface_name:str>",
               "uuid": "<endpoint_uuid:str>",
               "ipv4": "<ipv4_address:str>|dhcp|true",
               "netmask": "<ipv4_netmask:str>",
               "gateway": "<ipv4_gateway:str>",
               "nat": "<enable_nat_resolution:bool>",
               "ipv6": "dhcp|slaac|true",
               "port_group": [
                   "<port_group:str>"
               ]
           }
       ],
       "flows": [
           {
               "name": "<flow_name:str>",
               "source": {
                   "port_group": [
                       "<source_group:str>"
                   ]
               },
               "destination": {
                   "port_group": [
                       "<destination_group:str>"
                   ]
               },
               "add_reverse_direction": "<add_reverse_direction_flow:bool>",
               "type": "<flow_type:str>",
               "ecn": "<ecn_code_point:str|int>",
               "dscp": "<dscp_code_point:str|int>",
               "initial_time_to_wait": "<initial_time_to_wait:float>"
           }
       ],
       "report": {
           "html": "<enable_html_reporting:bool>",
           "json": "<enable_json_reporting:bool>",
           "junit_xml": "<enable_junit_xml_reporting:bool>"
       },
       "maximum_run_time": "<scenario_max_run_time:float>"
   }

The current release supports UDP frame blasting and stateful TCP (HTTP) flows.
Each type of flow has some *additional* specific parameters as follows:

UDP flow specific parameters
----------------------------

.. code-block:: json

   {
       "frame_size": "<frame_size_without_crc:int>",
       "bitrate": "<flow_bitrate:float>",
       "frame_rate": "<flow_frame_rate:float>",
       "duration": "<flow_duration:float>",
       "number_of_frames": "<number_of_frames:float>",
       "nat_keep_alive": "<activate_nat_keep_alive:bool>",
       "analysis": {
           "latency": "<enable_latency_analysis:bool>",
           "max_loss_percentage": "<max_loss_percentage:float>",
           "max_threshold_latency": "<max_threshold_latency:float>",
           "quantile": "<quantile:float>"
       }
   }

TCP (HTTP) flow specific parameters
-----------------------------------

.. code-block:: json

   {
       "tcp_server_port": "<tcp_server_port_number:int>",
       "tcp_client_port": "<tcp_client_port_number:int>",
       "duration": "<request_duration:float>",
       "request_size": "<request_size:float>",
       "maximum_bitrate": "<maximum_bitrate:float>",
       "receive_window_scaling": "<receive_window_scaling:int>",
       "slow_start_threshold": "<slow_start_threshold:int>",
       "enable_l4s": "<enable_l4s:bool>"
   }

JSON schema
===========

.. The :download: role always *copies* the file to a hashed directory.
.. :download:`Configuration file JSON schema<../json/cli-config-schema.json>`.
..
.. So we use a standard hyperlink instead.
..
.. This requires ``'json'`` in the list of ``html_extra_path``
.. in the Sphinx config file:
.. See also: https://stackoverflow.com/a/64704941
.. and: https://stackoverflow.com/a/70169322

The complete structure and documentation of the file is available
in `Configuration file JSON schema <../json/cli-config-schema.json>`_
and documented below.

.. jsonschema:: ../extra/byteblower-test-framework/json/cli-config-schema.json
   :lift_title: True
   :lift_definitions:
   :auto_target:
   :auto_reference:
