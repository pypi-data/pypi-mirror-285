"""Base class for SQS resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class SQSResourceSpec(AWSResourceSpec):
    """Base class for SQS resources."""

    service_name = "sqs"
