"""Base class for rds resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class RDSResourceSpec(AWSResourceSpec):
    """Base class for rds resources."""

    service_name = "rds"
