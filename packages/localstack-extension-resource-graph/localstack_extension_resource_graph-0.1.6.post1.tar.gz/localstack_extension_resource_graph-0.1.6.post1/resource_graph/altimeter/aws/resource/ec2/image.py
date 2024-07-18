"""Resource for EC2Images (AMIs)"""

from typing import Type

from botocore.client import BaseClient

from resource_graph.altimeter.aws.resource.resource_spec import ListFromAWSResult
from resource_graph.altimeter.aws.resource.ec2 import EC2ResourceSpec
from resource_graph.altimeter.core.graph.field.scalar_field import ScalarField
from resource_graph.altimeter.core.graph.field.tags_field import TagsField
from resource_graph.altimeter.core.graph.schema import Schema


class EC2ImageResourceSpec(EC2ResourceSpec):
    """Resource for EC2Images (AMIs)"""

    type_name = "image"
    schema = Schema(
        ScalarField("Name", optional=True),
        ScalarField("Description", optional=True),
        ScalarField("Public"),
        TagsField(),
    )

    @classmethod
    def list_from_aws(
        cls: Type["EC2ImageResourceSpec"],
        client: BaseClient,
        account_id: str,
        region: str,
    ) -> ListFromAWSResult:
        """Return a dict of dicts of the format:

            {'image_1_arn': {image_1_dict},
             'image_2_arn': {image_2_dict},
             ...}

        Where the dicts represent results from describe_images."""
        images = {}
        resp = client.describe_images(Owners=["self"])
        for image in resp["Images"]:
            image_id = image["ImageId"]
            resource_arn = cls.generate_arn(
                account_id=account_id, region=region, resource_id=image_id
            )
            images[resource_arn] = image
        return ListFromAWSResult(resources=images)
