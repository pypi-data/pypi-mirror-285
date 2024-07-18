"""Exceptions for access related errors."""

from resource_graph.altimeter.core.exceptions import AltimeterException


class AccountAuthException(AltimeterException):
    """Exception indicating auth was unable to be obtained to an account."""
