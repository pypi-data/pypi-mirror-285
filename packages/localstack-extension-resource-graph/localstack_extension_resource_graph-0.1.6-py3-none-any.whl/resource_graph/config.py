from localstack.constants import INTERNAL_RESOURCE_PATH

# handler path within the internal /_localstack endpoint
RESOURCE_GRAPH_PATH = f"{INTERNAL_RESOURCE_PATH}/resource-graph/"
GENERATE_GRAPH_PATH = f"{RESOURCE_GRAPH_PATH}/generate"
IMPORT_GRAPH_PATH = f"{RESOURCE_GRAPH_PATH}/import"
GET_ARNS_PATH = f"{RESOURCE_GRAPH_PATH}/arns"
GET_SUPPORTED_RESOURCES = f"{RESOURCE_GRAPH_PATH}/supported-resources"
COMPUTE_STATUS_PATH = f"{RESOURCE_GRAPH_PATH}/status"
