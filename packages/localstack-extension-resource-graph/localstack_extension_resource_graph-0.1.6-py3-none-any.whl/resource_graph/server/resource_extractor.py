import logging
import re
import xml.etree.ElementTree as ET
from typing import List, Type

from gremlin_python.driver.protocol import GremlinServerError
from gremlin_python.process.traversal import T
from localstack.utils.objects import singleton_factory

from resource_graph.altimeter.aws.settings import GRAPH_NAME

LOG = logging.getLogger(__name__)
LS_WEB_BASE_URL = "localhost.localstack.cloud"
WEB_SOCKET_PROTOCOL = "ws"
WEB_SOCKET_SECURE_PROTOCOL = "wss"
LOCALHOST_IP_ADDRESS = "127.0.0.1"
TRAVERSAL_SOURCE = "g"

RDF_DESCRIPTION_TAG = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
RDF_RESOURCE_TAG = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
RDF_NODE_ID_TAG = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID"


class ResourceExtractor:

    def __init__(self):
        self.arn_dict = dict()
        self.scanning = False
        self.importing = False
        self.error = False

    @staticmethod
    @singleton_factory
    def get() -> "ResourceExtractor":
        """
        Returns a singleton instance of the ResourceExtractor.

        :return: a resource extractor singleton
        """
        return ResourceExtractor()

    def _reset_with_error(self):
        self.scanning = False
        self.importing = False
        self.error = True

    def _extract_service_name(self, arn: str):
        pattern = (
            r"arn:aws:([^:]+):"  # Match anything after "arn:aws:" until the next colon
        )
        # Search for the pattern in the ARN
        match = re.match(pattern, arn)
        if match:
            return match.group(1)
        else:
            return None

    def get_compute_status(self):
        return self.scanning, self.importing, self.error

    def get_arn_dict(self):
        return self.arn_dict

    def start_scanner(self, regions=None):

        if regions is None:
            regions = []
        self.scanning = True

        from resource_graph.altimeter.aws.aws2n import generate_scan_id, aws2n
        from resource_graph.altimeter.aws.resource.resource_spec import AWSResourceSpec
        from resource_graph.altimeter.aws.scan.muxer.local_muxer import (
            LocalAWSScanMuxer,
        )
        from resource_graph.altimeter.aws.scan.settings import (
            DEFAULT_RESOURCE_SPEC_CLASSES,
        )
        from resource_graph.altimeter.core.config import AWSConfig
        from resource_graph.altimeter.aws.settings import SETTINGS_STR

        config = AWSConfig.from_str(SETTINGS_STR)
        if len(regions) > 0:
            config.scan.regions = regions

        if config.scan.ignored_resources:
            resource_spec_classes_list: List[Type[AWSResourceSpec]] = []
            for resource_spec_class in DEFAULT_RESOURCE_SPEC_CLASSES:
                if (
                    resource_spec_class.get_full_type_name()
                    not in config.scan.ignored_resources
                ):
                    resource_spec_classes_list.append(resource_spec_class)
            resource_spec_classes = tuple(resource_spec_classes_list)
        else:
            resource_spec_classes = DEFAULT_RESOURCE_SPEC_CLASSES
        scan_id = generate_scan_id()
        muxer = LocalAWSScanMuxer(
            scan_id=scan_id,
            config=config,
            resource_spec_classes=resource_spec_classes,
        )
        try:
            result = aws2n(scan_id=scan_id, config=config, muxer=muxer)
            self.scanning = False
            return None, result.rdf_path
        except Exception as ex:
            self._reset_with_error()
            LOG.error(ex)
            return ex, ""

    def read_xml_blocks(self, file_path: str, neptune_port: str):
        self.importing = True

        try:
            from localstack.pro.core.config import NEPTUNE_USE_SSL
        except ImportError:
            # TODO remove once we don't need compatibility with <3.6 anymore
            from localstack_ext.config import NEPTUNE_USE_SSL

        from gremlin_python.driver import client

        if NEPTUNE_USE_SSL:
            endpoint = LS_WEB_BASE_URL
            protocol = WEB_SOCKET_SECURE_PROTOCOL
        else:
            endpoint = LOCALHOST_IP_ADDRESS
            protocol = WEB_SOCKET_PROTOCOL

        conn_string = f"{protocol}://{endpoint}:{neptune_port}/gremlin"
        try:
            neptune_client = client.Client(conn_string, TRAVERSAL_SOURCE)
        except Exception as e:
            self._reset_with_error()
            raise Exception(e)
        tree = ET.parse(file_path)

        root = tree.getroot()
        edges = []
        for description in root.findall(RDF_DESCRIPTION_TAG):
            commandObj = {"label": "", "properties": []}
            vertexID = list(description.attrib.values())[0]
            isNodeID = list(description.attrib)[0].split("}")[1] == "nodeID"
            if vertexID.startswith("arn:aws"):
                service_name = self._extract_service_name(vertexID)
                if service_name:
                    if service_name not in self.arn_dict:
                        self.arn_dict[service_name] = []
                    self.arn_dict[service_name].append(vertexID)

            for child in description:
                tag = child.tag.split("}")[1]
                linkId = child.get(RDF_RESOURCE_TAG) or child.get(RDF_NODE_ID_TAG)
                resource = child.get(RDF_RESOURCE_TAG)
                if tag == "type" and resource is not None:
                    commandObj["label"] = (
                        f"g.addV('{resource.replace(f'{GRAPH_NAME}:', '')}')"
                    )
                    commandObj["properties"].insert(
                        0, f".property({T.id},'{vertexID}')"
                    )
                elif tag == "arn" and isNodeID:
                    edges.append(
                        f"g.V('{vertexID}').addE('{tag}').to(V('{child.text}'))"
                    )
                elif linkId is not None:
                    edges.append(
                        f"g.V('{vertexID}').addE('{tag}').to(V('{linkId}'))"
                    )
                else:
                    if tag != "id":
                        commandObj["properties"].append(
                            f".property('{tag}','{child.text}')"
                        )
            finalCommand = commandObj["label"] + "".join(commandObj["properties"])
            try:
                neptune_client.submit(finalCommand).all().result()
            except Exception as e:
                self._reset_with_error()
                raise Exception(e)
        for edge in edges:
            try:
                # Attempt to submit the edge
                neptune_client.submit(edge).all().result()
            except GremlinServerError as e:
                LOG.error("An error occurred while submitting the edge: %s", e)
        self.importing = False
