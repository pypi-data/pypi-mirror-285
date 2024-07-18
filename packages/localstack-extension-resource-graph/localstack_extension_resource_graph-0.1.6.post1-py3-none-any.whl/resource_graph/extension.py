import logging

from localstack.extensions.api import Extension, http
from localstack.services.internal import get_internal_apis
from localstack import config

from resource_graph.server.request_handler import RequestHandler
from resource_graph.util import Routes, Submount, Subdomain
from resource_graph.server.web import WebApp

LOG = logging.getLogger(__name__)


class ResourceGraph(Extension):
    name = "resource-graph"

    def update_gateway_routes(self, router: http.Router[http.RouteHandler]):

        LOG.info("Adding route for %s", self.name)
        get_internal_apis().add(RequestHandler())
        get_internal_apis().add(WebApp())
        from localstack.aws.handlers.cors import ALLOWED_CORS_ORIGINS

        webapp = Routes(WebApp())

        ALLOWED_CORS_ORIGINS.append(f"http://resource-graph.{config.LOCALSTACK_HOST}")
        ALLOWED_CORS_ORIGINS.append(f"https://resource-graph.{config.LOCALSTACK_HOST}")

        router.add(Submount("/resource-graph", webapp))
        router.add(Subdomain("resource-graph", webapp))
