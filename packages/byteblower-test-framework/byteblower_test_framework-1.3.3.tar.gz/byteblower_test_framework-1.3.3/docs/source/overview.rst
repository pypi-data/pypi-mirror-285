:Authors:
   Tom Ghyselinck <tom.ghyselinck@excentis.com>
:Date: 2021/12/10

.. footer::
   Copyright |copy| |year| - Excentis N.V.

.. footer::
   This document was generated on |date| at |time|.

.. |copy| unicode:: 0xA9 .. copyright sign
.. |year| date:: %Y
.. |date| date::
.. |time| date:: %H:%M

========
Overview
========

Command-line interface
======================

.. versionadded:: 1.1.0

We provide a user-friendly interface to the _`building blocks`:
Define and run a traffic test using a simple JSON configuration file.

Have a look at our :doc:`quick_start` to run your first test in no time!

Or jump to the detailed information in :doc:`cli/index` to see more detailed
information about the command-line options.

Example Test Scenarios
======================

You can find examples of test scenarios on :doc:`examples/index`.

Building blocks
===============

The ByteBlower Test Framework provides high-level building blocks for
different traffic test scenarios.

There are three major categories of building blocks:

* Traffic generation
* Traffic analysis
* Reporting

Next to these three, the framework also provides interfaces for ByteBlower
*host management* (ByteBlower Server and Meeting Point), *endpoint management*
(ByteBlower Ports, ByteBlower Endpoints, ...) and more!

.. _test-interface:

Test execution interface
------------------------

The *entrypoint* of the framework: A test Scenario, familiar from the
`ByteBlower GUI`_.

The entrypoint interfaces are defined in
:doc:`reference/byteblower_test_framework.run`.

.. _ByteBlower GUI: https://setup.byteblower.com/software.html#GUI

* :py:class:`~byteblower_test_framework.run.Scenario`

.. _host-management:

Host management
---------------

Connect to the ByteBlower Server or ByteBlower Meeting Point.

These interfaces are more in general called *host of a ByteBlower traffic
endpoint*.

The traffic generator/analyser host interfaces are defined in
:doc:`reference/byteblower_test_framework.host`.

.. .. todo::
..    Chassis management is work in progress.

* :py:class:`~byteblower_test_framework.host.Server`
* :py:class:`~byteblower_test_framework.host.MeetingPoint`

.. _endpoint-management:

Endpoint management
-------------------

Create and manage ByteBlower Ports and ByteBlower endpoints
(more in general called *traffic endpoints*).

The traffic endpoint interfaces are defined in
:doc:`reference/byteblower_test_framework.endpoint`.

* :py:class:`~byteblower_test_framework.endpoint.IPv4Port`
* :py:class:`~byteblower_test_framework.endpoint.NatDiscoveryIPv4Port`
* :py:class:`~byteblower_test_framework.endpoint.IPv6Port`
* :py:class:`~byteblower_test_framework.endpoint.IPv4Endpoint`
* :py:class:`~byteblower_test_framework.endpoint.IPv6Endpoint`

.. _traffic-generation:

Traffic generation
------------------

Define traffic flows between one or more source and destination ports
(traffic endpoints).

Each flow defines a specific type of network traffic with given addresses,
ports and metrics.

The generated traffic can be analysed by one or more
:ref:`analysers <traffic-analysis>`.

.. .. todo::
..    Further document purpose!

The traffic generation interfaces are defined in
:doc:`reference/byteblower_test_framework.traffic`.

.. * :py:class:`~byteblower_test_framework.traffic.Flow` implementations:

We have *basic* flow definitions for:

* UDP:
  :py:class:`~byteblower_test_framework.traffic.FrameBlastingFlow`
* Stateful TCP: :py:class:`~byteblower_test_framework.traffic.HTTPFlow`

Next to standard traffic tests, the framework also provides flows to form the
base of *application simulation*:

* Voice calls:
  :py:class:`~byteblower_test_framework.traffic.VoiceFlow`
* Video streaming:
  :py:class:`~byteblower_test_framework.traffic.VideoFlow`
* (traditional) gaming:
  :py:class:`~byteblower_test_framework.traffic.GamingFlow`

.. todo::
   Document frame generation (factory) interfaces.

.. _traffic-analysis:

Traffic analysis
----------------

Collect and analyse the traffic generated and received by the
:ref:`flows <traffic-generation>`.

An analyser has specific pass/fail criteria which can be fine-tuned
for each test. It is attached to a flow to analyse the traffic generated
and received by that specific flow.

.. note::
   Each analyser has its own right to exist. Most analysers can only be
   applied to a specific type of flow.

.. .. todo::
..    Further document purpose!

The traffic analysis interfaces are defined in
:doc:`reference/byteblower_test_framework.analysis`.

* Analyse frame count over time:
  :py:class:`~byteblower_test_framework.analysis.FrameLossAnalyser`
* Analyse latency and frame count over time:
  :py:class:`~byteblower_test_framework.analysis.LatencyFrameLossAnalyser`
* Analyse latency CDF and total frame count:
  :py:class:`~byteblower_test_framework.analysis.LatencyCDFFrameLossAnalyser`
* Calculate the MOS score of a voice flow:
  :py:class:`~byteblower_test_framework.analysis.VoiceAnalyser`
* Analyse HTTP and TCP statistics over time:
  :py:class:`~byteblower_test_framework.analysis.HttpAnalyser`
* Analyse HTTP and TCP statistics over time, including L4S related
  analysis (IP ECN markings):
  :py:class:`~byteblower_test_framework.analysis.L4SHttpAnalyser`

  .. note::
     Requires an :py:class:`~byteblower_test_framework.traffic.HTTPFlow`
     with TCP Prague enabled.

* Analyse a video buffer over time:
  :py:class:`~byteblower_test_framework.analysis.BufferAnalyser`

.. _reporting:

Reporting
---------

Generate one or more reports to visualize or post-process the
:ref:`analysis <traffic-analysis>`.

The *HTML* reports include interactive charts. The *JSON* reports are very
useful for automated post-processing. The *Unit XML* report finally can be
used to integrate in your favorite test automation platform (for example
Jenkins_, GitLab_, ...) and issue tracking system (for example JIRA_, ...).

.. _Jenkins: https://www.jenkins.io
.. _GitLab: https://www.gitlab.com
.. _JIRA: https://www.atlassian.com/software/jira

.. .. todo::
..    Further document purpose!

The reporting interfaces are defined in
:doc:`reference/byteblower_test_framework.report`.

* HTML reports:
  :py:class:`~byteblower_test_framework.report.ByteBlowerHtmlReport`
* JSON reports:
  :py:class:`~byteblower_test_framework.report.ByteBlowerJsonReport`
* Unit XML report:
  :py:class:`~byteblower_test_framework.report.ByteBlowerUnitTestReport`
