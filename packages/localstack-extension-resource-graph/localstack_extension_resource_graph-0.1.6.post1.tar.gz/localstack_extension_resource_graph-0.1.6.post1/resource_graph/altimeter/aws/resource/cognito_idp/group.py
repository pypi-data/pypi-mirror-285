from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.awslambda.function import (
    LambdaFunctionResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp.user_pools import (
    CognitoIDPUserPoolResourceSpec,
)
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp import CognitoIDPResourceSpec
from resource_graph.altimeter.core.exceptions import AltimeterException
from resource_graph.altimeter.core.graph.field.dict_field import (
    AnonymousDictField,
    DictField,
    AnonymousEmbeddedDictField,
)
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class UserMissingSubException(AltimeterException):
    """Missing field sub in user attributes error occured."""


class CognitoIDPGroupResourceSpec(CognitoIDPResourceSpec):
    type_name = "group"

    schema = Schema(
        ScalarField("GroupName"),
        ScalarField("CreationDate"),
        ScalarField("LastModifiedDate"),
        ResourceLinkField("UserPoolId", CognitoIDPUserPoolResourceSpec),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        user_pools = CognitoIDPUserPoolResourceSpec.list_from_aws(
            client, account_id, region
        )
        groups = {}
        for pool in user_pools.resources.values():
            returned_users = client.list_groups(UserPoolId=pool["Id"])
            for group in returned_users["Groups"]:
                group_name = group["GroupName"]
                resource_arn = f"arn:aws:cognito-idp:{region}:{account_id}:userpool/{pool['Id']}:group/{group_name}"
                groups[resource_arn] = group
        return ListFromAWSResult(resources=groups)
