from typing import Type, Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from resource_graph.altimeter.aws.resource.resource_spec import (
    ListFromAWSResult,
    AWSResourceSpec,
)
from resource_graph.altimeter.aws.resource.ssm import SSMResourceSpec
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.schema import Schema


class SSMParameterResourceSpec(SSMResourceSpec):
    type_name = "parameter"

    schema = Schema(
        ScalarField("Name"),
        ScalarField("Type"),
        ScalarField("Value"),
        ScalarField("Version"),
        ScalarField("LastModifiedDate"),
        ScalarField("DataType"),
        ScalarField("ARN"),
        ScalarField("Description", optional=True),
    )

    @classmethod
    def list_from_aws(
        cls: Type["AWSResourceSpec"], client: BaseClient, account_id: str, region: str
    ) -> ListFromAWSResult:
        parameters_resp = client.describe_parameters()
        parameters = {}

        for parameter in parameters_resp.get("Parameters", []):
            parameter_details = get_ssm_parameter_details(client, parameter["Name"])
            if "description" in parameter:
                parameter_details["description"] = parameter["description"]
            parameters[parameter_details["ARN"]] = parameter_details
        return ListFromAWSResult(resources=parameters)


def get_ssm_parameter_details(client: BaseClient, name: str) -> Dict[str, str]:
    """Get SNS queue attributes"""
    try:
        return client.get_parameter(Name=name)["Parameter"]
    except ClientError as c_e:
        raise c_e
