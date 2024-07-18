from dataclasses import dataclass


@dataclass(frozen=True)
class GraphMetadata:
    """A GraphMetadata represents the details of a graph.
    These details are stored in a metadata graph in Neptune and used by clients
    to find the latest available successfuly loaded graph.

    Args:
        uri: graph uri
        name: graph name
        version: graph version
        start_time: epoch timestamp of graph start time
        end_time: epoch timestamp of graph end time
    """

    uri: str
    name: str
    version: str
    start_time: int
    end_time: int
