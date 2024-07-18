from typing import Type, Dict

from resource_graph.altimeter.aws.resource.iam.user import IAMUserResourceSpec

from resource_graph.altimeter.aws.resource.ecs.task_definition import (
    ECSTaskDefinitionResourceSpec,
)
from resource_graph.altimeter.aws.resource.elbv2.target_group import (
    TargetGroupResourceSpec,
)

from resource_graph.altimeter.aws.resource.ecs.cluster import ECSClusterResourceSpec
from resource_graph.altimeter.aws.resource.iam.role import IAMRoleResourceSpec
from resource_graph.altimeter.aws.resource.secrets_manager.secrets import (
    SecretsmanagerSecretResourceSpec,
)

from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)

from resource_graph.altimeter.core.graph.field.dict_field import (
    EmbeddedDictField,
    DictField,
)

from resource_graph.altimeter.core.graph.field.list_field import ListField
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.ecs import ECSResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.core.graph.field.scalar_field import (
    ScalarField,
    EmbeddedScalarField,
)
from resource_graph.altimeter.core.graph.schema import Schema


class ECSServiceResourceSpec(ECSResourceSpec):
    type_name = "service"

    schema = Schema(
        ScalarField("serviceArn"),
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
        ScalarField(
            "createdBy"
        ),  # this is not resource link because this account is dummy one, does not exists
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        clusters = client.list_clusters()
        services = dict()
        for cluster in clusters.get("clusterArns", []):
            services_return = client.list_services(cluster=cluster)
            services_described = client.describe_services(
                cluster=cluster, services=services_return.get("serviceArns", [])
            )
            for service in services_described.get("services", []):
                services[service["serviceArn"]] = service
        return ListFromAWSResult(resources=services)
