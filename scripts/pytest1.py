import os
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
print(SCRIPT_DIR)
os.environ['BFE_SSL_CERT'] = SCRIPT_DIR+'/../cert/test.crt'

BFE_HOST = "batfish.nexariacloud.com"
BFE_PORT = 443
bf = Session(host=BFE_HOST, port=BFE_PORT)
if bf:
    print()
    print("***********************************************")
    print("Created BFE session on host {}".format(BFE_HOST))
    print("***********************************************")
    print()

REF_SNAPSHOT = ''
NEW_SNAPSHOT = ''
NETWORK_NAME="bgp_test_lab"
bf.set_network(NETWORK_NAME)
print()
print("***********************************************")
print("Network is set as {}".format(NETWORK_NAME))
print("***********************************************")
print()


snapshots = bf.list_snapshots()
#case when tere are just 2 snapshots, where reference snapshot is called baseline and is manually uploaded
if len(snapshots) == 2:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
        else: NEW_SNAPSHOT = snapshot
else:
    for snapshot in snapshots:
        if snapshot.startswith('baseline'):
            REF_SNAPSHOT = snapshot
            break
    NEW_SNAPSHOT = snapshots[0]

print()
print("***********************************************")
print("Snapshots being compared are {}, {}".format(REF_SNAPSHOT, NEW_SNAPSHOT))
print("***********************************************")
print()

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