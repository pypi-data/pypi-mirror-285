"""Shared type definitions and constants."""
from typing import Any, Dict  # for type hinting

LOGGING_PREFIX = 'ByteBlower Test: '

# Type aliases
TrafficEndpointConfig = Dict[str, Any]

# For the conversion from bits to bytes
BITS_PER_BYTE: int = 8
__all__ = [
    'TrafficEndpointConfig',
]
