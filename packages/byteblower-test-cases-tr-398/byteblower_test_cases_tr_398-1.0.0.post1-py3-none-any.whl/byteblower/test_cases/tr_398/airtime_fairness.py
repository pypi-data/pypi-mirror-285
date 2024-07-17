import logging
from datetime import timedelta  # for type hinting
from datetime import datetime
from os import getcwd
from os.path import join
from time import sleep
from typing import List, Optional, Tuple  # for type hinting

from byteblower_test_framework.analysis import FrameLossAnalyser, HttpAnalyser
from byteblower_test_framework.endpoint import IPv4Endpoint, IPv4Port
from byteblower_test_framework.factory import create_frame
from byteblower_test_framework.host import MeetingPoint, Server
from byteblower_test_framework.run import Scenario
from byteblower_test_framework.traffic import Flow  # for type hinting
from byteblower_test_framework.traffic import FrameBlastingFlow, HTTPFlow
from pandas import Timestamp  # for type hinting

from ._endpoint_factory import initialize_endpoint
from ._port_factory import initialize_port
from .definitions import BITS_PER_BYTE
from .exceptions import NoPacketsReceived
from .report_generator import html_report_generator, json_report_generator

# TR-398 Airtime Fairness wireless devices configuration
tr_config = [{
    "mode": "802.11n",
    "frequency_band": "2.4 GHz",
    "nss": 2,
    "sta_mode": {
        "STA1": "802.11n",
        "STA2": "802.11n",
        "STA3": "802.11b/g"
    },
    "expected_throughput": {
        "throughput1": 100 * 1e6,
        "throughput2": 100 * 1e6,
        "throughput3": 60 * 1e6
    }
}, {
    "mode": "802.11ac",
    "frequency_band": "5 GHz",
    "nss": 2,
    "sta_mode": {
        "STA1": "802.11n",
        "STA2": "802.11n",
        "STA3": "802.11a"
    },
    "expected_throughput": {
        "throughput1": 650 * 1e6,
        "throughput2": 550 * 1e6,
        "throughput3": 335 * 1e6
    }
}, {
    "mode": "802.11ax",
    "frequency_band": "2.4 GHz",
    "nss": 2,
    "sta_mode": {
        "STA1": "802.11n",
        "STA2": "802.11n",
        "STA3": "802.11n"
    },
    "expected_throughput": {
        "throughput1": 190 * 1e6,
        "throughput2": 130 * 1e6,
        "throughput3": 95 * 1e6
    }
}, {
    "mode": "802.11ax",
    "frequency_band": "5 GHz",
    "nss": 2,
    "sta_mode": {
        "STA1": "802.11n",
        "STA2": "802.11n",
        "STA3": "802.11ac"
    },
    "expected_throughput": {
        "throughput1": 900 * 1e6,
        "throughput2": 750 * 1e6,
        "throughput3": 600 * 1e6
    }
}]


def run(test_config: dict, report_path: str, report_prefix: str) -> None:
    """TR-398 Airtime Fairness test for a set of frame configurations.

    :param test_config: ByteBlower setup configuration parameters for the TR-398
       Airtime Fairness
    :type test_config: dict
    :param report_path: Path where to store the report files
    :type report_path: str
    :param report_prefix: Prefix of the report files
    :type report_prefix: str
    """
    server_name = test_config['server']
    meeting_point_name = test_config['meeting_point']

    server = Server(server_name)
    meeting_point = MeetingPoint(meeting_point_name)
    dut_config = test_config['dut']
    dut = initialize_port(server, dut_config)
    stations = [
        initialize_endpoint(meeting_point, station_config)
        for station_config in test_config['wlan_stations']
    ]
    sta1, sta2, sta3 = stations
    test_results = {}
    overall_test_status = True
    for config in tr_config:
        dut_mode = config['mode']
        frequency_band = config['frequency_band']
        nss = config['nss']
        sta_mode = config['sta_mode']
        expected_throughput = config.pop('expected_throughput')
        test_setups = {}
        report_with_config = {**config}
        result_index = f'{dut_mode} {frequency_band}'
        setup_name1 = "sta2-short_distance"
        setup_name2 = "sta2-medium_distance"
        setup_name3 = "sta3-short_distance"
        expected_tp1 = expected_throughput['throughput1']
        expected_tp2 = expected_throughput['throughput2']
        expected_tp3 = expected_throughput['throughput3']
        print(
            f"Configuring devices for: {dut_mode} - {frequency_band} - NSS={nss}"
        )
        print("Set the DUT Configuration:")
        print(f"- Mode: {dut_mode}")
        print(f"- Frequency Band: {frequency_band}")
        print(f"- NSS: {nss}")
        print("Set the STA Configuration:")
        for sta, sta_mode in sta_mode.items():
            print(f"- {sta}: {sta_mode}")

        # Setup 1
        print("Associate STA1 and STA2 with DUT")

        # Prompt user to confirm configuration
        input(
            "Press Enter when the devices are correctly configured to resume the test"
        )

        # Establish the LAN connection and wait for 10 seconds
        print("Waiting 10 seconds")
        sleep(10)

        # Measure the achievable downlink TCP throughput through STA1
        tcp_dl_sta1, tcp_dl_sta1_analyser = _configure_tcp_traffic(
            setup_name1, dut, sta1)
        _run_traffic([tcp_dl_sta1])

        sta1_data_rate = None
        try:
            # Record the value
            sta1_throughput_max_dl_1 = _calculate_tcp_throughput(
                tcp_dl_sta1_analyser)
            sta1_data_rate = sta1_throughput_max_dl_1 * 0.75
        except NoPacketsReceived:
            error_log = (
                'Failed calculating sta1 udp transmission rate'
                f'when running DUT with this configuration: {result_index}')
            logging.exception(error_log)
            tp_values2 = _generate_tp_dict('sta2', expected_tp2)
            _render_results(test_setups,
                            tp_values2,
                            setup_name2,
                            error_log=error_log)
            tp_values3 = _generate_tp_dict('sta3', expected_tp3)
            _render_results(test_setups,
                            tp_values3,
                            setup_name3,
                            error_log=error_log)
            logging.info("Proceeding to next DUT configuration")
            report_with_config['test_setups'] = test_setups
            report_with_config['status'] = {'passed': False}
            test_results[result_index] = report_with_config
            overall_test_status = False
            continue
        try:
            status1 = _run_setup(dut, sta1, sta2, test_setups, sta1_data_rate,
                                 sta1_throughput_max_dl_1, expected_tp1,
                                 setup_name1)
        except NoPacketsReceived as error:
            status1 = _handle_exception(test_setups, setup_name1, expected_tp1,
                                        error)

        # Setup 2

        # User instructions to move the device:
        print("Move STA2 to medium distance to the DUT")
        print(
            "(Please refer to the definition of"
            " close, medium, and far station distances table"
            " in the TR-398 Technical report by Broadband Forum)"
        )
        print("in the TR-398 Technical report by Broadband Forum)")
        input("Press Enter when this step is completed")

        # Wait 10 seconds before transmitting data again
        print("Waiting 10 seconds")
        sleep(10)

        try:
            status2 = _run_setup(dut, sta1, sta2, test_setups, sta1_data_rate,
                                 sta1_throughput_max_dl_1, expected_tp2,
                                 setup_name2)
        except NoPacketsReceived as error:
            status2 = _handle_exception(test_setups, setup_name2, expected_tp2,
                                        error)

        # Setup 3

        # User instruction to change settings:
        print("Disassociate STA2 from the DUT")
        print("then replace STA 2 with STA 3")

        input("Press Enter when this step is completed")
        # Wait 10 seconds before transmitting data again
        print("Waiting 10 seconds")
        sleep(10)

        # Measure the achievable downlink TCP throughput through STA3
        try:
            status3 = _run_setup(dut, sta1, sta3, test_setups, sta1_data_rate,
                                 sta1_throughput_max_dl_1, expected_tp3,
                                 setup_name3)
        except NoPacketsReceived as error:
            status3 = _handle_exception(test_setups, setup_name3, expected_tp3,
                                        error)

        setup_status = status1 and status2 and status3

        report_with_config['test_setups'] = test_setups
        report_with_config['status'] = {'passed': setup_status}

        test_results[result_index] = report_with_config

        overall_test_status = overall_test_status and setup_status
    test_results['status'] = {'passed': overall_test_status}

    path_and_prefix = join(
        report_path or getcwd(),
        report_prefix + "_" + datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Export results into  JSON file
    json_report_generator(test_results, path_and_prefix + ".json")
    # Generate HTML report
    html_report_generator(test_results, path_and_prefix + ".html")
    logging.info("TR-398 Airtime Fairness Test has finished")


def _run_setup(dut: IPv4Port, sta1: IPv4Endpoint, sta2: IPv4Endpoint,
               test_setups: dict, sta1_data_rate: float,
               sta1_throughput_max_dl: float, expected_tp: float,
               setup_name: str) -> bool:
    if "sta2" in setup_name:
        sta_b_prefix = "sta2"
    elif "sta3" in setup_name:
        sta_b_prefix = "sta3"
    # Note: Each time the setup is updated, we run this traffic pattern:
    # downlink TCP flow through one of the stations
    # to record its throughput value and two simultaneous UDP traffic streams
    # to use a downlink data rate set to 75% of STA1_Throughput_Max_DL_1 for
    # STA1 and 50% of STA2_Throughput_Max_DL_2 for STA2
    (sta2_throughput_max_dl, sta1_throughput, sta2_throughput, sta1_udp_tr,
     sta2_udp_tr) = _run_tr_pattern(setup_name, dut, sta1, sta2,
                                    sta1_data_rate)
    tp_values = _generate_tp_dict(
        sta_b_prefix,
        expected_tp,
        sta1_tcp_tp=sta1_throughput_max_dl,
        sta_b_tcp_tp=sta2_throughput_max_dl,
        sta1_udp_tr=sta1_udp_tr,
        sta1_udp_tp=sta1_throughput,
        sta_b_udp_tr=sta2_udp_tr,
        sta_b_udp_tp=sta2_throughput,
    )
    return _render_results(test_setups, tp_values, setup_name)


def _handle_exception(test_setups: dict, setup_name: str, expected_tp: float,
                      exception: NoPacketsReceived) -> bool:
    error_log = (
        f'No packets where received on STA: {exception.flow.destination.name}'
        f' while running {exception.flow.name}')
    logging.exception(error_log)
    tp_values = _generate_tp_dict("sta2", expected_tp)
    status = _render_results(test_setups,
                             tp_values,
                             setup_name,
                             error_log=error_log)
    return status


def _generate_tp_dict(sta_b_prefix: str,
                      expected_tp: float,
                      sta1_tcp_tp: Optional[float] = None,
                      sta_b_tcp_tp: Optional[float] = None,
                      sta1_udp_tr: Optional[float] = None,
                      sta1_udp_tp: Optional[float] = None,
                      sta_b_udp_tr: Optional[float] = None,
                      sta_b_udp_tp: Optional[float] = None) -> dict:
    tp_results = {
        "expected_throughput": expected_tp,
        "sta1_throughput_max_dl": sta1_tcp_tp,
        f"{sta_b_prefix}_throughput_max_dl": sta_b_tcp_tp,
        "sta1_udp_transmission_rate": sta1_udp_tr,
        "sta1_throughput": sta1_udp_tp,
        f"{sta_b_prefix}_udp_transmission_rate": sta_b_udp_tr,
        f"{sta_b_prefix}_throughput": sta_b_udp_tp
    }
    return tp_results


def _render_results(test_setups,
                    tp_values: dict,
                    setup_name: str,
                    error_log: str = None) -> Tuple[List, bool]:
    sta_a_prefix = 'sta1'
    if 'sta2' in setup_name:
        sta_b_prefix = 'sta2'
    elif 'sta3' in setup_name:
        sta_b_prefix = 'sta3'
    if not error_log:
        status, failure_causes = _validate_results(tp_values, sta_a_prefix,
                                                   sta_b_prefix)
        passed = not failure_causes
        status["passed"] = passed
        # Add the metric that did not meet the pass/fail criteria
        if not passed:
            status["failure_causes"] = failure_causes
        results = {"results": tp_values, "status": status}
    else:
        passed = False
        status = {"passed": passed}
        status['error_log'] = error_log
        for key in tp_values:
            if key != "expected_throughput":
                tp_values[key] = None
        results = {"results": tp_values, "status": status}
    test_setups[setup_name] = results
    return passed


def _validate_results(tp_values: dict, sta_a_prefix: str,
                      sta_b_prefix: str) -> Tuple[dict, List[str]]:
    """
    Check results according to the pass/fail criteria.

    Defined in the airtime fairness test in TR-398.
    """
    status = {}
    failure_causes = []
    if tp_values[f'{sta_a_prefix}_throughput'] < .45 * tp_values[
            f'{sta_a_prefix}_throughput_max_dl']:
        failure_causes.append(
            f'UDP throughput of {sta_a_prefix} '
            f'is less than 45% of the TCP throughput of {sta_a_prefix}')
        status[f'{sta_a_prefix}_throughput_max_dl'] = {'passed': False}
    else:
        status[f'{sta_a_prefix}_throughput_max_dl'] = {'passed': True}
    if tp_values[f'{sta_b_prefix}_throughput'] < .45 * tp_values[
            f'{sta_b_prefix}_throughput_max_dl']:
        failure_causes.append(
            f'UDP throughput of {sta_b_prefix} '
            f'is less than 45% of the TCP throughput of {sta_b_prefix}')
        status[f'{sta_b_prefix}_throughput_max_dl'] = {'passed': False}
    else:
        status[f'{sta_b_prefix}_throughput_max_dl'] = {'passed': True}
    if tp_values[f'{sta_a_prefix}_throughput'] + tp_values[
            f'{sta_b_prefix}_throughput'] < tp_values['expected_throughput']:
        failure_causes.append(
            f'The summation of {sta_a_prefix}_throughput and '
            f'{sta_b_prefix}_throughput is less than expected throughput')
        status['total_throughput'] = {'passed': False}
    else:
        status['total_throughput'] = {'passed': True}
    return status, failure_causes


def _run_tr_pattern(
    setup_name: str, dut: IPv4Port, sta1: IPv4Endpoint, sta_b: IPv4Endpoint,
    sta1_data_rate: float
) -> Tuple[Optional[float], Optional[float], Optional[float]]:

    # Measure the achievable downlink TCP throughput through STA2/STA3
    tcp_dl_sta_b, tcp_dl_sta_b_analyser = _configure_tcp_traffic(
        setup_name, dut, sta_b)
    _run_traffic([tcp_dl_sta_b])
    # Record the value
    sta_b_throughput_max_dl_1 = _calculate_tcp_throughput(
        tcp_dl_sta_b_analyser)

    # UDP data rates are according to TR-398 Airtime Fairness Test

    # Configure the downlink UDP stream for STA1
    udp_dl_sta1, udp_dl_sta1_analyser = _configure_udp_traffic(
        setup_name, dut, sta1, sta1_data_rate)

    # Configure the downlink UDP stream for STA2/STA3
    data_rate_sta_b = sta_b_throughput_max_dl_1 * 0.5
    udp_dl_sta_b, udp_dl_sta_b_analyser = _configure_udp_traffic(
        setup_name, dut, sta_b, data_rate_sta_b)

    # Simultaneously run the two UDP traffic streams for 120 seconds
    _run_traffic([udp_dl_sta1, udp_dl_sta_b])

    sta1_throughput_rx, sta1_throughput_tx = _calculate_udp_throughput(
        udp_dl_sta1_analyser)
    sta_b_throughput_rx, sta_b_throughput_tx = _calculate_udp_throughput(
        udp_dl_sta_b_analyser)

    return (sta_b_throughput_max_dl_1, sta1_throughput_rx, sta_b_throughput_rx,
            sta1_throughput_tx, sta_b_throughput_tx)


def _configure_tcp_traffic(
        setup_name: str, source: IPv4Port,
        destination: IPv4Endpoint) -> tuple[HTTPFlow, HttpAnalyser]:
    name = f'TCP traffic for setup: {setup_name}'
    flow = HTTPFlow(name=name, source=source, destination=destination)
    analyser = HttpAnalyser()
    flow.add_analyser(analyser)

    return flow, analyser


def _configure_udp_traffic(
        setup_name: str, source: IPv4Port, destination: IPv4Endpoint,
        data_rate: float) -> tuple[FrameBlastingFlow, FrameLossAnalyser]:
    name = f'UDP traffic for setup: {setup_name}'
    frame = create_frame(source_port=source)
    flow = FrameBlastingFlow(name=name,
                             source=source,
                             destination=destination,
                             bitrate=data_rate,
                             frame_list=[frame])
    analyser = FrameLossAnalyser()
    flow.add_analyser(analyser)

    return flow, analyser


def _run_traffic(flows: List[Flow]) -> None:
    """Run one or more configured flow simultaneously."""

    scenario = Scenario()
    for flow in flows:
        scenario.add_flow(flow)
    # Run the Scenario
    scenario.run(maximum_run_time=timedelta(seconds=120))
    scenario.release()


def _calculate_udp_throughput(
        analyser: FrameLossAnalyser
) -> Tuple[Optional[float], Optional[float]]:
    """Calculates the average udp throughput.
    
    :param analyser: object :class:`FrameLossAnalyser` contains data gathered 
       from the test
    :type analyser: FrameLossAnalyser
    :return:
       List of two UDP throughput values in bits per second:

       #. the received UDP throughput
       #. the transmitted UDP throughput

    :rtype: Tuple[Optional[float], Optional[float]]
    """
    total_bytes_rx = analyser.total_rx_bytes
    ts_rx_first = analyser.timestamp_rx_first
    ts_rx_last = analyser.timestamp_rx_last
    throughput_rx = _calculate_avg_throughput(total_bytes_rx, ts_rx_first,
                                              ts_rx_last, analyser.flow)
    # We calculate transmission throughput to report it instead
    # of configured data rate because of a small rounding error while configuring it
    total_bytes_tx = analyser.total_tx_bytes
    ts_tx_first = analyser.timestamp_tx_first
    ts_tx_last = analyser.timestamp_tx_last
    throughput_tx = _calculate_avg_throughput(total_bytes_tx, ts_tx_first,
                                              ts_tx_last, analyser.flow)
    return throughput_rx, throughput_tx


def _calculate_tcp_throughput(analyser: HttpAnalyser) -> Optional[float]:
    """Calculates the average TCP throughput.
    
    :param analyser: object :class:`HttpAnalyser` contains data gathered 
       from the test
    :type analyser: HttpAnalyser
    :return: the received TCP throughput
    :rtype: Optional[float]
    """
    # Gather data from the server side (not stations)
    # because we cant configure http server on endpoint
    total_bytes_rx = analyser.total_tx_server
    ts_rx_first = analyser.tx_first_server
    ts_rx_last = analyser.tx_last_server
    return _calculate_avg_throughput(total_bytes_rx, ts_rx_first, ts_rx_last,
                                     analyser.flow)


def _calculate_avg_throughput(total_bytes, ts_first: Timestamp,
                              ts_last: Timestamp, flow: Flow) -> float:
    duration = _subtract(ts_first, ts_last)
    if duration:
        return total_bytes / duration.total_seconds() * BITS_PER_BYTE
    raise NoPacketsReceived(flow=flow)


def _subtract(value, from_value):
    if value is not None and from_value is not None:
        return from_value - value
    return None
