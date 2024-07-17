**********************
Command-line interface
**********************

Installation
============

The installation of the TR-398 Airtime Fairness test case and its
command-line interface is described in :doc:`../quick_start`.

Define Test Scenario
====================

To run the ByteBlower TR-398 Airtime Fairness test case, you need to define
a traffic test scenario. This is stored in a file in ``JSON`` format.

Either start from our basic example.

Copy it to your working directory as ``tr_398.json``:

- Using `ByteBlower Endpoint <../json/airtime-fairness/endpoint/tr_398.json>`_

.. include:: ../_include/_example_test_scenario.rst

Or create your own:

Take a look at :doc:`../config/index` for all detailed information about
describing a traffic test scenario.

Usage
=====

The traffic test scenario can be run via command-line interface, either as
a script or Python module.

Prepare Python virtual environment
----------------------------------

Make sure that you have *activated* your virtual environment before using
the command-line interface.

#. Go to the directory where you installed byteblower-test-cases-tr-398
   in its virtual environment.
#. *Activate* your virtual environment

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

      .. code-block:: shell

         cd ".\my-byteblower-workspace"
         & ".\.venv\Scripts\activate.ps1"

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      .. code-block:: shell

         cd ./my-byteblower-workspace
         . ./.venv/bin/activate

Show command-line help
----------------------

To get help for the command-line arguments:

.. tabs::

   .. group-tab:: As a command-line script

      .. code-block:: shell

         byteblower-test-cases-tr-398-airtime-fairness --help

   .. group-tab:: As a Python module

      .. code-block:: shell

         python -m byteblower.test_cases.tr_398 --help

Run a test with default input/output parameters
-----------------------------------------------

.. tabs::

   .. group-tab:: As a command-line script

      .. code-block:: shell

         byteblower-test-cases-tr-398-airtime-fairness

   .. group-tab:: As a Python module

      .. code-block:: shell

         python -m byteblower.test_cases.tr_398

The command-line interface has the following default parameters:

Configuration file
   ``tr_398.json``

Configuration file search path
   ``.`` (*current directory*)

Report file path
   ``.`` (*current directory*)

This means that, by default:

- The *configuration file* (``tr_398.json``) will be loaded
  from the *current directory*
- The resulting reports will also be saved into the *current directory*.

Run a test with given input/output parameters
---------------------------------------------

Create a subdirectory ``reports`` to store the output report files:

.. tabs::

   .. group-tab:: Windows

      On Windows systems using PowerShell:

      .. code-block:: shell

         # Create reports folder to store HTML/JSON files
         md reports

   .. group-tab:: Linux and macOS

      On Unix-based systems (Linux, WSL, macOS):

      .. code-block:: shell

         # Create reports folder to store HTML/JSON files
         mkdir reports

- Specify a different *config file*
- Specify the subdirectory to *store the reports* to

.. note::

   * When the *config file* is an absolute path to the file, then the
     *config path* (``--config-path <config_path>``) is ignored.

.. tabs::

   .. group-tab:: As a command-line script

      .. code-block:: shell

         byteblower-test-cases-tr-398-airtime-fairness --config-file my_test_config.json --report-path reports

   .. group-tab:: As a Python module

      .. code-block:: shell

         python -m byteblower.test_cases.tr_398 --config-file my_test_config.json --report-path reports

Define your own test scenario
=============================

Have a look at :doc:`../config/index` for a complete overview of the
configuration format.
