"""Base class for CloudTrail resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class CloudTrailResourceSpec(AWSResourceSpec):
    """Base class for CloudTrail resources."""

    service_name = "cloudtrail"
