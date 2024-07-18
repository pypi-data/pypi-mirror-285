from typing import Type, List, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.sqs import SQSResourceSpec
from resource_graph.altimeter.core.graph.field.dict_field import AnonymousDictField
from resource_graph.altimeter.core.graph.field.list_field import ListField
from resource_graph.altimeter.core.graph.field.scalar_field import (
    ScalarField,
    EmbeddedScalarField,
)
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class SQSQueueResourceSpec(SQSResourceSpec):
    type_name = "queue"

    schema = Schema(
        ScalarField("QueueUrl"),
        AnonymousDictField(
            "Attributes",
            ScalarField("ApproximateNumberOfMessages"),
            ScalarField("ApproximateNumberOfMessagesNotVisible"),
            ScalarField("ApproximateNumberOfMessagesDelayed"),
            ScalarField("CreatedTimestamp"),
            ScalarField("DelaySeconds"),
            ScalarField("LastModifiedTimestamp"),
            ScalarField("MaximumMessageSize"),
            ScalarField("MessageRetentionPeriod"),
            ScalarField("QueueArn"),
            ScalarField("ReceiveMessageWaitTimeSeconds"),
            ScalarField("VisibilityTimeout"),
            ScalarField("SqsManagedSseEnabled"),
        ),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        queues_resp = client.list_queues()
        queues = {}

        for queue_url in queues_resp.get("QueueUrls", []):
            queue_dict = dict()
            queue_dict["QueueUrl"] = queue_url
            queue_dict["Tags"] = get_sqs_queue_tags(client, queue_url)
            queue_dict["Attributes"] = get_sqs_queue_attributes(client, queue_url)
            arn = queue_dict["Attributes"]["QueueArn"]
            queues[arn] = queue_dict
        return ListFromAWSResult(resources=queues)


def get_sqs_queue_tags(client: BaseClient, queue_url: str) -> List[Dict[str, str]]:
    """Get SQS queue tagging"""
    try:
        # {"a":"b","c":"d"} -> [{Key:"a",Value:"b"},...]
        tags = client.list_queue_tags(QueueUrl=queue_url).get("Tags", {})
        tagList = []
        for attr, value in tags.items():
            tagList.append(dict(Key=attr, Value=value))
        return tagList
    except ClientError as c_e:
        raise c_e


def get_sqs_queue_attributes(
    client: BaseClient, queue_url: str
) -> List[Dict[str, str]]:
    """Get SQS queue attributes"""
    try:
        return client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])[
            "Attributes"
        ]
    except ClientError as c_e:
        raise c_e
