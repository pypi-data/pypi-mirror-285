"""AWSResourceSpec subclass for ec2 resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class EC2ResourceSpec(AWSResourceSpec):
    """AWSResourceSpec subclass for ec2 resources."""

    service_name = "ec2"
