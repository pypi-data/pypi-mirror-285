"""Base class for GuardDuty resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class GuardDutyResourceSpec(AWSResourceSpec):
    """Base class for GuardDuty resources."""

    service_name = "guardduty"
