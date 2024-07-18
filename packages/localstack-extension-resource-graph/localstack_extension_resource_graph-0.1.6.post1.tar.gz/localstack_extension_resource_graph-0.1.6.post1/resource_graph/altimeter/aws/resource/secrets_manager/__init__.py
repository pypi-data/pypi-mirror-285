"""Base class for secrets manager resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class SecretsmanagerResourceSpec(AWSResourceSpec):
    """Base class for secrets manager resources."""

    service_name = "secretsmanager"
