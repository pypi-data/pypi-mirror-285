from typing import Type, Dict

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


class ECSClusterResourceSpec(ECSResourceSpec):
    type_name = "cluster"

    schema = Schema(
        ScalarField("clusterArn"),
        ScalarField("clusterName"),
        ScalarField("status"),
        ScalarField("registeredContainerInstancesCount"),
        ScalarField("runningTasksCount"),
        ScalarField("pendingTasksCount"),
        ScalarField("activeServicesCount"),
        ListField(
            "settings", EmbeddedDictField(ScalarField("name"), ScalarField("value"))
        ),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        clusters_return = client.list_clusters()
        clusters = dict()
        for arn in clusters_return.get("clusterArns", []):
            cluster_name = arn.split("/")[1]
            cluster_details = get_ecs_cluster_details(client, cluster_name)
            clusters[arn] = cluster_details
        return ListFromAWSResult(resources=clusters)


def get_ecs_cluster_details(client: BaseClient, cluster_name: str) -> Dict[str, str]:
    """Get SNS subscription attributes"""
    try:
        value = client.describe_clusters(
            clusters=[cluster_name],
            include=["ATTACHMENTS", "CONFIGURATIONS", "SETTINGS", "STATISTICS", "TAGS"],
        )["clusters"]
        if len(value) > 1:
            raise Exception("Non unique cluster arn found")
        return value[0]
    except ClientError as c_e:
        raise c_e
