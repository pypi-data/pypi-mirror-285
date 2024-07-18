from typing import Type, Dict

from resource_graph.altimeter.aws.resource.ecs.container_instance import (
    ECSContainerInstanceResourceSpec,
)
from resource_graph.altimeter.aws.resource.ecs.task_definition import (
    ECSTaskDefinitionResourceSpec,
)
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)

from resource_graph.altimeter.core.graph.field.dict_field import EmbeddedDictField

from resource_graph.altimeter.core.graph.field.list_field import ListField
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.ecs import ECSResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.schema import Schema


class ECSTaskResourceSpec(ECSResourceSpec):
    type_name = "task"

    schema = Schema(
        ScalarField("taskArn"),
        ResourceLinkField(
            "taskDefinitionArn", ECSTaskDefinitionResourceSpec, value_is_id=True
        ),
        ScalarField("platformFamily"),
        # ScalarField("attachments"), TODO if you want
        ScalarField("platformVersion"),
        ScalarField("memory"),
        ScalarField("launchType"),
        ScalarField("lastStatus"),
        # ScalarField("group"), actually do not know what this group is
        ScalarField("enableExecuteCommand"),
        ScalarField("desiredStatus"),
        ScalarField("cpu"),
        ListField(
            "containers",
            EmbeddedDictField(
                ScalarField("taskArn"),
                ResourceLinkField(
                    "containerArn", ECSContainerInstanceResourceSpec, value_is_id=True
                ),
                ScalarField("name"),
                ScalarField("image"),
                ScalarField("lastStatus"),
                ScalarField("healthStatus"),
                ScalarField("cpu"),
                ScalarField("memory"),
            ),
        ),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        clusters_return = client.list_clusters()
        tasks = dict()
        for arn in clusters_return.get("clusterArns", []):
            tasks_return = client.list_tasks(cluster=arn)
            task_arn = tasks_return.get("taskArns")
            tasks_described_return = client.describe_tasks(cluster=arn, tasks=task_arn)
            for task in tasks_described_return.get("tasks"):
                tasks[task["taskArn"]] = task
        return ListFromAWSResult(resources=tasks)
