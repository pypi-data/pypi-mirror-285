.. ! NOTE: This file is intended to be included by other documents !

.. ! Relative path for include of the json doesn't work when this file is
.. ! included from documents in different folder levels !

.. Use one of these example scenarios to get started.
.. Copy it to your working directory as ``byteblower_test_framework.json``:

.. - Using `ByteBlower Ports <../json/port/byteblower_test_framework.json>`_
.. - Using `ByteBlower Endpoint <../json/endpoint/byteblower_test_framework.json>`_

.. note::
   Make sure to update the example configuration to your actual test setup:

   - ByteBlower server host name or IP: ``server`` entry
   - ByteBlower Port configuration: ``interface`` and ``ipv4`` / ``ipv6`` /
     ``gateway`` / ``netmask`` / ``nat`` entries.

   and for the Endpoint example, also change:

   - Meeting Point host name or IP: ``meeting_point`` entry
   - ByteBlower Endpoint configuration: ``uuid`` and ``ipv4`` / ``ipv6``
     entries.
