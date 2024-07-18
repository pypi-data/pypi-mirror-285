"""Base class for cognito_identity resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class CognitoIdentityResourceSpec(AWSResourceSpec):
    """Base class for cognito_identity resources."""

    service_name = "cognito-identity"
