"""ResourceSpec classes for classic ecs resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class ECSResourceSpec(AWSResourceSpec):
    """Abstract base for ResourceSpec classes for classic ecs resources."""

    service_name = "ecs"
