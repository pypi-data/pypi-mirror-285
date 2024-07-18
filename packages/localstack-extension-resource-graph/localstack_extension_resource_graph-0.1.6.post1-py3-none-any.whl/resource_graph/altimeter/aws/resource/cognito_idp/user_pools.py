from typing import Type, List

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.awslambda.function import (
    LambdaFunctionResourceSpec,
)
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp import CognitoIDPResourceSpec
from resource_graph.altimeter.core.graph.field.dict_field import AnonymousDictField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class CognitoIDPUserPoolResourceSpec(CognitoIDPResourceSpec):
    type_name = "user-pool"

    schema = Schema(
        ScalarField("Id"),
        ScalarField("Name"),
        AnonymousDictField(
            "LambdaConfig",
            ResourceLinkField(
                "PreSignUp",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="PreSignUp",
            ),
            ResourceLinkField(
                "PostConfirmation",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="PostConfirmation",
            ),
            ResourceLinkField(
                "PostAuthentication",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="PostAuthentication",
            ),
            ResourceLinkField(
                "PreTokenGeneration",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="PreTokenGeneration",
            ),
            ResourceLinkField(
                "PreAuthentication",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="PreAuthentication",
            ),
            ResourceLinkField(
                "UserMigration",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="UserMigration",
            ),
            ResourceLinkField(
                "CustomMessage",
                LambdaFunctionResourceSpec,
                optional=True,
                value_is_id=True,
                alti_key="CustomMessage",
            ),
        ),
        ScalarField("LastModifiedDate"),
        ScalarField("CreationDate"),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        # TODO use pagination instead
        paginator = client.get_paginator("list_user_pools")
        user_pools = {}

        for resp in paginator.paginate(MaxResults=100):
            for user_pool in resp.get("UserPools", []):
                resource_arn = cls.generate_arn(
                    account_id=account_id, region=region, resource_id=user_pool["Id"]
                )
                user_pools[resource_arn] = user_pool
            return ListFromAWSResult(resources=user_pools)
