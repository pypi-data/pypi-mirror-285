********
Overview
********

Introduction
============

This test case is an implementation of the  `TR-398`_ `Airtime Fairness Test`_ test using
ByteBlower Test Framework.

TR-398 provides a set of performance test cases
with pass/fail requirements for 802.11n/ac/ax
implementations according to Institute of Electrical and Electronics Engineers
(IEEE) specification 802.11.

The primary goal of TR-398 is to provide a standard set of test cases
and framework to measure aspect of the performance between Access Point,
one or more reference Stations and if applicable, one Wi-Fi repeater, under 
controlled laboratory conditions.

.. _ByteBlower Test Framework: https://pypi.org/project/byteblower-test-framework/
.. _TR-398: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf
.. _Airtime Fairness Test: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf#page=39&zoom=100,84,750
.. _table of distances definitions: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf#page=28&zoom=100,84,484 
.. _Metrics: https://www.broadband-forum.org/pdfs/tr-398-3-0-0.pdf#page=41&zoom=100,84,655

.. footer::
   Copyright |copy| |year| - Excentis NV

.. |copy| unicode:: U+00A9 .. copyright sign
.. |year| date:: %Y


TR-398 Airtime Fairness introduction
====================================

`TR-398`_ `Airtime Fairness Test`_ specifies a test suite designed to analyze and report
on the capabilities of Access Points (APs) (also referred to as Device Under Test DUT). 

Airtime Fairness Test intends to verify the capability
of the access point to guarantee the fairness of airtime usage.

.. figure:: images/airtime_fairness_setup.png
   :width: 50%
   :align: center



This ByteBlower TR-398 Airtime Fairness test case allows you to:

#. Run Airtime Fairness tests based on TR-398 Airtime Fairness Test
#. Collect & Analyse statistics
#. Generate HTML & JSON reports

You know about TR-398 Airtime Fairness and you are thrilled to run the test?
Then you can immediately jump to our :doc:`quick_start`.

End-results must be clear, easy-to-understand, and are intended to be
used for comparison between vendors, please refer to our :ref:`example report <report_example>`.

.. image:: images/html_report_graph.png
   :target: ./examples/index.html#result-highlights

TR-398 Airtime Fairness basic requirements
------------------------------------------

- Wi-Fi device that can run the following configuration:
  802.11n 2.4 GHz, 802.11ac 5 GHz, 802.11ax 2.4 GHz, 802.11ax 5 GHz
- This test requires three stations from which two stations are used
  at the same time.
- One station MUST be running in optimum configuration.
- The second station MUST be able to vary between optimum configuration,
  weaker signal, and legacy mode configurations.
- Each station should have the ByteBlower Endpoint installed
  and connected to the ByteBlower MeetingPoint.
- ByteBlower Test Framework for traffic generation: TCP and UDP traffic is required
  throughout the test to measure different throughput values defined in  `Airtime Fairness Test`_.
- Statement of performance MUST include:
  
   #. Maximum measured TCP throughput for each station
   #. Maximum measured UDP throughput of each station under the specified UDP rates
   

TR-398 Airtime Fairness Test
----------------------------

The algorithm proceeds as follows:

- The test consists of four different DUT configuration, for each configuration there are
  three different setups:
  (STA1 and STA2 at close distance)
  (STA1 and STA2 at medium distance)
  (STA1 and STA3 at close distance)
  the distances are according to the `table of distances definitions`_ in the TR-398 Technical report

- In each setup, TCP traffic is used to determine maximum capacity
  of each station running by itself.

- UDP traffic is created on STA1 to run at 75% of the TCP throughput 

- UDP traffic is created on the second station 
  at 50% of the TCP throughput for that station. 

- The two UDP flows run simultaneously. This overdrives the AP and causes it to drop frames

- The pass/fail criteria are that
  each station gets at least 45% of the TCP throughput 
  when both stations are running the prescribed UDP traffic
  and that the summation of the UDP Throughput values for each station is larger than
  the expected throughput values defined in the TR-398 Airtime Fairness test `Metrics`_

Runtime overview
================

TR-398 Airtime Fairness test script execution flow goes through different stages 

#. Initialization

   This phase begins by importing the setup configuration from the
   :ref:`configuration file <config_file_example>`.

   Then, we proceed to two levels of validation:

   - Input validation: Validate the provided configuration for any eventual
     errors.
     For example, missing required parameters, incorrect parameter values,
     interfaces with IPv4 addresses and gateways in different subnets, etc.
   - Setup validation: This step aims to ensure that no problem arises
     when applying the provided configuration on the test network.
     For example, unreachable ByteBlower server,
     wrong ByteBlower interface name,
     ByteBlower Endpoint not registered on MeetingPoint, ...


#. Run TR-398 Airtime Fairness test

   After validating and initializing the testing network, we proceed to
   the TR-398 Airtime Fairness test for each DUT configuration.
   User is instructed to perform the required tasks defined in TR-398 Airtime Fairness
   to test the different setups and configurations.

   In case of errors that may occur during runtime, the script proceeds to the next setup
   or DUT configuration (depending on the error). The different fields in the report 
   are filled with null values for the setup that failed.

#. Export Results

   Two file formats are used to export recorded results: ``JSON`` and ``HTML``.
   These files include:

   - :ref:`Test results <report_example>` of each DUT configuration and station setup
     (TCP maximum throughput, UDP expected throughput, UDP measured throughput, ...)
   - Failure causes and error logs