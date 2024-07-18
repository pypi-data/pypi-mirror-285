from typing import Type, List, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.account import AccountResourceSpec
from resource_graph.altimeter.aws.resource.awslambda.function import (
    LambdaFunctionResourceSpec,
)
from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.sns import SNSResourceSpec
from resource_graph.altimeter.aws.resource.sns.topic import SNSTopicResourceSpec
from resource_graph.altimeter.aws.resource.sqs.queue import SQSQueueResourceSpec
from resource_graph.altimeter.core.graph.field.dict_field import AnonymousDictField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    ResourceLinkField,
    MultiOptionalResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class SNSSubscriptionResourceSpec(SNSResourceSpec):
    type_name = "subscription"

    schema = Schema(
        ScalarField("SubscriptionArn"),
        ResourceLinkField("Owner", AccountResourceSpec),
        ScalarField("Protocol"),
        MultiOptionalResourceLinkField(
            "Endpoint",
            ScalarField,
            [
                LambdaFunctionResourceSpec,
                SQSQueueResourceSpec,
            ],
        ),
        ResourceLinkField("TopicArn", SNSTopicResourceSpec, value_is_id=True),
        ScalarField("DeliveryPolicy", optional=True),
        ScalarField("FilterPolicy", optional=True),
        ScalarField("RawMessageDelivery", optional=True),
        ScalarField("RedrivePolicy", optional=True),
        ScalarField("SubscriptionRoleArn", optional=True),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        subscriptions_res = client.list_subscriptions()
        subscriptions = dict()
        for subscription in subscriptions_res.get("Subscriptions", []):
            arn = subscription["SubscriptionArn"]
            subscription = get_sns_subscription_attributes(client, arn)
            subscriptions[arn] = subscription
        return ListFromAWSResult(resources=subscriptions)


def get_sns_subscription_attributes(
    client: BaseClient, subscription_arn: str
) -> List[Dict[str, str]]:
    """Get SNS subscription attributes"""
    try:
        return client.get_subscription_attributes(SubscriptionArn=subscription_arn)[
            "Attributes"
        ]
    except ClientError as c_e:
        raise c_e
