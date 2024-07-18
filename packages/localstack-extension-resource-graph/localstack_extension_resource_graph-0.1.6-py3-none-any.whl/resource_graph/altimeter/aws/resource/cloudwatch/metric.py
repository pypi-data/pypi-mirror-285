"""Resource for IAM Policies"""

from typing import Any, Type, List, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.cloudwatch import CloudwatchResourceSpec
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.dict_field import (
    AnonymousDictField,
    AnonymousEmbeddedDictField,
)
from resource_graph.altimeter.core.graph.schema import Schema
from resource_graph.altimeter.aws.resource.resource_spec import ListFromAWSResult


class CloudwatchMetricResourceSpec(CloudwatchResourceSpec):
    """Resource for Cloudwatch Metrics"""

    type_name = "metric"
    schema = Schema(
        ScalarField("Namespace"),
        ScalarField("MetricName"),
        ListField(
            "Dimensions",
            AnonymousEmbeddedDictField(ScalarField("Name"), ScalarField("Value")),
            optional=True,
        ),
        ScalarField("Value", optional=True),
    )

    @classmethod
    def list_from_aws(
        cls: Type["CloudwatchMetricResourceSpec"],
        client: BaseClient,
        account_id: str,
        region: str,
    ) -> ListFromAWSResult:
        metrics = client.list_metrics()
        metrics_list = {}

        for metric in metrics.get("Metrics"):
            resource_arn = cls.generate_arn(
                account_id=account_id, region=region, resource_id=metric["MetricName"]
            )
            metrics_list[resource_arn] = metric
        return ListFromAWSResult(resources=metrics_list)
