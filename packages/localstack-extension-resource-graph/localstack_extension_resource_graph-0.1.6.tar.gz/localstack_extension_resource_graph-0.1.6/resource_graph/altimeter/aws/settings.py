"""AWS scan settings

Attributes:
    GRAPH_NAME: name for the AWS graph.
    GRAPH_VERSION: AWS graph version.  Generally this should change very rarely.
"""

GRAPH_NAME: str = "alti"
GRAPH_VERSION: str = "3"

SETTINGS_STR = """
# This configuration will cause altimeter to scan the currently logged in account.

artifact_path = "/tmp/resource_graph"
graph_name = "alti"
pruner_max_age_min = 4320 # prune graphs over 3 days old

[accessor]
    cache_creds = false

[scan]
    # accounts to scan
    accounts = ["000000000000"]
    # regions to scan. If empty, scan all available regions
    regions = ["us-east-1","eu-central-1"]
    # if true, discover and scan subaccounts of the above accounts
    scan_sub_accounts = false
    # preferred regions to use when scanning non-regional resources (e.g. IAM policies)
    preferred_account_scan_regions = [
        "us-east-1",
    ]
    ignored_resources = [
        "aws:support:severity-level",
        "aws:guardduty:detector",
    ]
[neptune]
    host = "localhost.localstack.cloud"
    port = "4511"
    region = "eu-central-1"

[concurrency]
    # The following settings control scan concurrency.
    #
    # In general, the maximum number of concurrent scan operations is
    #   max_account_scan_threads * max_svc_scan_threads
    max_account_scan_threads = 1            # number of account scan threads to spawn
    max_svc_scan_threads = 64               # the number of scan threads to spawn in each account scan thread
"""
