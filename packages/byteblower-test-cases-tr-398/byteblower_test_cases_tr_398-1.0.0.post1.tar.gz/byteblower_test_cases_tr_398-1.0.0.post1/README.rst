****************************
ByteBlower Test Case: TR 398
****************************

Introduction
============

This package contains an implementation of the `TR-398`_
Test using the `ByteBlower Test Framework`_.

.. _ByteBlower Test Framework: https://pypi.org/project/byteblower-test-framework/
.. _TR-398: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf
.. _Airtime Fairness Test: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf#page=39&zoom=100,84,750

.. footer::
   Copyright |copy| |year| - Excentis N.V.

.. |copy| unicode:: U+00A9 .. copyright sign
.. |year| date:: %Y

The primary goal of TR-398 is to provide a standard set of test cases
and framework to measure aspect of the performance between Access Point,
one or more reference Stations and if applicable, one Wi-Fi repeater, under
controlled laboratory conditions.

Release notes
=============

What can this version bring to you?
See our exciting new and existing features below!


📢 **New since v1.0.0!** 📢
---------------------------

It is with great pleasure that we announce our
new features of this test case!

- Support for `TR-398`_ `Airtime Fairness Test`_

TR-398 Airtime Fairness introduction
====================================
Airtime Fairness Test intends to verify the capability
of the access point to guarantee the fairness of airtime usage.

This ByteBlower TR-398 Airtime Fairness test case allows you to:

#. Run Airtime Fairness tests based on TR-398 Airtime Fairness Test
#. Collect & Analyse statistics
#. Generate HTML & JSON reports

For more detailed documentation, please have a look
at `Test Case: TR-398 Airtime Fairness`_ in the ByteBlower API documentation.

.. _Test Case\: TR-398 Airtime Fairness: https://api.byteblower.com/test-framework/latest/test-cases/tr-398/overview.html

Installation
============

Requirements
------------

* `ByteBlower Test Framework`_: ByteBlower |registered| is a traffic
  generator/analyser system for TCP/IP networks.
* Highcharts-excentis_: Used for generating graphs
* jinja2_: To create HTML reports

.. _Highcharts-excentis: https://pypi.org/project/highcharts-excentis/
.. |registered| unicode:: U+00AE .. registered sign
.. _jinja2: https://pypi.org/project/Jinja2/

Prepare runtime environment
---------------------------

We recommend managing the runtime environment in a Python virtual
environment. This guarantees proper separation of the system-wide
installed Python and pip packages.

Python
------

The ByteBlower Test Framework currently supports Python versions 3.7
up to 3.11.

Important: Working directory
----------------------------

All the following sections expect that you first moved to your working
directory where you want to run this project. You may also want to create
your configuration files under a sub-directory of your choice.

#. On Unix-based systems (Linux, WSL, macOS):

   .. code-block:: shell

      cd '/path/to/working/directory'

#. On Windows systems using PowerShell:

   .. code-block:: shell

      cd 'c:\path\to\working\directory'

Python virtual environment
--------------------------

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

   **Note**: *Mind the leading* ``.`` *which means* **sourcing**
   ``./.venv/bin/activate``.

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

   Make sure to specify the python version you're using.
   For example, for Python 3.8:

   .. code-block:: shell

      py -3.8 -m venv --clear .venv
      & ".\.venv\Scripts\activate.ps1"
      python -m pip install -U pip build

   .. _About Execution Policies: https://go.microsoft.com/fwlink/?LinkID=135170

To install the ByteBlower TR-398 test case and
its dependencies, first make sure that you have activated your
virtual environment:

#. On Unix-based systems (Linux, WSL, macOS):

   .. code-block:: shell

      . ./.venv/bin/activate

#. On Windows systems using PowerShell:

   .. code-block:: shell

      ./.venv/Scripts/activate.ps1

Then, run:

.. code-block:: shell

   pip install -U byteblower-test-cases-tr-398

Quick start
===========

Command-line interface
----------------------

After providing the appropriate test setup and frame configurations,
the test script can be run either as python module or as a command-line script.

For example (*to get help for the command-line arguments*):

#. As a python module:

   .. code-block:: shell

      # To get help for the command-line arguments:
      python -m byteblower.test_cases.tr_398 --help

#. As a command-line script:

   .. code-block:: shell

      # To get help for the command-line arguments:
      byteblower-test-cases-tr-398-airtime-fairness --help

To run the ByteBlower TR-398 Airtime Fairness test case,
you should first provide your test configuration file.

you can use the `Configuration file example`_ as a reference. Make sure to
update the example configuration to your actual setup configuration
(ByteBlower server host name or IP, source and destination ports)

``tr_398.json`` is the default configuration file name.
You can use the argument ``--config-file`` to specify your configuration file.


The reports will be stored under a subdirectory ``reports/``.

#. On Unix-based systems (Linux, WSL, macOS):

   .. code-block:: shell

      # Optional: create tr_398.json, then copy the configuration to it
      touch tr_398.json
      # Create reports folder to store HTML/JSON files
      mkdir reports
      # Run test
      byteblower-test-cases-tr-398-airtime-fairness --report-path reports

#. On Windows systems using PowerShell:

   .. code-block:: shell

      # Optional: create tr_398.json, then copy the configuration to it
      New-Item tr_398.json
      # Create reports folder to store HTML/JSON files
      md reports
      # Run test
      byteblower-test-cases-tr-398-airtime-fairness --report-path reports

Integrated
----------

.. code-block:: python

   from byteblower.test_cases.tr_398.airtime_fairness import run

   # Defining test configuration, report path and report file name prefix:
   test_config = {} # Here you should provide your test setup + frame(s') configuration(s)
   report_path = 'my-output-folder' # Optional: provide the path to the output folder, defaults to the current working directory
   report_prefix = 'my-dut-feature-test' # Optional: provide prefix of the output files, defaults to 'report'

   # Run the TR-398 Airtime fairness test:
   run(test_config, report_path=report_path, report_prefix=report_prefix)


Configuration file example
--------------------------

.. code-block:: json

   {
       "server":"byteblower-server.example.com.",
       "meeting_point": "byteblower-meeting-point.example.com.",
       "dut": {
           "name": "DUT",
           "interface": "trunk-1-2",
           "ipv4": "192.168.5.2",
           "netmask": "255.255.255.0",
           "gateway": "192.168.5.254"
       },
       "wlan_stations": [
           {
               "name": "STA1",
               "uuid": "017d7da0-9724-4459-a037-bcec9acf577a",
               "ipv4": true
           },
           {
               "name": "STA2",
               "uuid": "9956866a-03a7-43c8-9cb9-8d3570d8c6a4",
               "ipv4": true
           },
           {
               "name": "STA3",
               "uuid": "4d9a5fdb-32b4-4523-ace9-5972518de13b",
               "ipv4": true
           }
       ]
   }


More detailed documentation is available in the `Configuration file`_ section
of the documentation.

.. _Configuration file: https://api.byteblower.com/test-framework/latest/test-cases/tr-398/config/index.html
