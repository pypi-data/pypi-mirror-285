"""Base class for cognito_idp resources."""

from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec


class CognitoIDPResourceSpec(AWSResourceSpec):
    """Base class for cognito_idp resources."""

    service_name = "cognito-idp"
