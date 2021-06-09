import os
import json
from pybfe.client.session import Session
from intentionet.bfe.proto import api_gateway_pb2 as api

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
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
NETWORK_NAME="NEX-BFE"
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
print("Snapshots being compared are {}, {}".format(NEW_SNAPSHOT, REF_SNAPSHOT))
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

def init_snapshot_comparison(bf: Session, snapshot_name: str, reference_snapshot_name: str):

    init_resp = bf._api_gw.InitSnapshotComparison(
        api.InitSnapshotComparisonRequest(
            network_name=bf.network,
            snapshot_name=snapshot_name,
            reference_snapshot_name=reference_snapshot_name
        )
    )

def get_result(resp):

    result = {}
    
    # pick some categories to embed in the result 
    result["device_configuration"] = resp.configurations.num_results
    result["devices"] = resp.devices.num_results
    result["interfaces"] = resp.interfaces.num_results
    result["increased_flows"] = resp.reachability.has_increased_flows
    result["decreased_flows"] = resp.reachability.has_decreased_flows
    result["devices_routing"] = resp.routes.num_results
    result["bgp_peer_attributes"] = resp.rp_bgp_peer_attributes.num_results
    result["bgp_process_attributes"] = resp.rp_bgp_process_attributes.num_results
    result["ospf_interface"] = resp.rp_ospf_interface.num_results
    result["ospf_neighbors"] = resp.rp_ospf_neighbors.num_results
    result["ospf_process"] = resp.rp_ospf_process.num_results

    print(json.dumps(result, indent=4))

response = get_compare_metadata_results(bf, NEW_SNAPSHOT, REF_SNAPSHOT)
print(response)
print("before if", response.uninitialized)
if response.uninitialized:
    init_snapshot_comparison(bf, NEW_SNAPSHOT, REF_SNAPSHOT)
    response = get_compare_metadata_results(bf, NEW_SNAPSHOT, REF_SNAPSHOT)
    print(response)
    print("before while", response.uninitialized)
    while response.uninitialized:
        response = get_compare_metadata_results(bf, NEW_SNAPSHOT, REF_SNAPSHOT)
        print(response)
        print("while", response.uninitialized)
    else: 
        get_result(response)
else:
    get_result(response)


