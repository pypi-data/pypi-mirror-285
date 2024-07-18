from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.secrets_manager import (
    SecretsmanagerResourceSpec,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class SecretsmanagerSecretResourceSpec(SecretsmanagerResourceSpec):
    type_name = "secret"

    schema = Schema(
        ScalarField("ARN"),
        ScalarField("Name"),
        ScalarField("LastChangedDate"),
        ScalarField("LastAccessedDate", optional=True),
        ScalarField("CreatedDate"),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        secrets_resp = client.list_secrets()
        secrets = {}
        for secret in secrets_resp.get("SecretList", []):
            secrets[secret["ARN"][:-7]] = secret
        return ListFromAWSResult(resources=secrets)
