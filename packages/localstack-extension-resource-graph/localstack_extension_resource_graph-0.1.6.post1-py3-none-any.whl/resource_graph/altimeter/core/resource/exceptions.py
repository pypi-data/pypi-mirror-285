"""Resource related Exceptions."""

from resource_graph.altimeter.core.exceptions import AltimeterException


class ResourceSpecClassNotFoundException(AltimeterException):
    """A specified ResourceSpecClass can not be found."""


class MultipleResourceSpecClassesFoundException(AltimeterException):
    """More than one ResourceSpec class exist for a given specification."""
