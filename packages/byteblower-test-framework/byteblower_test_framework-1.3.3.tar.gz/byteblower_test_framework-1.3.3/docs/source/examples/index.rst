========
Examples
========

These test examples outline comprehensive test scenarios that can be run using
the ByteBlower Test Framework. A test is designed to assess the performance
and robustness of networks, incorporating both `Stateless`_ UDP-based
(*frame blasting*) and `Stateful`_ TCP-based (*HTTP*) flows.

.. _Stateless: https://support.excentis.com/knowledge/article/85
.. _Stateful: https://support.excentis.com/knowledge/article/86

This configuration is tailored to simulate realistic traffic patterns between
a typical service provider (NSI) and customer premise equipment (CPE), and
measuring key network metrics. This test is particularly valuable for Internet
Service Providers (ISPs), network equipment manufacturers, and large
organizations with intricate network infrastructures that demand very low
latency and high levels of reliability and speed.

A test scenario is versatile and can be employed to:

- *Validate Quality of Service (QoS) and Quality of Experience (QoE)*: It
  helps in ensuring that the network can handle varied types of traffic with
  specific quality requirements, which is crucial for service providers aiming
  to guarantee service level agreements (SLAs).

- *Benchmark Network Performance*: By testing with different frame sizes,
  rates, and protocols, network administrators can understand the performance
  boundaries of their networks and identify potential bottlenecks.

- *Simulate Real-World Traffic*: The configuration allows for simulating
  different types of traffic (e.g., UDP-based, HTTP), thereby providing
  insights into how a network would perform under typical or peak usage
  conditions.

- *Network Optimization and Planning*: The detailed analysis and reporting
  enable network engineers to make data-driven decisions for capacity planning
  and network optimization.

- *Troubleshooting and Diagnostics*: By highlighting packet loss, latency
  issues, and the behavior of the network under high load, the tests can
  pinpoint issues that need to be addressed to prevent future outages or
  performance degradation.

Our example test scenarios give you a quick-start to run your own tests.
Each example provides to detailed guidelines on how to use them,
what results to expect, and how to interpret these results.

Ready to start? You need only to choose which example to go with!

.. toctree::
   :maxdepth: 1

   Basic <basic>
   L4S <l4s>

.. ! FIXME: Putting ``tags`` *before* ``toctree`` messes up
.. !        the tracking in the navigation sidebar

.. tags:: Introduction
