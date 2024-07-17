"""Exception related to the TR-398 test implementation."""
from byteblower_test_framework.traffic import Flow  # For type hint


class Tr398Exception(Exception):
    """Base exception for all TR-398 tests related exceptions."""


class InvalidInput(Tr398Exception):
    """Raised when the user provided invalid input values."""


class NoPacketsReceived(Tr398Exception):
    """Raised when the destination did not receive any packets."""

    def __init__(self, *args: object, flow: Flow = None) -> None:
        super().__init__(*args)
        self.flow = flow
