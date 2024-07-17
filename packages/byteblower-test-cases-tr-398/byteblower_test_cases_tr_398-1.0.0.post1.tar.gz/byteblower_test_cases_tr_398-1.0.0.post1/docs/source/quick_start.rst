**************************
Installation & Quick start
**************************

Installation
============

Requirements
------------

* `ByteBlower Test Framework`_: ByteBlower |registered| is a traffic
  generator/analyser system for TCP/IP networks.
* Highcharts-excentis_: Used for generating graphs
* jinja2_: To create HTML reports

.. _ByteBlower Test Framework: https://pypi.org/project/byteblower-test-framework/.
.. _Highcharts-excentis: https://pypi.org/project/highcharts-excentis/
.. |registered| unicode:: U+00AE .. registered sign
.. _jinja2: https://pypi.org/project/Jinja2/

Prepare runtime environment
---------------------------

Python
^^^^^^

The ByteBlower Test Framework currently supports Python versions >= 3.7.

We recommend managing the runtime environment in a Python virtual
environment. This guarantees proper separation of the system-wide
installed Python and pip packages.

Important: Working directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the following sections expect that you first moved to your working
directory where you want to run this project. You may also want to create
your configuration files under a sub-directory of your choice.

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

      .. code-block:: shell

         cd 'c:\path\to\working\directory'

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      .. code-block:: shell

         cd '/path/to/working/directory'

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
or from https://www.python.org/downloads/.

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

            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

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

Install the ByteBlower TR-398 Airtime Fairness Test Case
--------------------------------------------------------

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

Then install (or update) the TR-398 Airtime Fairness test case
and its dependencies:

.. code-block:: shell

   pip install -U byteblower-test-cases-tr-398

The latest version from the TR-398 Airtime Fairness test case and its
dependencies will now be installed from `PyPI`_.

.. _PyPI: https://pypi.org/project/byteblower-test-cases-tr-398/

Example test scenario
=====================

To run your test using the command-line interface, define your test scenario
in a file in ``JSON`` format.

Use the example scenario to get started.
Copy it to your working directory as ``tr_398.json``:

- Using `ByteBlower Endpoint <json/airtime-fairness/endpoint/tr_398.json>`_

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

         byteblower-test-cases-tr-398-airtime-fairness

   .. group-tab:: As a Python module

      .. code-block:: shell

         python -m byteblower.test_cases.tr_398

By default:

- The *configuration file* (``tr_398.json``) will be loaded
  from the *current directory*.
- The resulting reports will also be saved into the *current directory*.

Take a look here for more details on using the :doc:`cli/index`.

From Python
-----------

The TR-398 Airtime Fairness test case can also be imported and used in Python
as follows:

.. code-block:: python

   from byteblower.test_cases.tr_398.airtime_fairness import run

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

   # Run the TR-398 Airtime Fairness test:
   run(test_config, report_path=report_path, report_prefix=report_prefix)

Define your own test scenario
=============================

Congratulations! You just ran your first traffic tests.

You want to define your own test scenarios? Great!

Have a look at :doc:`config/index` for a complete overview of the
configuration format.
