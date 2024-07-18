"""AWS Resource classes."""

from typing import Tuple, Type

from resource_graph.altimeter.aws.resource.cloudwatch.metric import (
    CloudwatchMetricResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_identity.identity_pool import (
    CognitoIdentityIdentityPoolResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp.group import (
    CognitoIDPGroupResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp.user import (
    CognitoIDPUserResourceSpec,
)
from resource_graph.altimeter.aws.resource.cognito_idp.user_pools import (
    CognitoIDPUserPoolResourceSpec,
)
from resource_graph.altimeter.aws.resource.ecs.cluster import ECSClusterResourceSpec
from resource_graph.altimeter.aws.resource.ecs.container_instance import (
    ECSContainerInstanceResourceSpec,
)
from resource_graph.altimeter.aws.resource.ecs.service import ECSServiceResourceSpec
from resource_graph.altimeter.aws.resource.ecs.task import ECSTaskResourceSpec
from resource_graph.altimeter.aws.resource.ecs.task_definition import (
    ECSTaskDefinitionResourceSpec,
)
from resource_graph.altimeter.aws.resource.rds.cluster import RDSClusterResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec
from resource_graph.altimeter.aws.resource.account import AccountResourceSpec
from resource_graph.altimeter.aws.resource.acm.certificate import (
    ACMCertificateResourceSpec,
)
from resource_graph.altimeter.aws.resource.awslambda.function import (
    LambdaFunctionResourceSpec,
)
from resource_graph.altimeter.aws.resource.cloudtrail.trail import (
    CloudTrailTrailResourceSpec,
)
from resource_graph.altimeter.aws.resource.dynamodb.dynamodb_table import (
    DynamoDbTableResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.flow_log import FlowLogResourceSpec
from resource_graph.altimeter.aws.resource.ec2.image import EC2ImageResourceSpec
from resource_graph.altimeter.aws.resource.ec2.instance import EC2InstanceResourceSpec
from resource_graph.altimeter.aws.resource.ec2.internet_gateway import (
    InternetGatewayResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.network_interface import (
    EC2NetworkInterfaceResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.region import RegionResourceSpec
from resource_graph.altimeter.aws.resource.ec2.route_table import (
    EC2RouteTableResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.transit_gateway_vpc_attachment import (
    TransitGatewayVpcAttachmentResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.security_group import (
    SecurityGroupResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.snapshot import EBSSnapshotResourceSpec
from resource_graph.altimeter.aws.resource.ec2.subnet import SubnetResourceSpec
from resource_graph.altimeter.aws.resource.ec2.transit_gateway import (
    TransitGatewayResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.volume import EBSVolumeResourceSpec
from resource_graph.altimeter.aws.resource.ec2.vpc import VPCResourceSpec
from resource_graph.altimeter.aws.resource.ec2.vpc_endpoint import (
    VpcEndpointResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.vpc_endpoint_service import (
    VpcEndpointServiceResourceSpec,
)
from resource_graph.altimeter.aws.resource.ec2.vpc_peering_connection import (
    VPCPeeringConnectionResourceSpec,
)
from resource_graph.altimeter.aws.resource.elbv1.load_balancer import (
    ClassicLoadBalancerResourceSpec,
)
from resource_graph.altimeter.aws.resource.elbv2.load_balancer import (
    LoadBalancerResourceSpec,
)
from resource_graph.altimeter.aws.resource.elbv2.target_group import (
    TargetGroupResourceSpec,
)
from resource_graph.altimeter.aws.resource.eks.cluster import EKSClusterResourceSpec
from resource_graph.altimeter.aws.resource.events.cloudwatchevents_rule import (
    EventsRuleResourceSpec,
)
from resource_graph.altimeter.aws.resource.events.event_bus import EventBusResourceSpec
from resource_graph.altimeter.aws.resource.guardduty.detector import (
    DetectorResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.account_password_policy import (
    IAMAccountPasswordPolicyResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.group import IAMGroupResourceSpec
from resource_graph.altimeter.aws.resource.iam.iam_oidc_provider import (
    IAMOIDCProviderResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.iam_saml_provider import (
    IAMSAMLProviderResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.instance_profile import (
    InstanceProfileResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.policy import (
    IAMPolicyResourceSpec,
    IAMAWSManagedPolicyResourceSpec,
)
from resource_graph.altimeter.aws.resource.iam.role import IAMRoleResourceSpec
from resource_graph.altimeter.aws.resource.iam.user import IAMUserResourceSpec
from resource_graph.altimeter.aws.resource.kms.key import KMSKeyResourceSpec
from resource_graph.altimeter.aws.resource.organizations.org import OrgResourceSpec
from resource_graph.altimeter.aws.resource.organizations.ou import OUResourceSpec
from resource_graph.altimeter.aws.resource.organizations.account import (
    OrgsAccountResourceSpec,
)
from resource_graph.altimeter.aws.resource.rds.instance import RDSInstanceResourceSpec
from resource_graph.altimeter.aws.resource.rds.snapshot import RDSSnapshotResourceSpec
from resource_graph.altimeter.aws.resource.route53.hosted_zone import (
    HostedZoneResourceSpec,
)
from resource_graph.altimeter.aws.resource.s3.bucket import S3BucketResourceSpec
from resource_graph.altimeter.aws.resource.secrets_manager.secrets import (
    SecretsmanagerSecretResourceSpec,
)
from resource_graph.altimeter.aws.resource.sns.subscription import (
    SNSSubscriptionResourceSpec,
)
from resource_graph.altimeter.aws.resource.sns.topic import SNSTopicResourceSpec
from resource_graph.altimeter.aws.resource.sqs.queue import SQSQueueResourceSpec
from resource_graph.altimeter.aws.resource.ssm.parameter import SSMParameterResourceSpec
from resource_graph.altimeter.aws.resource.support.severity_level import (
    SeverityLevelResourceSpec,
)

# To enable a resource to be scanned, add it here
DEFAULT_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    ACMCertificateResourceSpec,
    ClassicLoadBalancerResourceSpec,
    CloudTrailTrailResourceSpec,
    CloudwatchMetricResourceSpec,
    CognitoIdentityIdentityPoolResourceSpec,
    CognitoIDPGroupResourceSpec,
    CognitoIDPUserResourceSpec,
    CognitoIDPUserPoolResourceSpec,
    DetectorResourceSpec,
    DynamoDbTableResourceSpec,
    # EBSSnapshotResourceSpec, LS seems to spam snapshots, so we disable them here
    EBSVolumeResourceSpec,
    EC2ImageResourceSpec,
    EC2InstanceResourceSpec,
    EC2NetworkInterfaceResourceSpec,
    EC2RouteTableResourceSpec,
    ECSContainerInstanceResourceSpec,
    ECSClusterResourceSpec,
    ECSServiceResourceSpec,
    ECSTaskDefinitionResourceSpec,
    ECSTaskResourceSpec,
    EventBusResourceSpec,
    EventsRuleResourceSpec,
    FlowLogResourceSpec,
    IAMAccountPasswordPolicyResourceSpec,
    IAMAWSManagedPolicyResourceSpec,
    IAMGroupResourceSpec,
    IAMPolicyResourceSpec,
    IAMRoleResourceSpec,
    IAMOIDCProviderResourceSpec,
    IAMSAMLProviderResourceSpec,
    IAMUserResourceSpec,
    InstanceProfileResourceSpec,
    InternetGatewayResourceSpec,
    KMSKeyResourceSpec,
    LambdaFunctionResourceSpec,
    LoadBalancerResourceSpec,
    RDSClusterResourceSpec,
    RDSInstanceResourceSpec,
    RDSSnapshotResourceSpec,
    HostedZoneResourceSpec,
    S3BucketResourceSpec,
    SecurityGroupResourceSpec,
    SecretsmanagerSecretResourceSpec,
    SeverityLevelResourceSpec,
    SNSSubscriptionResourceSpec,
    SNSTopicResourceSpec,
    SQSQueueResourceSpec,
    SSMParameterResourceSpec,
    SubnetResourceSpec,
    TargetGroupResourceSpec,
    TransitGatewayResourceSpec,
    TransitGatewayVpcAttachmentResourceSpec,
    VPCPeeringConnectionResourceSpec,
    VPCResourceSpec,
    VpcEndpointResourceSpec,
    VpcEndpointServiceResourceSpec,
)

INFRA_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    AccountResourceSpec,
    RegionResourceSpec,
)

ORG_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    OrgResourceSpec,
    OrgsAccountResourceSpec,
    OUResourceSpec,
)

ALL_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    DEFAULT_RESOURCE_SPEC_CLASSES
    + INFRA_RESOURCE_SPEC_CLASSES
    + ORG_RESOURCE_SPEC_CLASSES
)
