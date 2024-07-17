==========================
Installation & Quick start
==========================

.. tags:: Introduction

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

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

      .. code-block:: shell

         py --list

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      *Use your distribution-specific tools to list
      the available Python versions.*

If no Python version is in the required range, you can download and install
Python 3.7 or above using your system package manager
or from https://www.python.org/ftp/python.

Prepare Python virtual environment: Create the virtual environment
and install/update ``pip`` and ``build``.

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

         .. note::
            On Microsoft Windows, it may be required to enable the
            Activate.ps1 script by setting the execution policy for the user.
            You can do this by issuing the following PowerShell command:

         .. code-block:: shell

            PS C:> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

         See `About Execution Policies`_ for more information.

         .. _About Execution Policies: https://go.microsoft.com/fwlink/?LinkID=135170

      Make sure to specify the Python version you're using.
      For example, for Python 3.8:

      .. code-block:: shell

         py -3.8 -m venv --clear .venv
         & ".\.venv\Scripts\activate.ps1"
         python -m pip install -U pip build

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      .. note::
         *Mind the leading* ``.`` *which means* **sourcing**
         ``./.venv/bin/activate``.

      .. code-block:: shell

         python3 -m venv --clear .venv
         . ./.venv/bin/activate
         pip install -U pip build

Install the ByteBlower Test Framework
-------------------------------------

First make sure that you have *activated* your virtual environment:

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

      .. code-block:: shell

         & ".\.venv\Scripts\activate.ps1"

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      .. code-block:: shell

         . ./.venv/bin/activate

Now install (or update) the ByteBlower Test Framework:

.. code-block:: shell

   pip install -U byteblower-test-framework

The ByteBlower Test Framework and its dependencieswill now be installed
from `PyPI`_.

.. _PyPI: https://pypi.org/project/byteblower-test-framework/

Example test scenario
=====================

To run your test using the command-line interface, define your test scenario
in a file in ``JSON`` format.

Use one of these example scenarios to get started.
Copy it to your working directory as ``byteblower_test_framework.json``:

- `Test scenario for ByteBlower Ports <json/port/byteblower_test_framework.json>`_
- `Test scenario for ByteBlower Endpoint <json/endpoint/byteblower_test_framework.json>`_

.. include:: _include/_example_test_scenario.rst

Run a test
==========

The traffic test scenario can be run via command-line interface (either as
a script or Python module), or integrated in your own Python script.

Command-line interface
----------------------

Run a test with default input/output parameters

.. tabs::

   .. group-tab:: As a command-line script

      .. code-block:: shell

         byteblower-test-framework

   .. group-tab:: As a Python module

      .. code-block:: shell

         python -m byteblower_test_framework

By default:

- The *configuration file* (``byteblower_test_framework.json``) will be loaded
  from the *current directory*.
- The resulting reports will also be saved into the *current directory*.

Take a look here for more details on using the :doc:`cli/index`.

From Python
-----------

The ByteBlower test framework can also be imported and used in Python
as follows:

.. code-block:: python

   from byteblower_test_framework import run

   # Show documentation
   help(run)

   # Defining test configuration, report path and report file name prefix:

   # Here you provide your test setup (ByteBlower server, ports, flows, ...),
   # or load it from a JSON file
   test_config = {}

   # Optional: provide the path to the output folder, defaults to the current
   # working directory
   report_path = 'my-output-folder'

   # Optional: provide prefix of the output files, defaults to 'report'
   report_prefix = 'my-dut-feature-test'

   # Run the traffic test:
   run(test_config, report_path=report_path, report_prefix=report_prefix)

Define your own test scenario
=============================

Congratulations! You just ran your first traffic tests.

You want to define your own test scenarios? Great!

Have a look at :doc:`config/index` for a complete overview of the
configuration format.
