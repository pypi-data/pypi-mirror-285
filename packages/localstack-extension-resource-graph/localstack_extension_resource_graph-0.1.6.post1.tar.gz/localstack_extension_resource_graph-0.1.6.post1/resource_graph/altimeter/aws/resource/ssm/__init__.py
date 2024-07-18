"""Base class for SSM resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class SSMResourceSpec(AWSResourceSpec):
    """Base class for SSM resources."""

    service_name = "ssm"
