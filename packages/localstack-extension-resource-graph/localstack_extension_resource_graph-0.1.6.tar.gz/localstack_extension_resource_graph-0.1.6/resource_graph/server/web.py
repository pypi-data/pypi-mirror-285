import mimetypes
import os
from pathlib import Path

from flask import redirect
from localstack.constants import (
    APPLICATION_OCTET_STREAM,
    INTERNAL_RESOURCE_PATH,
    LOCALHOST_HOSTNAME,
)
from localstack.http import route, Request, Response

from resource_graph.server import ui as web_ui

DOMAIN_NAME = f"resource-graph.{LOCALHOST_HOSTNAME}"
ROUTE_HOST = f"{DOMAIN_NAME}<port:port>"


class WebApp:
    @route("/", methods=["GET"], host=ROUTE_HOST)
    def forward_from_root(self, request: Request, **kwargs):
        return redirect(f"{INTERNAL_RESOURCE_PATH}/resource-graph/index.html")

    @route(f"{INTERNAL_RESOURCE_PATH}/resource-graph", methods=["GET"])
    def forward_from_extension_root(self, request: Request, **kwargs):
        return redirect(f"{INTERNAL_RESOURCE_PATH}/resource-graph/index.html")

    @route("/favicon.png", methods=["GET"], host=ROUTE_HOST)
    def serve_favicon(self, request: Request, **kwargs):
        return self.serve_static_file("/favicon.png")

    @route(f"{INTERNAL_RESOURCE_PATH}/resource-graph/<path:path>", methods=["GET"])
    def get_web_asset(self, request: Request, path: str, **kwargs):
        return self.serve_static_file(path)

    def serve_static_file(self, path: str):
        file_path = os.path.join(os.path.dirname(web_ui.__file__), path.lstrip("/"))
        if not os.path.exists(file_path):
            return Response("File not found", 404)
        mime_type = mimetypes.guess_type(os.path.basename(path))
        mime_type = mime_type[0] if mime_type else APPLICATION_OCTET_STREAM
        return Response(Path(file_path).open(mode="rb"), mimetype=mime_type)
