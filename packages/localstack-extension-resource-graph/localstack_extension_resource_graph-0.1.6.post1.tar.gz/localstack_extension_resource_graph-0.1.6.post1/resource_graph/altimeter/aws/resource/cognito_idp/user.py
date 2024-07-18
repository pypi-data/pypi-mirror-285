from typing import Type, List

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.awslambda.function import (
    LambdaFunctionResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp.group import (
    CognitoIDPGroupResourceSpec,
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
    EmbeddedResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class UserMissingSubException(AltimeterException):
    """Missing field sub in user attributes error occured."""


class CognitoIDPUserResourceSpec(CognitoIDPResourceSpec):
    type_name = "user"

    schema = Schema(
        ScalarField("Username"),
        ListField(
            "Attributes",
            AnonymousEmbeddedDictField(ScalarField("Name"), ScalarField("Value")),
        ),
        ScalarField("UserCreateDate"),
        ScalarField("UserLastModifiedDate"),
        ScalarField("Enabled"),
        ScalarField("UserStatus"),
        ResourceLinkField("UserPool", CognitoIDPUserPoolResourceSpec),
        ListField(
            "Groups",
            EmbeddedResourceLinkField(CognitoIDPGroupResourceSpec, value_is_id=True),
        ),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        user_pools = CognitoIDPUserPoolResourceSpec.list_from_aws(
            client, account_id, region
        )
        users = {}
        for pool in user_pools.resources.values():
            returned_users = client.list_users(UserPoolId=pool["Id"])
            for user in returned_users["Users"]:
                try:
                    res_id = [
                        x["Value"] for x in user["Attributes"] if x["Name"] == "sub"
                    ][0]
                except:
                    raise UserMissingSubException(
                        f"Missing files sub for user: {user['Username']} in user pool: {pool['Id']}"
                    )
                user["UserPool"] = pool["Id"]
                resource_arn = f"arn:aws:cognito-idp:{region}:{account_id}:userpool/{pool['Id']}:user/{res_id}"
                groups = get_groups_for_user(
                    client, user["Username"], pool["Id"], account_id, region
                )
                user["Groups"] = groups
                users[resource_arn] = user
        return ListFromAWSResult(resources=users)


def get_groups_for_user(
    client: BaseClient, username: str, pool_id: str, account_id: str, region: str
) -> List[str]:
    try:
        groups = client.admin_list_groups_for_user(
            Username=username, UserPoolId=pool_id
        )
        groups_arn = []
        for group in groups["Groups"]:
            group_name = group["GroupName"]
            resource_arn = f"arn:aws:cognito-idp:{region}:{account_id}:userpool/{pool_id}:group/{group_name}"
            groups_arn.append(resource_arn)
        return groups_arn
    except ClientError as c_e:
        raise c_e
