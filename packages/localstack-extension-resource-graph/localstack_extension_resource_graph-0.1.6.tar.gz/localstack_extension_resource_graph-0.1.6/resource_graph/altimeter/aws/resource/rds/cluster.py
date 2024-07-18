"""Resource for RDS"""

from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.rds import RDSResourceSpec
from resource_graph.altimeter.aws.resource.resource_spec import ListFromAWSResult
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class RDSClusterResourceSpec(RDSResourceSpec):
    """Resource for RDS"""

    type_name = "cluster"
    schema = Schema(
        TagsField(),
        ScalarField("AllocatedStorage"),
        ScalarField("DatabaseName", optional=True),
        ScalarField("DBClusterIdentifier"),
        ScalarField("DBClusterParameterGroup"),
        ScalarField("Status"),
        ScalarField("Endpoint"),
        ScalarField("ReaderEndpoint"),
        ScalarField("MultiAZ"),
        ScalarField("Engine"),
        ScalarField("EngineVersion"),
        ScalarField("Port"),
        ScalarField("MasterUsername"),
        ScalarField("StorageEncrypted"),
        ScalarField("DbClusterResourceId"),
        ScalarField("DBClusterArn"),
        ScalarField("IAMDatabaseAuthenticationEnabled"),
        # TODO re-add this once figure out how to support it since VPC
        # might be in another regions but you do not have info on which one
        # ListField(
        #     "VpcSecurityGroups",
        #     EmbeddedDictField(
        #         TransientResourceLinkField("VpcSecurityGroupId", SecurityGroupResourceSpec),
        #         ScalarField("Status")
        #     )
        # ),
    )

    @classmethod
    def list_from_aws(
        cls: Type["RDSClusterResourceSpec"],
        client: BaseClient,
        account_id: str,
        region: str,
    ) -> ListFromAWSResult:
        dbclusters = {}
        paginator = client.get_paginator("describe_db_clusters")
        for resp in paginator.paginate():
            for db in [x for x in resp.get("DBClusters", [])]:
                resource_arn = db["DBClusterArn"]
                dbclusters[resource_arn] = db
        return ListFromAWSResult(resources=dbclusters)
