"""Base class for KMS resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class KMSResourceSpec(AWSResourceSpec):
    """Base class for KMS resources."""

    service_name = "kms"
