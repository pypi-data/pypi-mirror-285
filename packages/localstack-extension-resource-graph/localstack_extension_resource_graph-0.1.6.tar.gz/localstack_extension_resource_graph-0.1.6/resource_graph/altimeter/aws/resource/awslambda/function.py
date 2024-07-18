"""Resource for LambdaFunctions"""

from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.resource_spec import ListFromAWSResult
from resource_graph.altimeter.aws.resource.ec2.vpc import VPCResourceSpec
from resource_graph.altimeter.aws.resource.awslambda import LambdaResourceSpec
from resource_graph.altimeter.aws.resource.iam.role import IAMRoleResourceSpec
from resource_graph.altimeter.core.graph.field.dict_field import AnonymousDictField
from resource_graph.altimeter.core.graph.field.resource_link_field import (
    TransientResourceLinkField,
)
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.schema import Schema


class LambdaFunctionResourceSpec(LambdaResourceSpec):
    """Resource for Lambda Functions"""

    type_name = "function"
    schema = Schema(
        ScalarField("FunctionName"),
        ScalarField("Runtime", optional=True),
        AnonymousDictField(
            "VpcConfig",
            TransientResourceLinkField("VpcId", VPCResourceSpec, optional=True),
            optional=True,
        ),
        TransientResourceLinkField("Role", IAMRoleResourceSpec, value_is_id=True),
    )

    @classmethod
    def list_from_aws(
        cls: Type["LambdaFunctionResourceSpec"],
        client: BaseClient,
        account_id: str,
        region: str,
    ) -> ListFromAWSResult:
        """Return a dict of dicts of the format:

            {'function_1_arn': {function_1_dict},
             'function_2_arn': {function_2_dict},
             ...}

        Where the dicts represent results from list_functions."""
        functions = {}
        paginator = client.get_paginator("list_functions")
        for resp in paginator.paginate():
            for function in resp.get("Functions", []):
                resource_arn = function["FunctionArn"]
                functions[resource_arn] = function
        return ListFromAWSResult(resources=functions)
