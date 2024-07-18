import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic_settings import BaseSettings

from resource_graph.altimeter.aws.log_events import AWSLogEvents
from resource_graph.altimeter.aws.resource_service_region_mapping import (
    build_aws_resource_region_mapping_repo,
)
from resource_graph.altimeter.aws.scan.muxer import AWSScanMuxer
from resource_graph.altimeter.aws.scan.scan import run_scan
from resource_graph.altimeter.core.artifact_io.reader import ArtifactReader
from resource_graph.altimeter.core.artifact_io.writer import ArtifactWriter, GZIP
from resource_graph.altimeter.core.config import AWSConfig
from resource_graph.altimeter.core.log import Logger

from resource_graph.altimeter.core.neptune.client import GraphMetadata


class AWS2NConfig(BaseSettings):
    config_path: str
    account_scan_lambda_name: str
    account_scan_lambda_timeout: int


@dataclass(frozen=True)
class AWS2NResult:
    rdf_path: str
    graph_metadata: Optional[GraphMetadata]
    json_path: Optional[str] = None


def generate_scan_id() -> str:
    """Generate a unique scan id"""
    now = datetime.now()
    scan_date = now.strftime("%Y%m%d")
    scan_time = str(int(now.timestamp()))
    scan_id = "/".join((scan_date, scan_time, str(uuid.uuid4())))
    return scan_id


def aws2n(scan_id: str, config: AWSConfig, muxer: AWSScanMuxer) -> AWS2NResult:
    """Scan AWS resources to json and convert to RDF"""
    artifact_reader = ArtifactReader.from_artifact_path(config.artifact_path)
    artifact_writer = ArtifactWriter.from_artifact_path(
        artifact_path=config.artifact_path, scan_id=scan_id
    )

    aws_resource_region_mapping_repo = build_aws_resource_region_mapping_repo(
        global_region_whitelist=config.scan.regions,
        preferred_account_scan_regions=config.scan.preferred_account_scan_regions,
        services_regions_json_url=config.services_regions_json_url,
    )

    logger = Logger()
    logger.info(
        AWSLogEvents.ScanConfigured,
        config=str(config),
        reader=str(artifact_reader.__class__),
        writer=str(artifact_writer.__class__),
    )
    scan_manifest, graph_set = run_scan(
        muxer=muxer,
        config=config,
        aws_resource_region_mapping_repo=aws_resource_region_mapping_repo,
        artifact_writer=artifact_writer,
        artifact_reader=artifact_reader,
    )
    json_path = scan_manifest.master_artifact
    rdf_path = artifact_writer.write_graph_set(name="master", graph_set=graph_set)
    graph_metadata = None

    return AWS2NResult(
        rdf_path=rdf_path, graph_metadata=graph_metadata, json_path=json_path
    )
