from typing import Type, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.cognito_identity import (
    CognitoIdentityResourceSpec,
)
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.core.graph.field.dict_field import (
    AnonymousEmbeddedDictField,
)
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.schema import Schema


class CognitoIdentityIdentityPoolResourceSpec(CognitoIdentityResourceSpec):
    type_name = "identity-pool"

    schema = Schema(
        ScalarField("IdentityPoolId"),
        ScalarField("IdentityPoolName"),
        ScalarField("AllowUnauthenticatedIdentities"),
        ScalarField("DeveloperProviderName"),
        ListField(
            "CognitoIdentityProviders",
            AnonymousEmbeddedDictField(
                ScalarField("ProviderName"),
                ScalarField("ServerSideTokenCheck"),
                ScalarField("ClientId"),
            ),
        ),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        identity_pools = {}
        paginator = client.get_paginator("list_identity_pools")
        for resp in paginator.paginate(MaxResults=1000):
            for identity_pool in resp.get("IdentityPools", []):
                resource_arn = cls.generate_arn(
                    account_id=account_id,
                    region=region,
                    resource_id=identity_pool["IdentityPoolId"],
                )
                pool_info = get_identity_pool_info(
                    client, identity_pool["IdentityPoolId"]
                )
                identity_pools[resource_arn] = pool_info

        return ListFromAWSResult(resources=identity_pools)


def get_identity_pool_info(client: BaseClient, pool_id: str) -> Dict[str, str]:
    try:
        return client.describe_identity_pool(IdentityPoolId=pool_id)
    except ClientError as c_e:
        raise c_e
