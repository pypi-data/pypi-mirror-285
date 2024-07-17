from os.path import abspath, dirname, join
from typing import Dict  # For type hinting

import jinja2
import pandas as pd
from byteblower_test_framework import __version__ as framework_version
from byteblowerll.byteblower import ByteBlower
from highcharts_excentis import Highchart

_PACKAGE_DIRECTORY = dirname(abspath(__file__))
_QUOTES = [
    (
        "The greatest glory in living lies not in never falling," +
        "<br>but in rising every time we fall.",
        "ByteBlower rises with you, optimizing networks" +
        "<br>to new heights of success.",
    ),
    (
        "In the journey of a thousand miles," +
        "<br>the first step is the most important.",
        "Begin your network optimization journey" +
        " with ByteBlower, your trusted guide.",
    ),
    (
        "Success is not final, failure is not fatal:" +
        "<br>It is the courage to continue that counts.",
        "ByteBlower empowers you to persevere" +
        "<br>in the pursuit of network perfection.",
    ),
    (
        "Believe you can and you're halfway there.",
        "ByteBlower believes in your network's potential," +
        " working tirelessly to ensure it reaches its destination.",
    ),
    (
        "The only limit to our realization of tomorrow" +
        "<br>will be our doubts of today.",
        "With ByteBlower by your side, doubtlessly" +
        "<br>forge ahead to unlock network excellence.",
    ),
    (
        "Embrace the challenges that come your way," +
        "<br>for they are the stepping stones" + "<br>to greatness.",
        "ByteBlower, your faithful companion in the world of testing, is here"
        + "<br>to help you conquer those challenges," +
        " one network improvement at a time",
    ),
]

_JINJA2_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
    searchpath=join(_PACKAGE_DIRECTORY, 'templates')))
_TEMPLATE = _JINJA2_ENV.get_template("report.html")


def _build_plot(setup_name: str, setup: dict, config_name: str):
    "Prepare Data and build Highcharts plots."

    if "sta2" in setup_name:
        sta_b_prefix = "sta2"
    elif "sta3" in setup_name:
        sta_b_prefix = "sta3"
    options = {
        "title": {
            "text": "",
            "align": "center"
        },
        "xAxis": {
            "categories":
            ["STA1",
             sta_b_prefix.upper(), "STA1+" + sta_b_prefix.upper()]
        },
        "yAxis": {
            "min": 0,
            "title": {
                "text": 'Throughput (Mbps)'
            }
        }
    }
    series = [{
        "name":
        "TCP max",
        "data": [
            setup["results"]["sta1_throughput_max_dl"],
            setup["results"][f"{sta_b_prefix}_throughput_max_dl"], 0
        ],
    }, {
        "name":
        "UDP Transmitted",
        "data": [
            setup["results"]["sta1_udp_transmission_rate"],
            setup["results"][f"{sta_b_prefix}_udp_transmission_rate"], 0
        ],
    }, {
        "name":
        "Expected",
        "data": [
            setup["results"]["sta1_throughput_max_dl"] * .45,
            setup["results"][f"{sta_b_prefix}_throughput_max_dl"] * .45,
            setup["results"]["expected_throughput"]
        ],
        "pointPlacement":
        0.05,
        "color":
        'rgba(158, 159, 163, 0.5)',
    }, {
        "name":
        "UDP Measured",
        "data": [
            setup["results"]["sta1_throughput"],
            setup["results"][f"{sta_b_prefix}_throughput"],
            setup["results"]["sta1_throughput"] +
            setup["results"][f"{sta_b_prefix}_throughput"]
        ]
    }]
    chart = Highchart(renderTo=setup_name + config_name)
    chart.set_dict_options(options)
    for element in series:
        chart.add_data_set(
            data=[round(value / 1e6, 2) for value in element["data"]],
            series_type=element.get("type", 'column'),
            name=element["name"],
            yAxis=element.get('yaxis', 0),
            tooltip={'valueSuffix': element.get('valueSuffix', 'Mbps')},
            pointPlacement=element.get("pointPlacement", 0),
            color=element.get("color", ""))
    chart.buildhtml()
    return chart.content


def html_report_generator(
    results: Dict,
    output_file: str,
) -> None:
    """Generate HTML report file based on TR-398 AirTime Fairness test results.

    :param results: throughput results of all configurations and setups
    :type results: Dict
    :param output_file: path + prefix of the HTML output file
    :type output_file: str
    """

    api_version = ByteBlower.InstanceGet().APIVersionGet()
    quote_head, quote_tagline = _QUOTES[0]
    status = results.pop("status")
    overall_status = status['passed']
    chart = Highchart(offline=True)
    chart.buildhtmlheader()
    js_resources = chart.htmlheader

    # Generate a new result dict with rendered plots
    for config_name, config_result in results.items():
        for setup_name, setup_result in config_result["test_setups"].items():
            if setup_result["results"]["sta1_throughput_max_dl"] is not None:
                setup_result["plot"] = _build_plot(setup_name, setup_result,
                                                   config_name)

    jinja_data = {
        "quote_head": quote_head,
        "quote_tagline": quote_tagline,
        "api_version": api_version,
        "framework_version": framework_version,
        "js_resources": js_resources,
        "status": overall_status,
        "results": results
    }

    # generate and save the HTML report file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(_TEMPLATE.render(jinja_data))


def json_report_generator(
    results: Dict,
    output_file: str,
) -> None:
    """Generate a JSON report file based on TR-398 Airtime Fairness test results.

    :param results: Set of: Used test configuration, results of
       all simulations, test status, and error logs
    :type results: Dict
    :param output_file: path + prefix of the JSON output file
    :type output_file: str
    """
    pd_series = pd.Series(results)
    pd_series.to_json(output_file, date_format='iso')
