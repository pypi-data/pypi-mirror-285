****************************
Example: Airtime Fairness
****************************


Test Scenario Definition
========================

This test scenario is designed to test the AP capabilities 
to guarantee the fairness of airtime usage under different setups and configurations.

The configuration for this scenario includes two types of traffic:

- *Basic TCP Flow*: Used to calculate the maximum throughput of each station  
- *Basic UDP Flow*: Two downstream flows running simultaneously for 120 seconds to test
  how the AP behaves

A traffic pattern is running one TCP flow for each station separately 
then running two simultaneous downstream UDP flows.

Throughout the testing period, we run a traffic pattern
for each setting and DUT configuration.

Before these flows are initiated, the user is instructed to perform different actions
(change stations, move stations or change the DUT configuration).

A detailed analysis of the changes effects on the throughput is generated.

Run a test
==========

The traffic test scenario can be run via command-line interface.
You can use the following steps:

#. Create a working directory and (preferably) a Python virtual environment
   within.
#. Activate the virtual environment and install the ByteBlower Test Case.
#. Copy the example files into your working directory:

   - `Test scenario for ByteBlower Endpoint <../json/airtime-fairness/endpoint/tr_398.json>`_

#. Update the example file to your own test setup (ByteBlower server,
   ByteBlower meeting point, port/endpoint configuration, etc.)
#. Run the test from your working directory using the command line interface:

   .. tabs::

      .. group-tab:: As a command-line script

         .. code-block:: shell

            byteblower-test-cases-tr-398-airtime-fairness

      .. group-tab:: As a Python module

         .. code-block:: shell

            python -m byteblower.test-cases-tr-398-airtime-fairness

More details regarding these steps are given in :doc:`../quick_start`.


.. _report_example:

Result highlights
=================
.. _TR-398: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf
.. _Airtime Fairness Test: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf#page=39&zoom=100,84,750

HTML report
-----------


Test Result
^^^^^^^^^^^
The HTML report begins with the test result. The FAIL status
appears when at least one of the pass/fail criteria parameters is not met.

.. image:: ../images/html_report_pass_fail.png

Results Summary
^^^^^^^^^^^^^^^
The results of the test are displayed per DUT configuration. 
Each DUT configuration has a summary table and three histogram graphs for each station setup

#. The summary table shows the different throughput values of each station and for the combined
   stations used in each setup to determine the AP capability to guarantee the fairness of airtime usage.
   
   .. image:: ../images/html_report_table.png
   
   - **TCP Max Throughput**: Maximum TCP throughput measured on each station,
     calculated to determine the maximum capacity of the station
   - **UDP Transmitted Throughput**: The configured UDP throughput for each station
     determined by `TR-398`_ `Airtime Fairness Test`_.
     (75% of TCP Max Throughput for STA1 and 50% of TCP Max Throughput for STA2)
   - **UDP Measured Throughput**: UDP throughput calculated on each station.
     For the two stations together it is the summation of the UDP throughput values 
     of the two stations.
   - **UDP Expected Throughput**: 45% of the UDP Measured Throughput on each station.
     For the two stations together it is a value defined  
     in the `TR-398`_ `Airtime Fairness Test`_ technical report
   - **Result**: PASS if the UDP Measured Throughput is larger than UDP Expected Throughput.
     (The icon is a hyperlink that redirects the user to the corresponding graph)
       

#. The histogram graphs displays a comparison between the different throughput values
   for the different station, the test status and the failure cause if there is one.

   .. image:: ../images/html_report_graph.png


JSON result file
----------------

The JSON report consists of sections, one for each DUT configuration. 
The overall test result is available in field ``status`` with the overall pass/fail status
in the ``passed`` field.

.. code-block:: json
    
    {
        "status": {
            "passed": false
            }
    }

Each of the DUT configuration sections has two parts:

DUT and STA's Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^
As defined in the `TR-398`_ `Airtime Fairness Test`_ technical report.

.. code-block:: json

    {
        "802.11n 2.4 GHz": {
            "mode": "802.11n",
            "frequency_band": "2.4 GHz",
            "nss": 2,
            "sta_mode": {
                "STA1": "802.11n",
                "STA2": "802.11n",
                "STA3": "802.11b/g"
            }
        }
    }



Test Setups Values and Status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Each DUT configuration have three test setups, each test setup consist of  ``results``
and  ``status``.

.. code-block:: json

    {
        "sta2-short_distance": {
            "results": {
                "expected_throughput": 100000000.0,
                "sta1_throughput_max_dl": 226279604.9125262797,
                "sta2_throughput_max_dl": 515250828.6235678792,
                "sta1_udp_transmission_rate": 169713670.4964444041,
                "sta1_throughput": 170803247.0876604021,
                "sta2_udp_transmission_rate": 257627920.6047901809,
                "sta2_throughput": 261004010.0360625386
            },
            "status": {
                "sta1_throughput_max_dl": {
                    "passed": true
                },
                "sta2_throughput_max_dl": {
                    "passed": true
                },
                "total_throughput": {
                    "passed": true
                },
                "passed": true
            }
        }
    }

The ``results`` field consists of throughput (bps) values calculated throughout the test.

- ``expected_throughput``: Value defined in the `TR-398`_ `Airtime Fairness Test`_ technical report
- ``sta1_throughput_max_dl``: Maximum TCP throughput measured on STA1
- ``sta2_throughput_max_dl``: Maximum TCP throughput measured on STA2
- ``sta1_udp_transmission_rate``: Configured UDP rate for STA1, 75% of TCP Max Throughput ``sta1_throughput_max_dl`` for STA1
- ``sta1_throughput``: UDP throughput calculated on STA1
- ``sta2_udp_transmission_rate``: Configured UDP rate for STA2, 50% of TCP Max Throughput ``sta2_throughput_max_dl`` for STA2
- ``sta2_throughput``: UDP throughput calculated on STA2

The ``status`` field shows the result of every pass/fail criteria and the overall status of the setup ``passed``.

- ``sta1_throughput_max_dl`` passes if ``sta1_throughput`` is larger than 45% of ``sta1_throughput_max_dl``
- ``sta2_throughput_max_dl`` passes if ``sta2_throughput`` is larger than 45% of ``sta2_throughput_max_dl``
- ``total_throughput`` passes if the summation of ``sta1_throughput`` and ``sta2_throughput`` is larger than  ``expected_throughput``

In case of errors that may occur during runtime, the script proceeds to the next setup
or DUT configuration (depending on the error).
(The whole DUT configuration is skipped if there was an error calculating 
``sta1_throughput_max_dl``) 
The different throughput fields are filled with ``null`` values  
and the ``status`` field shows an ``error_log`` field instead.

.. code-block:: json

    {
        "sta2-medium_distance": {
           "results": {
                    "expected_throughput": 335000000.0,
                    "sta1_throughput_max_dl": null,
                    "sta2_throughput_max_dl": null,
                    "sta1_udp_transmission_rate": null,
                    "sta1_throughput": null,
                    "sta2_udp_transmission_rate": null,
                    "sta2_throughput": null
            },
           "status": {
                    "passed": false,
                    "error_log": "No packets where received on STA: STA1 while running UDP traffic for setup: sta3-short_distance"
                }
            }
    }