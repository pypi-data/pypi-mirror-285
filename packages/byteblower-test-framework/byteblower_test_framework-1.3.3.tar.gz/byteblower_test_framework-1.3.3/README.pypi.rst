*************************
ByteBlower Test Framework
*************************

  An easy accessible library of basic test flows and reporting engines.

.. footer::
   Copyright |copy| |year| - Excentis N.V.

.. |registered| unicode:: U+00AE .. registered sign
.. |copy| unicode:: U+00A9 .. copyright sign
.. |year| date:: %Y

ByteBlower |registered| is a traffic generator/analyzer system
for TCP/IP networks.

This library provides you with the building blocks for:

#. Generating test traffic
#. Collect statistics
#. Analyze traffic statistics
#. Generate reports

Quick start guide
=================

Get started right away? Have a look at our `Installation & Quick start`_ guide.

.. _Installation & Quick start: https://api.byteblower.com/test-framework/latest/byteblower-test-framework/quick_start.html

Release notes
=============

What can this version bring to you?
See our exciting new and existing features below!

.. _Command-line interface: https://api.byteblower.com/test-framework/latest/byteblower-test-framework/cli/index.html
.. _Versioning: https://api.byteblower.com/test-framework/latest/byteblower-test-framework/versioning.html
.. _ByteBlower Endpoint: https://www.excentis.com/products/byteblower-endpoint/

**Note**: *Have a look at our* Versioning_ *for more information about
how releases are handled for the ByteBlower Test Framework*.

✨ **Test Cases** ✨
--------------------

The ByteBlower Test Framework serves as the base for many of our customer's
test cases.

At Excentis, we also develop common test cases and love to
share them with the community.

- `Test Case: TR-398`_

  - Guided `TR-398`_ Wi-Fi 802.11n/ac/ax performance validation tests

- `Test Case: RFC 2544 Throughput`_

  - Run an `RFC 2544`_ network performance test with ease!

- `Test Case: Low Latency`_

  - Run low latency validation tests on your network.

.. _Test Case\: TR-398: https://api.byteblower.com/test-framework/latest/test-cases/tr-398/overview.html
.. _TR-398: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf
.. _Test Case\: RFC 2544 Throughput: https://api.byteblower.com/test-framework/latest/test-cases/rfc-2544/overview.html
.. _Test Case\: Low Latency: https://api.byteblower.com/test-framework/latest/test-cases/low-latency/overview.html
.. _RFC 2544: https://datatracker.ietf.org/doc/html/rfc2544
.. _Low Latency, Low Loss, and Scalable Throughput (L4S): https://datatracker.ietf.org/doc/html/rfc9330

📢 **New since v1.3.0!** 📢
---------------------------

It is with great pleasure that we announce our
new features of the ByteBlower Test Framework!

- Support for `Low Latency, Low Loss, and Scalable Throughput (L4S)`_ on TCP

  - Run traffic tests on your L4S-enabled network!

- HTTP Flows: Including **TCP results over time** in the reports

  - Transmitted and received number of bytes
  - Average throughput over time
  - Round Trip Time (``RTT``)
  - Number of TCP retransmissions
  - ECN Congestion Experienced (``CE``) notification
    (*for L4S-enabled TCP flows*)

Features
--------

- Quick and easy automation of traffic tests using ByteBlower
- Straightforward building blocks for your own test scripts

  - Grouped in self-explaining categories
  - Designed with a small 😉 to the workflow you are used to from the GUI

- `Command-line interface`_

  - Run traffic tests with nothing more than a JSON configuration file!

- Supported ByteBlower endpoint types

  - ByteBlower Port (on a physical interface of a ByteBlower server)
  - `ByteBlower Endpoint`_ (mobile testing via app on your device)

- Endpoint configuration

  - IPv4

    - DHCP and manual address configuration (*ByteBlower Port only*)
    - Automatic handling of endpoints located behind a NAT/NAPT gateway!

  - IPv6

    - DHCPv6 and SLAAC address configuration (*ByteBlower Port only*)
    - ByteBlower Endpoint: Automatic resolving of Endpoint host's IPv6 address
      for each traffic flow.

- Traffic types

  - Stateless: frame blasting (UDP-based)
  - Stateful: HTTP (TCP-based)
  - Define IP Traffic class: DSCP & ECN

    - TCP Prague for `Low Latency, Low Loss, and Scalable Throughput (L4S)`_

- Application simulations

  - Voice over IP (VoIP) using the G.711 codec
  - Traditional gaming (*ByteBlower Endpoint only as destination*)
  - Video streaming (Netflix, YouTube, ...) (*ByteBlower Port only*)

- Standard analysis

  - Frame count: transmitted and received over time, frame loss and byte loss
  - Latency: Minimum, maximum, average and jitter over time
  - TCP

    - Average goodput on HTTP (layer 5)
    - Transmitted and received Bytes over time
    - TCP average throughput over time
    - Minimum, maximum and average Round Trip Time (``RTT``)
    - TCP Retransmission counts
    - ECN *Congestion Experienced* (``CE``) markings
      (*for L4S-enabled TCP flows*)

  - Aggregation of results over multiple flows
    (*frame blasting only*)
  - PASS/FAIL criteria can be provided to match your KPIs

- Application-specific analysis

  - Mean Opinion Score (``MOS``): Specific for Voice flows
  - Video buffer analysis: Specific for Video flows (*ByteBlower Port only*)

- Reporting

  - Summary *and* realtime results
  - HTML: Neat to share with your chief, customers, vendors, ...

    - Incorporating our brand new style!
    - Interactive charts
    - Includes overview of all latency CCDF results

  - JSON: Allows for machine post-processing
  - XML JUnit: Useful for integration in automation tools

- Helpers

  - Ease-of-use for configuration and/or post-processing
    of the analyzed results

- `Example scripts`_

.. _Example scripts: https://api.byteblower.com/test-framework/index.html#examples

Changelog
---------

For all details, please have a look at our Changelog_.

.. _Changelog: https://api.byteblower.com/test-framework/latest/changelog.html

Requirements
============

* byteblowerll_ (`ByteBlower API`_): Our lower layer API for client-server
  communication (`API documentation <https://api.byteblower.com/python>`_)
* scapy_: Used for frame generation and parsing
* junit-xml_: Used for Unit test report generation
* pandas_: Used for data collection
* highcharts-excentis_: Used for generating graphs
* jinja2_: User for HTML report templating

.. _ByteBlower API: https://setup.byteblower.com/
.. _byteblowerll: https://pypi.org/project/byteblowerll/
.. _scapy: https://pypi.org/project/scapy/
.. _junit-xml: https://pypi.org/project/junit-xml/
.. _pandas: https://pypi.org/project/pandas/
.. _highcharts-excentis: https://pypi.org/project/highcharts-excentis/
.. _jinja2: https://pypi.org/project/Jinja2/

Supported platforms
-------------------

The ByteBlower Test Framework in general supports Python version 3.7 to 3.11.

.. note::
   **NOTE**: *Python >= 3.12 is not yet supported because the ByteBlower API
   libraries are not yet available for Python 3.12* (`byteblowerll`_).

The framework has been tested for the following operating system platforms
and Python versions:

+------------------+----------------------------+----------------+------------------------+
| OS platform      | Distribution               | Python version | source                 |
+==================+============================+================+========================+
| Windows 10       | up to feature release 21H2 | Python 3.10    | `Official Python`_     |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.9     | `Official Python`_     |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.8     | `Official Python`_     |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.7     | `Official Python`_     |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.9     | `Windows Apps`_        |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.8     | `Windows Apps`_        |
+------------------+----------------------------+----------------+------------------------+
| Windows 10       | up to feature release 21H2 | Python 3.7     | `Windows Apps`_        |
+------------------+----------------------------+----------------+------------------------+
| macOS            | up to Monterey             | Python 3.9     | `Official Python`_     |
|                  |                            |                | (**Intel-only!**)      |
+------------------+----------------------------+----------------+------------------------+
| macOS            | up to Monterey             | Python 3.8     | `Official Python`_     |
|                  |                            |                | (**Intel-only!**)      |
+------------------+----------------------------+----------------+------------------------+
| Linux            | Debian 11 (bullseye)       | Python 3.9.2   | `Debian packages`_     |
+------------------+----------------------------+----------------+------------------------+
| Linux            | Debian 10 (buster)         | Python 3.7.3   | `Debian packages`_     |
+------------------+----------------------------+----------------+------------------------+
| Linux            | Ubuntu 20.04 (Focal Fossa) | Python 3.8.2   | `Ubuntu packages`_     |
+------------------+----------------------------+----------------+------------------------+
| Linux            | Ubuntu 22.04 (Focal Fossa) | Python 3.10.4  | `Ubuntu packages`_     |
+------------------+----------------------------+----------------+------------------------+
| Docker           | python:3.10-slim-buster    | Python 3.10.11 | `Docker Python`_       |
+------------------+----------------------------+----------------+------------------------+
| Docker           | python:3.9-slim-buster     | Python 3.9.16  | `Docker Python`_       |
+------------------+----------------------------+----------------+------------------------+
| Docker           | python:3.8-slim-buster     | Python 3.8.16  | `Docker Python`_       |
+------------------+----------------------------+----------------+------------------------+
| Docker           | python:3.7-slim-buster     | Python 3.7.13  | `Docker Python`_       |
+------------------+----------------------------+----------------+------------------------+

.. _Official Python: https://www.python.org
.. _Windows Apps: https://apps.microsoft.com/
.. _Debian packages: https://packages.debian.org/search?suite=all&exact=1&searchon=names&keywords=python3
.. _Ubuntu packages: https://packages.ubuntu.com/search?keywords=python3&searchon=names&exact=1&suite=all&section=all
.. _Docker Python: https://hub.docker.com/_/python

Installation
============

Prepare runtime environment
---------------------------

We recommend managing the runtime environment in a Python virtual
environment. This guarantees proper separation of the system-wide
installed Python and pip packages.

Python virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure to use the right Python version (>= 3.7, <= 3.11),
list all Python versions installed in your machine by running:

#. On Windows systems using PowerShell:

   .. code-block:: shell

      py --list

If no Python version is in the required range, you can download and install
Python 3.7 or above using your system package manager
or from https://www.python.org/ftp/python.

Prepare Python virtual environment: Create the virtual environment
and install/update ``pip`` and ``build``.

#. On Unix-based systems (Linux, WSL, macOS):

   **Note**:
   *Mind the leading* ``.`` *which means* **sourcing** ``./.venv/bin/activate``.

   .. code-block:: shell

      python3 -m venv --clear .venv
      . ./.venv/bin/activate
      pip install -U pip build

#. On Windows systems using PowerShell:

      **Note**: On Microsoft Windows, it may be required to enable the
      Activate.ps1 script by setting the execution policy for the user.
      You can do this by issuing the following PowerShell command:

      .. code-block:: shell

         PS C:> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

      See `About Execution Policies`_ for more information.

   .. code-block:: shell

      py -3.8 -m venv --clear .venv
      & ".\.venv\Scripts\activate.ps1"
      python -m pip install -U pip build

.. _About Execution Policies: https://go.microsoft.com/fwlink/?LinkID=135170

Install the ByteBlower Test Framework from PyPI
-----------------------------------------------

First make sure that your *activated* your virtual environment:

#. On Unix-based systems (Linux, WSL, macOS):

   .. code-block:: shell

      . ./.venv/bin/activate

#. On Windows systems using PowerShell:

   .. code-block:: shell

      & ".\.venv\Scripts\activate.ps1"

Now install (or update) the ByteBlower Test Framework:

.. code-block:: shell

   pip install -U byteblower-test-framework

Documentation
=============

Online usage documentation: `ByteBlower Test Framework documentation`_

.. _ByteBlower Test Framework documentation: https://api.byteblower.com/test-framework/latest/

The API documentation is also always available in the API:

.. code-block:: python

   help(any_api_object)

Some examples:

For classes (and their members):

.. code-block:: python

   from byteblower_test_framework.host import Server
   from byteblower_test_framework.endpoint import IPv4Port
   from byteblower_test_framework.traffic import FrameBlastingFlow

   help(Server)
   help(Server.start)
   help(Server.info)
   help(IPv4Port)
   help(FrameBlastingFlow)

   from byteblower_test_framework.report import ByteBlowerHtmlReport

   help(ByteBlowerHtmlReport)

For objects (and their members):

.. code-block:: python

   from byteblower_test_framework.host import Server

   my_server = Server('byteblower-39.lab.excentis.com.')

   help(my_server)
   help(my_server.start)

Usage
=====

First make sure that your *activated* your virtual environment:

#. On Unix-based systems (Linux, WSL, macOS):

   .. code-block:: shell

      . ./.venv/bin/activate

#. On Windows systems using PowerShell:

   .. code-block:: shell

      & ".\.venv\Scripts\activate.ps1"

Let's give it a test run: Import the test framework and show its
documentation:

.. code-block:: shell

   python

.. code-block:: python

   import byteblower_test_framework
   help(byteblower_test_framework)

This shows you the ByteBlower Test Framework module documentation.

Command-line interface
----------------------

To get help for command line arguments:

#. As a command-line script:

   .. code-block:: shell

      byteblower-test-framework --help

#. As a python module:

   .. code-block:: shell

      python -m byteblower_test_framework --help


For a quick start, you can run a simple test using the JSON configuration of
one of the example files below:

* `Test scenario for ByteBlower Ports <https://api.byteblower.com/test-framework/json/byteblower-test-framework/port/byteblower_test_framework.json>`_
* `Test scenario for ByteBlower Endpoint <https://api.byteblower.com/test-framework/json/byteblower-test-framework/endpoint/byteblower_test_framework.json>`_

Save you configuration in your working directory as
``byteblower_test_framework.json``. Please make sure you change the server and
ports configuration according to the setup you want to run your test on.

The ``byteblower_test_framework.json`` can be used then to run the test in the
command line interface using:

.. code-block:: shell

   byteblower-test-framework

The resulting reports will be saved into the current directory.

To specify a different *config file name* and *report path* using:

.. code-block:: shell

   byteblower-test-framework --config-file path/to/my_test_config.json  --report-path path/to/my_test_reports_directory

You can find more details on how to customize your own configuration file
in `Configuration file`_.

.. _Configuration file: https://api.byteblower.com/test-framework/latest/byteblower-test-framework/config/index.html

.. note::
   **To-do**: *We will provide a quick start guide in the future.*

Development
===========

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Would you like to contribute to this project? You're very welcome! 😊

Please contact us at `ByteBlower Support`_ and we'll be there to guide you.

Support
=======

.. See http://docutils.sourceforge.net/0.4/docs/ref/rst/directives.html#image

If you have any questions or feature request you can contact the ByteBlower
support team using:

|globe|: `Excentis Support Portal`_

|e-mail|: `ByteBlower Support`_

|telephone|: +32 (0) 9 269 22 91

.. e-mail icon:
.. |e-mail| unicode:: U+1F582

.. globe icon:
.. |globe| unicode:: U+1F30D
.. .. |globe| unicode:: U+1F310

.. telephone icon:
.. |telephone| unicode:: U+1F57D

.. ByteBlower logo
.. ! NOTE: ``:height:`` is not required, but added as workaround
..         * for https://github.com/pypa/readme_renderer/issues/304
.. image:: http://static.excentis.com/byteblower_blue_transparent_background.png
   :width: 400
   :height: 131
   :scale: 60
   :align: right
   :alt: ByteBlower
   :target: byteblower_

.. "A product by Excentis" logo
.. ! NOTE: ``:height:`` is not required, but added as workaround
..         * for https://github.com/pypa/readme_renderer/issues/304
.. image:: http://static.excentis.com/Aproductby.png
   :width: 320
   :height: 17
   :scale: 60
   :align: right
   :alt: A product by Excentis
   :target: excentis_

.. _byteblower: https://byteblower.com
.. _excentis: https://www.excentis.com
.. _Excentis Support Portal: https://support.excentis.com
.. _ByteBlower Support: mailto:support.byteblower@excentis.com
