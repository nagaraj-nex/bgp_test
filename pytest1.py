import os
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api

os.environ['BFE_SSL_CERT'] = "nexbfe.crt"
BFE_HOST = "batfish.nexariacloud.com"
BFE_PORT = 443
bf = Session(host=BFE_HOST, port=BFE_PORT)

os.environ['BFE_SSL_CERT'] = "nexbfe.crt"
BFE_HOST = "batfish.nexariacloud.com"
BFE_PORT = 443
bf = Session(host=BFE_HOST, port=BFE_PORT)

REF_SNAPSHOT = ''
NEW_SNAPSHOT = ''
NETWORK_NAME="bgp_test_lab"
bf.set_network(NETWORK_NAME)

snapshots = bf.list_snapshots()
#case when tere are just 2 snapshots, where reference snapshot is called baseline and is manually uploaded
if len(snapshots) == 2:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
        else: NEW_SNAPSHOT = snapshot

def get_compare_metadata_results(bf: Session, snapshot_name: str, reference_snapshot_name: str):
    """
    Gets snapshot comparison results.
    Returns a map from comparison type to either a count of changes or whether that type has changed.
    """
    resp = bf._api_gw.GetSnapshotComparisonMetadata(
        api.GetSnapshotComparisonMetadataRequest(
            network_name=bf.network,
            snapshot_name=snapshot_name,
            reference_snapshot_name=reference_snapshot_name
        )
    )
    return resp

response = get_compare_metadata_results(bf, REF_SNAPSHOT, NEW_SNAPSHOT)
print(response)