import json
import logging

from localstack.constants import (
    LOCALHOST_HOSTNAME,
)
from localstack.http import Request, route
from localstack.utils.strings import to_str

from resource_graph.altimeter.aws.scan.settings import DEFAULT_RESOURCE_SPEC_CLASSES
from resource_graph.config import (
    GENERATE_GRAPH_PATH,
    GET_ARNS_PATH,
    GET_SUPPORTED_RESOURCES,
    IMPORT_GRAPH_PATH,
    COMPUTE_STATUS_PATH,
)
from resource_graph.server.resource_extractor import ResourceExtractor

LOG = logging.getLogger(__name__)

DOMAIN_NAME = f"resource-graph.{LOCALHOST_HOSTNAME}"
ROUTE_HOST = f"{DOMAIN_NAME}<port:port>"


class RequestHandler:
    resource_extractor: ResourceExtractor
    rdf_path: str

    def __init__(self):
        self.resource_extractor = ResourceExtractor.get()
        self.rdf_path = None

    @route(GET_SUPPORTED_RESOURCES, methods=["GET"])
    def handle_get_supported_resources(self, request: Request, **kwargs):
        resList = []
        for x in DEFAULT_RESOURCE_SPEC_CLASSES:
            resList.append(f"{x.service_name}:{x.type_name}")
        return {"resources": sorted(resList)}

    @route(COMPUTE_STATUS_PATH, methods=["GET"])
    def handle_get_compute_status(self, request: Request, **kwargs):
        scanning, importing, error = self.resource_extractor.get_compute_status()
        return {"scanning": scanning, "importing": importing, "error": error}

    @route(GENERATE_GRAPH_PATH, methods=["GET"])
    def handle_generate_file(self, request: Request, **kwargs):
        e, path = self.resource_extractor.start_scanner()
        if not e:
            self.rdf_path = path
            return {"status": "success"}
        else:
            return {"status": "error", "error": e}

    @route(GET_ARNS_PATH, methods=["GET"])
    def handle_get_arns(self, request: Request, **kwargs):
        return self.resource_extractor.get_arn_dict()

    @route(IMPORT_GRAPH_PATH, methods=["POST"])
    def handle_replicate(self, request: Request, **kwargs):
        payload = _get_json(request)
        if "port" not in payload:
            return {"status": "error", "error": "missing neptune port in payload"}
        regions = payload["regions"] if "regions" in payload else []
        try:
            if not self.rdf_path:
                e, path = self.resource_extractor.start_scanner(regions)
                if e:
                    raise Exception(e)
                self.rdf_path = path
            self.resource_extractor.read_xml_blocks(self.rdf_path, payload["port"])
            return {"status": "success"}
        except Exception as e:
            LOG.error(e)
            return {"status": "error", "error": e}


def _get_json(request: Request) -> dict:
    try:
        return request.json
    except Exception:
        return json.loads(to_str(request.data))
