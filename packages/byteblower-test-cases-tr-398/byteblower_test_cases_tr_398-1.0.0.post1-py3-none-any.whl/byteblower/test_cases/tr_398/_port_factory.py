"""Factory functions to create and initialize :class:`~Port` instances."""
import logging

from byteblower_test_framework.endpoint import Port  # for type hinting
from byteblower_test_framework.endpoint import (IPv4Port, IPv6Port,
                                                NatDiscoveryIPv4Port)
from byteblower_test_framework.exceptions import log_api_error
from byteblower_test_framework.host import Server  # for type hinting

from .definitions import LOGGING_PREFIX as _LOGGING_PREFIX
from .definitions import TrafficEndpointConfig  # for type hinting
from .exceptions import InvalidInput

__all__ = ('initialize_port', )


class PortFactory:
    """Factory for :class:`Port` objects."""

    @staticmethod
    def build_port(server: Server, **port_config) -> Port:
        """Create a :class:`Port`.

        The function can create either :class:`IPv4Port`,  :class:`NatDiscoveryIPv4Port`
        or :class:`IPv6Port` objects.

        :param server: The :class:`Server` object to create the port on
        :type server: Server
        :param port_config: The configuration for the port.
        :type port_config: TrafficEndpointConfig
        :return: The newly created port
        :rtype: Port
        """
        if 'ipv4' in port_config:
            nat = port_config.pop('nat', False)
            if nat:
                port_class = NatDiscoveryIPv4Port
            else:
                port_class = IPv4Port
        elif 'ipv6' in port_config:
            port_class = IPv6Port
        else:
            raise InvalidInput(
                'Please provide either IPv4 or IPv6 configuration')
        port = port_class(server, **port_config)
        return port


@log_api_error
def initialize_port(server: Server,
                    port_config: TrafficEndpointConfig) -> Port:
    """Create a :class:`Port`.

    The function can create either :class:`IPv4Port`,
    :class:`NatDiscoveryIPv4Port` or :class:`IPv6Port` objects.

    :param server: The :class:`Server` object to create the port on
    :type server: Server
    :param port_config: The configuration for the port.
    :type port_config: TrafficEndpointConfig
    :return: The newly created port
    :rtype: Port
    """
    logging.info('%sInitializing port', _LOGGING_PREFIX)
    port: Port = PortFactory.build_port(server, **port_config)
    logging.info('%sInitialized port %r'
                 ' with IP address %r, network %r', _LOGGING_PREFIX, port.name,
                 port.ip, port.network)

    return port
