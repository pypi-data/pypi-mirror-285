from typing import Type, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.ecs import ECSResourceSpec
from resource_graph.altimeter.aws.resource.iam.role import IAMRoleResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.secrets_manager.secrets import (
    SecretsmanagerSecretResourceSpec,
)
from resource_graph.altimeter.core.graph.field.dict_field import (
    EmbeddedDictField,
    DictField,
)
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import (
    ScalarField,
    EmbeddedScalarField,
)
from resource_graph.altimeter.core.graph.schema import Schema


class ECSTaskDefinitionResourceSpec(ECSResourceSpec):
    type_name = "task_definition"

    schema = Schema(
        ScalarField("taskDefinitionArn"),
        ListField(
            "containerDefinitions",
            EmbeddedDictField(
                ScalarField("name"),
                ScalarField("image"),
                ScalarField("cpu"),
                ScalarField("memoryReservation", optional=True),
                ListField(
                    "portMappings",
                    EmbeddedDictField(
                        ScalarField("containerPort"),
                        ScalarField("hostPort"),
                        ScalarField("protocol"),
                    ),
                ),
                ScalarField("essential"),
                ListField(
                    "environment",
                    EmbeddedDictField(
                        ScalarField("name"),
                        ScalarField("value"),
                    ),
                ),
                ListField(
                    "secrets",
                    EmbeddedDictField(
                        ScalarField("name"),
                        ResourceLinkField(
                            "valueFrom",
                            SecretsmanagerSecretResourceSpec,
                            value_is_id=True,
                        ),
                    ),
                    optional=True,
                ),
                DictField("logConfiguration", ScalarField("logDriver", optional=True), optional=True),
            ),
        ),
        ScalarField("family"),
        ResourceLinkField("taskRoleArn", IAMRoleResourceSpec, value_is_id=True),
        ResourceLinkField("executionRoleArn", IAMRoleResourceSpec, value_is_id=True, optional=True),
        ScalarField("networkMode"),
        ScalarField("revision"),
        ScalarField("status"),
        ScalarField("cpu"),
        ScalarField("memory"),
        ScalarField("registeredAt"),
        ListField("compatibilities", EmbeddedScalarField()),
        ListField("requiresCompatibilities", EmbeddedScalarField()),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        tasks = dict()
        tasks_return = client.list_task_definitions()
        for arn in tasks_return.get("taskDefinitionArns", []):
            task_details = get_ecs_task_definition_details(client, arn)
            for container in task_details["containerDefinitions"]:
                if "secrets" in container:
                    for secret in container["secrets"]:
                        secret["valueFrom"] = ":".join(
                            secret["valueFrom"].split(":")[:7]
                        )
            tasks[arn] = task_details
        return ListFromAWSResult(resources=tasks)


def get_ecs_task_definition_details(
    client: BaseClient, task_arn: str
) -> Dict[str, str]:
    """Get SNS subscription attributes"""
    try:
        return client.describe_task_definition(
            taskDefinition=task_arn,
            include=["TAGS"],
        )["taskDefinition"]
    except ClientError as c_e:
        raise c_e
