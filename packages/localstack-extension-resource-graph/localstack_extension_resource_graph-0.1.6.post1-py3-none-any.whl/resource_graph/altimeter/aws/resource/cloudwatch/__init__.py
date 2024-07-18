"""Base class for Cloudwatch resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class CloudwatchResourceSpec(AWSResourceSpec):
    """Base class for Cloudwatch resources."""

    service_name = "cloudwatch"
