"""Base class for SNS resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class SNSResourceSpec(AWSResourceSpec):
    """Base class for SNS resources."""

    service_name = "sns"
