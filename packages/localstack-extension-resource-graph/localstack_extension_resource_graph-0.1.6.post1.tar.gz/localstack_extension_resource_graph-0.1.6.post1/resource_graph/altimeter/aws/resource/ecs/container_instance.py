from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.ecs import ECSResourceSpec
from resource_graph.altimeter.aws.resource.ecs.cluster import ECSClusterResourceSpec
from resource_graph.altimeter.aws.resource.ecs.task_definition import (
    ECSTaskDefinitionResourceSpec,
)
from resource_graph.altimeter.aws.resource.elbv2.target_group import (
    TargetGroupResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.user import IAMUserResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.core.graph.field.dict_field import (
    EmbeddedDictField,
)
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import (
    ScalarField,
)
from resource_graph.altimeter.core.graph.schema import Schema


class ECSContainerInstanceResourceSpec(ECSResourceSpec):
    type_name = "container_instance"

    schema = Schema(
        ScalarField("containerInstanceArn"),
        ScalarField("capacityProviderName"),
        ScalarField("version"),
        ScalarField("status"),
        ScalarField("statusReason"),
        ScalarField("agentUpdateStatus"),
        ScalarField("serviceName"),
        ResourceLinkField("clusterArn", ECSClusterResourceSpec, value_is_id=True),
        ListField(
            "loadBalancers",
            EmbeddedDictField(
                ResourceLinkField(
                    "targetGroupArn", TargetGroupResourceSpec, value_is_id=True
                ),
                ScalarField("containerName"),
                ScalarField("containerPort"),
            ),
        ),
        ScalarField("status"),
        ScalarField("desiredCount"),
        ScalarField("runningCount"),
        ScalarField("pendingCount"),
        ScalarField("launchType"),
        ResourceLinkField(
            "taskDefinition", ECSTaskDefinitionResourceSpec, value_is_id=True
        ),
        ResourceLinkField("createdBy", IAMUserResourceSpec, value_is_id=True),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        clusters = client.list_clusters()
        container_instances = dict()
        for cluster in clusters.get("clusterArns", []):
            containers_return = client.list_container_instances(cluster=cluster)
            container_instances_return = containers_return.get("containerInstanceArns", [])
            if len(container_instances_return) > 0:
                containers_described = client.describe_container_instances(
                    cluster=cluster,
                    containerInstances=containers_return.get("containerInstanceArns", []),
                )
                for container in containers_described.get("containerInstances", []):
                    container_instances[container["containerInstanceArn"]] = container

        return ListFromAWSResult(resources=container_instances)
