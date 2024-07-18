from typing import Type, List, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.account import AccountResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.sns import SNSResourceSpec
from resource_graph.altimeter.core.graph.field.dict_field import AnonymousDictField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class SNSTopicResourceSpec(SNSResourceSpec):
    type_name = "topic"

    schema = Schema(
        AnonymousDictField(
            "Attributes",
            ResourceLinkField("Owner", AccountResourceSpec),
            ScalarField("Policy"),
            ScalarField("TopicArn"),
            ScalarField("DisplayName"),
            ScalarField("SubscriptionsPending"),
            ScalarField("SubscriptionsConfirmed"),
            ScalarField("SubscriptionsDeleted"),
            ScalarField("DeliveryPolicy"),
            ScalarField("EffectiveDeliveryPolicy"),
        ),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        topics_resp = client.list_topics()
        topics = dict()
        for topic in topics_resp.get("Topics", []):
            arn = topic["TopicArn"]
            topic["Tags"] = get_sns_topic_tags(client, arn)
            topic["Attributes"] = get_sns_topic_attributes(client, topic["TopicArn"])
            topics[arn] = topic
        return ListFromAWSResult(resources=topics)


def get_sns_topic_tags(client: BaseClient, topic_arn: str) -> List[Dict[str, str]]:
    """Get SNS topic tagging"""
    try:
        return client.list_tags_for_resource(ResourceArn=topic_arn).get("Tags", [])
    except ClientError as c_e:
        raise c_e


def get_sns_topic_attributes(
    client: BaseClient, topic_arn: str
) -> List[Dict[str, str]]:
    """Get SNS topic attributes"""
    try:
        return client.get_topic_attributes(TopicArn=topic_arn)["Attributes"]
    except ClientError as c_e:
        raise c_e
