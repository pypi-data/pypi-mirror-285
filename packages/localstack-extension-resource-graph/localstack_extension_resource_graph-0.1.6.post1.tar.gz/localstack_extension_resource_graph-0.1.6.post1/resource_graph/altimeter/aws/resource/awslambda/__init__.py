"""Base class for lambda resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class LambdaResourceSpec(AWSResourceSpec):
    """Base class for lambda resources."""

    service_name = "lambda"
